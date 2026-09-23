"""Persistent Chroma index with local Ollama embeddings and corpus identity."""

import hashlib
import json
from pathlib import Path
from urllib.request import Request, build_opener, ProxyHandler


def embed(texts, model="nomic-embed-text"):
    req = Request(
        "http://127.0.0.1:11434/api/embed",
        data=json.dumps({"model": model, "input": texts, "truncate": False}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with build_opener(ProxyHandler({})).open(req, timeout=120) as response:
        return json.load(response)["embeddings"]


def collection(kb_path, index_path, model):
    import chromadb
    from chromadb.config import Settings

    raw = Path(kb_path).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    docs = json.loads(raw)
    if len({d["id"] for d in docs}) != len(docs):
        raise ValueError("duplicate source ID")
    with build_opener(ProxyHandler({})).open(
        "http://127.0.0.1:11434/api/tags", timeout=5
    ) as response:
        models = json.load(response)["models"]
    normalized = model if ":" in model else model + ":latest"
    matches = [m for m in models if m["name"] == normalized]
    if len(matches) != 1:
        raise ValueError("embedding model missing or ambiguous")
    model_digest = matches[0]["digest"]
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


def index(kb_path, index_path, model="nomic-embed-text"):
    col, docs, digest = collection(kb_path, index_path, model)
    vectors = embed([d["title"] + " " + d["text"] for d in docs], model)
    col.upsert(
        ids=[d["id"] for d in docs],
        embeddings=vectors,
        documents=[d["text"] for d in docs],
        metadatas=[{"source_json": json.dumps(d)} for d in docs],
    )
    return dict(
        count=col.count(),
        corpus_sha256=digest,
        embedding_model=model,
        embedding_digest=col.metadata["embedding_digest"],
        collection=col.name,
    )


def retrieve_vector(query, kb_path, index_path, model="nomic-embed-text", k=3):
    col, docs, digest = collection(kb_path, index_path, model)
    if col.count() != len(docs):
        raise ValueError("index missing/stale; run index command")
    result = col.query(
        query_embeddings=embed([query], model),
        n_results=min(k, len(docs)),
        include=["metadatas", "distances"],
    )
    return [
        dict(**json.loads(meta["source_json"]), distance=distance, corpus_sha256=digest)
        for meta, distance in zip(result["metadatas"][0], result["distances"][0])
    ]
