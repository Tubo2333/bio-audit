"""demo 定制组件封装（N-a 骨架层 · N-b 窗口实现）。

设计依据：demo-redesign-design v0.3 §3.1（组件职责澄清）/ §3.2（工坊页）。

职责边界（Standards/Spec 双轴审查结论，勿混淆）：
- ``Cascader`` 第一级 = 范式（DEG / Pan-Cancer / scRNA）——范式选择唯一入口；
- ``GroupSelect`` = 案例类型分组（经典轨迹 / 黄金对照 / 真实评测）——只整理
  轨迹，不选范式；两者职责不重叠；
- ``TrajectoryMultiSelect`` = 轨迹对比（≤3 条并排，决策行按 ontology 顺序
  对齐，缺失列显示"无此决策"）；
- ``SplitButton`` = 主操作（运行审计）+ 下拉（导出 JSON / 复制证据链 /
  查看规则匹配明细）。

N-a 交付签名与文档，N-b 交付完整交互；在 N-b 完成前调用将显式报错
（不允许静默占位行为混入后续页面）。
"""
from __future__ import annotations

#: 案例类型分组（供 Cascader 第二级 / GroupSelect 共用；组与范式的
#: 可用性约束见 :func:`groups_for_paradigm`）
GROUPS = ("经典轨迹", "黄金对照", "真实评测")

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


class Cascader:
    """范式 → 案例类型 → 轨迹 三级联动（N-b 实现）。

    契约：上级变更清空下级状态（st.session_state 持久化键由本组件独占）。
    """

    def __init__(self, key_prefix: str = "cascader"):
        self.key_prefix = key_prefix

    def render(self) -> tuple[str | None, str | None, str | None]:
        """渲染三级选择；返回 (paradigm, group, trajectory_id)，N-b 实现。"""
        raise NotImplementedError("Cascader 由 N-b 窗口实现（demo-redesign-design §3.2）")


def trajectory_multiselect(
    available: list[dict],
    key: str = "traj_compare",
) -> list[str]:
    """轨迹多选对比（≤3 条，空状态提示；N-b 实现）。"""
    raise NotImplementedError(
        "trajectory_multiselect 由 N-b 窗口实现（demo-redesign-design §3.2）"
    )


def split_button(
    primary_label: str,
    key: str = "split_run",
    on_run=None,
) -> str | None:
    """Split Button：主操作 + 下拉导出/复制/明细（N-b 实现）。"""
    raise NotImplementedError("split_button 由 N-b 窗口实现（demo-redesign-design §3.2）")
