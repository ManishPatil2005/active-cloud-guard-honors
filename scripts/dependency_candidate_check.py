"""Offline patched-package smoke; optional local Chroma with explicit vectors."""

import importlib.metadata
import importlib.util
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cloudguard.evidence import evidence_main


def collect(args):
    required = {
        "pip": "26.2",
        "pytest": "9.0.3",
        "oauthlib": "4.0.0",
        "requests-oauthlib": "2.0.0",
    }
    versions = {name: importlib.metadata.version(name) for name in required}
    if versions != required:
        raise ValueError("candidate version mismatch")
    from oauthlib.oauth2 import BackendApplicationClient
    from requests_oauthlib import OAuth2Session

    client = BackendApplicationClient(client_id="synthetic-client")
    session = OAuth2Session(client=client)
    body = session._client.prepare_request_body(scope=["read"])
    if "grant_type=client_credentials" not in body:
        raise ValueError("OAuth request preparation mismatch")
    session.close()
    vector = {"status": "not_installed", "qualified": False}
    if importlib.util.find_spec("chromadb") is not None:
        import chromadb
        from chromadb.config import Settings

        if importlib.metadata.version("chromadb") != "1.0.20":
            raise ValueError("unexpected Chroma version")
        store = chromadb.EphemeralClient(settings=Settings(anonymized_telemetry=False))
        collection = store.create_collection("candidate-check", embedding_function=None)
        collection.add(ids=["synthetic-one"], embeddings=[[1.0, 0.0]])
        if collection.count() != 1 or collection.get(ids=["synthetic-one"], include=[])[
            "ids"
        ] != ["synthetic-one"]:
            raise ValueError("explicit-vector roundtrip mismatch")
        store.delete_collection("candidate-check")
        vector = {"status": "ephemeral_explicit_vector_roundtrip", "qualified": True}
    return {
        "output": dict(
            status="offline_candidate_smoke",
            versions=versions,
            oauth_request_preparation=True,
            vector=vector,
            production_ready=False,
            independent_evaluation=False,
            limits=[
                "No OAuth server, model inference, sensor or exploit test.",
                "Smoke and dependency matching do not certify all package/native internals or persistent storage.",
            ],
        )
    }, 0


if __name__ == "__main__":
    raise SystemExit(evidence_main(collect))
