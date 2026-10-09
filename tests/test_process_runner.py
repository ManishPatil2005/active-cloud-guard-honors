import io
import subprocess
import sys
from unittest.mock import patch

import pytest

from cloudguard import process_runner as runner


def test_real_process_retains_both_streams_and_nonzero_status():
    result = runner.run_bounded(
        [
            sys.executable,
            "-c",
            "import sys;print('out');print('err',file=sys.stderr);sys.exit(2)",
        ],
        timeout=10,
    )
    assert result.returncode == 2
    assert result.stdout.strip() == "out" and result.stderr.strip() == "err"


@pytest.mark.parametrize("stream", [1, 2])
def test_real_process_output_limit_is_combined_bounded_and_reaped(stream):
    with pytest.raises(runner.BoundedProcessError) as error:
        runner.run_bounded(
            [sys.executable, "-c", f"import os;os.write({stream},b'X'*1000000)"],
            timeout=10,
            output_limit=10000,
        )
    assert error.value.code == "output_limit"
    assert len(error.value.stdout) + len(error.value.stderr) <= 10000
    assert error.value.diagnostic["direct_child_reaped"]
    assert error.value.diagnostic["pipes_closed"]
    assert not error.value.diagnostic["external_job_completion_verified"]


def test_real_timeout_kills_and_reaps_owned_child():
    with pytest.raises(runner.BoundedProcessError) as error:
        runner.run_bounded(
            [sys.executable, "-c", "import time;time.sleep(10)"], timeout=0.3
        )
    assert error.value.code == "timeout"
    assert (
        error.value.diagnostic["direct_child_reaped"]
        and error.value.diagnostic["pipes_closed"]
    )


def test_interrupt_kills_and_reaps_owned_child():
    with patch.object(runner, "_pause", side_effect=KeyboardInterrupt):
        with pytest.raises(runner.BoundedProcessError) as error:
            runner.run_bounded(
                [sys.executable, "-c", "import time;time.sleep(10)"], timeout=10
            )
    assert (
        error.value.code == "interrupted"
        and error.value.diagnostic["direct_child_reaped"]
    )


def test_invalid_utf8_is_not_successful_metadata():
    with pytest.raises(runner.BoundedProcessError) as error:
        runner.run_bounded(
            [sys.executable, "-c", "import os;os.write(1,b'\\xff')"], timeout=10
        )
    assert error.value.code == "invalid_utf8" and error.value.stdout == b"\xff"


@pytest.mark.parametrize(
    "options",
    [
        {"timeout": True},
        {"timeout": 0},
        {"timeout": float("nan")},
        {"timeout": 181},
        {"output_limit": True},
        {"output_limit": 0},
        {"output_limit": 8000001},
    ],
)
def test_bad_budget_refuses_before_launch(options):
    with patch.object(runner.subprocess, "Popen") as launch, pytest.raises(ValueError):
        runner.run_bounded(["trusted"], **options)
    launch.assert_not_called()


@pytest.mark.parametrize(
    "command", ["not a shell command", [], [None], [""], ["x\0y"], ["x" * 4097]]
)
def test_bad_arguments_refuse_before_launch(command):
    with patch.object(runner.subprocess, "Popen") as launch, pytest.raises(ValueError):
        runner.run_bounded(command)
    launch.assert_not_called()


def test_launch_failure_is_owned_without_private_message():
    with patch.object(runner.subprocess, "Popen", side_effect=OSError("PRIVATE")):
        with pytest.raises(runner.BoundedProcessError) as error:
            runner.run_bounded(["missing"])
    assert error.value.code == "launch_failed" and "PRIVATE" not in str(error.value)


def test_cleanup_failure_never_claims_reaped():
    class Process:
        stdout = io.BytesIO(b"")
        stderr = io.BytesIO(b"")
        returncode = None

        def poll(self):
            return None

        def kill(self):
            raise OSError("PRIVATE")

        def wait(self, timeout):
            raise subprocess.TimeoutExpired("trusted", timeout)

    # Buffered fake pipes implement the reader API; no native child is launched.
    process = Process()
    process.stdout = io.BufferedReader(process.stdout)
    process.stderr = io.BufferedReader(process.stderr)
    with patch.object(runner.subprocess, "Popen", return_value=process):
        with pytest.raises(runner.BoundedProcessError) as error:
            runner.run_bounded(["trusted"], timeout=0.01)
    assert not error.value.diagnostic["direct_child_reaped"]
    assert "PRIVATE" not in str(error.value)


def test_unknown_diagnostic_code_refused():
    with pytest.raises(ValueError):
        runner.BoundedProcessError("PRIVATE unknown")


def test_interrupt_during_reap_remains_unverified():
    class Process:
        stdout = io.BufferedReader(io.BytesIO(b""))
        stderr = io.BufferedReader(io.BytesIO(b""))
        returncode = None

        def poll(self):
            return None

        def kill(self):
            pass

        def wait(self, timeout):
            raise KeyboardInterrupt

    with (
        patch.object(runner.subprocess, "Popen", return_value=Process()),
        patch.object(runner, "_pause", side_effect=KeyboardInterrupt),
    ):
        with pytest.raises(runner.BoundedProcessError) as error:
            runner.run_bounded(["trusted"], timeout=10)
    assert (
        error.value.code == "interrupted"
        and not error.value.diagnostic["direct_child_reaped"]
    )
