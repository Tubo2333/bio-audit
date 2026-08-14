"""本体包（阶段 B2 落地，当前为骨架占位）。

设计依据：docs/specs/2026-08-13-ontology-design-v1.md + refactor-plan-v1.1
（P1 校验器三职责：覆盖报告 / 语义边界 / 冲突完整性；aliases；internal_ref）。

B2 待落地：
- 34 个决策类型定义文件（含 A4 design→fail-closed、G3 unit 维度、G4 confound 键、
  G5 适用性谓词、G6 方向性待补清单）
- context_schema（missing 三档：fail-closed / skip / fail-open，A1-A5 交互规则）
- 未知决策类型 → unclassified + 待补清单（规则集增长入口）
"""

ONTOLOGY_VERSION = "0.0.0"  # B2 落地后提升；C1 三元组之 ontology 版本
