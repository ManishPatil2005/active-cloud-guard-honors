"""Typed receipt consistency; invented facts are never research attestation."""

import copy
import json

import pytest

from cloudguard import runtime, runtime_receipts as receipts
from cloudguard.clock_check import compare
from cloudguard.runtime_intake import TYPED_PROTOCOL, inspect
from cloudguard.verification import load_inventory
from test_runtime_intake import ROOT, make_bundle, command, execute, save


@pytest.fixture
def typed(tmp_path):
    bundle = make_bundle(tmp_path)
    root, manifest = bundle
    manifest["schema_version"] = TYPED_PROTOCOL
    container = "f" * 64
    snapshot = dict(
        id=container,
        image="sha256:" + "0" * 64,
        started_at="2026-01-01T00:00:00Z",
        running=True,
        restarts=0,
        project="honors-cloud-guard",
        service="redis",
    )
    first = dict(wall_ns=1767312000 * 10**9, monotonic_mid_ns=10**9, sampling_span_ns=2)
    last = dict(
        wall_ns=first["wall_ns"] + 4 * 10**9,
        monotonic_mid_ns=5 * 10**9,
        sampling_span_ns=2,
    )
    clock = dict(first=first, last=last, **compare(first, last))
    trial = dict(
        fixture_only=True,
        image=receipts.IMAGE,
        container_id=container,
        deployment_binding_authenticated=False,
        raw_log_sha256="1" * 64,
        matched_event_count=12,
        event_type_counts=dict(execve=1, open=1, connect=10),
        target_identity_before=snapshot,
        target_identity_after=copy.deepcopy(snapshot),
        target_identity_stable=True,
        measurement=dict(
            timing_protocol="per_call_brackets_v1",
            start_unix_ns=first["wall_ns"],
            end_unix_ns=last["wall_ns"],
            clock_sampling=clock,
            elapsed_monotonic_ns=clock["elapsed_monotonic_ns"],
            clock_difference_ns=clock["clock_difference_ns"],
        ),
    )
    accounting = json.loads(
        (
            ROOT / "output/engine2-instrumented-normalized-20260928/accounting.json"
        ).read_text()
    )
    accounting.update(
        inventory_sha256=manifest["inventory"]["sha256"],
        raw_sha256=trial["raw_log_sha256"],
        line_count=12,
        diagnostic_line_count=0,
        validated_event_count=12,
        event_type_counts=dict(execve=1, open=1, connect=10),
    )
    refresh(bundle, accounting, trial)
    return bundle, accounting, trial


def refresh(bundle, accounting, trial):
    root, manifest = bundle
    trial_ref = save(root, "receipts/trial-source.json", trial)
    accounting["trial_sha256"] = trial_ref["sha256"]
    account_ref = save(root, "receipts/accounting-source.json", accounting)
    run = manifest["runs"][0]
    for kind in run["receipts"]:
        wrapper = dict(
            schema_version="runtime_receipt_v1",
            kind=kind,
            run_id=run["run_id"],
            capture_sha256=run["capture"]["sha256"],
            inventory_sha256=manifest["inventory"]["sha256"],
            collection_protocol="acg_falco_selected_v1",
            origin="synthetic_fixture",
            source=account_ref if kind == "accounting" else trial_ref,
        )
        run["receipts"][kind] = save(root, f"receipts/{kind}-wrapper.json", wrapper)


def check(typed):
    bundle, _, _ = typed
    return execute(bundle)


def test_typed_counts_identity_local_timing_are_not_eligibility(typed):
    report = check(typed)
    assert report["protocol"] == TYPED_PROTOCOL
    checks = report["runs"][0]["selected_receipt_checks"]
    assert checks["accounting"]["recorded_outcome"] == "normalized"
    assert checks["accounting"]["coverage_verified"] is False
    assert checks["identity"]["recorded_outcome"] == "stable"
    assert checks["identity"]["deployment_binding_authenticated"] is False
    assert checks["timing"]["local_clock_within_tolerance"] is True
    assert checks["timing"]["collector_alignment_verified"] is False
    assert report["unique_artifact_count"] == 8  # Shared source counted once.
    assert report["model_fitting_authorized"] is False
    assert report["independent_evaluation_verified"] is False
    assert report["runs"][0]["receipt_semantics_verified"] is False
    assert report["runs"][0]["evaluation_eligible"] is False
    assert report["actions_executed"] == []
    assert "honors-cloud-guard" not in json.dumps(report)
    assert "monotonic_mid_ns" not in json.dumps(report)
    assert "fixture_only" not in json.dumps(report)


@pytest.mark.parametrize("kind", ["accounting", "identity", "timing"])
def test_preserve_recorded_negative_outcomes(typed, kind):
    bundle, accounting, trial = typed
    if kind == "accounting":
        accounting.update(
            status="rejected",
            rejected_record_count=1,
            rejection_reasons=dict(event_result=1),
            line_count=13,
        )
    elif kind == "identity":
        trial["target_identity_after"]["restarts"] = 1
        trial["target_identity_stable"] = False
    else:
        clock = trial["measurement"]["clock_sampling"]
        clock["last"]["wall_ns"] += 100_000_000
        clock.update(compare(clock["first"], clock["last"]))
        trial["measurement"].update(
            end_unix_ns=clock["last"]["wall_ns"],
            clock_difference_ns=clock["clock_difference_ns"],
        )
    refresh(bundle, accounting, trial)
    report = check(typed)
    outcome = report["runs"][0]["selected_receipt_checks"][kind]["recorded_outcome"]
    assert outcome in ("rejected", "changed_or_not_running", "rejected_local_timing")
    assert report["model_fitting_authorized"] is False


@pytest.mark.parametrize("kind", ["accounting", "identity", "timing"])
def test_missing_typed_roles_stay_unknown(typed, kind):
    bundle, _, _ = typed
    bundle[1]["runs"][0]["receipts"][kind] = None
    report = check(typed)
    assert report["runs"][0]["missing_receipts"] == [kind]
    assert kind not in report["runs"][0]["selected_receipt_checks"]
    assert report["runs"][0]["evaluation_eligible"] is False


@pytest.mark.parametrize(
    "field,value",
    [
        ("schema_version", "unsupported"),
        ("kind", "timing"),
        ("run_id", "wrong"),
        ("capture_sha256", "0" * 64),
        ("inventory_sha256", "0" * 64),
        ("collection_protocol", "unknown"),
        ("origin", "recorded_projection"),
        ("extra", True),
    ],
)
def test_wrapper_context_rejected(typed, field, value):
    bundle, _, _ = typed
    root, manifest = bundle
    ref = manifest["runs"][0]["receipts"]["accounting"]
    wrapper = json.loads((root / ref["path"]).read_text())
    wrapper[field] = value
    manifest["runs"][0]["receipts"]["accounting"] = save(root, ref["path"], wrapper)
    with pytest.raises(ValueError):
        check(typed)


@pytest.mark.parametrize(
    "change", ["source_hash", "source_path", "source_self", "source_oversize", "opaque"]
)
def test_typed_source_boundary(typed, change):
    bundle, _, _ = typed
    root, manifest = bundle
    ref = manifest["runs"][0]["receipts"]["accounting"]
    wrapper = json.loads((root / ref["path"]).read_text())
    if change == "source_hash":
        wrapper["source"]["sha256"] = "0" * 64
    elif change == "source_path":
        wrapper["source"]["path"] = "../outside.json"
    elif change == "source_self":
        wrapper["source"] = ref
    elif change == "source_oversize":
        wrapper["source"] = save(
            root, "receipts/oversize-source.json", {"fixture": "x" * 1_000_000}
        )
    else:
        wrapper = {"declared_pass": True}
    manifest["runs"][0]["receipts"]["accounting"] = save(root, ref["path"], wrapper)
    with pytest.raises(ValueError):
        check(typed)


@pytest.mark.parametrize(
    "change",
    [
        "inventory",
        "total",
        "kinds",
        "reasons",
        "lines",
        "status",
        "boolean_count",
        "float_count",
        "unknown_kind",
        "positive_coverage",
        "actions",
    ],
)
def test_accounting_mismatch_or_unsupported_claims(typed, change):
    bundle, account, trial = typed
    if change == "inventory":
        account["inventory_sha256"] = "0" * 64
    elif change == "total":
        account["validated_event_count"] += 1
    elif change == "kinds":
        account["event_type_counts"]["connect"] -= 1
        account["event_type_counts"]["open"] += 1
    elif change == "reasons":
        account["rejection_reasons"] = dict(event_result=1)
    elif change == "lines":
        account["line_count"] += 1
    elif change == "status":
        account["receipt_counts_match"] = False
    elif change == "boolean_count":
        account["diagnostic_line_count"] = False
    elif change == "float_count":
        account["validated_event_count"] = 12.0
    elif change == "unknown_kind":
        account["event_type_counts"]["arbitrary"] = 0
    elif change == "positive_coverage":
        account["collection_coverage"] = "complete"
    else:
        account["actions_executed"] = ["isolate"]
    refresh(bundle, account, trial)
    with pytest.raises(ValueError):
        check(typed)


@pytest.mark.parametrize(
    "change",
    [
        "container",
        "image",
        "authenticated",
        "before_id",
        "after_id",
        "stable_flag",
        "stable_one",
        "running_one",
        "restart_float",
        "naive_time",
        "extra",
        "missing_after",
    ],
)
def test_identity_mismatch(typed, change):
    bundle, account, trial = typed
    if change == "container":
        trial["container_id"] = "a" * 64
    elif change == "image":
        trial["image"] = "unsupported"
    elif change == "authenticated":
        trial["deployment_binding_authenticated"] = True
    elif change == "before_id":
        trial["target_identity_before"]["id"] = "a" * 64
    elif change == "after_id":
        trial["target_identity_after"]["id"] = "a" * 64
    elif change == "stable_flag":
        trial["target_identity_stable"] = False
    elif change == "stable_one":
        trial["target_identity_stable"] = 1
    elif change == "running_one":
        trial["target_identity_before"]["running"] = 1
    elif change == "restart_float":
        trial["target_identity_before"]["restarts"] = 0.0
    elif change == "naive_time":
        trial["target_identity_before"]["started_at"] = "2026-01-01T00:00:00.000"
    elif change == "extra":
        trial["target_identity_before"]["secret"] = "do not echo"
    else:
        trial.pop("target_identity_after")
    refresh(bundle, account, trial)
    with pytest.raises(ValueError):
        check(typed)


@pytest.mark.parametrize(
    "change",
    [
        "protocol",
        "first_float",
        "span_boolean",
        "elapsed",
        "difference",
        "uncertainty",
        "flag",
        "flag_one",
        "start",
        "end",
        "measurement_float",
        "excluded_boolean",
        "excluded_range",
    ],
)
def test_timing_mismatch(typed, change):
    bundle, account, trial = typed
    measurement = trial["measurement"]
    clock = measurement["clock_sampling"]
    if change == "protocol":
        measurement["timing_protocol"] = "unknown"
    elif change == "first_float":
        clock["first"]["wall_ns"] = float(clock["first"]["wall_ns"])
    elif change == "span_boolean":
        clock["first"]["sampling_span_ns"] = True
    elif change in ("elapsed", "difference", "uncertainty"):
        clock[
            dict(
                elapsed="elapsed_monotonic_ns",
                difference="clock_difference_ns",
                uncertainty="sampling_uncertainty_ns",
            )[change]
        ] += 1
    elif change in ("flag", "flag_one"):
        clock["within_tolerance"] = False if change == "flag" else 1
    elif change == "start":
        measurement["start_unix_ns"] += 1
    elif change == "end":
        measurement["end_unix_ns"] += 1
    elif change == "measurement_float":
        measurement["elapsed_monotonic_ns"] = float(measurement["elapsed_monotonic_ns"])
    else:
        trial["correlation"] = dict(
            zero_excluded_samples=True if change == "excluded_boolean" else 5
        )
    refresh(bundle, account, trial)
    with pytest.raises(ValueError):
        check(typed)


@pytest.mark.parametrize("field", ["trial_sha256", "raw_sha256"])
def test_cross_role_sources_bound(typed, field):
    bundle, account, trial = typed
    refresh(bundle, account, trial)
    account[field] = "0" * 64
    root, manifest = bundle
    ref = manifest["runs"][0]["receipts"]["accounting"]
    wrapper = json.loads((root / ref["path"]).read_text())
    wrapper["source"] = save(root, "receipts/accounting-source.json", account)
    manifest["runs"][0]["receipts"]["accounting"] = save(root, ref["path"], wrapper)
    with pytest.raises(ValueError, match="source binding"):
        check(typed)


def test_identity_timing_cannot_reference_different_trials(typed):
    bundle, _, trial = typed
    root, manifest = bundle
    manifest["runs"][0]["receipts"]["accounting"] = None
    ref = manifest["runs"][0]["receipts"]["timing"]
    wrapper = json.loads((root / ref["path"]).read_text())
    trial["different_trial_declaration"] = True
    wrapper["source"] = save(root, "receipts/different-trial.json", trial)
    manifest["runs"][0]["receipts"]["timing"] = save(root, ref["path"], wrapper)
    with pytest.raises(ValueError, match="same selected trial"):
        check(typed)


def test_source_postflight_change_rejected(typed, monkeypatch):
    bundle, _, _ = typed
    original = receipts.accounting

    def changing(*args):
        result = original(*args)
        path = bundle[0] / "receipts/accounting-source.json"
        path.write_bytes(path.read_bytes() + b" ")
        return result

    monkeypatch.setattr(receipts, "accounting", changing)
    with pytest.raises(ValueError, match="changed during intake"):
        check(typed)


def test_actual_historical_local_clock_pass_is_not_collector_alignment():
    trial = json.loads(
        (ROOT / "output/engine2-readiness-repeats-20261005/trial-3.json").read_text()
    )
    result = receipts.timing(trial)
    assert result["local_clock_within_tolerance"] is True
    assert result["recorded_collector_zero_excluded_samples"] == 4
    assert result["collector_alignment_verified"] is False
    assert result["long_term_stability_verified"] is False


def test_actual_historical_accounting_matches_saved_export():
    account = json.loads(
        (
            ROOT / "output/engine2-instrumented-normalized-20260928/accounting.json"
        ).read_text()
    )
    assets, digest = load_inventory(ROOT / "testbed/inventory.json")
    capture = runtime.load_capture(
        ROOT / "output/engine2-instrumented-normalized-20260928/capture.json", assets
    )
    result = receipts.accounting(account, capture, digest)
    assert result["recorded_outcome"] == "normalized"
    assert result["coverage_verified"] is False


def test_v1_example_report_unchanged():
    result = inspect(ROOT / "data/runtime/intake-example/manifest.json")
    old = json.loads(
        (ROOT / "output/engine2-intake-synthetic-20261006.json").read_text()
    )
    assert result == old


def test_typed_cli_and_redacted_source_failure(typed, tmp_path):
    bundle, _, _ = typed
    check(typed)
    root, manifest = bundle
    output = tmp_path / "typed-report.json"
    assert command(root / "manifest.json", output).returncode == 0
    assert json.loads(output.read_text())["protocol"] == TYPED_PROTOCOL
    wrapper_ref = manifest["runs"][0]["receipts"]["accounting"]
    wrapper = json.loads((root / wrapper_ref["path"]).read_text())
    wrapper["source"] = save(
        root, "receipts/private-invalid.json", {"private": "must never appear in error"}
    )
    manifest["runs"][0]["receipts"]["accounting"] = save(
        root, wrapper_ref["path"], wrapper
    )
    save(root, "manifest.json", manifest)
    rejected = tmp_path / "typed-rejected.json"
    result = command(root / "manifest.json", rejected)
    assert result.returncode == 1 and not result.stderr
    assert "must never appear" not in result.stdout + rejected.read_text()
    assert json.loads(rejected.read_text())["model_fitting_authorized"] is False


def test_committed_typed_example_is_fixture_only():
    report = inspect(ROOT / "data/runtime/intake-example/manifest-typed-counted.json")
    checks = report["runs"][0]["selected_receipt_checks"]
    assert set(checks) == {"accounting", "identity", "timing"}
    assert all(row["origin_declared"] == "synthetic_fixture" for row in checks.values())
    assert report["observed_window_count"] == 3
    assert report["review_submissions"] == []
    assert report["independent_evaluation_verified"] is False
    assert report["model_fitting_authorized"] is False


@pytest.mark.parametrize(
    "change",
    [
        "empty_receipts",
        "sensor_origin",
        "not_running",
        "negative_elapsed",
        "wide_sample",
        "unsupported_asset",
    ],
)
def test_selected_scope_edge_cases(typed, change):
    bundle, account, trial = typed
    root, manifest = bundle
    run = manifest["runs"][0]
    if change == "empty_receipts":
        run["receipts"] = dict.fromkeys(run["receipts"])
    elif change in ("sensor_origin", "unsupported_asset"):
        capture = json.loads((root / run["capture"]["path"]).read_text())
        if change == "sensor_origin":
            capture["source"] = "normalized_sensor_export"
        else:
            run["receipts"]["accounting"] = None
            capture["bindings"][0]["asset_id"] = "compose/other"
            manifest["inventory"] = save(
                root,
                "inventory/assets.json",
                [{"asset_id": "compose/other", "host": "127.0.0.1", "port": 16379}],
            )
        run["capture"] = save(root, run["capture"]["path"], capture)
        refresh(bundle, account, trial)
        if change == "unsupported_asset":
            run["receipts"]["accounting"] = None
        with pytest.raises(ValueError):
            check(typed)
        return
    elif change == "not_running":
        trial["target_identity_before"]["running"] = False
        trial["target_identity_after"]["running"] = False
        trial["target_identity_stable"] = False
        refresh(bundle, account, trial)
    else:
        row = trial["measurement"]["clock_sampling"]
        if change == "negative_elapsed":
            row["last"]["monotonic_mid_ns"] = 0
        else:
            row["last"]["sampling_span_ns"] = 5_000_001
        row.update(compare(row["first"], row["last"]))
        trial["measurement"].update(
            elapsed_monotonic_ns=row["elapsed_monotonic_ns"],
            clock_difference_ns=row["clock_difference_ns"],
        )
        refresh(bundle, account, trial)
    report = check(typed)
    assert report["runs"][0]["evaluation_eligible"] is False
    checks = report["runs"][0]["selected_receipt_checks"]
    if change == "empty_receipts":
        assert checks == {}
        assert len(report["runs"][0]["missing_receipts"]) == 3
    elif change == "not_running":
        assert checks["identity"]["recorded_outcome"] == "changed_or_not_running"
    else:
        assert checks["timing"]["local_clock_within_tolerance"] is False


@pytest.mark.parametrize("explicit_fixture", [False, True])
def test_recorded_projection_declaration_is_not_authentication(typed, explicit_fixture):
    bundle, account, trial = typed
    root, manifest = bundle
    run = manifest["runs"][0]
    capture = json.loads((root / run["capture"]["path"]).read_text())
    capture["source"] = (
        "normalized_sensor_export"  # Invented declaration, not collection.
    )
    run["capture"] = save(root, run["capture"]["path"], capture)
    if not explicit_fixture:
        trial.pop("fixture_only")
    refresh(bundle, account, trial)
    for kind, ref in run["receipts"].items():
        wrapper = json.loads((root / ref["path"]).read_text())
        wrapper["origin"] = "recorded_projection"
        run["receipts"][kind] = save(root, ref["path"], wrapper)
    if explicit_fixture:
        with pytest.raises(ValueError, match="explicit fixture"):
            check(typed)
    else:
        report = check(typed)
        assert report["independent_evaluation_verified"] is False
        assert report["runs"][0]["binding_verified"] is False
        assert report["runs"][0]["evaluation_eligible"] is False


@pytest.mark.parametrize("change", ["total", "boolean_kind", "different_kinds"])
def test_trial_count_claims_must_match_accounting_source(typed, change):
    bundle, account, trial = typed
    if change == "total":
        trial["matched_event_count"] = 13
    elif change == "boolean_kind":
        trial["event_type_counts"]["execve"] = True
    else:
        trial["event_type_counts"]["open"] = 2
        trial["event_type_counts"]["connect"] = 9
    refresh(bundle, account, trial)
    with pytest.raises(ValueError, match="trial counts"):
        check(typed)


def test_preserved_preliminary_fixture_rejects_missing_trial_counts():
    with pytest.raises(ValueError, match="trial counts"):
        inspect(ROOT / "data/runtime/intake-example/manifest-typed.json")
