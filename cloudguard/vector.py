"""Persistent Chroma index with local Ollama embeddings and corpus identity."""

import hashlib
import json
import math
from urllib.request import Request, build_opener, ProxyHandler
from .llm import LocalOnlyRedirect, identity_from_models
from .limits import knowledge, json_response, json_value, INPUT_BYTES


def embed(texts, model="nomic-embed-text"):
    if (
        not isinstance(texts, list)
        or not 1 <= len(texts) <= 256
        or any(not isinstance(text, str) for text in texts)
    ):
        raise ValueError("embedding input count/type outside bounds")
    if sum(len(text.encode()) for text in texts) > INPUT_BYTES:
        raise ValueError("embedding input byte budget exceeded")
    req = Request(
        "http://127.0.0.1:11434/api/embed",
        data=json.dumps({"model": model, "input": texts, "truncate": False}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with build_opener(ProxyHandler({}), LocalOnlyRedirect()).open(
        req, timeout=120
    ) as response:
        payload = json_response(response)
    if not isinstance(payload, dict) or "embeddings" not in payload:
        raise ValueError("invalid embedding response envelope")
    vectors = payload["embeddings"]
    if not isinstance(vectors, list) or len(vectors) != len(texts):
        raise ValueError("embedding row count mismatch")
    dimension = None
    for row in vectors:
        if not isinstance(row, list) or not 1 <= len(row) <= 8192:
            raise ValueError("embedding dimension outside bounds")
        if dimension is not None and len(row) != dimension:
            raise ValueError("embedding dimensions disagree")
        dimension = len(row)
        if any(
            type(v) not in (int, float)
            or (isinstance(v, float) and not math.isfinite(v))
            or not -1e100 <= v <= 1e100
            for v in row
        ):
            raise ValueError("invalid embedding numeric value")
    return vectors


def collection(kb_path, index_path, model):
    raw, docs = knowledge(kb_path)
    import chromadb
    from chromadb.config import Settings

    digest = hashlib.sha256(raw).hexdigest()
    with build_opener(ProxyHandler({}), LocalOnlyRedirect()).open(
        "http://127.0.0.1:11434/api/tags", timeout=5
    ) as response:
        payload = json_response(response)
    model_digest = identity_from_models(payload, model)
    identity = hashlib.sha256((digest + model_digest).encode()).hexdigest()
    client = chromadb.PersistentClient(
        path=str(index_path), settings=Settings(anonymized_telemetry=False)
    )
    col = client.get_or_create_collection(
        name="knowledge-" + identity[:24],
        embedding_function=None,
        metadata={
            "corpus_sha256": digest,
            "embedding_model": model,
            "embedding_digest": model_digest,
            "hnsw:space": "cosine",
        },
    )
    return col, docs, digest


def index(kb_path, index_path, model="nomic-embed-text", *, force=False):
    col, docs, digest = collection(kb_path, index_path, model)
    expected = {d["id"] for d in docs}
    existing = set(col.get(include=[])["ids"])
    if not force and col.count() == len(docs) and existing == expected:
        return dict(
            count=col.count(),
            corpus_sha256=digest,
            embedding_model=model,
            embedding_digest=col.metadata["embedding_digest"],
            collection=col.name,
            reused=True,
            embedded_documents=0,
        )
    vectors = embed([d["title"] + " " + d["text"] for d in docs], model)
    col.upsert(
        ids=[d["id"] for d in docs],
        embeddings=vectors,
        documents=[d["text"] for d in docs],
        metadatas=[{"source_json": json.dumps(d)} for d in docs],
    )
    if existing - expected:
        col.delete(ids=sorted(existing - expected))
    return dict(
        count=col.count(),
        corpus_sha256=digest,
        embedding_model=model,
        embedding_digest=col.metadata["embedding_digest"],
        collection=col.name,
        reused=False,
        embedded_documents=len(docs),
    )


def retrieve_vector(query, kb_path, index_path, model="nomic-embed-text", k=3):
    if type(k) is not int or not 1 <= k <= 256:
        raise ValueError("vector result count outside bounds")
    col, docs, digest = collection(kb_path, index_path, model)
    if col.count() != len(docs):
        raise ValueError("index missing/stale; run index command")
    result = col.query(
        query_embeddings=embed([query], model),
        n_results=min(k, len(docs)),
        include=["metadatas", "distances"],
    )
    count = min(k, len(docs))
    if not isinstance(result, dict):
        raise ValueError("invalid vector result envelope")
    rows = []
    for field in ("ids", "metadatas", "distances"):
        value = result.get(field)
        if (
            not isinstance(value, list)
            or len(value) != 1
            or not isinstance(value[0], list)
            or len(value[0]) != count
        ):
            raise ValueError("invalid vector result rows")
        rows.append(value[0])
    sources = {doc["id"]: doc for doc in docs}
    accepted, seen, total_bytes = [], set(), 0
    for source_id, meta, distance in zip(*rows):
        if (
            not isinstance(source_id, str)
            or source_id not in sources
            or source_id in seen
            or not isinstance(meta, dict)
            or not isinstance(meta.get("source_json"), str)
            or type(distance) not in (int, float)
            or not -1e100 <= distance <= 1e100
            or not math.isfinite(distance)
        ):
            raise ValueError("invalid vector source or distance")
        stored = meta["source_json"]
        if len(stored) > INPUT_BYTES:
            raise ValueError("vector source byte budget exceeded")
        total_bytes += len(stored.encode("utf-8"))
        if total_bytes > INPUT_BYTES:
            raise ValueError("vector source byte budget exceeded")
        if json.dumps(json_value(stored), sort_keys=True) != json.dumps(
            sources[source_id], sort_keys=True
        ):
            raise ValueError("vector source differs from current corpus")
        seen.add(source_id)
        # The current corpus, not index metadata, supplies returned knowledge.
        accepted.append(
            dict(sources[source_id], distance=distance, corpus_sha256=digest)
        )
    return accepted
