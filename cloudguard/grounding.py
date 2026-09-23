"""Narrow evidence checks for the two authentication policies in the smoke study.

This is a deterministic admission guard, NOT independent ground truth or proof of
RAG improvement. Uncovered policy types still require human review.
"""

import re


def corroborate(finding, locations):
    source_ids = finding["source_ids"]
    location = finding["location"]
    value = locations.get(location)
    if "postgres-trust" in source_ids:
        matched = (
            location.endswith("/POSTGRES_HOST_AUTH_METHOD")
            and str(value).lower() == "trust"
        )
        if location.startswith("line:"):
            matched = bool(re.match(r"host\S*\s+.*\s+trust\s*$", str(value).strip()))
        return "corroborated" if matched else "unsupported_postgres_trust_claim"
    if "redis-security" in source_ids:
        # Array command: require the option and its adjacent value in the same array.
        match = re.match(r"^(.*?/command)/(\d+)$", location)
        if match:
            prefix = match[1]
            tokens = [
                v
                for key, v in sorted(
                    locations.items(),
                    key=lambda pair: int(pair[0].rsplit("/", 1)[1])
                    if pair[0].startswith(prefix + "/")
                    and pair[0].rsplit("/", 1)[1].isdigit()
                    else -1,
                )
                if key.startswith(prefix + "/")
            ]
            command = " ".join(map(str, tokens))
        else:
            command = str(value)
        matched = bool(re.search(r"(?:--)?protected-mode(?:\s+|=)no\b", command))
        return "corroborated" if matched else "unsupported_redis_protection_claim"
    return "requires_human_entailment_review"
