"""demo 定制组件封装（N-a 骨架签名 · N-b 窗口完整实现）。

设计依据：demo-redesign-design v0.3 §3.1（组件职责澄清）/ §3.2（工坊页）。

职责边界（Standards/Spec 双轴审查结论，勿混淆）：
- ``Cascader`` 第一级 = 范式（DEG / Pan-Cancer / scRNA）——范式选择唯一入口；
  第二级 = 案例类型分组（Group Select 语义：经典轨迹 / 黄金对照 / 真实评测）
  ——只整理轨迹，不选范式（分组永不改变范式状态）；上级变更清空下级状态；
- ``trajectory_multiselect`` = 轨迹对比（≤3 条并排，决策行按 ontology 顺序
  对齐，缺失列显示"无此决策"）；
- ``split_button`` = 主操作（运行审计）+ 下拉（导出 JSON / 复制证据链 /
  查看规则匹配明细）。

契约：全部交互状态经 st.session_state 持久化（刷新不丢）；组件独占各自的
key 命名空间（key_prefix），恢复演示默认态由页面调用 reset 方法实现。
"""
from __future__ import annotations

from typing import Callable

import streamlit as st

#: 案例类型分组（供 Cascader 第二级 / GroupSelect 共用；组与范式的
#: 可用性约束见 :func:`groups_for_paradigm`）
GROUPS = ("经典轨迹", "黄金对照", "真实评测")

#: 范式选项（第一级；顺序即展示顺序）
PARADIGMS = ("deg", "pan", "scrna")
PARADIGM_LABELS = {"deg": "DEG", "pan": "Pan-Cancer", "scrna": "scRNA"}

#: 轨迹上限（对比并排；设计 §3.2 钉死 ≤3）
MAX_COMPARE = 3


def groups_for_paradigm(paradigm: str | None) -> tuple[str, ...]:
    """范式 → 可用案例类型组。

    黄金对照/真实评测仅 scRNA 范式（设计 §3.2：DEG/pan 下为空 →
    引导文案"黄金对照仅 scRNA 范式"，不出现空列表）。
    未选范式（None）时返回全组——由 UI 层在未选态展示引导，不产生空列表。
    """
    if paradigm in ("deg", "pan"):
        return ("经典轨迹",)
    return GROUPS


#: 案例（轨迹卡）统一形状：{id, label, sub, paradigm, group}
#: 由页面经 :meth:`Cascader.render` 的 resolver 提供（数据层不耦合组件）
Case = dict


class Cascader:
    """范式 → 案例类型 → 轨迹 三级联动（上级变更清空下级状态）。

    交互状态键（``{key_prefix}_paradigm/_group/_trajectory``）由本组件独占，
    st.session_state 持久化——刷新不丢级联状态。上级变更时显式清空下级键
    （st.selectbox 的 key 值若不在新选项中会静默回落，必须主动 reset）。
    未选过（首次渲染）时应用 ``defaults``（演示默认路径，见设计 §3.2）。
    """

    def __init__(self, key_prefix: str = "cascader", defaults: dict | None = None):
        self.key_prefix = key_prefix
        self.k_paradigm = f"{key_prefix}_paradigm"
        self.k_group = f"{key_prefix}_group"
        self.k_trajectory = f"{key_prefix}_trajectory"
        # 上级值的"派生基线"（值变化 → 清空下级）；与控件键分离，避免误清
        self.k_paradigm_base = f"{key_prefix}_paradigm_base"
        self.k_group_base = f"{key_prefix}_group_base"
        # 默认演示路径由调用方（页面）单一事实源传入（Standards #7 闭环：
        # 组件不内置第二份默认值，防漂移）
        if defaults is None:
            raise ValueError("Cascader.defaults 必填（演示默认路径由页面常量提供）")
        self.defaults = defaults

    # ── 状态管理 ──

    def _apply_defaults(self) -> None:
        """首次渲染（或 reset 后）把默认演示路径写入控件键。

        派生基线同步初始化：首次渲染不把已播种值误判为"上级变更"而清空
        下级（预置态如 黄金对照 + 指定轨迹 直接可用）。
        """
        for key, value in self.defaults.items():
            k = getattr(self, f"k_{key}")
            if k not in st.session_state:
                st.session_state[k] = value
        if self.k_paradigm_base not in st.session_state:
            st.session_state[self.k_paradigm_base] = (
                st.session_state.get(self.k_paradigm))
        if self.k_group_base not in st.session_state:
            st.session_state[self.k_group_base] = st.session_state.get(self.k_group)

    def reset_defaults(self) -> None:
        """恢复演示默认态：三个控件键直接写回默认值（页面随后 rerun）。"""
        st.session_state[self.k_paradigm] = self.defaults["paradigm"]
        st.session_state[self.k_group] = self.defaults["group"]
        st.session_state[self.k_trajectory] = self.defaults["trajectory"]

    # ── 渲染 ──

    def render(
        self,
        resolver: Callable[[str, str], list[Case]],
    ) -> tuple[str | None, str | None, str | None]:
        """渲染三级联动；返回 (paradigm, group, case_id)。

        Parameters
        ----------
        resolver : (paradigm, group) -> list[Case]
            按范式×组解析可选案例（由页面从 demo/data 构建；组件不碰数据层）。
        """
        self._apply_defaults()

        # ── 第一级：范式（变更 → 清空组与轨迹）──
        paradigm = st.selectbox(
            "① 分析范式",
            options=list(PARADIGMS),
            format_func=lambda p: PARADIGM_LABELS[p],
            key=self.k_paradigm,
            help="范式决定规则集（deg / pan / scrna）与可用案例类型。",
        )
        if paradigm != st.session_state.get(self.k_paradigm_base):
            for k in (self.k_group, self.k_trajectory, self.k_group_base):
                st.session_state.pop(k, None)
            st.session_state[self.k_paradigm_base] = paradigm

        # ── 第二级：案例类型（Group Select 语义：只整理轨迹，不选范式）──
        groups = groups_for_paradigm(paradigm)
        if st.session_state.get(self.k_group) not in groups:
            st.session_state.pop(self.k_group, None)
        group = st.selectbox(
            "② 案例类型",
            options=list(groups),
            key=self.k_group,
            help="黄金对照 / 真实评测仅 scRNA 范式提供。",
        )
        if group != st.session_state.get(self.k_group_base):
            st.session_state.pop(self.k_trajectory, None)
            st.session_state[self.k_group_base] = group

        # DEG/pan 下黄金对照/真实评测为空 → 引导文案（设计 §3.2：
        # "黄金对照仅 scRNA 范式"，不出现空列表）
        if paradigm in ("deg", "pan"):
            st.markdown(
                '<div class="ba-guide">黄金对照与真实评测仅 <b>scRNA</b> 范式'
                "提供——当前 DEG / Pan-Cancer 范式无对应资产，"
                "切换到 scRNA 后可查看。</div>",
                unsafe_allow_html=True,
            )

        # ── 第三级：轨迹 ──
        cases = resolver(paradigm, group)
        if not cases:
            # 该组无案例（DEG/pan 的黄金对照等在上方已有引导；此处通用兜底）
            st.markdown(
                '<div class="ba-guide">当前「%s」组下暂无案例。</div>'
                % st.session_state.get(self.k_group, group),
                unsafe_allow_html=True,
            )
            return paradigm, group, None

        if st.session_state.get(self.k_trajectory) not in {c["id"] for c in cases}:
            st.session_state.pop(self.k_trajectory, None)
        trajectory = st.selectbox(
            "③ 案例轨迹",
            options=[c["id"] for c in cases],
            format_func=lambda cid: next(
                (c["label"] for c in cases if c["id"] == cid), cid
            ),
            key=self.k_trajectory,
        )
        return paradigm, group, trajectory


def trajectory_multiselect(
    available: list[Case],
    key: str = "traj_compare",
) -> list[str]:
    """轨迹对比多选（≤3 条；空状态提示；选项 = 当前范式的经典轨迹）。

    上限由 Streamlit ``max_selections`` 钉死（≥1.24 支持，1.31 兼容）；
    选中列表存 ``session_state[key]``，刷新不丢。
    """
    if not available:
        st.markdown(
            '<div class="ba-guide">当前范式暂无经典轨迹可对比。</div>',
            unsafe_allow_html=True,
        )
        return []
    selected = st.multiselect(
        "轨迹对比（≤3 条并排）",
        options=[c["id"] for c in available],
        format_func=lambda cid: next(
            (c["label"] for c in available if c["id"] == cid), cid
        ),
        key=key,
        max_selections=MAX_COMPARE,
        help="最多 3 条轨迹并行审计，结果并排对比（决策行按本体顺序对齐）。",
    )
    if not selected:
        st.markdown(
            '<div class="ba-guide">尚未选择轨迹——在上方级联选一条经典轨迹，'
            "或直接从此处多选（≤3 条）。</div>",
            unsafe_allow_html=True,
        )
    return list(selected)


def split_button(
    primary_label: str,
    key: str = "split_run",
    on_run: Callable[[], None] | None = None,
    render_menu: Callable[[], None] | None = None,
    disabled: bool = False,
) -> str | None:
    """Split Button：主按钮（运行审计）+ 下拉菜单（导出/复制/明细）。

    返回触发动作："run"（主按钮）或菜单项写入的动作 id（``{key}_menu_action``）；
    未触发返回 None。菜单内容由 ``render_menu`` 在 popover 内渲染（页面注入
    数据与按钮）。菜单按钮通过写 ``st.session_state[f"{key}_menu_action"]``
    回传动作——popover 点击后自动关闭，页面在下一轮 rerun 消费该动作。
    """
    c_main, c_caret = st.columns([5, 1], gap="small")
    with c_main:
        clicked = st.button(
            primary_label,
            key=f"{key}_primary",
            type="primary",
            use_container_width=True,
            disabled=disabled,
        )
    with c_caret:
        with st.popover("▾", use_container_width=True, disabled=disabled):
            if render_menu is not None:
                render_menu()
    if clicked:
        if on_run is not None:
            on_run()
        return "run"
    return st.session_state.pop(f"{key}_menu_action", None)
