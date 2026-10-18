"""Offline grouped runtime artifact/label consistency, never research eligibility.

No collection, prediction, fitting, service or network operations. Supplied
roles, groups, reviewer identities/blinding and receipts are not attestation.
"""

import hashlib
import copy
import json
import math
from pathlib import Path
import re
import stat

from cloudguard import runtime
from cloudguard.runtime_receipts import inspect_receipts
from cloudguard.verification import HASH, object_schema, validate, load_inventory

PROTOCOL = "runtime_intake_v1"
TYPED_PROTOCOL = "runtime_intake_v2"
ANNOTATION_PROTOCOL = "runtime_annotation_index_v1"
FILE_LIMIT = 1_000_000
TOTAL_LIMIT = 8_000_000
WINDOW_LIMIT = 2000
# Exact-byte guard only; these historical exploratory exports are not held-out data.
KNOWN_DEVELOPMENT_CAPTURES = frozenset(
    {
        "5dc76e982fec7258ebebeeb96f2021271a1d8b8d8acedc83f1871d1ddb6fb2ae",
        "948aecb953f522ee49521a871b9179d263a21aebb238bda15a8ba9ee582ffebc",
    }
)
ID = dict(
    type="string",
    minLength=1,
    maxLength=128,
    pattern=r"^[A-Za-z0-9_./:-]+$",
    **{"not": {"pattern": r"\s"}},
)
REF = object_schema(
    dict(path=dict(type="string", minLength=1, maxLength=256), sha256=HASH)
)
OPTIONAL_REF = {"anyOf": [REF, {"type": "null"}]}
LABEL = object_schema(
    dict(
        run_id=ID,
        asset_id=ID,
        start_epoch=dict(type="integer", minimum=0, maximum=4_134_067_200),
        label={"enum": ["benign", "suspicious", "unknown"]},
        reason=dict(type="string", minLength=1, maxLength=500),
    )
)
LABELS = dict(type="array", maxItems=WINDOW_LIMIT, items=LABEL)
REVIEW = object_schema(
    dict(
        schema_version={"const": "runtime_review_v1"},
        reviewer_id=ID,
        origin={"enum": ["synthetic_fixture", "human_submission"]},
        guidelines_sha256=HASH,
        blinded=dict(type="boolean", const=True),
        labels=LABELS,
    )
)
ADJUDICATION = object_schema(
    dict(
        schema_version={"const": "runtime_adjudication_v1"},
        adjudicator_id=ID,
        guidelines_sha256=HASH,
        review_sha256=dict(
            type="array", minItems=2, maxItems=2, uniqueItems=True, items=HASH
        ),
        labels=LABELS,
    )
)
MANIFEST = object_schema(
    dict(
        schema_version={"const": PROTOCOL},
        dataset_id=ID,
        inventory=REF,
        guidelines=REF,
        window_seconds=dict(type="integer", minimum=1, maximum=3600),
        runs=dict(
            type="array",
            minItems=1,
            maxItems=20,
            items=object_schema(
                dict(
                    run_id=ID,
                    capture=REF,
                    data_role={"enum": ["development", "candidate_evaluation"]},
                    split={"enum": ["development", "train", "validation", "test"]},
                    groups=object_schema(
                        dict(template_family=ID, deployment_id=ID, run_family=ID)
                    ),
                    receipts=object_schema(
                        dict(
                            accounting=OPTIONAL_REF,
                            identity=OPTIONAL_REF,
                            timing=OPTIONAL_REF,
                        )
                    ),
                )
            ),
        ),
        reviews=dict(type="array", maxItems=2, items=REF),
        adjudication=OPTIONAL_REF,
    )
)
MANIFEST_V2 = copy.deepcopy(MANIFEST)
MANIFEST_V2["properties"]["schema_version"] = {"const": TYPED_PROTOCOL}


def _json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate intake JSON key")
            result[key] = value
        return result

    def real(value):
        parsed = float(value)
        if not math.isfinite(parsed):
            raise ValueError("nonfinite intake number")
        return parsed

    def nonfinite(value):
        raise ValueError("nonfinite intake constant")

    return json.loads(
        raw, object_pairs_hook=pairs, parse_float=real, parse_constant=nonfinite
    )


def _raw(path, limit=FILE_LIMIT):
    if path.is_symlink() or not stat.S_ISREG(path.stat().st_mode):
        raise ValueError("regular artifact required")
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    if len(raw) > limit:
        raise ValueError("intake artifact byte limit exceeded")
    return raw


class _Bundle:
    def __init__(self, root):
        self.root = root.resolve(strict=True)
        self.files = {}
        self.bytes = 0

    def path(self, name, kind):
        if (
            not isinstance(name, str)
            or len(name) > 256
            or not re.fullmatch(
                r"[A-Za-z0-9][A-Za-z0-9_.-]*(?:/[A-Za-z0-9][A-Za-z0-9_.-]*)+", name
            )
        ):
            raise ValueError("invalid bundle-relative artifact path")
        parts = name.split("/")
        extension = ".md" if kind == "guidelines" else ".json"
        if parts[0] != kind or not parts[-1].endswith(extension):
            raise ValueError("artifact path does not match its role")
        path = self.root
        for part in parts:
            path = path / part
            if path.is_symlink():
                raise ValueError("symlink artifact path refused")
        resolved = path.resolve(strict=True)
        if not resolved.is_relative_to(self.root):
            raise ValueError("artifact escapes bundle")
        return resolved

    def read(self, ref, kind):
        path = self.path(ref["path"], kind)
        if ref["path"] not in self.files:
            raw = _raw(path)
            self.bytes += len(raw)
            if self.bytes > TOTAL_LIMIT:
                raise ValueError("aggregate intake byte limit exceeded")
            self.files[ref["path"]] = (kind, raw, hashlib.sha256(raw).hexdigest())
        _, raw, digest = self.files[ref["path"]]
        if digest != ref["sha256"]:
            raise ValueError("artifact hash mismatch")
        return path, raw

    def unchanged(self):
        for name, (kind, raw, digest) in self.files.items():
            if hashlib.sha256(_raw(self.path(name, kind))).hexdigest() != digest:
                raise ValueError("artifact changed during intake")


def _labels(document, keys):
    result = {}
    for entry in document["labels"]:
        key = (entry["run_id"], entry["asset_id"], entry["start_epoch"])
        if type(entry["start_epoch"]) is not int or key in result or key not in keys:
            raise ValueError("duplicate or unbound review window")
        result[key] = entry["label"]
    if set(result) != keys:
        raise ValueError("review must cover exactly observed windows")
    return result


def _reviewer_agreement(votes, keys):
    """Descriptive original-vote counts after intake validation, before adjudication."""
    labels = ("benign", "suspicious", "unknown")
    matrix = {a: {b: 0 for b in labels} for a in labels}
    marginals = [
        {label: sum(value == label for value in review.values()) for label in labels}
        for review in votes
    ]
    paired = len(votes) == 2
    if paired:
        for key in keys:
            matrix[votes[0][key]][votes[1][key]] += 1
    known = sum(matrix[a][b] for a in labels[:2] for b in labels[:2])
    matching = sum(matrix[a][a] for a in labels[:2])
    # Integer numerator/denominator avoid a floating comparison near chance=1.
    chance_numerator = sum(
        sum(matrix[a][b] for b in labels[:2]) * sum(matrix[b][a] for b in labels[:2])
        for a in labels[:2]
    )
    denominator = known * known - chance_numerator
    pairs = len(keys) if paired else 0
    return dict(
        protocol="runtime_reviewer_agreement_v1",
        status="paired_original_votes" if paired else "requires_two_reviews",
        observed_windows=len(keys),
        supplied_reviews=len(votes),
        paired_windows=pairs,
        label_order=list(labels),
        rows="first_manifest_review",
        columns="second_manifest_review",
        original_label_pair_counts=matrix,
        original_reviewer_label_counts=marginals,
        known_pairs=known,
        unknown_pairs=pairs - known,
        known_pair_coverage=known / pairs if pairs else None,
        all_label_agreement_fraction=(
            sum(matrix[a][a] for a in labels) / pairs if pairs else None
        ),
        known_agreement_fraction=matching / known if known else None,
        known_chance_agreement=(chance_numerator / (known * known) if known else None),
        known_cohen_kappa=(
            (matching * known - chance_numerator) / denominator if denominator else None
        ),
        kappa_undefined_reason=(
            "requires_two_reviews"
            if not paired
            else "no_known_pairs"
            if not known
            else "chance_agreement_is_one"
            if not denominator
            else None
        ),
        computed_before_adjudication=True,
        independent_review_verified=False,
        limitations=[
            "Known-pair kappa excludes pairs containing unknown; coverage and full table must accompany it.",
            "Matching unknown labels indicates matching uncertainty, not a correct security decision.",
            "Descriptive counts only: correlated windows, prevalence and reviewer independence require study review; no confidence interval or acceptance threshold.",
        ],
    )


def inspect(
    manifest_path, *, include_window_index=False, include_review_agreement=False
):
    """Read a dedicated local bundle; return minimized declarations/consistency.

    v1 receipts are opaque; v2 checks selected source facts, never eligibility.
    Reviewer reasons/receipt contents are never included in the returned report.
    Optional unit keys are not a blinded packet; the default report is unchanged.
    """
    if (
        type(include_window_index) is not bool
        or type(include_review_agreement) is not bool
    ):
        raise ValueError("exact boolean intake options required")
    manifest_path = Path(manifest_path)
    original = _raw(manifest_path, 100_000)
    manifest = _json(original)
    typed = (
        isinstance(manifest, dict) and manifest.get("schema_version") == TYPED_PROTOCOL
    )
    validate(manifest, MANIFEST_V2 if typed else MANIFEST)
    if type(manifest["window_seconds"]) is not int:
        raise ValueError("exact integer window size required")
    bundle = _Bundle(manifest_path.parent)
    inventory_path, inventory_raw = bundle.read(manifest["inventory"], "inventory")
    _json(inventory_raw)
    assets, inventory_hash = load_inventory(inventory_path)
    if inventory_hash != manifest["inventory"]["sha256"]:
        raise ValueError("inventory changed during loading")
    _, guidelines = bundle.read(manifest["guidelines"], "guidelines")
    if not guidelines.decode("utf-8", errors="strict").strip():
        raise ValueError("nonempty UTF-8 guidelines required")
    runs, run_ids, capture_ids, capture_hashes, seen_events, groups, keys = (
        [],
        set(),
        set(),
        set(),
        set(),
        {},
        set(),
    )
    for run in manifest["runs"]:
        path, raw = bundle.read(run["capture"], "captures")
        capture_document = _json(raw)  # Strict parsing before reused loading.
        capture = runtime.load_capture(path, assets)
        validate(capture["capture_id"], ID)
        validate(capture["scenario_group"], ID)
        if capture["sha256"] != run["capture"]["sha256"]:
            raise ValueError("capture changed during loading")
        if (
            run["run_id"] in run_ids
            or capture["capture_id"] in capture_ids
            or capture["sha256"] in capture_hashes
        ):
            raise ValueError("duplicate run or capture")
        run_ids.add(run["run_id"])
        capture_ids.add(capture["capture_id"])
        capture_hashes.add(capture["sha256"])
        if (run["data_role"] == "development") != (run["split"] == "development"):
            raise ValueError("development data cannot enter evaluation partitions")
        if capture["source"] == "synthetic" and run["data_role"] != "development":
            raise ValueError("synthetic capture is development only")
        if (
            capture["sha256"] in KNOWN_DEVELOPMENT_CAPTURES
            and run["data_role"] != "development"
        ):
            raise ValueError("known exploratory capture is development only")
        declared_groups = dict(run["groups"], scenario_group=capture["scenario_group"])
        for kind, identifier in declared_groups.items():
            group_key = (kind, identifier)
            if group_key in groups and groups[group_key] != run["split"]:
                raise ValueError("related group crosses declared partitions")
            groups[group_key] = run["split"]
        events = runtime.event_keys(capture)
        if seen_events & events:
            raise ValueError("overlapping runtime event projections")
        seen_events |= events
        observed = runtime.windows(capture, manifest["window_seconds"])
        keys.update(
            (run["run_id"], row["asset_id"], row["start_epoch"]) for row in observed
        )
        if len(keys) > WINDOW_LIMIT:
            raise ValueError("aggregate review window limit exceeded")
        checked, missing = [], []
        for kind, ref in run["receipts"].items():
            if ref is None:
                missing.append(kind)
            else:
                _, receipt = bundle.read(ref, "receipts")
                if not isinstance(_json(receipt), dict):
                    raise ValueError("receipt must be a JSON object")
                checked.append(kind)
        if typed:

            def receipt_json(ref):
                return _json(bundle.read(ref, "receipts")[1])

            receipt_checks = inspect_receipts(
                run, capture, capture_document, inventory_hash, receipt_json
            )
        runs.append(
            dict(
                run_id=run["run_id"],
                capture_id=capture["capture_id"],
                capture_sha256=capture["sha256"],
                source=capture["source"],
                data_role_declared=run["data_role"],
                split_declared=run["split"],
                observed_window_count=len(observed),
                event_count=len(capture["events"]),
                collection_coverage="partial_or_unknown",
                binding_verified=False,
                receipt_hashes_checked=checked,
                missing_receipts=missing,
                receipt_semantics_verified=False,
                evaluation_eligible=False,
            )
        )
        if typed:
            runs[-1]["selected_receipt_checks"] = receipt_checks
    submissions, reviewers, votes = [], set(), []
    for ref in manifest["reviews"]:
        _, raw = bundle.read(ref, "labels")
        document = _json(raw)
        validate(document, REVIEW)
        if (
            document["blinded"] is not True
            or document["guidelines_sha256"] != manifest["guidelines"]["sha256"]
            or document["reviewer_id"] in reviewers
        ):
            raise ValueError("review declaration or guidelines mismatch")
        reviewers.add(document["reviewer_id"])
        votes.append(_labels(document, keys))
        submissions.append(
            dict(
                reviewer_id_declared=document["reviewer_id"],
                origin_declared=document["origin"],
                sha256=ref["sha256"],
                blinding_declared=True,
            )
        )
    agreement = dict(
        known_pairs=0,
        known_agreements=0,
        known_disagreements=0,
        unknown_pairs=0,
        known_agreement_fraction=None,
    )
    if len(votes) == 2:
        for key in keys:
            a, b = votes[0][key], votes[1][key]
            if "unknown" in (a, b):
                agreement["unknown_pairs"] += 1
            else:
                agreement["known_pairs"] += 1
                agreement["known_agreements" if a == b else "known_disagreements"] += 1
        if agreement["known_pairs"]:
            agreement["known_agreement_fraction"] = (
                agreement["known_agreements"] / agreement["known_pairs"]
            )
    adjudicated = None
    if manifest["adjudication"] is not None:
        if len(votes) != 2:
            raise ValueError("adjudication requires two supplied reviews")
        ref = manifest["adjudication"]
        _, raw = bundle.read(ref, "labels")
        document = _json(raw)
        validate(document, ADJUDICATION)
        if document["guidelines_sha256"] != manifest["guidelines"]["sha256"] or set(
            document["review_sha256"]
        ) != {row["sha256"] for row in submissions}:
            raise ValueError("adjudication review/guidelines binding mismatch")
        labels = _labels(document, keys)
        for key, value in labels.items():
            if votes[0][key] == votes[1][key] != "unknown" and value != votes[0][key]:
                raise ValueError("adjudication contradicts an agreed known vote")
        adjudicated = dict(
            sha256=ref["sha256"],
            adjudicator_id_declared=document["adjudicator_id"],
            label_counts={
                name: sum(value == name for value in labels.values())
                for name in ("benign", "suspicious", "unknown")
            },
        )
    bundle.unchanged()
    if _raw(manifest_path, 100_000) != original:
        raise ValueError("manifest changed during intake")
    report = dict(
        protocol=manifest["schema_version"],
        dataset_id=manifest["dataset_id"],
        status="artifact_consistency_checked",
        manifest_sha256=hashlib.sha256(original).hexdigest(),
        inventory_sha256=inventory_hash,
        guidelines_sha256=manifest["guidelines"]["sha256"],
        window_seconds=manifest["window_seconds"],
        observed_window_count=len(keys),
        empty_capture_count=sum(row["event_count"] == 0 for row in runs),
        missing_windows_not_materialized=True,
        runs=runs,
        review_submissions=submissions,
        pre_adjudication_agreement=agreement,
        adjudication=adjudicated,
        unique_artifact_bytes=bundle.bytes,
        unique_artifact_count=len(bundle.files),
        independent_evaluation_verified=False,
        model_fitting_authorized=False,
        predictions_computed=False,
        actions_executed=[],
        limitations=[
            "Grouping/roles/reviewer identity/blinding are supplied declarations, not authenticated independence.",
            (
                "Typed receipts check selected source/count/identity/endpoint consistency only; complete protocol, collector alignment, coverage, authentication and eligibility are not verified."
                if typed
                else "Receipt hashes are checked; receipt protocols/timing/coverage/identity and real-data eligibility are not verified."
            ),
            "Event overlap uses the existing lossy runtime projection; renamed/structurally similar cases are not fully detected.",
            "No threat accuracy, model fitting, independent labels or eligibility is established by this report.",
        ],
    )
    if include_window_index:
        report["observed_window_index"] = [
            dict(run_id=run_id, asset_id=asset_id, start_epoch=start)
            for run_id, asset_id, start in sorted(keys)
        ]
    if include_review_agreement:
        report["reviewer_agreement"] = _reviewer_agreement(votes, keys)
    return report


def annotation_index(manifest_path):
    """Index validated observed units without votes, answers or predictions.

    Coordinator-only: identifiers may reveal scenarios. Integrity/consistency
    never establish approval, independent annotation or eligibility.
    """
    report = inspect(manifest_path, include_window_index=True)
    return dict(
        protocol=ANNOTATION_PROTOCOL,
        status="observed_units_indexed",
        manifest_sha256=report["manifest_sha256"],
        inventory_sha256=report["inventory_sha256"],
        guidelines_sha256=report["guidelines_sha256"],
        window_seconds=report["window_seconds"],
        observed_window_count=report["observed_window_count"],
        empty_capture_count=report["empty_capture_count"],
        missing_windows_not_materialized=True,
        units=report["observed_window_index"],
        labels_created=False,
        supervisor_approval_verified=False,
        blinding_verified=False,
        independent_evaluation_verified=False,
        model_fitting_authorized=False,
        predictions_computed=False,
        actions_executed=[],
        limitations=[
            "Coordinator index only; run/asset identifiers may reveal scenarios. Not a blinded reviewer packet.",
            "No labels, independent context, human approval or annotation are created; document hashes are not signatures.",
            "Only observed nonempty units are indexed; expected missing intervals and full coverage are not established.",
            "Intake consistency checks are inherited, not research eligibility, collector alignment or threat effectiveness.",
        ],
    )
