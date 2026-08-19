"""63.7 复现链路共享模块（N-c 采集演示 · 机制层；工坊页现象层共用）。

设计依据：demo-redesign-design v0.3 §6（63.7 复现技术说明）+ N1b 报告 §5.5。
**单一事实源**：工坊页 `01_workshop._golden_b_chain`（现象层）与采集页
`02_capture` 的勾选实时重算（机制层）共用本模块——两处数字必须一致
（台账 §10.1-2，验收会独立重算核对）。

输入全部为 demo/data 提炼副本（自包含性硬约束，禁止读仓库外
cellvoyager-outputs）：
- ``verdicts_10X_B.jsonl``：M1 声明重建（``provenance_source == "M1声明"``，
  按 verdict_id 去重取末条 → 11 条，含 skip_doublet——它会被交叉验证判虚报
  撤销，随后按 expected 补入）；
- ``golden_agent_10X_B_executed.py``：M3 解析输入（解析专用副本，不执行）；
- ``windowL_10X_B_expected.json``：63.7 断言基准（provenance 保留
  source=windowL_10X_B_expected.json）。

链路（设计 §6）：M1 重建 → M3 解析（79 候选）→ ``expected_types_for``
（11 决策）→ ``CrossValidator.validate(..., expected_types=...)`` →
stats{consistent 10, false_positive 1, expected_added 1} → final 11 决策
→ ``run_audit`` → **63.7 · blocked**（与断言基准实时比对）。

外围层纪律：只调 bioaudit.capture 公共类 + bioaudit.api.run_audit，
零评分路径改动（引擎/规则/本体/黄金资产零改动，golden 0 差异硬验收）。
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from bioaudit.api.audit import run_audit
from bioaudit.capture.cross_validator import CrossValidator
from bioaudit.capture.expected_types import expected_types_for
from bioaudit.capture.m3_parser import M3Parser
from bioaudit.capture.models import PROVENANCE_SOURCE_M1

#: demo/data 提炼副本路径（模块自包含：不依赖 sys.path / cwd；启动校验
#: 由 app.py 的 verify_data_ready 统一把关）。
_DATA_DIR = Path(__file__).resolve().parent / "data"
#: 说明（Standards #F4 闭环）：63.7 链路的路径**以本模块为单一事实源**；
#: data_index 同名公开函数（executed_10X_B_path / windowL_10X_B_expected_path）
#: 保留为索引接口（N1a 交付契约，N-d/N-e 可能使用），不再被链路调用。
VERDICTS_PATH = _DATA_DIR / "verdicts_10X_B.jsonl"
EXECUTED_PATH = _DATA_DIR / "golden_agent_10X_B_executed.py"
BENCHMARK_PATH = _DATA_DIR / "windowL_10X_B_expected.json"

#: 会话事实声明（declared，三级可信源：调用参数 > 数据元数据 > declared；
#: 评测者/数据事实注入，与 Agent 自证 M1 严格区分——G-2 纪律）。
#: sequencing=10X_scRNA_seq → 平台键 scrna_10x → 11 决策预期清单；
#: 补入决策的上下文 = M1 事实（Agent 声明 context）优先，不伪造。
DECLARED: dict[str, str] = {"sequencing": "10X_scRNA_seq"}


def load_m1_declarations() -> list[dict]:
    """从 verdicts 提炼副本重建 M1 声明（provenance_source == M1声明，
    按 verdict_id 去重取末条）。"""
    records: dict[str, dict] = {}
    for line in VERDICTS_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if rec.get("provenance_source") != PROVENANCE_SOURCE_M1:
            continue
        snap = rec.get("score_snapshot") or {}
        records[rec["verdict_id"]] = {
            "step_id": rec.get("step_id"),
            "decision_type": rec.get("decision_type"),
            "choice": rec.get("choice"),
            "rationale": snap.get("agent_rationale", ""),
            "context": snap.get("context", {}),
            "verdict_id": rec.get("verdict_id"),
        }
    return list(records.values())


def default_expected() -> list[str]:
    """当前配置下 10X scRNA 预期决策点清单（11 决策，B7 豁免已应用）。"""
    return expected_types_for("scrna", dict(DECLARED))


def run_chain(expected: Optional[list[str]] = None) -> dict:
    """完整 63.7 复现链路（expected 可注入——采集页勾选交互传子集）。

    Returns
    -------
    dict
        n_m1 / m3_n_candidates / stats / alignments（序列化）/
        added / final_n / state（run_audit 结果）/ had_error /
        generated_at / benchmark（断言基准）——键名与 N1b 工坊页
        ``_golden_b_chain`` 返回一致（现象/机制共用同一形状）。
    """
    m1 = load_m1_declarations()
    parser = M3Parser(act="scrna", metadata=None, declared=dict(DECLARED))
    m3 = parser.parse_code(
        EXECUTED_PATH.read_text(encoding="utf-8"),
        source="golden_agent_10X_B_executed.py",
    )
    expected_list = list(expected) if expected is not None else default_expected()

    result = CrossValidator(act="scrna").validate(
        m1, m3,
        session_id="demo_capture_goldenB_63_7",
        expected_types=expected_list,
        expected_context=dict(DECLARED),
    )

    # final 轨迹（final-only 消费纪律 B4）：一致声明 + 补入决策
    consistent_keys = {
        (a.m1["step_id"], a.m1["decision_type"])
        for a in result.alignments if a.status == "consistent" and a.m1
    }
    final_decisions = [
        {k: d[k] for k in ("step_id", "decision_type", "choice", "rationale", "context")}
        for d in m1 if (d["step_id"], d["decision_type"]) in consistent_keys
    ]
    final_decisions += [
        {k: d[k] for k in ("step_id", "decision_type", "choice", "rationale", "context")}
        for d in result.added_decisions
    ]
    state = run_audit(final_decisions, act="scrna")
    had_error = bool(state.get("error"))
    if had_error:
        state.setdefault("trajectory_score", 0.0)
        state.setdefault("eval_verdict", "error")
        state.setdefault("dimension_scores", {})
        state.setdefault("step_scores", [])
        state.setdefault("critical_issues", [])

    return {
        "n_m1": len(m1),
        "m3_n_candidates": len(m3.candidates),
        "m3_n_uncertain": len(m3.uncertain),
        "stats": dict(result.stats),
        "alignments": [
            {
                "decision_type": a.decision_type,
                "status": a.status,
                "expected_added": a.expected_added,
                "auto_added": a.auto_added,
                "m1_choice": a.m1["choice"] if a.m1 else None,
                "m3_tool": a.m3["tool_call"] if a.m3 else None,
                "m3_choice": a.m3["choice"] if a.m3 else None,
                "n_instances": len(a.instances),
                "detail": a.detail,
            }
            for a in result.alignments
        ],
        "added": [
            {"decision_type": d["decision_type"], "choice": d["choice"],
             "context": d.get("context", {})}
            for d in result.added_decisions
        ],
        "final_n": len(final_decisions),
        "state": state,
        "had_error": had_error,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "benchmark": load_benchmark(),
    }


def load_benchmark() -> dict:
    """63.7 断言基准（demo/data 提炼副本，provenance 保留
    source=windowL_10X_B_expected.json）。"""
    bench = json.loads(BENCHMARK_PATH.read_text(encoding="utf-8"))
    return {
        "trajectory_score": bench["audit"]["trajectory_score"],
        "eval_verdict": bench["audit"]["eval_verdict"],
        "n_decisions": bench["final_trajectory"]["n_decisions"],
        "expected_effective": bench["expected_types"]["effective"],
        "provenance": bench.get("provenance", {}),
    }


def chain_matches_benchmark(chain: dict, bench: dict) -> tuple[bool, list[str]]:
    """实时重算 vs 断言基准核对（分数 + verdict + 决策数 + 补入类型）。"""
    state = chain["state"]
    mismatches: list[str] = []
    if abs(state["trajectory_score"] - bench["trajectory_score"]) >= 1e-9:
        mismatches.append(
            f"分数 {state['trajectory_score']:.1f} != 基准 {bench['trajectory_score']:.1f}"
        )
    if state["eval_verdict"] != bench["eval_verdict"]:
        mismatches.append(
            f"verdict {state['eval_verdict']} != 基准 {bench['eval_verdict']}"
        )
    if chain["final_n"] != bench["n_decisions"]:
        mismatches.append(
            f"决策数 {chain['final_n']} != 基准 {bench['n_decisions']}"
        )
    added_types = [a["decision_type"] for a in chain["added"]]
    if added_types != ["doublet_detection"]:
        mismatches.append(f"补入类型 {added_types} != 预期 [doublet_detection]")
    return not mismatches, mismatches
