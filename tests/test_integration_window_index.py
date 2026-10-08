import copy
from pathlib import Path
from unittest.mock import patch

import pytest

from cloudguard import integration, runtime_ml

ROOT = Path(__file__).resolve().parents[1]


class CountedWindows(list):
    def __init__(self, rows):
        super().__init__(rows)
        self.traversals = 0
        self.visits = 0

    def __iter__(self):
        self.traversals += 1
        for row in super().__iter__():
            self.visits += 1
            yield row


def replay(**options):
    return integration.replay(
        ROOT / "data/integration/redis-auth-only.yaml",
        [ROOT / "data/runtime/ml-baseline-synthetic.json"],
        ROOT / "data/runtime/ml-observation-synthetic.json",
        ROOT / "testbed/inventory.json",
        **({"runtime_ml": "isolation-forest"} | options),
    )


def test_comparator_mapping_has_one_index_traversal_after_validation():
    original = runtime_ml.compare_synthetic
    counted = []

    def observe(*args, **kwargs):
        report = original(*args, **kwargs)
        report["windows"] = CountedWindows(report["windows"])
        counted.append(report["windows"])
        return report

    with patch.object(runtime_ml, "compare_synthetic", side_effect=observe):
        result = replay()
    assert len(result["asset_contexts"]) == 4
    # One identity-validation traversal plus one mapping-index traversal.
    assert counted[0].traversals == 2
    assert counted[0].visits == 6
    expected = {
        context["asset_id"]: [
            i
            for i, row in enumerate(list.__iter__(counted[0]))
            if row["asset_id"] == context["asset_id"]
        ]
        for context in result["asset_contexts"]
    }
    assert {
        context["asset_id"]: context["runtime_comparator_window_indices"][
            "isolation_forest"
        ]
        for context in result["asset_contexts"]
    } == expected


def test_index_matches_legacy_mapping_without_mutating_reports():
    rows = [
        {"asset_id": "b", "start_epoch": 120, "status": "abstained"},
        {"asset_id": "a", "start_epoch": 60, "status": "scored"},
        {"asset_id": "b", "start_epoch": 60, "status": "scored"},
    ]
    reports = {"first": {"windows": rows}, "second": {"windows": list(reversed(rows))}}
    before = copy.deepcopy(reports)
    indexed = integration._index_comparator_windows(reports)
    for name, report in reports.items():
        for asset in ("a", "b", "missing"):
            assert indexed[name].get(asset, []) == [
                i for i, row in enumerate(report["windows"]) if row["asset_id"] == asset
            ]
    assert reports == before
    indexed["first"]["b"].clear()
    assert indexed["second"]["b"] == [0, 2]
    assert reports == before


def test_empty_report_index():
    assert integration._index_comparator_windows({}) == {}
    assert integration._index_comparator_windows({"empty": {"windows": []}}) == {
        "empty": {}
    }


def test_index_traversal_count_does_not_depend_on_asset_count():
    rows = CountedWindows(
        [{"asset_id": f"asset-{i % 50}", "start_epoch": i} for i in range(1000)]
    )
    indexed = integration._index_comparator_windows({"test": {"windows": rows}})
    assert len(indexed["test"]) == 50
    assert rows.traversals == 1 and rows.visits == 1000
    for i in range(50):
        assert indexed["test"][f"asset-{i}"] == list(range(i, 1000, 50))


@pytest.mark.parametrize("pipeline", [False, True])
def test_complete_report_matches_legacy_mapping(pipeline):
    def legacy(comparators):
        return {
            name: {
                asset: [
                    i
                    for i, row in enumerate(report["windows"])
                    if row["asset_id"] == asset
                ]
                for asset in {row["asset_id"] for row in report["windows"]}
            }
            for name, report in comparators.items()
        }

    options = dict(
        runtime_ml="both",
        engine1_pipeline=pipeline,
        kb=ROOT / "knowledge/sources.json" if pipeline else None,
    )
    optimized = replay(**options)
    with patch.object(integration, "_index_comparator_windows", side_effect=legacy):
        reference = replay(**options)
    if pipeline:
        # Existing pipeline timing is deliberately variable, not calculated evidence.
        optimized["engine1"].pop("timings_ms")
        reference["engine1"].pop("timings_ms")
    assert optimized == reference
