"""Bound a trusted local client's pipes/deadline, not its remote jobs/descendants."""

from dataclasses import dataclass
import math
import os
import subprocess
import threading
import time


class BoundedProcessError(RuntimeError):
    CODES = frozenset(
        {
            "launch_failed",
            "output_limit",
            "pipe_read_failed",
            "pipe_close_failed",
            "timeout",
            "interrupted",
            "supervision_failed",
            "cleanup_failed",
            "pipes_incomplete",
            "invalid_utf8",
        }
    )

    def __init__(
        self, code, stdout=b"", stderr=b"", *, reaped=False, pipes_closed=False
    ):
        if type(code) is not str or code not in self.CODES:
            raise ValueError("invalid process diagnostic code")
        if (
            type(stdout) is not bytes
            or type(stderr) is not bytes
            or len(stdout) + len(stderr) > 8_000_000
            or type(reaped) is not bool
            or type(pipes_closed) is not bool
        ):
            raise ValueError("invalid process diagnostic envelope")
        super().__init__("bounded process rejected: " + code)
        self.code = code
        self.stdout = stdout
        self.stderr = stderr
        self.diagnostic = {
            "code": code,
            "direct_child_reaped": reaped,
            "pipes_closed": pipes_closed,
            "external_job_completion_verified": False,
        }


@dataclass(frozen=True)
class ProcessResult:
    returncode: int
    stdout: str
    stderr: str


@dataclass(frozen=True)
class BinaryProcessResult:
    returncode: int
    stdout: bytes
    stderr: bytes


def _pause():
    time.sleep(0.01)


def run_bounded(command, *, timeout=30, output_limit=2_000_000, binary=False):
    if type(binary) is not bool:
        raise ValueError("binary must be a boolean")
    if (
        not isinstance(command, (list, tuple))
        or not 1 <= len(command) <= 100
        or any(
            not isinstance(arg, str) or not 1 <= len(arg) <= 4096 or "\0" in arg
            for arg in command
        )
    ):
        raise ValueError("invalid process argument list")
    if (
        type(timeout) not in (int, float)
        or not math.isfinite(timeout)
        or not 0 < timeout <= 180
    ):
        raise ValueError("invalid process timeout")
    if type(output_limit) is not int or not 1 <= output_limit <= 8_000_000:
        raise ValueError("invalid process output limit")
    deadline = time.monotonic() + timeout
    try:
        process = subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
    except OSError as error:
        raise BoundedProcessError("launch_failed") from error
    lock = threading.Lock()
    stop = threading.Event()
    buffers = [bytearray(), bytearray()]
    fault = []

    def consume(stream, index):
        try:
            while not stop.is_set():
                chunk = stream.read1(4096)
                if not chunk:
                    break
                with lock:
                    remaining = output_limit - sum(len(b) for b in buffers)
                    buffers[index].extend(chunk[:remaining])
                    if len(chunk) > remaining:
                        fault.append("output_limit")
                        stop.set()
        except Exception:
            with lock:
                fault.append("pipe_read_failed")
                stop.set()
        finally:
            try:
                stream.close()
            except OSError:
                with lock:
                    fault.append("pipe_close_failed")

    threads = [
        threading.Thread(target=consume, args=(stream, index), daemon=True)
        for index, stream in enumerate((process.stdout, process.stderr))
    ]
    code = None
    reaped = False
    try:
        for thread in threads:
            thread.start()
        while True:
            with lock:
                if fault:
                    code = fault[0]
                    break
            if process.poll() is not None and not any(t.is_alive() for t in threads):
                break
            if time.monotonic() >= deadline:
                code = "timeout"
                break
            _pause()
    except KeyboardInterrupt:
        code = "interrupted"
    except Exception:
        code = "supervision_failed"
    finally:
        stop.set()
        try:
            if process.poll() is None:
                process.kill()
            process.wait(timeout=5)
            reaped = True
        except (OSError, subprocess.TimeoutExpired):
            code = code or "cleanup_failed"
        except KeyboardInterrupt:
            code = "interrupted"
        join_deadline = time.monotonic() + 1
        for thread in threads:
            if thread.ident is not None:
                thread.join(timeout=max(0, join_deadline - time.monotonic()))
        for thread, stream in zip(threads, (process.stdout, process.stderr)):
            if thread.ident is None:
                stream.close()
        closed = (
            not any(t.is_alive() for t in threads)
            and process.stdout.closed
            and process.stderr.closed
        )
        if not closed:
            code = code or "pipes_incomplete"
    with lock:
        if fault:
            code = code or fault[0]
        stdout, stderr = (bytes(buffer) for buffer in buffers)
    if code:
        raise BoundedProcessError(
            code, stdout, stderr, reaped=reaped, pipes_closed=closed
        )
    if binary:
        return BinaryProcessResult(process.returncode, stdout, stderr)
    try:
        return ProcessResult(
            process.returncode, stdout.decode("utf-8"), stderr.decode("utf-8")
        )
    except UnicodeError as error:
        raise BoundedProcessError(
            "invalid_utf8", stdout, stderr, reaped=reaped, pipes_closed=closed
        ) from error
