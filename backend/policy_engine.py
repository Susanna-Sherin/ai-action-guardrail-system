"""
Pure rule-evaluation logic for the Action Guardrail.

No I/O beyond loading the YAML file once. Given a tool-call object and the
loaded policy, evaluate_action() walks the rules in order and returns the
first match's outcome. If nothing matches, the policy's default_action
applies.

This module has zero dependency on FastAPI, the DB, or the LLM -- it's
tested in complete isolation (see tests/test_policy_engine.py).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml
from simpleeval import EvalWithCompoundTypes, InvalidExpression

logger = logging.getLogger("guardrail.policy_engine")

VALID_ACTIONS = {"block", "require_hitl", "log_and_allow"}


class PolicyLoadError(Exception):
    """Raised when the policy YAML is missing, malformed, or invalid."""


class PolicyEvaluationError(Exception):
    """Raised when a rule's condition can't be evaluated (bad expression)."""


def load_policy(path: str | Path) -> dict[str, Any]:
    """Load and lightly validate a policy YAML file."""
    path = Path(path)
    if not path.exists():
        raise PolicyLoadError(f"Policy file not found: {path}")

    with path.open("r") as f:
        try:
            policy = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            raise PolicyLoadError(f"Invalid YAML in {path}: {exc}") from exc

    if not policy or "rules" not in policy:
        raise PolicyLoadError(f"Policy file {path} must define a top-level 'rules' list")

    for rule in policy["rules"]:
        for required in ("name", "match", "action"):
            if required not in rule:
                raise PolicyLoadError(f"Rule missing required field '{required}': {rule}")
        if rule["action"] not in VALID_ACTIONS:
            raise PolicyLoadError(
                f"Rule '{rule['name']}' has invalid action '{rule['action']}'. "
                f"Must be one of {VALID_ACTIONS}"
            )
        if "tool" not in rule["match"] or "condition" not in rule["match"]:
            raise PolicyLoadError(f"Rule '{rule['name']}' match block needs 'tool' and 'condition'")

    policy.setdefault("default_action", "log_and_allow")
    if policy["default_action"] not in VALID_ACTIONS:
        raise PolicyLoadError(f"default_action must be one of {VALID_ACTIONS}")

    logger.info("Loaded policy from %s with %d rule(s)", path, len(policy["rules"]))
    return policy


def evaluate_action(tool_call: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    """
    Evaluate a single tool call against the policy.

    tool_call: {"tool": "db_delete", "params": {"record_count": 500, ...}}
    Returns: {"outcome": "block"|"require_hitl"|"log_and_allow",
              "matched_rule": str | None,
              "reason": str}
    """
    tool = tool_call.get("tool")
    params = tool_call.get("params", {})

    for rule in policy["rules"]:
        if rule["match"]["tool"] != tool:
            continue

        condition = rule["match"]["condition"]
        try:
            matched = EvalWithCompoundTypes(names={"params": params}).eval(condition)
        except InvalidExpression as exc:
            raise PolicyEvaluationError(
                f"Rule '{rule['name']}' condition failed to evaluate: {exc}"
            ) from exc
        except Exception as exc:
            raise PolicyEvaluationError(
                f"Rule '{rule['name']}' condition raised an unexpected error: {exc}"
            ) from exc

        if matched:
            logger.info("Tool call %s matched rule '%s' -> %s", tool, rule["name"], rule["action"])
            return {
                "outcome": rule["action"],
                "matched_rule": rule["name"],
                "reason": f"Matched rule '{rule['name']}': {condition}",
            }

    logger.info("Tool call %s matched no rule -> default '%s'", tool, policy["default_action"])
    return {
        "outcome": policy["default_action"],
        "matched_rule": None,
        "reason": "No rule matched; default action applied",
    }
