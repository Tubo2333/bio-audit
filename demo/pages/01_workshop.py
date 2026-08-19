"""审计工坊页（N-a 空壳 → N-b 完整实现）。

设计依据：demo-redesign-design v0.3 §3.2（核心页）——本页 = 现象层
（expected_types 补入 → L0 → blocked 的演示；机制层交互归 N-c 采集页）。

页面结构：
1. 选择与运行：Cascader 三级联动（范式 → 案例类型 → 轨迹）+ 轨迹对比
   multi-select（≤3 条并排）+ Split Button（运行审计 / 导出 / 复制 / 明细）；
2. 经典轨迹结果区：并排对比表 + 单条结果全元素（大卡 / verdict 色点 /
   快照徽章 / 维度条 / 决策状态点 / 证据卡 / 时间轴）；
3. 黄金对照 / 真实评测卡：产物读取（demo/data 摘要 + provenance + 快照徽章
   + 口径注）——黄金 B（10X）附 63.7 现象链路演示（真实重算）；
4. 演示恢复：session_state 持久化 + 「恢复演示默认态」按钮（2 次点击）。

缓存纪律（设计 §5）：st.cache_resource 预热 RuleRegistry；
(trajectory_id, act) 缓存 run_audit 结果；63.7 链路整体缓存。
外围层纪律：只调 bioaudit.api + capture 公共类 + demo/data，零评分路径改动。
"""
from __future__ import annotations

import html
import json
import re
from datetime import datetime, timezone

import capture_chain  # demo/ 同目录模块；N-c 起共享 63.7 链路（现象/机制单一事实源）
import components
import data_index
import result_view
import streamlit as st

from bioaudit.api.audit import match_details, run_audit
from bioaudit.ontology.loader import get_ontology
from bioaudit.report import current_snapshot

# ── 演示默认态（设计 §3.2 推荐路径：scrna_correct + scrna_error 并排）──
DEFAULT_PARADIGM = "scrna"
DEFAULT_GROUP = "经典轨迹"
DEFAULT_TRAJECTORY = "scrna_correct"
DEFAULT_COMPARE = ["scrna_correct", "scrna_error"]
COMPARE_KEY = "traj_compare"

#: 黄金 B（10X expected）案例 id（demo/data 键名钉死，N1a §4）
GOLDEN_B_EXPECTED_ID = "windowL_10X_B_expected"

#: K1 后重评口径的 ruleset 版本（从 eval_summary 数据 note 提取，单一事实源）
_RULESET_RE = re.compile(r"ruleset\s+([0-9]+\.[0-9]+\.[0-9]+)")


def _kaliber_note() -> str:
    """29/30 双口径注：29.0 实测口径 = 当前快照；30.0 = K1 后重评口径
    （版本号从 demo/data eval_summary note 提取——禁止照抄设计示例的
    1.5.0，台账 §5 教训 #2）。"""
    snap = current_snapshot()
    eval_note = ""
    for r in data_index.eval_summary()["runs"]:
        if r["id"] == "cellvoyager_g":
            eval_note = str(r.get("note", ""))
            break
    m = _RULESET_RE.search(eval_note)
    k1_version = m.group(1) if m else "？"
    return (
        "口径注：29.0 = D5 修复后实测（当前快照 ruleset "
        f"{snap.ruleset_version}）；评测页 30.0 = K1 后重评（ruleset "
        f"{k1_version} 口径）——同一 Agent 运行，两套口径不混写"
    )


# ── 缓存（设计 §5：规则库 cache_resource；(trajectory, act) 结果缓存）──

@st.cache_resource(show_spinner=False)
def _warm_registry(act: str) -> int:
    """预热规则文件（cache_resource，设计 §5 缓存纪律字面要求）。

    注意（Standards #2 闭环）：run_audit 内部自建 RuleRegistry（引擎边界，
    不注入外部实例），本预热使规则文件进入 OS 页缓存并满足验收
    "st.cache_resource 缓存 RuleRegistry"；真正的计算节流由
    :func:`_run_audit_cached` 的 (trajectory, act) 结果缓存承担。
    """
    from bioaudit.paths import rules_dir_for
    from bioaudit.storage.rule_registry import RuleRegistry

    registry = RuleRegistry(rules_dir_for(act))
    registry.load_all()
    return registry.rule_count


def _fill_error_state(state: dict) -> None:
    """run_audit error 态兜底键（页面渲染不裸解引用，Standards #4 闭环）。"""
    state.setdefault("trajectory_score", 0.0)
    state.setdefault("eval_verdict", "error")
    state.setdefault("dimension_scores", {})
    state.setdefault("step_scores", [])
    state.setdefault("critical_issues", [])


@st.cache_data(show_spinner=False)
def _run_audit_cached(trajectory_id: str, act: str) -> dict:
    """(trajectory, act) 缓存 run_audit——控件交互 rerun 不重算一切。

    返回 {"state", "generated_at", "had_error"}；轨迹本体读 bioaudit 包内 v2。
    error 态不在此处弹窗（缓存语义只弹一次），由页面渲染 error 卡。
    """
    _warm_registry(act)
    path = data_index.trajectories_dir() / f"{trajectory_id}.json"
    trajectory = json.loads(path.read_text(encoding="utf-8"))
    state = run_audit(trajectory, act=act)
    had_error = bool(state.get("error"))
    if had_error:
        _fill_error_state(state)
    return {
        "state": state,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "had_error": had_error,
    }


@st.cache_data(show_spinner=False)
def _golden_b_chain() -> dict:
    """63.7 现象链路（demo-redesign-design §6 完整复现，输入全为 demo/data 副本）。

    声明轨迹（M1，含 skip_doublet）→ M3 解析 executed.py → expected_types
    11 决策清单 → 交叉验证（补入 doublet_detection=expected）→ run_audit
    → 63.7 · blocked。断言基准 = demo/data/windowL_10X_B_expected.json。

    N-c 起：链路本体收敛到 ``capture_chain.run_chain``（采集页机制层共用
    单一事实源——两处数字必须一致）；本函数保留为现象层的缓存包装。
    """
    _warm_registry("scrna")
    return capture_chain.run_chain()


# ── 案例清单构建（Cascader resolver；数据全部来自 demo/data）──

def _classic_cases(paradigm: str) -> list[dict]:
    return [
        {
            "id": t["trajectory_id"],
            "label": f"{t['trajectory_id']} · {t['golden_score']:.1f} "
                     f"{t['golden_verdict']}",
            "sub": f"{t['n_decisions']} 决策",
            "paradigm": t["act"],
            "group": "经典轨迹",
        }
        for t in data_index.trajectories_index()["trajectories"]
        if t["act"] == paradigm
    ]


def _golden_cases(paradigm: str) -> list[dict]:
    return [
        {
            "id": e["id"],
            "label": f"{e['id']} · {e['trajectory_score']:.1f} "
                     f"{e['eval_verdict']}（{e['platform']}）",
            "sub": f"{e['n_decisions']} 决策",
            "paradigm": e["paradigm"],
            "group": "黄金对照",
        }
        for e in data_index.golden_summary()["entries"]
        if e["paradigm"] == paradigm
    ]


def _eval_cases(paradigm: str) -> list[dict]:
    return [
        {
            "id": r["id"],
            "label": f"{r['id']} · {r['trajectory_score']:.1f} "
                     f"{r['eval_verdict']}",
            "sub": f"{r['n_decisions']} 决策",
            "paradigm": "scrna",
            "group": "真实评测",
        }
        for r in data_index.eval_summary()["runs"]
        if paradigm == "scrna"
    ]


def _resolver(paradigm: str, group: str) -> list[dict]:
    if group == "经典轨迹":
        return _classic_cases(paradigm)
    if group == "黄金对照":
        return _golden_cases(paradigm)
    if group == "真实评测":
        return _eval_cases(paradigm)
    return []


# ── 结果区渲染 ─────────────────────────────────────────────

def _run_snapshot(state: dict) -> dict:
    """审计运行时刻的快照三元组（state.report.snapshot，Standards #9 闭环：
    快照徽章用 run 自带快照而非渲染时 current_snapshot）。"""
    report = state.get("report") or {}
    return report.get("snapshot") or current_snapshot().as_dict()


def _render_full_result(entry: dict) -> None:
    """单条轨迹完整结果页元素。"""
    tid = entry["trajectory_id"]
    state = entry["state"]
    if entry.get("had_error"):
        st.error(
            f"审计管道异常（{state.get('error_code')}）：{state.get('error')}"
        )
        return
    result_view.render_score_header(
        state, _run_snapshot(state), entry["generated_at"],
        source=f"实时 run_audit · {html.escape(tid)}",
    )
    if tid == "scrna_melanoma_cellvoyager":
        st.markdown(
            f'<div class="ba-callout ba-callout-note">{html.escape(_kaliber_note())}</div>',
            unsafe_allow_html=True,
        )
    result_view.render_decision_points(state, get_ontology())
    result_view.render_timeline(state, get_ontology())
    result_view.render_evidence_cards(state, get_ontology())


def _render_case_card(entry: dict) -> None:
    """黄金对照 / 真实评测卡（产物读取：demo/data 摘要 + provenance +
    快照徽章 + 口径注 + L 分布/问题行）。两卡共用实现（Standards #8 闭环）。"""
    snap = current_snapshot().as_dict()
    pseudo = {
        "trajectory_score": entry["trajectory_score"],
        "eval_verdict": entry["eval_verdict"],
        "dimension_scores": entry.get("dimension_scores", {}),
        "step_scores": [],
    }
    prov = entry.get("provenance", {})
    generated = prov.get("generated_at") or prov.get("exported_at") or "?"
    result_view.render_score_header(
        pseudo, snap, generated,
        source=f"产物读取 · {html.escape(str(prov.get('source', '?')))}",
        n_decisions=entry.get("n_decisions"),
    )
    counts = entry.get("level_counts") or {}
    if counts:
        dist = " · ".join(
            f"L{lv}×{n}"
            for lv, n in sorted(counts.items(), key=lambda kv: -int(kv[0]))
            if n
        )
        st.markdown(
            f'<div class="ba-mono ba-l-dist">L 分布：{html.escape(dist)}</div>',
            unsafe_allow_html=True,
        )
    for issue in entry.get("critical_issues") or []:
        st.markdown(
            f'<div class="ba-issue-line">⚠ {html.escape(str(issue))}</div>',
            unsafe_allow_html=True,
        )
    note = entry.get("note", "")
    if note:
        st.markdown(
            f'<div class="ba-callout ba-callout-note">{html.escape(str(note))}</div>',
            unsafe_allow_html=True,
        )
    if entry.get("score_original") is not None:
        st.caption(
            f"原始实测 {entry['score_original']:.1f} · "
            f"{entry.get('verdict_original')}（J 后重评口径并存，防第三套数字）"
        )


def _render_golden_b_phenomenon(entry: dict) -> None:
    """expected_types 现象演示（黄金 B 10X）：补入 → L0 → blocked 链路。"""
    if entry["id"] != GOLDEN_B_EXPECTED_ID:
        return
    st.markdown(
        '<div class="ba-section-title">expected_types 现象演示</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="ba-callout ba-callout-warn">黄金 B（10X）版静默跳过了'
        "双联体检测——预期决策点缺失，将被 expected_types 补入，"
        "演示「补入 → L0 → blocked」完整链路。</div>",
        unsafe_allow_html=True,
    )
    if st.button("演示补入链路（实时重算）", key="ws_goldenb_run",
                 type="primary"):
        st.session_state["ws_goldenb_show"] = True
    if not st.session_state.get("ws_goldenb_show"):
        return
    chain = _golden_b_chain()
    state = chain["state"]
    stats = chain["stats"]
    added = chain["added"]
    # 补入类型动态化（Standards #6 闭环）：不硬编码 doublet_detection，
    # 以实际补入为准；与预期不符时明确警示
    added_types = [a["decision_type"] for a in added]
    added_label = "、".join(added_types) if added_types else "（无）"
    type_ok = added_types == ["doublet_detection"]
    if not type_ok:
        st.error(
            f"补入决策类型异常（预期 doublet_detection，实际 {added_types}）"
        )
    st.markdown(
        '<div class="ba-chain">'
        f'<div class="ba-chain-step"><b>① 声明轨迹（M1）</b>'
        f'：{chain["n_m1"]} 条声明，含 doublet_detection = skip_doublet'
        "（无任何双联体工具调用）</div>"
        f'<div class="ba-chain-step"><b>② M3 解析</b>：executed.py → '
        f'{chain["m3_n_candidates"]} 候选，双联体零执行证据</div>'
        f'<div class="ba-chain-step"><b>③ 交叉验证</b>：consistent '
        f'{stats["consistent"]} / 虚报 {stats["false_positive"]}'
        "（skip_doublet 撤销）/ 漏报 "
        f'{stats["false_negative"]} / 未验证 {stats["unverified"]}</div>'
        '<div class="ba-chain-step ba-chain-step-highlight"><b>④ 预期决策点'
        f'缺失，已补入</b>：{html.escape(added_label)}（provenance = expected，'
        "该做没做，B7 未豁免）→ 参与评分</div>"
        f'<div class="ba-chain-step"><b>⑤ 补入后评分</b>：'
        f'D1.1 → {html.escape(added_label)} L0（危险）→ '
        f"<b>{state['trajectory_score']:.1f} · {state['eval_verdict']}</b>"
        f"（{chain['final_n']} 决策）</div>"
        "</div>",
        unsafe_allow_html=True,
    )
    # 断言基准核对（demo/data 副本）
    bench = chain["benchmark"]
    ok = (
        abs(state["trajectory_score"] - bench["trajectory_score"]) < 1e-9
        and state["eval_verdict"] == bench["eval_verdict"]
        and chain["final_n"] == bench["n_decisions"]
        and type_ok
    )
    st.markdown(
        f'<div class="ba-callout {"ba-callout-ok" if ok else "ba-callout-err"}">'
        f'与断言基准一致（windowL_10X_B_expected.json：{bench["trajectory_score"]:.1f}'
        f" · {bench['eval_verdict']} · {bench['n_decisions']} 决策）"
        f"{'✓' if ok else '✗ 不一致！'}</div>",
        unsafe_allow_html=True,
    )
    result_view.render_score_header(
        state, _run_snapshot(state), chain["generated_at"],
        source="63.7 复现（demo/data 副本）",
    )
    if chain.get("had_error"):
        st.error(f"链路审计异常：{state.get('error')}")
    result_view.render_decision_points(state, get_ontology())
    st.caption("机制层（勾选预期清单实时重算、declared 注入）在采集演示页（N-c）。")


# ── 菜单动作（导出 / 复制 / 明细）──────────────────────────

def _evidence_text(results: dict[str, dict]) -> str:
    lines: list[str] = []
    for tid, entry in results.items():
        lines.append(f"# {tid}（{entry['state']['trajectory_score']:.1f} · "
                     f"{entry['state']['eval_verdict']}）")
        for s in entry["state"].get("step_scores", []):
            lines.append(f"## {s['decision_type']} · {s['agent_choice']}")
            for cite in s.get("evidence_citations") or []:
                lines.append(f"- {cite}")
    return "\n".join(lines)


def _render_menu(results: dict[str, dict], key: str) -> None:
    """Split Button 下拉内容：导出 JSON / 复制证据链 / 匹配明细。"""
    if not results:
        st.caption("运行审计后可导出 / 复制 / 查看明细")
        return
    export = {
        tid: entry["state"] for tid, entry in results.items()
    }
    export_payload = {
        "exported_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "snapshot": current_snapshot().as_dict(),
        "results": export,
    }
    st.download_button(
        "导出 JSON 报告",
        data=json.dumps(export_payload, ensure_ascii=False, indent=2),
        file_name=f"bioaudit_workshop_{'_'.join(results)}.json",
        mime="application/json",
        key=f"{key}_export",
        use_container_width=True,
    )
    if st.button("复制证据链", key=f"{key}_copy", use_container_width=True):
        st.session_state[f"{key}_menu_action"] = "copy_evidence"
    if st.button("查看规则匹配明细", key=f"{key}_detail",
                 use_container_width=True):
        st.session_state[f"{key}_menu_action"] = "match_details"


def _render_match_details(results: dict[str, dict]) -> None:
    """规则匹配明细（bioaudit.api.match_details —— 外围 API，只读查询）。"""
    for tid, entry in results.items():
        # act 取 run_audit state 自带字段（Standards #10 闭环：不用 id 前缀启发式）
        act = entry["state"].get("act")
        st.markdown(f"**{html.escape(tid)}**")
        for s in entry["state"].get("parsed_steps", []):
            try:
                details = match_details(
                    s["decision_type"], s.get("normalized_context", {}), act=act
                )
            except Exception as exc:  # 外围查询失败不拖垮页面
                details = []
                st.caption(
                    f"{html.escape(str(s['decision_type']))}: "
                    f"明细查询失败（{html.escape(str(exc))}）"
                )
            if not details:
                continue
            with st.expander(
                f"{html.escape(str(s['decision_type']))} · "
                f"{html.escape(str(s.get('original', {}).get('choice', '')))}"
            ):
                for rd in details:
                    icon = "✓" if rd.get("matched") else "—"
                    st.markdown(
                        f"`{icon}` **{html.escape(str(rd.get('rule_id', '?')))}** "
                        f"{html.escape(str(rd.get('title', '')))}"
                    )
                    for check in rd.get("checks", [])[:6]:
                        st.caption(
                            f"　{'✓' if check.get('pass') else '✗'} "
                            f"`{html.escape(str(check.get('expr', '')))}` → "
                            f"`{html.escape(str(check.get('actual', '')))}`"
                        )


# ── 主渲染 ─────────────────────────────────────────────────

def render() -> None:
    st.markdown('<h1 class="ba-page-title">审计工坊</h1>', unsafe_allow_html=True)
    st.markdown(
        '<div class="ba-page-sub">选一条（或对比至多三条）真实轨迹，'
        "实时跑完整审计管道——分数由引擎现场计算，零硬编码。"
        "演示默认路径：scrna_correct + scrna_error 并排对比。</div>",
        unsafe_allow_html=True,
    )

    cascade = components.Cascader(
        defaults={
            "paradigm": DEFAULT_PARADIGM,
            "group": DEFAULT_GROUP,
            "trajectory": DEFAULT_TRAJECTORY,
        }
    )

    # ── 演示恢复（session_state 持久化；2 次点击回讲稿起点）──
    r1, r2 = st.columns([3, 1])
    with r2:
        if st.button("恢复演示默认态", key="ws_reset", use_container_width=True):
            if st.session_state.get("ws_reset_armed"):
                cascade.reset_defaults()
                st.session_state[COMPARE_KEY] = list(DEFAULT_COMPARE)
                st.session_state["ws_paradigm_for_compare"] = DEFAULT_PARADIGM
                st.session_state["ws_last_cascader"] = (
                    DEFAULT_PARADIGM, DEFAULT_TRAJECTORY)
                st.session_state.pop("ws_goldenb_show", None)
                st.session_state["ws_reset_armed"] = False
                # 回讲稿起点：默认两条并排结果就绪（缓存命中，秒级）
                with st.spinner("恢复演示默认态…"):
                    st.session_state["ws_results"] = {
                        tid: _run_audit_cached(tid, DEFAULT_PARADIGM)
                        for tid in DEFAULT_COMPARE
                    }
                st.rerun()
            else:
                st.session_state["ws_reset_armed"] = True
                st.toast("再次点击确认恢复演示默认态（回讲稿起点）")
    with r1:
        st.caption("演示状态存于浏览器会话（刷新不丢）；恢复按钮 2 次点击生效。")

    # ── ① 选择与运行 ──
    c_sel, c_cmp = st.columns([1.3, 1], gap="large")
    with c_sel:
        st.markdown('<div class="ba-section-title">① 选择案例</div>',
                    unsafe_allow_html=True)
        paradigm, group, traj_id = cascade.render(_resolver)
    with c_cmp:
        st.markdown('<div class="ba-section-title">② 对比与运行</div>',
                    unsafe_allow_html=True)
        available = _classic_cases(paradigm) if group == "经典轨迹" else []
        # 范式变更 → 清空对比区 + 抑制本轮自动加入（防止跨范式残留/误加）
        if st.session_state.get("ws_paradigm_for_compare") != paradigm:
            st.session_state.pop(COMPARE_KEY, None)
            st.session_state["ws_compare_just_cleared"] = True
            st.session_state["ws_paradigm_for_compare"] = paradigm
        just_cleared = st.session_state.pop("ws_compare_just_cleared", False)
        # 首次进入（或复位后）播种默认对比
        if "ws_compare_seeded" not in st.session_state:
            st.session_state[COMPARE_KEY] = list(DEFAULT_COMPARE)
            st.session_state["ws_compare_seeded"] = True
        # 级联所选经典轨迹自动加入对比（≤3；重复不添加；范式刚切换的
        # 当轮不自动加入——轨迹可能仍是上一范式的默认值）
        last = st.session_state.get("ws_last_cascader")
        if traj_id and last != (paradigm, traj_id) and not just_cleared:
            st.session_state["ws_last_cascader"] = (paradigm, traj_id)
            if group == "经典轨迹":
                picked = list(st.session_state.get(COMPARE_KEY, []))
                if traj_id not in picked and len(picked) < components.MAX_COMPARE:
                    st.session_state[COMPARE_KEY] = picked + [traj_id]
        selected = components.trajectory_multiselect(available)
        st.caption(
            "对比限同范式（跨范式混表对比分数违反口径分列纪律）；"
            "同范式内决策数不同的轨迹并排时，缺失列显示「无此决策」"
            "——错位即信息。"
        )

        runnable = group == "经典轨迹" and bool(selected)
        run_action = components.split_button(
            "运行审计",
            key="ws_split",
            disabled=not runnable,
            render_menu=lambda: _render_menu(
                st.session_state.get("ws_results", {}), "ws_split"
            ),
        )

    # ── ② 运行：写入 session_state（持久化；刷新不丢结果）──
    if run_action == "run" and runnable:
        with st.spinner("实时运行完整审计管道（7 步）…"):
            results = {
                tid: _run_audit_cached(tid, paradigm) for tid in selected
            }
        st.session_state["ws_results"] = results

    # ── ③ 结果区 ──
    if group == "经典轨迹":
        results: dict = st.session_state.get("ws_results", {})
        results = {tid: r for tid, r in results.items() if tid in selected}
        if not selected:
            st.markdown(
                '<div class="ba-guide">尚未选择轨迹——选一条经典轨迹后点击'
                "「运行审计」。</div>",
                unsafe_allow_html=True,
            )
        elif not results:
            st.markdown(
                '<div class="ba-guide">已选轨迹未运行——点击「运行审计」'
                "开始实时评分。</div>",
                unsafe_allow_html=True,
            )
        else:
            entries = [
                {"trajectory_id": tid, **results[tid]} for tid in selected
                if tid in results
            ]
            labels = {c["id"]: c["label"] for c in available}
            result_view.render_comparison(entries, get_ontology(), labels)
            for entry in entries:
                st.markdown("---")
                st.markdown(
                    f'<div class="ba-result-title ba-mono">'
                    f'{html.escape(entry["trajectory_id"])}</div>',
                    unsafe_allow_html=True,
                )
                _render_full_result(entry)
            # 菜单动作消费（复制证据链 / 匹配明细）
            if run_action == "copy_evidence":
                text = _evidence_text(results)
                # 浏览器策略：rerun 后执行 clipboard 无用户手势可能被拒，
                # try/catch 降级 + 手动复制兜底（F2 闭环）；
                # 字符串内 "</script>" 需转义防 HTML 注入（Standards #3 闭环）
                js_text = json.dumps(text).replace("</", "<\\/")
                st.components.v1.html(
                    "<script>"
                    "try{navigator.clipboard.writeText("
                    + js_text
                    + ").then(()=>{window.parent.postMessage('ba_copied','*')})"
                    ".catch(()=>{window.parent.postMessage('ba_copy_failed','*')});}"
                    "catch(e){window.parent.postMessage('ba_copy_failed','*');}"
                    "</script>",
                    height=0,
                )
                st.toast("证据链已复制到剪贴板（如浏览器拦截，见下方手动复制区）")
                with st.expander("证据链文本（手动复制兜底）", expanded=False):
                    st.code(text, language=None)
            if run_action == "match_details":
                with st.expander("规则匹配明细（技术观众）", expanded=True):
                    _render_match_details(results)
    else:
        # 黄金对照 / 真实评测：产物读取卡（demo/data 摘要 + provenance）
        st.markdown('<div class="ba-section-title">案例档案（产物读取）</div>',
                    unsafe_allow_html=True)
        if group == "黄金对照":
            entry = next(
                (e for e in data_index.golden_summary()["entries"]
                 if e["id"] == traj_id), None
            )
            if entry:
                _render_case_card(entry)
                _render_golden_b_phenomenon(entry)
        elif group == "真实评测":
            entry = next(
                (r for r in data_index.eval_summary()["runs"] if r["id"] == traj_id),
                None,
            )
            if entry:
                _render_case_card(entry)


if __name__ == "__main__":
    render()
