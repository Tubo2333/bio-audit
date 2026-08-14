"""Bio-Audit — 生信 AI Agent 方法学决策的确定性审计层（Scientific Decision CI）。

单仓库重构（bio-audit-v2, 阶段 1 B1）：引擎 / 规则集 / 轨迹 / 验证资产 / API / UI 薄壳。
引擎基线：fullflow-demo（D5 修复后 + DEG 双副本统一 + mappings 补齐）。
"""

__version__ = "0.1.0"

# 快照三元组（v1.1 C1）：规则集版本见 bioaudit/rules/ruleset.json；
# ontology 版本在阶段 B2 落地（当前 0.0.0 占位）。
ENGINE_VERSION = __version__
ONTOLOGY_VERSION = "0.0.0"
