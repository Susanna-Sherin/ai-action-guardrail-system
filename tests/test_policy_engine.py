"""
Phase 1 tests -- the policy engine tested in complete isolation, no FastAPI,
no DB, no LLM. These prove the core rule-evaluation logic is correct before
anything else gets built on top of it.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.policy_engine import (
    PolicyEvaluationError,
    PolicyLoadError,
    evaluate_action,
    load_policy,
)

POLICY_PATH = Path(__file__).resolve().parent.parent / "backend" / "policy.yaml"


@pytest.fixture(scope="module")
def policy():
    return load_policy(POLICY_PATH)


def test_policy_loads_with_three_rules(policy):
    assert len(policy["rules"]) == 3
    assert policy["default_action"] == "log_and_allow"


def test_bulk_delete_is_blocked(policy):
    result = evaluate_action(
        {"tool": "db_delete", "params": {"table": "customers", "record_count": 500}},
        policy,
    )
    assert result["outcome"] == "block"
    assert result["matched_rule"] == "block_bulk_delete"


def test_small_delete_is_allowed(policy):
    result = evaluate_action(
        {"tool": "db_delete", "params": {"table": "customers", "record_count": 5}},
        policy,
    )
    assert result["outcome"] == "log_and_allow"
    assert result["matched_rule"] is None  # falls through to default


def test_external_email_requires_hitl(policy):
    result = evaluate_action(
        {
            "tool": "send_email",
            "params": {"recipient": "x@partner.com", "recipient_domain": "partner.com", "body": "hi"},
        },
        policy,
    )
    assert result["outcome"] == "require_hitl"
    assert result["matched_rule"] == "hitl_external_email"


def test_internal_email_is_allowed(policy):
    result = evaluate_action(
        {
            "tool": "send_email",
            "params": {"recipient": "x@company.com", "recipient_domain": "company.com", "body": "hi"},
        },
        policy,
    )
    assert result["outcome"] == "log_and_allow"
    assert result["matched_rule"] is None


def test_confidential_read_is_logged_and_flagged(policy):
    result = evaluate_action(
        {"tool": "read_file", "params": {"path": "/data/confidential/report.pdf"}},
        policy,
    )
    assert result["outcome"] == "log_and_allow"
    assert result["matched_rule"] == "log_confidential_read"


def test_non_confidential_read_falls_to_default(policy):
    result = evaluate_action(
        {"tool": "read_file", "params": {"path": "/data/public/report.pdf"}},
        policy,
    )
    assert result["matched_rule"] is None
    assert result["outcome"] == "log_and_allow"


def test_unknown_tool_falls_to_default(policy):
    result = evaluate_action({"tool": "unknown_tool", "params": {}}, policy)
    assert result["matched_rule"] is None
    assert result["outcome"] == "log_and_allow"


def test_missing_policy_file_raises():
    with pytest.raises(PolicyLoadError):
        load_policy("does_not_exist.yaml")


def test_malformed_policy_raises(tmp_path):
    bad_file = tmp_path / "bad.yaml"
    bad_file.write_text("rules:\n  - name: broken\n    action: block\n")  # missing 'match'
    with pytest.raises(PolicyLoadError):
        load_policy(bad_file)


def test_invalid_action_value_raises(tmp_path):
    bad_file = tmp_path / "bad_action.yaml"
    bad_file.write_text(
        "rules:\n"
        "  - name: broken\n"
        "    match: {tool: db_delete, condition: \"True\"}\n"
        "    action: delete_everything\n"
    )
    with pytest.raises(PolicyLoadError):
        load_policy(bad_file)


def test_bad_condition_raises_evaluation_error(tmp_path):
    bad_file = tmp_path / "bad_condition.yaml"
    bad_file.write_text(
        "rules:\n"
        "  - name: broken_condition\n"
        "    match: {tool: db_delete, condition: \"params['record_count'] >>> 100\"}\n"
        "    action: block\n"
        "default_action: log_and_allow\n"
    )
    bad_policy = load_policy(bad_file)
    with pytest.raises(PolicyEvaluationError):
        evaluate_action({"tool": "db_delete", "params": {"record_count": 5}}, bad_policy)
