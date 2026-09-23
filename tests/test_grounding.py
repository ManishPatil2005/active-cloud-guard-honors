from cloudguard.grounding import corroborate


def test_password_reference_cannot_corroborate_trust():
    finding = {
        "location": "/services/app/environment/POSTGRES_PASSWORD",
        "source_ids": ["postgres-trust"],
    }
    assert (
        corroborate(finding, {finding["location"]: "${PG_PASSWORD}"})
        == "unsupported_postgres_trust_claim"
    )


def test_trust_corroboration_requires_actual_value():
    finding = {
        "location": "/services/app/environment/POSTGRES_HOST_AUTH_METHOD",
        "source_ids": ["postgres-trust"],
    }
    assert corroborate(finding, {finding["location"]: "trust"}) == "corroborated"
    assert (
        corroborate(finding, {finding["location"]: "scram-sha-256"})
        == "unsupported_postgres_trust_claim"
    )


def test_redis_protection_adjacent_command_tokens():
    finding = {"location": "/services/app/command/1", "source_ids": ["redis-security"]}
    locations = {
        "/services/app/command/0": "redis-server",
        "/services/app/command/1": "--protected-mode",
        "/services/app/command/2": "no",
    }
    assert corroborate(finding, locations) == "corroborated"
    locations["/services/app/command/2"] = "yes"
    assert corroborate(finding, locations) == "unsupported_redis_protection_claim"


def test_other_sources_remain_review_required():
    assert (
        corroborate({"location": "x", "source_ids": ["aws-sg"]}, {"x": "value"})
        == "requires_human_entailment_review"
    )
