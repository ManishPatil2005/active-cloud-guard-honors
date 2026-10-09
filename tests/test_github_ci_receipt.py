import copy
import json
from unittest.mock import patch

import pytest

from cloudguard.process_runner import ProcessResult
from scripts import github_ci_receipt as module

RUN = "12345"
SHA = "a" * 40
DATA = {
    "databaseId": int(RUN),
    "headSha": SHA,
    "status": "completed",
    "conclusion": "success",
    "url": f"https://github.com/{module.REPOSITORY}/actions/runs/{RUN}",
    "jobs": [
        {
            "databaseId": index,
            "name": name,
            "status": "completed",
            "conclusion": "success",
            "steps": [
                {
                    "name": module.TEST_STEP,
                    "status": "completed",
                    "conclusion": "success",
                }
            ],
        }
        for index, name in enumerate(sorted(module.JOB_NAMES), 1)
    ],
}


def collect(data):
    with (
        patch.dict("os.environ", {"ACG_CI_RUN_ID": RUN, "ACG_CI_EXPECTED_SHA": SHA}),
        patch.object(
            module, "run_bounded", return_value=ProcessResult(0, json.dumps(data), "")
        ) as process,
    ):
        reports, code = module.collect(None)
    return reports["output"], code, process


def test_both_actual_test_steps_required_and_read_only_request():
    report, code, process = collect(DATA)
    assert code == 0 and report["both_regression_jobs_succeeded"] is True
    command = process.call_args.args[0]
    assert command[:4] == ["gh", "run", "view", RUN]
    assert command[5] == module.REPOSITORY
    assert process.call_args.kwargs == {"timeout": 30, "output_limit": 1_000_000}
    assert (
        report["production_ready"] is False
        and report["independent_evaluation"] is False
    )


@pytest.mark.parametrize(
    "change",
    [
        "failed_run",
        "failed_job",
        "skipped_test",
        "missing_test",
        "missing_job",
        "pending",
    ],
)
def test_partial_failed_skipped_missing_is_not_qualified(change):
    data = copy.deepcopy(DATA)
    if change == "failed_run":
        data["conclusion"] = "failure"
    elif change == "failed_job":
        data["jobs"][0]["conclusion"] = "failure"
    elif change == "skipped_test":
        data["jobs"][0]["steps"][0]["conclusion"] = "skipped"
    elif change == "missing_test":
        data["jobs"][0]["steps"] = []
    elif change == "missing_job":
        data["jobs"].pop()
    else:
        data["status"] = "in_progress"
    report, code, _ = collect(data)
    assert code == 1 and report["both_regression_jobs_succeeded"] is False


@pytest.mark.parametrize(
    "field,value",
    [
        ("databaseId", True),
        ("databaseId", 99),
        ("headSha", "b" * 40),
        ("url", "https://example.test"),
        ("status", "invented"),
        ("jobs", None),
    ],
)
def test_foreign_or_invalid_run_is_refused(field, value):
    data = copy.deepcopy(DATA)
    data[field] = value
    with pytest.raises(ValueError, match="identity/envelope"):
        collect(data)


def test_duplicate_jobs_and_regression_steps_refused():
    data = copy.deepcopy(DATA)
    data["jobs"][1] = copy.deepcopy(data["jobs"][0])
    with pytest.raises(ValueError, match="job identity"):
        collect(data)
    data = copy.deepcopy(DATA)
    data["jobs"][0]["steps"] *= 2
    with pytest.raises(ValueError, match="duplicate"):
        collect(data)


@pytest.mark.parametrize("run_id,sha", [("other/path", SHA), (RUN, "main"), ("", SHA)])
def test_invalid_selection_refused_before_any_network(run_id, sha):
    with (
        patch.dict("os.environ", {"ACG_CI_RUN_ID": run_id, "ACG_CI_EXPECTED_SHA": sha}),
        patch.object(module, "run_bounded") as process,
    ):
        with pytest.raises(ValueError, match="explicit"):
            module.collect(None)
    process.assert_not_called()


def test_existing_receipt_refused_before_selection_or_remote_read(tmp_path):
    output = tmp_path / "negative.json"
    output.write_bytes(b"failed CI history")
    with (
        patch("sys.argv", ["receipt", "--output", str(output)]),
        patch.object(module, "run_bounded") as process,
    ):
        assert module.evidence_main(module.collect) == 1
    process.assert_not_called()
    assert output.read_bytes() == b"failed CI history"
