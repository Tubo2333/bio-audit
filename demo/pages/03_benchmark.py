"""评测与奖励页（N-a 空壳 · N-d 窗口填充）。

设计依据：demo-redesign-design v0.3 §3.4（四 tab 降载）。
N-d 填充内容（预置结构）：
  Tab 1 benchmark：60 任务摘要（recall 0.820 / precision 0.7455 / F1 0.7810 /
      IRR κ=0.8336 / gap +0.046，M 后 0.0449 注明——全部读 demo/data 提炼摘要）；
  Tab 2 平台对照：Smart-seq2 vs 10X 黄金对照决策集差异（10X 多双联体/UMI/批次）；
  Tab 3 reward：level→reward 映射 + spike-in 掉分演示（读校准产物）；
  Tab 4 真实评测档案：CellVoyager 两次运行 + 成本 + 黄金对照定位声明 + R0 锚定。
"""
from __future__ import annotations

import streamlit as st


def render() -> None:
    st.markdown('<h1 class="ba-page-title">评测与奖励</h1>', unsafe_allow_html=True)
    st.markdown(
        '<div class="ba-page-sub">凭什么信这套评分：60 任务 benchmark、'
        "双平台黄金对照、reward 校准与真实评测档案。</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="ba-placeholder">评测与奖励 · 建设中（N-d 窗口填充）<br>'
        "benchmark 摘要 → 平台对照 → reward 映射 → 真实评测档案</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    render()
