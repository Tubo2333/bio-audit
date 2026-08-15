"""规则覆盖审计（refactor-plan-v1.1 E5；execution-plan D5.12）。

任务集准入：覆盖全部 34 决策类型 + 38 唯一规则；零触发规则 = 0 或显式豁免
清单（附理由）。本模块是 benchmark-validate 的覆盖闸。

实现：
- 类型覆盖：任务 decisions 的 decision_type 并集 vs 本体 34 类型；
- 规则覆盖：对每条任务跑 RuleMatcher（与评分同路径的匹配层），收集命中的
  rule_id 并集 vs ruleset.json 的 38 唯一规则；
- 零触发清单：未命中类型/规则 + 豁免理由字段（由审计者显式填写）。

golden 不变量：本模块只读匹配（不评分、不聚合），不改任何评分路径。
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from bioaudit.benchmark.manifest import load_tasks
from bioaudit.engine.matcher import RuleMatcher
from bioaudit.models.decision import Decision
from bioaudit.paths import ACT_RULE_SUBDIRS, ONTOLOGY_DIR, rules_dir_for
from bioaudit.storage.rule_registry import RuleRegistry

#: 本体 34 类型（决策类型定义文件）
ONTOLOGY_TYPES = sorted(p.stem for p in (ONTOLOGY_DIR / "decision_types").glob("*.yaml"))


def collect_task_types(tasks: list[dict]) -> dict[str, int]:
    """任务集 → {decision_type: 出现次数}。"""
    counts: dict[str, int] = {}
    for t in tasks:
        for d in t["decisions"]:
            counts[d["decision_type"]] = counts.get(d["decision_type"], 0) + 1
    return counts


def collect_matched_rules(tasks: list[dict]) -> dict[str, dict]:
    """任务集 → 规则命中 {rule_id: {n_decisions, examples: [task_id...]}}。

    与评分同路径：RuleMatcher(registry[act]).match(Decision) —— 只匹配不评分。
    """
    registries = {}
    for act in ACT_RULE_SUBDIRS:
        reg = RuleRegistry(rules_dir_for(act))
        reg.load_all()
        registries[act] = reg

    matched: dict[str, dict] = {}
    for t in tasks:
        act = t["act"]
        matcher = RuleMatcher(registries[act])
        for d in t["decisions"]:
            try:
                parsed, rules = matcher.match(Decision(**d))
            except Exception:
                continue  # 单条解析失败不阻断审计（与引擎行为一致：BadDecision → -1）
            for r in rules:
                entry = matched.setdefault(r.rule_id, {"n_decisions": 0, "examples": []})
                entry["n_decisions"] += 1
                if t["trajectory_id"] not in entry["examples"]:
                    entry["examples"].append(t["trajectory_id"])
    return matched


def audit(
    tasks_dir: Optional[Path | str] = None,
    exemptions: Optional[dict[str, str]] = None,
) -> dict:
    """覆盖审计主入口 → 结构化报告。

    exemptions: {rule_id 或 decision_type: 豁免理由}——零触发规则的显式豁免
    清单（D5.12：零触发 = 0 或显式豁免附理由）。
    """
    from bioaudit.benchmark.paths import TASKS_DIR

    td = Path(tasks_dir) if tasks_dir else TASKS_DIR
    tasks = load_tasks(td)
    exemptions = exemptions or {}

    type_counts = collect_task_types(tasks)
    matched = collect_matched_rules(tasks)

    # 38 唯一规则（从规则文件读取 rule_id，跨范式副本去重）
    import yaml as _yaml

    rd = Path(__file__).resolve().parent.parent / "rules" / "data"
    unique_rules: set[str] = set()
    for f in rd.rglob("*.yaml"):
        data = _yaml.safe_load(f.read_text(encoding="utf-8"))
        rid = data.get("rule_id") if isinstance(data, dict) else None
        if rid:
            unique_rules.add(str(rid))
    unique_rules = sorted(unique_rules)

    missing_types = [t for t in ONTOLOGY_TYPES if t not in type_counts]
    missing_rules = [r for r in unique_rules if r not in matched]

    # 豁免后为零触发规则
    remaining_missing_rules = [r for r in missing_rules if r not in exemptions]

    ok = not missing_types and not remaining_missing_rules
    return {
        "ok": ok,
        "n_ontology_types": len(ONTOLOGY_TYPES),
        "n_types_covered": len(type_counts),
        "missing_types": missing_types,
        "n_rules_total": len(unique_rules),
        "n_rules_matched": len(matched),
        "missing_rules": missing_rules,
        "zero_trigger_rules": missing_rules,
        "exemptions": {k: v for k, v in exemptions.items() if k in missing_rules},
        "remaining_missing_rules": remaining_missing_rules,
        "type_counts": dict(sorted(type_counts.items())),
        "rule_counts": {r: m["n_decisions"] for r, m in sorted(matched.items())},
        "note": "覆盖审计：34 类型 + 38 规则；零触发 = 0 或显式豁免（附理由，D5.12）",
    }


__all__ = ["ONTOLOGY_TYPES", "collect_task_types", "collect_matched_rules", "audit"]
