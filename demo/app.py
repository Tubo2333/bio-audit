"""Bio-Audit 新演示入口（窗口 N 重建 · N-a 骨架层）。

设计依据：docs/specs/2026-08-16-demo-redesign-design.md（v0.3 定稿）§3.1/§4/§5。

本文件只做四件事：
1. 主题注入（theme.css，深色审计台，data-testid 选择器）；
2. 启动数据校验（demo/data/ 清单 + manifest 指纹，缺失给中文提示不崩溃）；
3. 侧边栏页级导航（四页，不用 st.tabs 承载整页）；
4. 条件渲染（按当前页调用 pages/*.py 的 render()）。

外围层纪律：demo 只调 bioaudit.api + capture 公共类，不碰评分路径
（引擎/规则/本体/黄金资产零改动，golden 0 差异硬验收）。
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

import streamlit as st

from bioaudit.report import current_snapshot

DEMO_ROOT = Path(__file__).resolve().parent
# 任意 cwd 启动均可用（streamlit run demo/app.py 或绝对路径）：demo/ 自身入 path
if str(DEMO_ROOT) not in sys.path:
    sys.path.insert(0, str(DEMO_ROOT))

import data_index  # noqa: E402

# ── 页面注册表（侧边栏导航顺序即列表顺序）──────────────────────────────
PAGES: list[tuple[str, str, str]] = [
    ("workshop", "审计工坊", "pages.01_workshop"),
    ("capture", "采集演示", "pages.02_capture"),
    ("benchmark", "评测与奖励", "pages.03_benchmark"),
    ("about", "关于", "pages.04_about"),
]
PAGE_TITLES = {pid: label for pid, label, _mod in PAGES}
DEFAULT_PAGE = PAGES[0][0]


def _inject_theme() -> None:
    """注入深色审计台主题（theme.css）。1.x 版本锁定的动机之一：data-testid 稳定。"""
    css = (DEMO_ROOT / "theme.css").read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def _render_banner(page_title: str) -> None:
    """顶部横幅：品牌 mark + 三元组版本徽章 + 当前页名（可信 UI 起点）。"""
    snap = current_snapshot()
    st.markdown(
        f"""
        <div class="ba-banner">
          <span class="ba-brand">BIO-AUDIT</span>
          <span class="ba-badge">engine {snap.engine_version}</span>
          <span class="ba-badge">ruleset {snap.ruleset_version}</span>
          <span class="ba-badge">ontology {snap.ontology_version}</span>
          <span class="ba-banner-page">{page_title}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_sidebar() -> None:
    """侧边栏页级导航：radio 页级切换（选中态由 theme.css 定制为琥珀左边条）。

    自动 multipage 导航（pages/ 目录扫描）由 theme.css 隐藏——本应用以
    条件渲染为准，避免双导航。
    """
    with st.sidebar:
        st.markdown('<div class="ba-sidebar-title">Bio-Audit 演示</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="ba-sidebar-sub">科学决策审计 · 深色审计台</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="ba-nav-rule"></div>', unsafe_allow_html=True)
        st.radio(
            "页面导航",
            options=[pid for pid, _l, _m in PAGES],
            format_func=lambda pid: PAGE_TITLES[pid],
            key="page",
            label_visibility="collapsed",
        )
        st.markdown('<div class="ba-nav-rule"></div>', unsafe_allow_html=True)
        st.caption("数据仅读 demo/data/ + 包内资产")


def _render_page() -> None:
    page_id = st.session_state.page
    mod_name = next((m for pid, _l, m in PAGES if pid == page_id), PAGES[0][2])
    module = importlib.import_module(mod_name)
    module.render()


def main() -> None:
    st.set_page_config(page_title="Bio-Audit 审计演示", page_icon="🔬",
                       layout="wide", initial_sidebar_state="expanded")
    _inject_theme()

    # 页状态：radio(key="page") 持久化；首跑显式初始化（横幅先于侧边栏渲染）
    if "page" not in st.session_state:
        st.session_state.page = DEFAULT_PAGE

    # ── 启动数据校验（自包含性硬约束：demo 只读 demo/data/，缺失不崩溃）──
    problems = data_index.verify_data_ready()
    if problems:
        st.error(
            "演示数据缺失或指纹不匹配（demo/data/ 未就绪）：\n\n"
            + "\n".join(f"- {p}" for p in problems)
            + "\n\n请先运行 `python demo/scripts/export_demo_data.py` 生成演示数据，"
              "然后再启动本应用。"
        )
        st.stop()

    _render_banner(PAGE_TITLES.get(st.session_state.page, "演示"))
    _render_sidebar()
    _render_page()


if __name__ == "__main__":
    main()
