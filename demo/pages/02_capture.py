"""采集演示页（N-a 空壳 · N-c 窗口填充）。

设计依据：demo-redesign-design v0.3 §3.3（机制层）+ §6（63.7 复现技术说明）。
N-c 填充内容（预置结构）：
  1. 四类判定可视化：声明 vs 事实对齐表（一致/虚报/漏报/未验证四色）
     + verdict 状态位流转时间线（provisional → final/revoked）。
  2. expected_types 机制交互：勾选预期决策点清单 → 实时重算 → 63.7 blocked
     完整复现（输入全部来自 demo/data 提炼副本：verdicts_10X_B.jsonl +
     golden_agent_10X_B_executed.py + windowL_10X_B_expected.json 断言基准）。
  3. declared 注入：降级为高级折叠区（expandable + 工具提示）。
"""
from __future__ import annotations

import streamlit as st


def render() -> None:
    st.markdown('<h1 class="ba-page-title">采集演示</h1>', unsafe_allow_html=True)
    st.markdown(
        '<div class="ba-page-sub">机制层演示：采集交叉验证如何抓出'
        "「声明了但没做 / 做了但没声明」——63.7 blocked 的完整复现。</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="ba-placeholder">采集演示 · 建设中（N-c 窗口填充）<br>'
        "四类判定可视化 → verdict 状态位流转 → expected_types 交互 → 63.7 复现</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    render()
