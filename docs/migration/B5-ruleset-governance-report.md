# B5 完成报告（阶段 1 · 规则治理）— 2026-08-14

> 执行窗口 ⑦ · B5：ruleset.json 正式启用 + 三元组快照 + ruleset-validate 三闸 +
> D2 冲突裁决 + D4 修复条目映射表。
> 依据：execution-plan-v1（§六.五 B5 验收清单 6 项，冻结）、refactor-plan-v1.1
> （D1/D2/D4/C1/P2）、B2 完成报告 §五遗留 1、audit-report（A13/A14）。
> 验收对照见文末 §六（逐条打勾）。

## 一、产出清单

```
src/bioaudit/rules/
├── ruleset.json              # ★ 重新生成 v1.1.0：semver + 43 文件内容哈希 + 38 唯一 rule_id
│                             #   + engine/ontology 版本 + 生成日期（posix 相对路径）
├── manifest.py               # ★ 清单加载/校验/生成（load_ruleset / verify_manifest /
│                             #   generate_manifest；semver 正则校验，版本唯一事实源）
├── validator.py              # ★ ruleset-validate 三闸（清单 + D2 冲突 + golden）
└── __init__.py               # RULESET_VERSION 从 ruleset.json 读取（不再硬编码，fail-closed）

src/bioaudit/ontology/validator.py   # D2 冲突检测升级为范式感知（scope=same-rule-set）
src/bioaudit/api/audit.py            # report 三元组快照写全（C1/P2，不再 None）
src/bioaudit/cli.py                  # + bio-audit ruleset-validate 子命令
scripts/generate_scrna_r0.py         # （B6-5，见 B6 报告）
tests/test_ruleset_governance.py     # ★ 9 项治理测试（清单/三元组/三闸/变更流程/fail-closed）
tests/test_ontology.py               # 冲突测试更新 + 2 项 D2 合成检测用例

docs/specs/2026-08-14-d2-adjudication.md   # ★ D2 裁决书（2 处逐条裁决 + 漂移记录）
docs/specs/2026-08-14-fix-tracking.md      # ★ D4 修复条目映射表（78 条：已修 52/挂账 14/排期 12）
docs/specs/2026-08-13-golden-baseline/asset_manifest.json  # G1.3 条目更新 + change_log
docs/api-contract.md                       # report 三元组 schema 示例（B5 字段）
CONTRIBUTING.md                            # D1 规则变更流程更新（三闸 + semver + CI）
```

## 二、B5-1 ruleset.json 正式启用

- `RULESET_VERSION` 由硬编码 `"1.0.0"` 改为 **从 ruleset.json 读取**
  （`bioaudit.rules.manifest.load_ruleset`；缺失/非 semver → import 失败，fail-closed）。
- ruleset.json **重新生成 v1.1.0**（`generate_manifest`）：43 文件 SHA256 + size、
  38 唯一 rule_id、engine_version=0.1.3、ontology_version=0.1.0、生成日期；
  路径改为 posix 相对（跨平台 CI 稳定）。
- `verify_manifest()` 五项检查：semver / 清单↔磁盘一一对应 / 内容哈希与 size /
  YAML→Rule schema / 唯一 rule_id=38（DEG/pancancer 5 对同名副本为 C2 预期，
  计 duplicate_copies=5 告警不报错）。
- 篡改守卫测试：改一个字节 → hash_mismatch 报错（`test_verify_manifest_detects_hash_mismatch`）。
- **注意（行尾纪律）**：篡改测试必须用 read_bytes/write_bytes——Windows 文本模式
  write_text 会把 `\n` 转 `\r\n` 破坏文件字节（实测踩坑，已修复并加注释）。

## 三、B5-2 三元组快照完整（C1/P2）

`run_audit` 的 report 由 B3 时的 `ruleset_version: None / ontology_version: None`
改为 **current_snapshot()** 完整写死：

```json
"engine_version": "0.1.3",
"ruleset_version": "1.1.0",
"ontology_version": "0.1.0",
"snapshot": {"ruleset_version": "1.1.0", "ontology_version": "0.1.0", "engine_version": "0.1.3"}
```

- ruleset 版本读 ruleset.json；ontology 版本读本体（paradigms.yaml 0.1.0）；
  engine 版本 = 包版本（本次 0.1.2 → **0.1.3**，B5/B6 功能变更；0.1.2 为 B3/B4 窗口的 CHANGELOG 记录，代码侧补对齐）。
- 契约文档 docs/api-contract.md report schema 示例同步；契约测试
  `test_report_snapshot_triple_complete` 守卫非 None。

## 四、B5-3 ruleset-validate 一条命令（D1）

`bio-audit ruleset-validate [--json] [--baseline PATH]` 三闸一次跑完：

| 闸 | 内容 | 命令内部 |
|----|------|---------|
| 1 | 清单校验（semver/哈希/唯一 id/schema） | `manifest.verify_manifest` |
| 2 | 冲突完整性（D2 范式感知）+ 本体覆盖/语义边界 | `ontology.validator.validate` |
| 3 | golden 重放（20 轨迹 137 决策 0 差异） | `regression.replay_golden` |

退出码：0 = 三闸全绿；1 = 任一失败（CI 门禁拦截 = D1"失败自动回退"）。
实测：`✅ 规则治理校验通过（三闸全绿）` exit 0；篡改规则 → 闸 1 FAIL exit 1（测试守卫）。

## 五、B5-4 D2 冲突裁决（2 处，逐条）

完整裁决书：**docs/specs/2026-08-14-d2-adjudication.md**。摘要：

1. **deg_method/MAST（G1.1 L1 vs G1.3 L2，scRNA 内）** → 裁决：**以 G1.1 为准**。
   裸 MAST（细胞级、无重复校正）伪重复未解决 = L1；`MAST_with_replicate_correction` = L2。
   G1.3 规则文本修订（MAST 移入 level_1，L2 列表改 corrected variant）；
   audit-report A13（wilcoxon 分歧）一并核销（两规则 wilcoxon 变体已在 L1 一致）。
   **评分影响 0**（strictest 取分前后均 L1；20 轨迹无 MAST 选择；scrna_r0 combo_3 S10
   重生成逐字节一致）→ **基线未更新**（C4 流程未触发，无漂移原因需记录）。
2. **multiple_testing_correction/bonferroni（G1.2 L2 vs M1.2 L1，跨范式）** → 裁决：
   **范式隔离成立，非真冲突**（required_context 互斥、运行时按范式 registry 隔离；
   bulk 全基因组 FWER 过保守 L1 vs scRNA 高特异性场景保守可接受 L2，各自语境成立）。
   两规则原文保留；冲突检测器升级为**范式感知**（scope=same-rule-set，
   与运行时按范式建 registry 语义一致）。

裁决后：validate-ontology / ruleset-validate 冲突数 = **0**。
规则集版本 1.0.0 → 1.1.0（内容修订，minor）；asset_manifest.json G1.3 条目
45055f06…→d711130e… + change_log（不静默改，全程留痕）。

## 六、B5-5 D4 修复条目映射表

**docs/specs/2026-08-14-fix-tracking.md**：audit-report 全部 **78 条**问题
（A17+B10+C16+D12+E5+F12+G6）→ 状态清单：**已修 52 / 挂账 14 / 排期 12**，
每条附窗口证据（阶段 0 A1-A6 / 窗口 B1-B6）。活文档，后续窗口完成排期项即更新。

## 七、验收对照（B5 验收清单 6 项）

| # | 验收项 | 结果 |
|---|--------|------|
| 1 | ruleset.json 正式启用：38 唯一 rule_id + 内容哈希 + semver；report.ruleset_version 读它（不再 None） | ✅ ruleset.json v1.1.0（43 文件哈希/38 唯一 id/semver）；RULESET_VERSION 与 report 均读文件；测试守卫 |
| 2 | 三元组快照完整：engine + ruleset + ontology 全部写进 report | ✅ report.engine_version/ruleset_version/ontology_version/snapshot 全非 None（0.1.3/1.1.0/0.1.0） |
| 3 | `bio-audit ruleset-validate`：校验器 + 冲突检查 + golden replay 一条命令 | ✅ 三闸一条命令，exit 0/1；9 项测试含篡改→FAIL |
| 4 | D2 冲突裁决 2 处，裁决结果写进 docs | ✅ 裁决书 docs/specs/2026-08-14-d2-adjudication.md（逐条：改规则文本 / 范式隔离+检测器升级）；冲突归零 |
| 5 | 修复条目映射表（D4）：audit-report 全部问题 → 状态清单 | ✅ docs/specs/2026-08-14-fix-tracking.md（78 条全量） |
| 6 | 回归：规则治理改动后 golden 0 差异；若裁决改变评分按 C4 更新基线并记录漂移原因 | ✅ golden **0 差异**（20 轨迹 137 决策）；裁决 0 评分变化 → 基线未动，无漂移原因；asset_manifest change_log 记录 G1.3 哈希变更 |

## 八、遗留项（不阻塞 B5 验收）

1. PR 门禁的远端载体：仓库当前无 git remote（本地 git）；.github/workflows/ci.yml
   已就绪（B6），推送到 GitHub 后 D1"PR 强制"生效。
2. A2（未知方法 L0→-1）等排期项见 fix-tracking.md（阶段 1 后半段 missing 语义同批）。
