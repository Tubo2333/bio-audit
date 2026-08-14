"""规则集包（v1 蓝图：规则集版本化打包 + shared_evidence）。

- data/{DEG,pancancer,scRNA}/**: 43 条规则 YAML（A3 统一后 DEG 血统）
- ruleset.json: 规则集快照清单（C1 三元组之 ruleset 版本；B5 semver/CI 完善）
"""

from bioaudit.paths import RULES_DIR

RULESET_VERSION = "1.0.0"  # 与 ruleset.json 同步；规则变更走 D1 治理流程

__all__ = ["RULES_DIR", "RULESET_VERSION"]
