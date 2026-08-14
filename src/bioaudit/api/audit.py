"""审计 API 单一入口（v1 蓝图：api/ 单一入口 run_audit / audit_decision / reward）。

自 fullflow-demo/src/orchestration/graph.py 迁移 7 步管道，变更：
- 路径全部包内锚定（bioaudit.paths），零 cwd 依赖（F7）
- 支持按范式（act）加载规则集：deg / pan / scrna（与 golden 复算口径一致）；
  不传 act 则加载全量规则（C2 去重后 38 唯一规则）
- B1/B3：输入 schema 校验（pydantic Decision），非法输入显式报错；
  完整 API 契约（错误码/paradigm 参数）在 B3 落地

返回 dict（与旧 run_audit state 兼容）：
session_id / parsed_steps / matched_rules / step_scores / conflicts /
dimension_scores / trajectory_score / eval_verdict / critical_issues /
error_chains / report
"""

import logging
import uuid

from bioaudit.engine.aggregator import ScoreAggregator
from bioaudit.engine.conflict_detector import ConflictDetector
from bioaudit.engine.error_tracer import ErrorPropagationTracer
from bioaudit.engine.evaluator import LEVEL_TO_SCORE, RuleEvaluator
from bioaudit.engine.matcher import RuleMatcher
from bioaudit.models.decision import Decision, ParsedStep
from bioaudit.models.score import DecisionScore
from bioaudit.paths import rules_dir_for
from bioaudit.storage.event_store import AuditEvent, EventStore
from bioaudit.storage.rule_registry import RuleRegistry

logger = logging.getLogger(__name__)


def _registry_for(act: str | None = None) -> RuleRegistry:
    """按范式建 registry；None → 全量规则（38 唯一）。"""
    registry = RuleRegistry(rules_dir_for(act))
    registry.load_all()
    return registry


def run_audit(
    trajectory: list[dict],
    act: str | None = None,
    profile_id: str = "default",
    session_id: str | None = None,
    human_overrides: dict | None = None,
) -> dict:
    """Run a complete 7-step audit pipeline over a trajectory of decisions.

    Parameters
    ----------
    trajectory : list[dict]
        决策列表，每项满足 bioaudit.models.decision.Decision 的 schema
        （step_id / decision_type / choice / rationale / context / ...）。
    act : str | None
        范式规则集："deg" | "pan" | "scrna"；None = 全量规则。
    human_overrides : dict[str, int]
        {step_id: level} 人工覆写（非法 level 会在 B3 契约中校验）。

    Returns
    -------
    dict
        完整审计状态（含 report）。错误时 state["error"] 非空。
    """
    registry = _registry_for(act)
    matcher = RuleMatcher(registry)
    evaluator = RuleEvaluator()
    aggregator = ScoreAggregator()
    conflict_detector = ConflictDetector()
    error_tracer = ErrorPropagationTracer()

    session_id = session_id or f"audit_{uuid.uuid4().hex[:8]}"
    human_overrides = human_overrides or {}

    event_store = EventStore()
    event_store.start_session(session_id)

    state: dict = {
        "session_id": session_id,
        "profile_id": profile_id,
        "act": act,
        "error": None,
    }

    # ── Step 1: Parse（B1/B3：pydantic 校验，非法输入显式报错）──
    try:
        parsed_steps = []
        for item in trajectory:
            decision = Decision(**item)
            parsed, _ = matcher.match(decision)
            parsed_steps.append(parsed.model_dump())
        state["parsed_steps"] = parsed_steps
        event_store.append(AuditEvent(
            event_type="parse_complete", node="parse",
            payload={"n_decisions": len(parsed_steps)},
        ))
    except Exception as e:
        state["error"] = f"Parse failed: {e}"
        return state

    # ── Step 2: Match rules ──
    try:
        matched = {}
        for step_dict in state["parsed_steps"]:
            parsed = ParsedStep(**step_dict)
            rules = matcher.match_parsed(parsed)
            matched[parsed.step_id] = [r.rule_id for r in rules]
            event_store.append(AuditEvent(
                event_type="rule_matched", node="match",
                payload={"step_id": parsed.step_id, "n_rules": len(rules),
                         "rule_ids": [r.rule_id for r in rules]},
            ))
        state["matched_rules"] = matched
    except Exception as e:
        state["error"] = f"Rule matching failed: {e}"
        return state

    # ── Step 3: Evaluate decisions ──
    try:
        step_scores = []
        for step_dict in state["parsed_steps"]:
            parsed = ParsedStep(**step_dict)
            rule_ids = state["matched_rules"].get(parsed.step_id, [])
            rules = [registry.get_rule(rid) for rid in rule_ids]
            rules = [r for r in rules if r is not None]

            override = human_overrides.get(parsed.step_id)
            if override is not None:
                score = evaluator.evaluate(parsed, rules)
                score.level = override
                score.numeric_score = LEVEL_TO_SCORE.get(override, 0.5)
                score.explanation += f" [human override: Lvl -> {override}]"
                event_store.append(AuditEvent(
                    event_type="human_overrode", node="evaluate",
                    payload={"step_id": parsed.step_id, "new_level": override},
                ))
            else:
                score = evaluator.evaluate(parsed, rules)

            step_scores.append(score.model_dump())
            event_store.append(AuditEvent(
                event_type="decision_scored", node="evaluate",
                payload={"step_id": parsed.step_id, "level": score.level,
                         "agent_choice": parsed.original.choice},
            ))
        state["step_scores"] = step_scores
    except Exception as e:
        state["error"] = f"Evaluation failed: {e}"
        return state

    # ── Step 4: Detect conflicts ──
    try:
        all_conflicts = []
        for step_dict in state["parsed_steps"]:
            step_id = step_dict["step_id"]
            rule_ids = state["matched_rules"].get(step_id, [])
            rules = [registry.get_rule(rid) for rid in rule_ids]
            rules = [r for r in rules if r is not None]
            if len(rules) >= 2:
                parsed = ParsedStep(**step_dict)
                scores_per_rule = evaluator.evaluate_all_rules(parsed, rules)
                conflicts = conflict_detector.detect(
                    step_id, rules, scores_per_rule
                )
                all_conflicts.extend(conflicts)
                for c in conflicts:
                    event_store.append(AuditEvent(
                        event_type="conflict_detected",
                        node="detect_conflicts", payload=c,
                    ))
        state["conflicts"] = all_conflicts
    except Exception as e:
        logger.warning(f"Conflict detection failed (non-fatal): {e}")
        state["conflicts"] = []

    # ── Step 5: Aggregate ──
    try:
        scores = [DecisionScore(**s) for s in state["step_scores"]]
        agg = aggregator.aggregate(scores)
        state["dimension_scores"] = agg.dimension_scores
        state["trajectory_score"] = agg.trajectory_score
        state["eval_verdict"] = agg.verdict
        state["critical_issues"] = agg.critical_issues
        event_store.append(AuditEvent(
            event_type="aggregation_complete", node="aggregate",
            payload={"trajectory_score": agg.trajectory_score,
                     "verdict": agg.verdict},
        ))
    except Exception as e:
        state["error"] = f"Aggregation failed: {e}"
        return state

    # ── Step 6: Trace error propagation ──
    try:
        scores = [DecisionScore(**s) for s in state["step_scores"]]
        chains = error_tracer.trace(scores)
        state["error_chains"] = [c.model_dump() for c in chains]
        event_store.append(AuditEvent(
            event_type="propagation_traced", node="trace",
            payload={"n_error_chains": len(chains)},
        ))
    except Exception as e:
        logger.warning(f"Error tracing failed (non-fatal): {e}")
        state["error_chains"] = []

    # ── Step 7: Generate report（C1 三元组快照字段预留，B5 正式绑定）──
    try:
        report = {
            "audit_id": state["session_id"],
            "profile": state["profile_id"],
            "act": act,
            "engine_version": __import__("bioaudit").ENGINE_VERSION,
            "ruleset_version": None,   # B5: 从 rules/ruleset.json 读取并写死
            "ontology_version": None,  # B5: 本体版本
            "n_decisions": len(state.get("parsed_steps", [])),
            "n_rules_matched": sum(
                len(v) for v in state.get("matched_rules", {}).values()
            ),
            "trajectory_score": state.get("trajectory_score", 0),
            "verdict": state.get("eval_verdict", "unknown"),
            "critical_issues": state.get("critical_issues", []),
            "dimension_scores": state.get("dimension_scores", {}),
            "error_chains": state.get("error_chains", []),
            "conflicts_needing_review": [
                c for c in state.get("conflicts", [])
                if c.get("resolution") == "NEEDS_HUMAN_REVIEW"
            ],
        }
        state["report"] = report
        event_store.append(AuditEvent(
            event_type="report_generated", node="report", payload=report,
        ))
    except Exception as e:
        state["error"] = f"Report generation failed: {e}"

    return state


def audit_decision(
    decision: dict,
    act: str | None = None,
    mappings_dir=None,
) -> dict:
    """单决策审计（B1/B3 契约入口之一；reward 入口在阶段 4）。

    返回 DecisionScore 的 model_dump()，含 matched_rules / level / explanation /
    evidence_citations / alternatives / reward_signal。
    """
    from bioaudit.engine.evaluator import RuleEvaluator
    from bioaudit.engine.matcher import RuleMatcher

    registry = _registry_for(act)
    matcher = RuleMatcher(registry, mappings_dir)
    evaluator = RuleEvaluator()

    parsed, rules = matcher.match(Decision(**decision))
    score = evaluator.evaluate(parsed, rules)
    return score.model_dump()


def match_details(
    decision_type: str,
    context: dict,
    act: str | None = None,
) -> list[dict]:
    """透明匹配明细（UI 展示"引擎检查了什么"；规则/条件逐条评估）。"""
    registry = _registry_for(act)
    return registry.match_with_details(decision_type, context)
