# Contributing（规则贡献指南 / Rule Contribution Guide）

Bio-Audit 的核心资产是**文献锚定的科学规则**。规则即代码，变更走 PR（v1.1 D1）。

## 规则变更流程（D1 治理，B5 完善 CI）

1. 修改 `src/bioaudit/rules/data/<范式>/<rule_id>.yaml`（或新增文件）
2. 更新 `src/bioaudit/rules/ruleset.json` 的 `version`（semver，破坏性变更升 major）
3. 本地跑 `python scripts/golden_replay.py` —— 分数漂移必须逐条解释
4. 提交 PR：本体/冲突/覆盖三类校验（B2/B5 落地后进 CI，失败自动回退）

## 规则文件规范

- `rule_id` 全局唯一；同 `decision_type` 不同 `choice` 不得评不同 level（D2 冲突检查）
- 每条规则必须带 `evidence`（PMID/DOI/URL + confidence 五档）
- `condition` 引用 context 键须与 `data/mappings/context_keys.yaml` 对齐
- 未知方法不得评 L0——返回 -1（无法评估）或补规则（A2 方向）

## 代码规范

- Python >= 3.10；ruff（`pip install -e ".[dev]"`）
- 数据路径一律走 `bioaudit.paths`，禁止相对 cwd 路径
- 引擎改动必须通过 `tests/test_golden.py`（0 差异）与 `tests/`

## 许可

Apache-2.0（H13）。提交即视为同意贡献条款。
