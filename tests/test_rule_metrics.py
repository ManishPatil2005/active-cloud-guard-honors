import pytest

from cloudguard.metrics import rule_metrics


def test_wrong_rule_does_not_get_true_positive_credit():
    result = rule_metrics({"a": ["AUTH"]}, {"a": ["NET"]})
    assert (result["tp"], result["fp"], result["fn"]) == (0, 1, 1)
    assert (result["precision"], result["recall"], result["f1"]) == (0, 0, 0)


def test_exact_case_identity_prevents_cross_case_matching():
    result = rule_metrics({"a": ["R"], "b": []}, {"a": [], "b": ["R"]})
    assert result["per_rule"] == {"R": {"tp": 0, "fp": 1, "fn": 1}}
    assert result["mismatched_cases"] == 2


def test_multiple_rules_and_empty_case_conserve_totals():
    result = rule_metrics(
        {"a": ["A", "B"], "b": ["A"], "c": []},
        {"a": ["A", "C"], "b": ["A"], "c": []},
    )
    assert (result["tp"], result["fp"], result["fn"]) == (2, 1, 1)
    assert result["expected_instances"] == result["predicted_instances"] == 3
    assert result["exact_match_cases"] == 2
    assert result["precision"] == result["recall"] == result["f1"] == 2 / 3
    assert result["tn"] is None and result["false_positive_rate"] is None


@pytest.mark.parametrize(
    "expected,actual,precision,recall,f1",
    [([], [], None, None, None), (["R"], [], None, 0, 0), ([], ["R"], 0, None, 0)],
)
def test_undefined_denominators(expected, actual, precision, recall, f1):
    result = rule_metrics({"a": expected}, {"a": actual})
    assert (result["precision"], result["recall"], result["f1"]) == (
        precision,
        recall,
        f1,
    )


@pytest.mark.parametrize(
    "bad",
    [
        None,
        {},
        [],
        {"": []},
        {1: []},
        {"a": None},
        {"a": "R"},
        {"a": [True]},
        {"a": [None]},
        {"a": [""]},
        {"a": [" "]},
        {"a": ["R", "R"]},
        {"a": [{}]},
        {"a": ["R" * 257]},
    ],
)
@pytest.mark.parametrize("side", ["labels", "predictions"])
def test_invalid_identity_or_shape_is_rejected(bad, side):
    with pytest.raises(ValueError):
        rule_metrics(bad, {"a": []}) if side == "labels" else rule_metrics(
            {"a": []}, bad
        )


def test_case_inventory_must_match():
    with pytest.raises(ValueError, match="exactly match"):
        rule_metrics({"a": []}, {"b": []})


def test_input_order_does_not_change_accounting_or_mutate_inputs():
    labels, predictions = {"b": ["Z", "A"], "a": []}, {"a": [], "b": ["A", "Z"]}
    result = rule_metrics(labels, predictions)
    assert result == rule_metrics(dict(reversed(list(labels.items()))), predictions)
    assert list(result["per_rule"]) == ["A", "Z"]
    assert labels["b"] == ["Z", "A"]


@pytest.mark.parametrize("kind", ["cases", "rules", "case_length"])
def test_resource_limits(kind):
    bad = (
        {str(i): [] for i in range(10001)}
        if kind == "cases"
        else {"a": [str(i) for i in range(1001)]}
        if kind == "rules"
        else {"a" * 1025: []}
    )
    with pytest.raises(ValueError):
        rule_metrics(bad, bad)
