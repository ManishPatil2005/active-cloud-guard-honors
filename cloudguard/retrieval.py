"""Auditable lexical retrieval baseline. Deliberately not called vector RAG."""

import hashlib
import math
import re
from collections import Counter
from .limits import knowledge, INPUT_BYTES


def tokens(text):
    # IaC uses identifiers such as POSTGRES_PASSWORD; index constituent words too.
    return re.findall(r"[a-z0-9]+", text.lower().replace("_", " "))


def retrieve(query, kb_path, k=3):
    if not isinstance(query, str) or len(query.encode()) > INPUT_BYTES:
        raise ValueError("query byte budget exceeded")
    if type(k) is not int or not 1 <= k <= 256:
        raise ValueError("retrieval count outside bounds")
    raw, docs = knowledge(kb_path)
    counts = [Counter(tokens(d["title"] + " " + d["text"])) for d in docs]
    terms = set(tokens(query))
    results = []
    for doc, count in zip(docs, counts):
        relevance = sum(
            (1 + math.log(count[t]))
            * math.log(1 + len(docs) / (1 + sum(t in c for c in counts)))
            for t in terms
            if count[t]
        )
        if relevance:
            results.append(
                dict(
                    **doc,
                    relevance=round(relevance, 6),
                    corpus_sha256=hashlib.sha256(raw).hexdigest(),
                )
            )
    return sorted(results, key=lambda d: (-d["relevance"], d["id"]))[:k]
