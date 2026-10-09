"""Two-process synthetic embedded-storage qualification, not server security."""

import hashlib
import importlib.metadata
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cloudguard.evidence import evidence_main
from cloudguard.limits import json_value
from cloudguard.process_runner import run_bounded, BoundedProcessError

ROOT = Path(__file__).resolve().parents[1]
CHILD = """
import importlib.metadata, json, sys
phase, directory = sys.argv[1:]
def guard(event, args):
    if event in {'socket.connect', 'socket.bind', 'socket.getaddrinfo'}:
        raise RuntimeError('Python socket activity refused')
sys.addaudithook(guard)
assert importlib.metadata.version('chromadb') == '1.0.20'
import chromadb
from chromadb.config import Settings
client = chromadb.PersistentClient(path=directory,
                                  settings=Settings(anonymized_telemetry=False))
if phase == 'write':
    collection = client.create_collection('synthetic-vectors', embedding_function=None)
    collection.add(ids=['synthetic-one', 'synthetic-two'],
                   embeddings=[[1.0, 0.0], [0.0, 1.0]],
                   documents=['invented first vector', 'invented second vector'])
else:
    assert phase == 'read'
    collection = client.get_collection('synthetic-vectors', embedding_function=None)
count = collection.count()
assert count == 2
assert set(collection.get(include=[])['ids']) == {'synthetic-one', 'synthetic-two'}
nearest = collection.query(query_embeddings=[[1.0, 0.0]], n_results=1,
                           include=['distances'])['ids']
assert nearest == [['synthetic-one']]
if phase == 'read':
    client.delete_collection('synthetic-vectors')
print(json.dumps({'phase': phase, 'stored_count': count,
                  'nearest_id': nearest[0][0], 'deleted_collection': phase == 'read'}))
"""


def collect(args):
    if importlib.metadata.version("chromadb") != "1.0.20":
        raise ValueError("unexpected Chroma version")
    temporary = ROOT / "tmp"
    temporary.mkdir(exist_ok=True)
    directory = Path(tempfile.mkdtemp(prefix="vector-storage-", dir=temporary))
    steps, failure = [], None
    for phase in ("write", "read"):
        step = {"phase": phase, "status": "not_attempted"}
        steps.append(step)
        if failure is not None:
            continue
        try:
            result = run_bounded(
                [sys.executable, "-I", "-c", CHILD, phase, str(directory)],
                timeout=60,
                output_limit=100_000,
            )
            if result.returncode != 0:
                raise ValueError("vector child rejected")
            report = json_value(result.stdout)
            if (
                not isinstance(report, dict)
                or set(report)
                != {"phase", "stored_count", "nearest_id", "deleted_collection"}
                or type(report["stored_count"]) is not int
                or type(report["deleted_collection"]) is not bool
                or report
                != {
                    "phase": phase,
                    "stored_count": 2,
                    "nearest_id": "synthetic-one",
                    "deleted_collection": phase == "read",
                }
            ):
                raise ValueError("vector child envelope mismatch")
            step.update(status="passed", result=report)
        except (Exception, KeyboardInterrupt) as error:
            failure = type(error).__name__
            step.update(status="rejected", error_type=failure)
            if isinstance(error, BoundedProcessError):
                step["diagnostic"] = error.diagnostic
    accepted = failure is None
    return {
        "output": {
            "status": "synthetic_storage_checks_passed"
            if accepted
            else "synthetic_storage_checks_incomplete",
            "chromadb_version": "1.0.20",
            "child_source_sha256": hashlib.sha256(CHILD.encode()).hexdigest(),
            "store_directory": directory.relative_to(ROOT).as_posix(),
            "steps": steps,
            "cold_process_reopen_verified": accepted,
            "explicit_vectors_only": True,
            "production_ready": False,
            "independent_evaluation": False,
            "server_security_verified": False,
            "network_isolation_verified": False,
            "limits": [
                "Two fixed synthetic vectors/fresh trusted directory only; no existing index or model server.",
                "Python socket audit guards are not OS/native network isolation.",
                "Clean process exit/reopen is not crash, concurrency, durability or security qualification.",
                "Chroma advisory matches remain open; no server/RBAC/pentest or general clearance.",
                "Synthetic storage artifacts are retained under ignored tmp for failure review.",
            ],
        }
    }, 0 if accepted else 1


if __name__ == "__main__":
    raise SystemExit(evidence_main(collect))
