"""Observe one explicitly selected private-repository CI run; no dispatch/retry."""

from datetime import datetime, timezone
import os
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cloudguard.evidence import evidence_main
from cloudguard.limits import json_value
from cloudguard.process_runner import run_bounded

REPOSITORY = "ManishPatil2005/active-cloud-guard-honors"
JOB_NAMES = {"regression (windows-2025)", "regression (ubuntu-24.04)"}
TEST_STEP = "Run full regressions including installed wheel"


def collect(args):
    run_id = os.environ.get("ACG_CI_RUN_ID", "")
    expected = os.environ.get("ACG_CI_EXPECTED_SHA", "")
    if not re.fullmatch(r"[0-9]{1,20}", run_id) or not re.fullmatch(
        r"[0-9a-f]{40}", expected
    ):
        raise ValueError("explicit numeric run ID and exact source SHA required")
    response = run_bounded(
        [
            "gh",
            "run",
            "view",
            run_id,
            "--repo",
            REPOSITORY,
            "--json",
            "databaseId,headSha,status,conclusion,url,jobs",
        ],
        timeout=30,
        output_limit=1_000_000,
    )
    if response.returncode != 0:
        raise ValueError("CI metadata query rejected")
    raw = json_value(response.stdout)
    url = f"https://github.com/{REPOSITORY}/actions/runs/{run_id}"
    if (
        not isinstance(raw, dict)
        or type(raw.get("databaseId")) is not int
        or str(raw["databaseId"]) != run_id
        or raw.get("headSha") != expected
        or raw.get("url") != url
        or raw.get("status")
        not in {"completed", "in_progress", "queued", "requested", "waiting", "pending"}
        or not isinstance(raw.get("jobs"), list)
        or len(raw["jobs"]) > 2
    ):
        raise ValueError("CI run identity/envelope mismatch")
    jobs, seen = [], set()
    for job in raw["jobs"]:
        if (
            not isinstance(job, dict)
            or job.get("name") not in JOB_NAMES
            or job["name"] in seen
            or type(job.get("databaseId")) is not int
            or not isinstance(job.get("steps"), list)
            or len(job["steps"]) > 64
        ):
            raise ValueError("CI job identity/envelope mismatch")
        seen.add(job["name"])
        selected = [
            step
            for step in job["steps"]
            if isinstance(step, dict) and step.get("name") == TEST_STEP
        ]
        if len(selected) > 1:
            raise ValueError("duplicate regression step")
        step_passed = (
            len(selected) == 1
            and selected[0].get("status") == "completed"
            and selected[0].get("conclusion") == "success"
        )
        jobs.append(
            {
                "id": job["databaseId"],
                "name": job["name"],
                "status": job.get("status"),
                "conclusion": job.get("conclusion"),
                "regression_step_succeeded": step_passed,
            }
        )
    accepted = (
        raw["status"] == "completed"
        and raw.get("conclusion") == "success"
        and seen == JOB_NAMES
        and all(
            job["status"] == "completed"
            and job["conclusion"] == "success"
            and job["regression_step_succeeded"]
            for job in jobs
        )
    )
    return {
        "output": {
            "status": "ci_run_observation",
            "observed_at_utc": datetime.now(timezone.utc).isoformat(),
            "repository": REPOSITORY,
            "run_id": raw["databaseId"],
            "head_sha": expected,
            "run_url": url,
            "run_status": raw["status"],
            "run_conclusion": raw.get("conclusion"),
            "jobs": jobs,
            "both_regression_jobs_succeeded": accepted,
            "production_ready": False,
            "independent_evaluation": False,
            "limits": [
                "GitHub metadata observation, not authenticated signatures or independent scientific evaluation.",
                "Test counts, skips and package/host scope require original downloaded receipts.",
                "No dispatch, rerun, deployment, source upload or autonomous monitoring by this reader.",
            ],
        }
    }, 0 if accepted else 1


if __name__ == "__main__":
    raise SystemExit(evidence_main(collect))
