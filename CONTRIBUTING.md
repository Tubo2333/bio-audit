# Contributing（规则贡献指南 / Rule Contribution Guide）

Bio-Audit 的核心资产是**文献锚定的科学规则**。规则即代码，变更走 PR（v1.1 D1）。

## 规则变更流程（D1 治理，B5/B6 落地 CI 三闸）

1. 修改 `src/bioaudit/rules/data/<范式>/<rule_id>.yaml`（或新增文件）
2. **一条命令本地验证**：`bio-audit ruleset-validate`
   —— 三闸全绿才算通过（B5）：
   - 闸 1 清单校验：ruleset.json semver + 43 文件内容哈希 + 38 唯一 rule_id + YAML→Rule schema
   - 闸 2 冲突完整性：同规则集内 同 decision_type + choice 不同 level（D2，范式感知）
   - 闸 3 golden 重放：20 轨迹 137 决策与冻结基线 0 差异（分数漂移必须逐条解释，C4）
3. **提升 semver 并重新生成清单**：`python -c "from bioaudit.rules.manifest import generate_manifest; generate_manifest(ruleset_version='x.y.z')"`
   （版本语义：破坏性评分变更升 major；内容修订升 minor；纯元数据升 patch。不得静默改。）
4. 提交 PR：CI（GitHub Actions，B6）在 Python 3.10/3.12 双版本跑
   pytest + golden + ruleset-validate，**失败即红 = 自动回退（不合并）**
5. 规则变更同时同步 `docs/specs/2026-08-13-golden-baseline/asset_manifest.json`
   的对应条目（change_log 记录旧→新哈希），并更新 CHANGELOG.md

## 规则文件规范

- `rule_id` 全局唯一；**同一规则集内**同 `decision_type` 不同 `choice` 不得评不同 level
  （D2 冲突检查，B5 起范式感知：跨范式语境差异合法，裁决书见
  docs/specs/2026-08-14-d2-adjudication.md）
- 每条规则必须带 `evidence`（PMID/DOI/URL + confidence 五档）
- `condition` 引用 context 键须与 `data/mappings/context_keys.yaml` 对齐
- 未知方法不得评 L0——返回 -1（无法评估）或补规则（A2 方向）

## 代码规范

- Python >= 3.10；ruff（`pip install -e ".[dev]"`）
- 数据路径一律走 `bioaudit.paths`，禁止相对 cwd 路径
- 引擎改动必须通过 `tests/test_golden.py`（0 差异）与 `tests/`

## 许可

Apache-2.0（H13）。提交即视为同意贡献条款。
