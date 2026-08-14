"""包内路径锚定（audit F7 修复：所有路径相对 cwd → 包内锚定）。

本模块是全部数据资源的唯一解析入口：引擎、UI、脚本一律从这里取路径，
**不依赖当前工作目录**（任意 cwd 下 import 均可用）。

实现选择：以 ``Path(__file__).resolve()`` 派生（等价于
``importlib.resources.files("bioaudit")`` 的效果，且在 editable 安装与
wheel 安装两种模式下都可用；包数据声明见 pyproject.toml package-data）。
"""

from pathlib import Path

# 包根（src/bioaudit/）
PKG_DIR = Path(__file__).resolve().parent

# ── 数据资源锚点 ──
RULES_DIR = PKG_DIR / "rules" / "data"          # 43 条规则 YAML（DEG/pancancer/scRNA）
TRAJECTORIES_DIR = PKG_DIR / "data" / "trajectories"  # 20 条轨迹 JSON
MAPPINGS_DIR = PKG_DIR / "data" / "mappings"    # aliases / context_keys / dep_graph / type_to_dim
VALIDATION_DIR = PKG_DIR / "data" / "validation"  # 验证数据（full_audit_results 等）
REPORT_DATA_DIR = PKG_DIR / "data" / "report"   # 报告数据（ai_error_patterns.md）

# 范式 → 规则子目录（golden 复算按范式分别建 registry）
ACT_RULE_SUBDIRS = {
    "deg": "DEG",
    "pan": "pancancer",
    "scrna": "scRNA",
}


def rules_dir_for(act: str) -> Path:
    """按范式取规则目录；未知范式回退到全量规则目录（C2 去重后 38 唯一规则）。"""
    sub = ACT_RULE_SUBDIRS.get(act)
    return RULES_DIR / sub if sub else RULES_DIR


def trajectory_path(name: str) -> Path:
    """按轨迹名（不含扩展名）解析轨迹文件路径。"""
    return TRAJECTORIES_DIR / f"{name}.json"
