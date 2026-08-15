"""预注册协议（refactor-plan-v1.1 E1；execution-plan D2.6）。

v1.1 裁决：阶段 3 验收"隐藏集与公开集一致"改为 **预注册 gap 容忍区间 + 负向告警**
——两集分数 gap 超出预注册容忍区间 → 负向告警（泄漏信号），替代"两集一致"验收。

本模块是**预注册记录的唯一事实源**（record 常量冻结，2026-08-16）：
- 公开/隐藏集划分方法（分层随机：范式 × 难度，seed=42，70/30）
- gap 统计量与容忍区间
- IRR 门槛（E3：κ/α ≥ 0.8 准入）与难度 rubric 版本

实现要点：
- ``assign_split``：确定性（给定任务清单 → 同一划分）；划分在 gold+难度冻结后
  一次性执行并写入 taskset.json（E1：先预注册、后划分、再评测）。
- ``check_gap``：|Δ| 超出容忍区间 → alarm=True（泄漏信号负向告警）。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

PRE_REGISTRATION_VERSION = "pr.v1"
RECORD_ID = "benchmark-pr-2026-08-16-01"

#: 预注册记录（冻结；任何修改需走评审并提升 RECORD_ID）
PRE_REGISTRATION: dict[str, Any] = {
    "record_id": RECORD_ID,
    "date": "2026-08-16",
    "version": PRE_REGISTRATION_VERSION,
    "split": {
        "method": "stratified_random_by_paradigm_and_difficulty",
        "seed": 42,
        "public_ratio": 0.7,
        "note": "按范式×难度分层后按 seed 确定性划分；划分在 gold+难度冻结后"
                "执行并写入 taskset.json",
    },
    "gap": {
        "statistic": "mean(trajectory_score/100) over tasks: public - hidden",
        "tolerance_interval": [-0.10, 0.10],
        "alarm_rule": "Δ 超出 [-0.10, 0.10] → 负向告警（泄漏信号），替代'两集一致'验收（E1）",
        "report_note": "gap 只作为泄漏信号登记；不据此修改任何分数或任务",
    },
    "irr_gate": {
        "primary": "cohen_kappa_3class >= 0.8",
        "secondary": "krippendorff_alpha_nominal >= 0.8",
        "calibration_batch_size": 10,
        "note": "校准批 10 条双标注达标后放量（E3）",
    },
    "difficulty_rubric_version": "difficulty.v1",
    "annotation_rubric_version": "annotation.v1",
    "model_policy": "生成器与评测 Agent 不同模型（E6）；模型信息记录在任务集元数据",
    "contamination_policy": "任务/生成器提示词中规则标识/标题命中登记为污染特征（E2），命中即标记",
}


def pre_registration_path(pkg_root: Optional[Path] = None) -> Path:
    """预注册记录落盘路径（docs 侧副本 + 包内 record）。"""
    base = pkg_root or Path(__file__).resolve().parent
    return base / "pre_registration.json"


def save_pre_registration(pkg_root: Optional[Path] = None) -> Path:
    """把预注册记录写为 JSON（机器可读 + 版本冻结）。"""
    out = pre_registration_path(pkg_root)
    out.write_text(json.dumps(PRE_REGISTRATION, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    return out


def load_pre_registration(path: Optional[Path | str] = None) -> dict:
    """读取预注册记录（与常量一致性校验）。"""
    p = Path(path) if path else pre_registration_path()
    data = json.loads(p.read_text(encoding="utf-8"))
    if data.get("record_id") != RECORD_ID:
        raise ValueError(f"预注册记录版本不匹配: {data.get('record_id')} != {RECORD_ID}")
    return data


# ── 公开/隐藏集划分（E1：预注册方法，确定性执行）──────────────────────────────


def assign_split(
    tasks: list[dict],
    seed: Optional[int] = None,
    public_ratio: Optional[float] = None,
) -> dict[str, str]:
    """确定性分层划分：{trajectory_id: 'public'|'hidden'}。

    分层键 = (act, difficulty.label)；每层内按 seed 打散后取前
    public_ratio 比例为 public；n≥2 的层保证至少 1 条进 hidden（隐藏集
    不可为空）；单任务层归 public。全部分层后若 hidden 仍为空（病态输入），
    确定性地把最后一条（按 id 排序）转 hidden。
    同一 (tasks, seed, public_ratio) 输入 → 同一输出（可复现）。
    """
    import numpy as np

    rng = np.random.default_rng(seed if seed is not None else PRE_REGISTRATION["split"]["seed"])
    ratio = public_ratio if public_ratio is not None else PRE_REGISTRATION["split"]["public_ratio"]

    by_stratum: dict[tuple[str, int], list[str]] = {}
    for t in tasks:
        key = (t["act"], int(t["difficulty"]["label"]))
        by_stratum.setdefault(key, []).append(t["trajectory_id"])

    assignment: dict[str, str] = {}
    for key, ids in sorted(by_stratum.items()):
        ids = sorted(ids)
        perm = rng.permutation(len(ids))
        ordered = [ids[i] for i in perm]
        if len(ordered) == 1:
            n_public = 1  # 单任务层 → public（隐藏集由其它层保证非空）
        else:
            n_public = int(round(len(ordered) * ratio))
            n_public = min(max(n_public, 1), len(ordered) - 1)
        for i, tid in enumerate(ordered):
            assignment[tid] = "public" if i < n_public else "hidden"
    if assignment and "hidden" not in set(assignment.values()):
        # 病态兜底：全部单任务层 → 最后一条（id 序）转 hidden
        last = sorted(assignment)[-1]
        assignment[last] = "hidden"
    return assignment


# ── gap 检查（E1：负向告警）───────────────────────────────────────────────────


def check_gap(
    public_scores: list[float],
    hidden_scores: list[float],
    tolerance: Optional[list[float]] = None,
) -> dict:
    """预注册 gap 统计：Δ = mean(public) − mean(hidden)（分数已归一化 0..1）。

    返回：delta / in_tolerance / alarm（超出区间 → True，泄漏信号负向告警）。
    """
    tol = tolerance if tolerance is not None else PRE_REGISTRATION["gap"]["tolerance_interval"]
    if not public_scores or not hidden_scores:
        return {"delta": None, "in_tolerance": None, "alarm": False,
                "n_public": len(public_scores), "n_hidden": len(hidden_scores),
                "note": "某侧为空，gap 不可计算（不告警，记为数据缺口）"}
    import numpy as np

    delta = float(np.mean(public_scores) - np.mean(hidden_scores))
    lo, hi = tol
    in_tolerance = lo <= delta <= hi
    return {
        "statistic": PRE_REGISTRATION["gap"]["statistic"],
        "tolerance_interval": tol,
        "delta": round(delta, 4),
        "in_tolerance": in_tolerance,
        "alarm": not in_tolerance,
        "n_public": len(public_scores),
        "n_hidden": len(hidden_scores),
        "note": PRE_REGISTRATION["gap"]["report_note"],
    }


__all__ = [
    "PRE_REGISTRATION_VERSION",
    "RECORD_ID",
    "PRE_REGISTRATION",
    "pre_registration_path",
    "save_pre_registration",
    "load_pre_registration",
    "assign_split",
    "check_gap",
]
