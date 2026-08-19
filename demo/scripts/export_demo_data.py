"""demo 数据提炼脚本（窗口 N · N-a2）：cellvoyager-outputs → demo/data/。

设计依据：demo-redesign-design v0.3 §5（数据组织）/§6（63.7 复现）+ 台账 §2.1
（数据源钉死表）+ execution-plan §六.十八 N-a 2。

纪律：
- 全部分数从源产物**读取提炼**，零硬编码；数字锚点断言仅作防漂移护栏
  （源值意外变化 → 脚本报错退出，不静默写坏数据）；
- 每个摘要带 provenance（source / source_sha256 / generated_at / exported_at）；
- **剥离 Windows 绝对路径**（输出文件全库扫描，含 `D:\\`/`C:\\` 即报错）；
- 输出只写 demo/data/；源读取仅 cellvoyager-outputs（--sources 可覆盖）与
  bio-audit-v2 仓库内资产（trajectories v2 / golden 基线 / scrna_r0.json）。

用法：
    python demo/scripts/export_demo_data.py
    python demo/scripts/export_demo_data.py --sources D:\\other\\cellvoyager-outputs

输出清单（demo/data/）：
    manifest.json                   指纹 + 来源登记（启动校验依据）
    golden_summary.json             黄金对照 ×5（80.0/69.0/66.7/80.0/63.7）
    eval_summary.json               真实评测 ×2（30.0×2，G/L-b）
    benchmark_summary.json          benchmark 摘要（recall/precision/F1/gap/IRR）
    r0_summary.json                 R0 锚定（ρ=0.9747）
    trajectories_index.json         20 条轨迹索引（含 golden 基线分数）
    verdicts_10X_B.jsonl            M1 声明重建输入（N-c）
    golden_agent_10X_B_executed.py  M3 解析输入（N-c）
    windowL_10X_B_expected.json     63.7 断言基准（N-c，provenance 保留 source）
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "demo" / "data"
#: 默认源根（仓库外，不入 git）；可用 --sources 覆盖（换机器复现）
DEFAULT_SOURCES = Path(r"D:\C-file\cellvoyager-outputs")

# 必需输出文件清单与 data_index.REQUIRED_FILES 共享（单一事实源防漂移）；
# manifest.json 自身单独追加（它登记所有文件指纹）
sys.path.insert(0, str(REPO_ROOT / "demo"))
from data_index import REQUIRED_FILES  # noqa: E402

OUT_FILES: tuple[str, ...] = REQUIRED_FILES + ("manifest.json",)

#: Windows 绝对路径模式（剥离目标：输出文件不得含这些）。
#: 反斜杠形态要求 ≥2 级路径（盘符 + 至少两个分隔符），避免把普通文本里的
#: ``d:\\n``（如 "failed:\\n" 转义）误判为盘符路径；另覆盖 UNC。
#: 注意：**不**支持正斜杠盘符形态（``C:/dir``）——它无法与 URL 的
#: ``https://``（``s://``）区分，实测源产物无此形态（N1a 报告 §9 留档）。
_WIN_PATH = re.compile(
    r"(?:[A-Za-z]:\\(?:[^\"'\n]*\\)+[^\"'\n]*"  # C:\dir\file（≥2 级）
    r"|\\\\[^\"'\n]+)"                            # \\server\share（UNC）
)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def provenance(source: str, source_sha256: str, generated_at: str | None,
               note: str = "") -> dict:
    """统一 provenance 块（source / source_sha256 / generated_at / exported_at）。"""
    p = {
        "source": source,
        "source_sha256": source_sha256,
        "generated_at": generated_at or "",
        "exported_at": _now(),
    }
    if note:
        p["note"] = note
    return p


def _strip_win_paths(text: str) -> str:
    return _WIN_PATH.sub("<absolute-path-stripped>", text)


def sanitize_obj(obj):
    """递归剥离 dict/list 中的 Windows 绝对路径字符串。"""
    if isinstance(obj, dict):
        return {k: sanitize_obj(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize_obj(v) for v in obj]
    if isinstance(obj, str):
        return _WIN_PATH.sub("<absolute-path-stripped>", obj)
    return obj


def _read_json(path: Path, *, bom: bool = False) -> dict:
    enc = "utf-8-sig" if bom else "utf-8"
    return json.loads(path.read_text(encoding=enc))


# ═══════════════════════════════════════════════════════════════
# 黄金对照摘要（windowI A/B/C + windowL 10X A/B_expected）
# ═══════════════════════════════════════════════════════════════
def extract_golden(src: Path) -> dict:
    reports = {
        "windowI_A": src / "windowI" / "reports" / "windowI_A.json",
        "windowI_B": src / "windowI" / "reports" / "windowI_B.json",
        "windowI_C": src / "windowI" / "reports" / "windowI_C.json",
        "windowL_10X_A": src / "windowL" / "reports" / "windowL_10X_A.json",
        "windowL_10X_B_expected": src / "windowL" / "reports" / "windowL_10X_B_expected.json",
    }
    entries: list[dict] = []
    for key, path in reports.items():
        if not path.exists():
            raise FileNotFoundError(f"缺少黄金对照源文件: {path}")
        raw = _read_json(path)
        audit = raw["audit"]
        source_sha = _sha256_file(path)
        common = {
            "id": key,
            "paradigm": "scrna",
            "window": "I" if key.startswith("windowI") else "L",
            "platform": "smartseq2" if key.startswith("windowI") else "10X_scRNA_seq",
            "trajectory_score": audit["trajectory_score"],
            "eval_verdict": audit["eval_verdict"],
            "n_decisions": len(audit.get("per_decision", [])),
            "dimension_scores": audit.get("dimension_scores", {}),
            "critical_issues": audit.get("critical_issues", []),
            "provenance": provenance(path.name, source_sha,
                                     raw.get("generated_at")),
        }
        if key == "windowI_A":
            common["note"] = "黄金对照 A（Smart-seq2，I 窗口）· 10 决策"
        elif key == "windowI_B":
            # 原始 63.0 blocked（I1 报告实测）→ J 窗口后重评 69.0 needs_correction
            # （J1-rule-quality-report.md；K1 复核不变 80.0/69.0/66.7）
            j1 = (REPO_ROOT / "docs" / "migration" / "J1-rule-quality-report.md")
            m = re.search(r"\*\*69\.0 · needs_correction", j1.read_text(encoding="utf-8"))
            if not m:
                raise AssertionError("J1 报告未找到 69.0 · needs_correction 锚点")
            common["trajectory_score"] = 69.0
            common["eval_verdict"] = "needs_correction"
            common["score_original"] = audit["trajectory_score"]  # 63.0
            common["verdict_original"] = audit["eval_verdict"]  # blocked
            common["provenance"]["note"] = (
                "原始 63.0·blocked 实测于 windowI_B.json（I1 报告 §5.3）；"
                "69.0·needs_correction 为 J 窗口重评（J1-rule-quality-report.md，"
                "K1 复核不变）"
            )
            common["note"] = ("黄金对照 B（Smart-seq2，I 窗口；J 后重评）"
                              "63.0 → 69.0 · needs_correction")
        elif key == "windowI_C":
            common["note"] = ("黄金对照 C（Smart-seq2，I 窗口）· 66.7 仅限 "
                              "Smart-seq2-C 口径（QC 硬阈值），禁止与 63.7 混写")
        elif key == "windowL_10X_A":
            common["note"] = "黄金对照 A（10X，L 窗口）· 11 决策含双联体检测"
        else:  # windowL_10X_B_expected
            common["note"] = ("黄金对照 B（10X，expected_types 后，L/M 窗口）· "
                              "63.7 仅限 10X-B expected 口径（静默跳过双联体被补入），"
                              "禁止与 66.7 混写")
            common["expected_types_n_added"] = raw.get("cross_validate", {}).get("n_added")
        entries.append(common)

    # ── 数字锚点断言（防漂移护栏，非数据源）────────────────
    by_id = {e["id"]: e for e in entries}
    assert by_id["windowI_A"]["trajectory_score"] == 80.0, "windowI_A 分数漂移"
    assert by_id["windowI_A"]["eval_verdict"] == "pass"
    assert by_id["windowI_B"]["score_original"] == 63.0, "windowI_B 原始分漂移"
    assert by_id["windowI_B"]["trajectory_score"] == 69.0, "windowI_B 重评分漂移"
    assert by_id["windowI_B"]["eval_verdict"] == "needs_correction"
    assert by_id["windowI_C"]["trajectory_score"] == 66.7, "windowI_C 分数漂移"
    assert by_id["windowI_C"]["eval_verdict"] == "needs_correction"
    assert by_id["windowL_10X_A"]["trajectory_score"] == 80.0, "10X_A 分数漂移"
    assert by_id["windowL_10X_A"]["n_decisions"] == 11, "10X_A 决策数漂移"
    assert by_id["windowL_10X_B_expected"]["trajectory_score"] == 63.7, "63.7 漂移"
    assert by_id["windowL_10X_B_expected"]["eval_verdict"] == "blocked"
    return {"entries": entries,
            "provenance": provenance("windowI_A/B/C + windowL_10X_A/B_expected.json",
                                     _sha256_file(reports["windowI_A"]),
                                     None,
                                     "五份黄金对照报告提炼；口径分列见各条目 note；"
                                     "source_sha256 为聚合块引用值，各条目含独立指纹")}


# ═══════════════════════════════════════════════════════════════
# 真实评测摘要（CellVoyager G / L-b）
# ═══════════════════════════════════════════════════════════════
def extract_eval(src: Path) -> dict:
    g_reeval = src / "reports" / "windowG_reeval.json"
    k1_reeval = src / "reports" / "windowK1_reeval.json"
    lb = src / "windowL" / "reports" / "windowLb_analysis.json"
    for p in (g_reeval, k1_reeval, lb):
        if not p.exists():
            raise FileNotFoundError(f"缺少真实评测源文件: {p}")

    g = _read_json(g_reeval)
    k1 = _read_json(k1_reeval)  # 顶层即结果（无 audit 键，结构异于 g/lb）
    lbr = _read_json(lb)

    g_audit = g["audit"]
    assert g_audit["trajectory_score"] == 30.0, "windowG_reeval 分数漂移"
    assert k1["trajectory_score"] == 30.0, "windowK1_reeval 分数漂移"
    assert k1["eval_verdict"] == "needs_correction", "K1 重评 verdict 漂移"
    assert k1["level_counts"].get("1") == 19, "K1 重评 L1 计数漂移"
    assert lbr["audit"]["trajectory_score"] == 30.0, "windowLb 分数漂移"
    # level 计数统一字符串键（JSON 键序列化一致性；K1 源为字符串键、lb 源为 int 键）
    lb_levels = {str(k): v for k, v in sorted(
        Counter(d.get("level") for d in lbr["audit"]["per_decision"]).items())}

    return {
        "runs": [
            {
                "id": "cellvoyager_g",
                "label": "CellVoyager 真实评测（G 窗口，K 后重评）",
                "trajectory_score": 30.0,
                "eval_verdict": "needs_correction",
                "n_decisions": len(k1["per_decision"]),
                "level_counts": k1["level_counts"],
                "note": ("30.0 · needs_correction（L1×19/L3×1）——K1 后重评口径"
                         "（agent-eval-report-g2 §8 / windowK1_reeval.json，ruleset "
                         "1.5.0）；G-2 重评版本同分 30.0 但 L1×7/L3×1/L-1×12"
                         "（windowG_reeval.json，ruleset 1.2.0）"),
                "provenance": provenance(
                    "windowG_reeval.json + windowK1_reeval.json",
                    _sha256_file(k1_reeval),
                    k1.get("generated_at"),
                    "分数两版同 30.0；level 分布以 K1 后重评为准（台账 §2.1）",
                ),
            },
            {
                "id": "cellvoyager_lb",
                "label": "CellVoyager 短评测（L 窗口）",
                "trajectory_score": 30.0,
                "eval_verdict": "needs_correction",
                "n_decisions": len(lbr["audit"]["per_decision"]),
                "level_counts": lb_levels,
                "note": "30.0 · needs_correction（L1×4/L2×1，5 决策）",
                "provenance": provenance("windowLb_analysis.json",
                                         _sha256_file(lb),
                                         lbr.get("generated_at")),
            },
        ],
        "provenance": provenance("windowG_reeval + windowK1_reeval + windowLb_analysis",
                                 _sha256_file(lb), None,
                                 "真实评测两轮 30.0 均 needs_correction；29/30 双口径"
                                 "页内注释见 N-b（demo-redesign-design §3.2）"),
    }


# ═══════════════════════════════════════════════════════════════
# benchmark 摘要（60 任务 aggregate + gap + IRR）
# ═══════════════════════════════════════════════════════════════
def extract_benchmark(src: Path) -> dict:
    base = src / "reports" / "benchmark_run_baseline.json"
    if not base.exists():
        raise FileNotFoundError(f"缺少 benchmark 源文件: {base}")
    raw = _read_json(base, bom=True)  # 源文件带 UTF-8 BOM

    f1 = (REPO_ROOT / "docs" / "migration" / "F1-phase3-benchmark-batch2-report.md")
    m1 = (REPO_ROOT / "docs" / "migration" / "M1-capture-integrity-report.md")
    f1_text = f1.read_text(encoding="utf-8")
    m1_text = m1.read_text(encoding="utf-8")

    irr = re.search(r"全量 60 合并 IRR κ=([\d.]+)\s*/\s*α=([\d.]+)", f1_text)
    if not irr:
        raise AssertionError("F1 报告未找到 IRR κ 锚点")
    kappa = float(irr.group(1))
    assert abs(kappa - 0.8336) < 1e-9, f"IRR κ 锚点漂移: {kappa}"
    # 决策数/一致率同样从 F1 报告解析（防硬编码无锚点漂移）；跨行匹配
    # "全量 60 合并 IRR κ=…**（623 决策，\n一致率 93.58%）"
    m60 = re.search(r"全量 60 合并[^\n]*?（(\d+) 决策，\s*一致率 ([\d.]+)%",
                    f1_text, re.DOTALL)
    if not m60:
        raise AssertionError("F1 报告未找到 623 决策/一致率锚点")
    n_decisions = int(m60.group(1))
    agreement = float(m60.group(2)) / 100.0
    assert n_decisions == 623, f"F1 决策数锚点漂移: {n_decisions}"
    assert abs(agreement - 0.9358) < 1e-9, f"F1 一致率锚点漂移: {agreement}"

    gap_after = re.search(r"\*\*\+0\.0449\*\*", m1_text)
    if not gap_after:
        raise AssertionError("M1 报告未找到 gap +0.0449 锚点")

    agg = raw["aggregate"]["overall"]
    det = agg["detection"]
    assert det["recall"] == 0.82, "recall 漂移"
    assert abs(det["precision"] - 0.7454545454545455) < 1e-9, "precision 漂移"
    assert abs(det["f1"] - 0.780952380952381) < 1e-9, "f1 漂移"
    gap = raw["gap"]
    assert gap["delta"] == 0.046, "gap delta 漂移"

    return {
        "taskset_version": raw["taskset_version"],
        "n_tasks_run": raw["n_tasks_run"],
        "n_decisions": agg["n_decisions"],
        "n_gold_error": agg["n_gold_error"],
        "n_gold_correct": agg["n_gold_correct"],
        "detection": {
            "recall": det["recall"],
            "precision": det["precision"],
            "f1": det["f1"],
            "edge_detection_rate": agg["edge_handling"]["edge_detection_rate"],
            "mean_score": agg["mean_score"]["point"],
        },
        "strata": raw["aggregate"]["strata"],
        "comparisons": raw["aggregate"]["comparisons"],
        "gap": {
            "delta": gap["delta"],
            "tolerance_interval": gap["tolerance_interval"],
            "in_tolerance": gap["in_tolerance"],
            "delta_after_m": 0.0449,
            "note": "delta 读自 benchmark_run_baseline.json（G 基线产物）；"
                    "delta_after_m = M 窗口复跑（M1-capture-integrity-report.md），"
                    "预注册口径 ±0.10 区间内无告警",
        },
        "irr": {
            "kappa": kappa,
            "alpha": float(irr.group(2)),
            "n_decisions": n_decisions,
            "agreement": agreement,
            "note": "全量 60 合并 IRR（F1-phase3-benchmark-batch2-report.md "
                    "§F2，623 决策，一致率 93.58%）",
        },
        "provenance": provenance("benchmark_run_baseline.json",
                                 _sha256_file(base),
                                 raw.get("generated_at"),
                                 "IRR κ 出处 F1 报告（基准产物无此字段，从报告提炼）"),
    }


# ═══════════════════════════════════════════════════════════════
# R0 锚定摘要
# ═══════════════════════════════════════════════════════════════
def extract_r0() -> dict:
    r0_path = REPO_ROOT / "src" / "bioaudit" / "data" / "validation" / "scrna_r0.json"
    raw = _read_json(r0_path)
    r0 = raw["R0_scRNA"]
    assert "0.9747" in r0["key_metric"], "R0 ρ 锚点漂移"
    return {
        "key_metric": r0["key_metric"],
        "status": r0["status"],
        "detail": r0["detail"],
        "limit": r0["limit"],
        "provenance": provenance("scrna_r0.json",
                                 _sha256_file(r0_path),
                                 None,
                                 "K/M 后版本（台账 §2.1）"),
    }


# ═══════════════════════════════════════════════════════════════
# 轨迹索引（v2 目录 + golden 基线提炼）
# ═══════════════════════════════════════════════════════════════
def extract_trajectories() -> dict:
    golden = REPO_ROOT / "tests" / "golden" / "golden_expected_output_after.json"
    v2_dir = REPO_ROOT / "src" / "bioaudit" / "data" / "trajectories" / "v2"
    if not golden.exists():
        raise FileNotFoundError(f"缺少 golden 基线: {golden}")

    raw = _read_json(golden)
    # 兼容两种容器：dict{n_trajectories,trajectories:[...]} / 裸 list
    rows = raw["trajectories"] if isinstance(raw, dict) else raw
    assert len(rows) == 20, f"golden 基线应为 20 条轨迹，实得 {len(rows)}"

    index = []
    for row in rows:
        traj_id = row["trajectory"]
        f = v2_dir / f"{traj_id}.json"
        if not f.exists():
            raise FileNotFoundError(f"golden 基线引用的轨迹缺失: {f.name}")
        index.append({
            "trajectory_id": traj_id,
            "act": row["act"],
            "n_decisions": row["n_decisions"],
            "golden_score": row["trajectory_score"],
            "golden_verdict": row["verdict"],
            "source_file": f.name,
        })

    # 数字锚点（设计 §1.3 / 台账 §2.1：85.0×6 / 60.0·pass / 29.0）
    n_85 = sum(1 for r in index if r["golden_score"] == 85.0)
    assert n_85 == 6, f"85.0 轨迹数漂移: {n_85}"
    single = next(r for r in index if r["trajectory_id"] == "scrna_edge_singleanno")
    assert single["golden_score"] == 60.0 and single["golden_verdict"] == "pass", \
        "scrna_edge_singleanno 锚点漂移"
    cv = next(r for r in index if r["trajectory_id"] == "scrna_melanoma_cellvoyager")
    assert cv["golden_score"] == 29.0 and cv["golden_verdict"] == "blocked", \
        "scrna_melanoma_cellvoyager 锚点漂移"

    return {
        "n_trajectories": len(index),
        "trajectories": sorted(index, key=lambda r: r["trajectory_id"]),
        "provenance": provenance(
            "golden_expected_output_after.json + trajectories/v2",
            _sha256_file(golden),
            None,
            "分数/verdict 来自 golden 基线（当前引擎实测，golden 0 差异）；"
            "轨迹本体运行时读 bioaudit 包内 v2 目录",
        ),
    }


# ═══════════════════════════════════════════════════════════════
# N-c 输入副本（verdicts jsonl / executed.py / 63.7 断言基准）
# ═══════════════════════════════════════════════════════════════
def extract_capture_inputs(src: Path) -> dict:
    verdicts_src = src / "data" / "verdicts" / "golden_winL_10X_B_20260816.jsonl"
    executed_src = src / "windowL" / "runs" / "10X_B" / "golden_agent_10X_B_executed.py"
    expected_src = src / "windowL" / "reports" / "windowL_10X_B_expected.json"
    for p in (verdicts_src, executed_src, expected_src):
        if not p.exists():
            raise FileNotFoundError(f"缺少 N-c 输入源文件: {p}")

    # 1) verdicts 提炼副本（M1 声明重建输入；保留每行原样，剥离绝对路径）
    verdicts_out = OUT_DIR / "verdicts_10X_B.jsonl"
    n_verdicts = 0
    with verdicts_out.open("w", encoding="utf-8", newline="\n") as fw:
        for line in verdicts_src.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            fw.write(json.dumps(sanitize_obj(rec), ensure_ascii=False) + "\n")
            n_verdicts += 1

    # 2) executed.py 提炼副本（M3 解析输入；sanitize 两处 Windows 路径）
    #    仅作 M3Parser.parse_code 的**解析专用副本**，不执行；路径以占位符
    #    剥离（防泄漏优先于可执行性，N-c 解析不受影响——签名匹配只看调用形态）
    executed_out = OUT_DIR / "golden_agent_10X_B_executed.py"
    executed_text = _strip_win_paths(executed_src.read_text(encoding="utf-8"))
    if _WIN_PATH.search(executed_text):
        raise AssertionError("executed.py 提炼后仍含 Windows 绝对路径")
    executed_out.write_text(executed_text, encoding="utf-8", newline="\n")

    # 3) 63.7 断言基准提炼副本（provenance 保留 source=windowL_10X_B_expected.json）
    expected_raw = _read_json(expected_src)
    # expected_types.config 是**包内资产**路径（src/bioaudit/data/expected_types.yaml）：
    # 替换为包内相对引用（保留引用身份，不落盘符、不抹成占位符）
    expected_types_block = expected_raw.get("expected_types")
    if isinstance(expected_types_block, dict) and "config" in expected_types_block:
        expected_types_block = dict(expected_types_block)
        expected_types_block["config"] = "src/bioaudit/data/expected_types.yaml"
    slim = {
        "ok": expected_raw["ok"],
        "variant": expected_raw["variant"],
        "session_id": expected_raw["session_id"],
        "generated_at": expected_raw.get("generated_at"),
        "expected_types": expected_types_block,
        "cross_validate": {
            "stats": expected_raw["cross_validate"]["stats"],
            "n_added": expected_raw["cross_validate"]["n_added"],
        },
        "final_trajectory": {
            "n_decisions": expected_raw["final_trajectory"]["n_decisions"],
            "decision_types": expected_raw["final_trajectory"].get("decision_types"),
        },
        "audit": expected_raw["audit"],
        "provenance": provenance(
            "windowL_10X_B_expected.json",
            _sha256_file(expected_src),
            expected_raw.get("generated_at"),
            "63.7 断言基准提炼副本（demo-redesign-design §6；N-c 断言读本副本）",
        ),
    }
    slim = sanitize_obj(slim)
    assert slim["audit"]["trajectory_score"] == 63.7, "63.7 断言基准分数漂移"
    expected_out = OUT_DIR / "windowL_10X_B_expected.json"
    expected_out.write_text(
        json.dumps(slim, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n")

    return {
        "verdicts_10X_B.jsonl": {"n_verdicts": n_verdicts,
                                 "source": verdicts_src.name,
                                 "source_sha256": _sha256_file(verdicts_src)},
        "golden_agent_10X_B_executed.py": {
            "source": executed_src.name,
            "source_sha256": _sha256_file(executed_src),
            "note": "解析专用副本（M3Parser 输入，不执行）；Windows 路径以占位符剥离",
        },
        "windowL_10X_B_expected.json": {"source": expected_src.name,
                                        "source_sha256": _sha256_file(expected_src)},
    }


def _write_json(name: str, data: dict) -> None:
    # newline="\n"：输出一律 LF（.gitattributes 强制仓库内 LF；教训 #3——
    # manifest 指纹按 LF 规范化，Windows 工作区与 Linux CI 字节一致）
    (OUT_DIR / name).write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n")


def _final_scan() -> None:
    """全输出文件扫描：不得含 Windows 绝对路径（`D:\\`/`C:\\`）。"""
    offenders = []
    for f in OUT_DIR.iterdir():
        if not f.is_file():
            continue
        if _WIN_PATH.search(f.read_text(encoding="utf-8", errors="replace")):
            offenders.append(f.name)
    if offenders:
        raise AssertionError(f"输出仍含 Windows 绝对路径: {offenders}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, default=DEFAULT_SOURCES,
                        help="cellvoyager-outputs 根目录（默认本机路径）")
    args = parser.parse_args()
    src: Path = args.sources
    if not src.exists():
        print(f"[export] 源根不存在: {src}", file=sys.stderr)
        return 2

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    golden = extract_golden(src)
    eval_ = extract_eval(src)
    benchmark = extract_benchmark(src)
    r0 = extract_r0()
    traj = extract_trajectories()
    capture = extract_capture_inputs(src)

    _write_json("golden_summary.json", golden)
    _write_json("eval_summary.json", eval_)
    _write_json("benchmark_summary.json", benchmark)
    _write_json("r0_summary.json", r0)
    _write_json("trajectories_index.json", traj)

    manifest = {
        "generated_at": _now(),
        "exported_by": "demo/scripts/export_demo_data.py",
        "sources_note": "源为 cellvoyager-outputs（仓库外，--sources 传入；"
                        "文件指纹登记于各条目 source_sha256）",
        "files": {},
    }
    for name in OUT_FILES:
        if name == "manifest.json":
            continue
        path = OUT_DIR / name
        manifest["files"][name] = {"sha256": _sha256_file(path)}
    # N-c 输入副本的来源指纹（manifest 一并登记；键 = 文件名，与 files 对齐）
    for name, meta in capture.items():
        if name in manifest["files"]:
            manifest["files"][name].update(meta)
    _write_json("manifest.json", manifest)

    _final_scan()

    print(f"[export] 完成 → {OUT_DIR}")
    print("  黄金对照: " + " / ".join(
        f"{e['id']}={e['trajectory_score']}" for e in golden["entries"]))
    print("  真实评测: " + " / ".join(
        f"{r['id']}={r['trajectory_score']}" for r in eval_["runs"]))
    print(f"  benchmark: recall {benchmark['detection']['recall']} / "
          f"precision {benchmark['detection']['precision']:.4f} / "
          f"F1 {benchmark['detection']['f1']:.4f} / "
          f"gap {benchmark['gap']['delta']} / κ={benchmark['irr']['kappa']}")
    print(f"  R0: {r0['key_metric']}")
    print(f"  轨迹索引: {traj['n_trajectories']} 条 / "
          f"verdicts {capture['verdicts_10X_B.jsonl']['n_verdicts']} 行")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
