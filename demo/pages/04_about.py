"""关于页（N-a 空壳 · N-d 窗口填充）。

设计依据：demo-redesign-design v0.3 §3.5（Spec 轴必改项）。
N-d 填充内容（预置结构）：
  项目一句话 + 三价值层（lint/benchmark/reward）白话 + 工程数字
  （269 测试 / CI 双矩阵 / golden 0 差异 / 三元组快照）+ 路线图 +
  MCP 说明（文字 + 代码示例，不作演示页）+ takeaway 三句话 +
  旧痛点 × 新手段对照表。
"""
from __future__ import annotations

import streamlit as st


def render() -> None:
    st.markdown('<h1 class="ba-page-title">关于</h1>', unsafe_allow_html=True)
    st.markdown(
        '<div class="ba-page-sub">Bio-Audit 是什么、为什么可信、接下来做什么。</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="ba-placeholder">关于 · 建设中（N-d 窗口填充）<br>'
        "一句话定位 → 三价值层 → 工程数字 → 路线图 → MCP → takeaway</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    render()
