"""审计工坊页（N-a 空壳 · N-b 窗口填充）。

设计依据：demo-redesign-design v0.3 §3.2（核心页）。
N-b 填充内容（预置结构）：
  1. Cascader 三级联动：范式（DEG/Pan-Cancer/scRNA）→ 案例类型（经典轨迹/
     黄金对照/真实评测）→ 轨迹；上级变更清空下级；DEG/pan 下黄金对照为空
     → 引导文案"黄金对照仅 scRNA 范式"（components.Cascader）。
  2. Multi-select 轨迹对比（≤3 条并排；决策行按 ontology 顺序对齐、
     缺失列显示"无此决策"，错位即信息）。
  3. Split Button：运行审计（实时 run_audit）+ 导出 JSON / 复制证据链 /
     查看规则匹配明细。
  4. 结果页全元素：总分大卡 + verdict 色点 + 快照徽章 + 维度进度条 +
     决策状态点（level 五档徽章配色 L3 绿/L2 青/L1 黄/L0 红/L-1 灰）+
     证据卡（PMID）+ 时间轴（decisions + ontology stages 推导）。
  5. expected_types 现象演示（黄金 B：跳过双联体 → 补入 → 63.7 blocked）。
  6. 演示恢复：session_state 持久化 + "恢复演示默认态"按钮。
"""
from __future__ import annotations

import streamlit as st


def render() -> None:
    st.markdown('<h1 class="ba-page-title">审计工坊</h1>', unsafe_allow_html=True)
    st.markdown(
        '<div class="ba-page-sub">选一条（或对比至多三条）真实轨迹，'
        "实时跑完整审计管道——分数由引擎现场计算，零硬编码。</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="ba-placeholder">审计工坊 · 建设中（N-b 窗口填充）<br>'
        "范式级联选择 → 轨迹对比 → 运行审计 → 结果全元素</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    render()
