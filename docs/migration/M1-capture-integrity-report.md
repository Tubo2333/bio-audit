# 窗口 M 报告：采集完整性（expected_types 强制预期决策点 + missing 三档运行时强制 + A1-A5 挂账批次）

> **日期**：2026-08-16（窗口 M）
> **性质**：采集层语义大改——**先设计后实现**：设计提案
> `docs/migration/M1-design-proposal.md` 经 **ask_user_question 实际走通项目负责人
> 在线确认**（2026-08-16，5 项全确认：expected_types 语义 / Option B 规则引用驱动 /
> level=-2 独立编码 / B7 判定与词表评级 / 10X-B 闭环重跑方式）。本报告措辞一律
> 用"经项目负责人确认"，不称"已批准"（吸取 J1 流程教训）。
> **对应验收**：execution-plan §六.十七 M1–M3（10 项，2026-08-16 冻结）
> **执行顺序**：M-a（expected_types + 10X-B 闭环）→ M-b（A1-A5 + override + 词表）→ M-c（回归连锁）
> **版本**：engine **0.2.1 → 0.3.0**（missing 强制/override 修复/未验证状态）·
> ruleset **1.6.0 → 1.7.0**（词表补齐）· ontology **0.1.2 → 0.1.3**（data_source 类型修复）

---

## 1. 结论摘要（直给）

| 子任务 | 结果 | 关键数字 |
|---|---|---|
| **M-a expected_types 强制预期决策点** | ✅ 落地 | 配置 `data/expected_types.yaml`（10X 11 决策 / Smart-seq2 10 决策，A 版实证）；缺失预期决策补入 provenance=expected；B7 豁免（optional + 谓词满足） |
| **10X-B 闭环** | ✅ **63.7 · blocked 走采集链路** | doublet_detection 补入（choice=skip_doublet 取 M1 声明）→ D1.1 L0；不再依赖引擎级补验（L 报告 §4.3.1 追加） |
| **M-b missing 三档运行时强制** | ✅ Option B 规则引用驱动 | fail-closed 键缺失且被候选规则引用 → **未验证 level=-2**（与 -1 区分、同掩码）；**golden 0 漂移**、任务 13 决策受影响（pca_dimension 缺 n_genes） |
| **override_n2 键映射修复** | ✅ | G1.1 读 `n_patients`（原硬编码 n_replicates）；n=0 falsy 修复；候选级 override（D4 死代码问题修复） |
| **B7 合理省略 + 词表补齐** | ✅ | 判定入口 = expected_types 评测配置层；PCA_arbitrary→**L1**、no_trajectory→**L0**（K 遗留①收尾） |
| **M-c 回归连锁** | ✅ 全绿 | golden **0 差异**（C4 基线更新 2 决策 + 双副本）；pytest **269/269**（+23）；三/四/五闸 + validate-ontology + capture-validate + MCP 全 PASS；ruff **38 < 40 基线**；benchmark/gap/reward 复跑留档（见 §9） |

**一句话**：采集层"静默跳过不可见"的洞补上了（10X-B 跳过双联体 → 采集链路直接出
63.7 blocked），missing 三档从"设计定稿"变成"运行时强制"，评分语义与 -1 显式区分
（未验证 -2），A1-A5 挂账批次（A3 键映射/A5 类型强制/B7 合理省略）收尾。

---

## 2. M1.1/M2.7 设计确认记录（清单 M1.1/M2.7）

- **流程**：先设计后实现——设计提案落盘 `docs/migration/M1-design-proposal.md`
  （含影响面实测：Option A vs B 量化对比），经 **ask_user_question 提交项目负责人
  在线确认**（2026-08-16），5 项全部确认后落地。
- **确认内容**：
  1. **expected_types 语义**：清单放评测配置（`data/expected_types.yaml`，per 范式×平台，
     非引擎硬编码）；默认清单 = L 窗口 A 版实证决策集（10X 11 / Smart-seq2 10）；
     缺失预期决策补入 provenance=expected（choice 优先取 M1 已撤销声明，无则
     not_performed）；仅显式 optional 且 when_not_applicable 谓词满足才豁免（B7/G5
     保守原则）。
  2. **missing 强制范围 = Option B（规则引用驱动）**：fail-closed 键缺失**且被该类型
     候选规则引用**（required_context ∪ context_constraints ∪ override 键）→ 未验证；
     无规则引用的键缺失不凭空降级（实测 golden 0 / 任务 13，vs Option A 45/197）。
  3. **未验证状态 = level=-2 独立编码**（与 -1 区分；聚合/reward 同掩码；报告列缺失键）。
  4. **B7 判定与词表评级**：判定入口在评测配置层（引擎不猜研究范围）；
     PCA_arbitrary→L1、no_trajectory→L0；无谓词证据保守"该做没做"；benchmark 差异
     预注册留档（§9.2），不追溯改标注。
  5. **10X-B 闭环重跑方式**：复用 windowL 已有 WAL/verdict/notebook 产物 + expected_types
     配置重跑采集链路（零新执行成本）。
- **实施修正 1 处（已记录）**：默认清单初稿含 api_data_integrity，实测 A 版最终轨迹
  11/10 决策不含该类型（M3 无确定性签名）→ 已移除（10X-B 重跑验证仅 doublet_detection
  补入）。

---

## 3. M-a：expected_types 实现（清单 M1.2）

### 3.1 代码落地

| 产物 | 内容 |
|---|---|
| `src/bioaudit/data/expected_types.yaml` | 评测配置：scrna_10x 11 决策 / scrna_smartseq2 10 决策 / pan·deg 骨架（当前不启用强制）；变更走评审 |
| `src/bioaudit/capture/expected_types.py` | 配置加载 + 平台解析（facts.sequencing 驱动）+ B7 豁免谓词注册表（11 个 when_not_applicable 谓词）+ 补入决策构造 |
| `capture/models.py` | 新增 `PROVENANCE_SOURCE_EXPECTED = "expected"` |
| `capture/cross_validator.py` | `validate()` 预期补入：无最终证据（双方都无 / M1 虚报撤销）→ 补入 added_decisions + **final verdict（来源 expected）**；对齐记录 `expected_added=True`（不新增对齐行）；stats 新增 `expected_added` |
| `paths.py` | `EXPECTED_TYPES_PATH` 包内锚点 |
| `cli.py` | `cross-validate --expected` 支持 YAML 评测配置（按范式×平台解析 + B7 豁免） |

**关键语义**：补入决策参与评分（L0 威慑落点）；final-only 纪律保持（报告/reward
只消费 final）；choice 取 Agent 自己的声明（不伪造），无声明才用 not_performed。

### 3.2 10X-B 闭环（清单 M1.2 核心）

**重跑**（`windowL/analyze_run.py --expected-config`，复用已有产物，零新执行成本；
新会话 `golden_winL_10X_B_expected`，不触碰原会话 verdict）：

| 项 | 值 |
|---|---|
| effective expected_types | 11 决策（10X 标准管线） |
| 交叉验证 | consistent 10 / 虚报 1（skip_doublet 撤销）/ 漏报 0 / 未验证 1 + **expected_added 1** |
| 补入决策 | `doublet_detection / skip_doublet`（provenance=expected，verdict final，context = M1 事实：sequencing=10X_scRNA_seq / n_cells=59,399 / data_category=umi_counts / n_patients=23 / has_batch=true） |
| final 轨迹 | **11 决策** |
| **评分** | **63.7 · blocked**（data_handling 0.6375，D1.1 L0）——与 L 窗口引擎级补验数字一致，**路径不同：直接出自采集链路** |
| 产物 | `cellvoyager-outputs/windowL/reports/windowL_10X_B_expected.json`（本地，不入仓库） |

**意义**：L 报告 §6.2 登记发现①（阴性声明不可验证 → L0 威慑依赖"决策被声明"）闭环——
10X 平台 doublet_detection 为标准管线预期决策点，静默跳过也会被补入 → D1.1 L0 →
blocked。L 报告 §4.3 追加记录（§4.3.1），原"引擎级补验"段落保留为历史留档；
**不再标注"引擎级补验"**。

### 3.3 G/L 窗口真实评测带 expected_types 复跑（清单 M1.3）

- **10X-A**：expected_types 含 doublet_detection 但 A 版有 M1+M3 一致证据 → 不补入，
  11 决策 80.0 pass 不变（闭环重跑验证）。
- **L-b（CellVoyager 聚焦短分析）**：qc_filtering"执行了但未捕获"（M3 签名缺口 +
  M1 未声明）→ qc_filtering 为标准管线预期决策点 → 若带 expected_types 重跑会被补入
  （choice=not_performed → 参与评分）。**如实声明**：L-b 原始运行未带 expected_types
  （机制自本窗口起生效），历史分数不追溯重判；复跑需重放 WAL 数据，排期评估
  （不阻塞，如实登记）。
- **G 窗口（CellVoyager 20 决策）**：同 L-b 处理——机制自本窗口生效，历史不追溯。

---

## 4. M-b：missing 三档运行时强制（清单 M2.4）

### 4.1 语义（Option B，项目负责人确认）

| 档位 | 触发（缺失键且被候选规则引用） | 行为 |
|---|---|---|
| **fail-closed** | required_context / context_constraints / override 条件键 | 决策 **未验证（level=-2）**，跳过规则求值（含 override）——评估前提不成立 |
| **skip** | 同上 | 跳过依赖该键的规则（`skipped_rule_ids` 溯源，A1 交互规则不静默） |
| **fail-open** | 同上 | 视为满足（仅无害键）；**A2 运行时断言**：被候选规则引用且缺失 → 警告留痕（静态校验器已禁，防绕过） |
| **类型/枚举（A5/A3）** | 非法值/枚举外值 | 该键标 unverified → 按档位处理（枚举外值实测仅 api_data_integrity.data_source——**本体修复 enum→string**，ontology 0.1.3） |

- **A5 顺序**：先按最严档位定决策状态，再规则求值（`context_guard.resolve` →
  `score_decision`，run_audit / audit_decision / golden 重放三处共用同一入口，防漂移）。
- **未验证状态表示**：`level=-2`，`LEVEL_LABELS[-2]`，`DecisionScore.missing_keys`
  （报告列缺失键）；聚合/verdict 与 -1 同掩码；reward mask（原因 `level_unverified` 与
  `level_minus_one` 区分）。
- **影响面（实测）**：golden **0 漂移**（现有上下文均规则充足）；benchmark 任务
  **13 决策**（pca_dimension 缺 n_genes，D2.2 约束引用）→ 未验证。

### 4.2 override_n2 键映射修复（清单 M2.5）

- **键映射**：evaluator 不再硬编码 `n_replicates`——解析规则 `override_n2.condition`
  取键（G1.1 → `n_patients`、M1.1 → `n_replicates`，各规则自声明）；
- **n=0 falsy 修复**（fix-tracking A3）：显式 `key in ctx` + 数值强转，0 正确触发；
- **候选级 override**（D4 意图落地）：override 在 required_context 门外独立生效——
  修复 G1.1 的 `n_patients >= 3` 约束门使 `n_patients <= 2` override 成死代码的问题
  （n=2 时旧实现规则不匹配 → override 永不触发）；
- **override 键计入规则引用**（missing 强制联动：n 键缺失 → 未验证）；
- 影响：golden 0 漂移（scRNA n_patients 均 ≥10；deg_edge_n2 行为保持）。

### 4.3 B7/G5 合理省略判定 + 词表补齐（清单 M2.6）

- **判定入口 = expected_types 评测配置层**：optional:true + when_not_applicable 谓词
  满足（事实由评测者声明）→ 合理省略豁免（不补入不评分）；**引擎层不猜研究范围**，
  无谓词证据的"声明跳过"按词表保守评级。
- **词表条目评级（项目负责人确认）**：
  - `PCA_arbitrary` → D2.1 **L1**（任意选维无客观依据，与 PCA_fixed_10/15 同原则；
    K 遗留①收尾）；
  - `no_trajectory` → T1.1 **L0**（该做没做：结论缺失时间维度证据；B7 豁免在评测
    配置层判定）。
- **规则修订走 B5 三闸 + ruleset semver**：1.6.0 → **1.7.0**（45 文件 / 40 唯一规则）；
  三闸 PASS（清单 / 冲突 0 / golden 按 C4）。

---

## 5. M-c：回归连锁（清单 M3.8/M3.9）

### 5.1 golden C4 漂移记录（逐条归因，基线更新）

漂移共 **4 处（2 条轨迹）**，全部归因；基线双副本更新（`tests/golden/` +
`docs/specs/2026-08-13-golden-baseline/`，old 4c4d1b3d → new b88e919e）：

| 轨迹 | 决策 | 变化 | 原因 |
|---|---|---|---|
| scrna_melanoma_cellvoyager | S7 dim_reduction PCA_arbitrary | -1 → **L1** | M2.6 词表补齐（任意选维 = 有风险） |
| scrna_melanoma_cellvoyager | S11 trajectory_inference no_trajectory | -1 → **L0** | M2.6 词表补齐（该做没做；B7 豁免在评测配置层） |
| scrna_melanoma_cellvoyager | dimension_scores | method_selection 0.63 → **0.4929** | S7/S11 由掩码变可评（L1 0.3 + L0 0.0 入维） |
| deg_edge_n2 | E1 deg_method | level 0 不变，explanation 增 override 语义 | M2.5 候选级 override 文案（评分零变化） |

- 轨迹分 29.0 / verdict blocked 不变（data_handling 0.29 仍主导）；
- asset_manifest change_log **+2 条**（D2.1/T1.1 哈希变更 45055f06…→dbb23546…、8f9145da…→40775421…）；
  assets 条目同步；
- **missing 强制（Option B）与 override 修复对 golden 零影响**（不触发 C4）。

### 5.2 benchmark-run 60 任务复跑 + gap 预注册解释

| 指标 | K 基线（1.6.0） | **M 后（1.7.0）** | 变化与归因 |
|---|---|---|---|
| mean | 0.5542 | **0.5572** [0.4862, 0.6267] | +0.003（S7/S11 由掩码变可评，方向相抵） |
| recall | 0.820 | **0.820** | 不变（TP=41/50；无 gold=error 决策依赖词表外） |
| precision | 0.7736 | **0.7455** | **-0.028（FP 12→14）** |
| F1 | 0.7961 | **0.7810** | -0.015 |
| edge 检出率 | 0.6458 | **0.6146**（59/96） | -0.031（-3 检出 = pca_dimension default_10×5 未验证不再检出 + S7×2 补入检出） |
| gap | +0.048 | **+0.0449** ∈ [-0.10, +0.10] | 区间内，无告警（预注册口径不变） |

**FP +2 预注册解释（不追溯改标注）**：bmd_scrna_007/020 的 S11 no_trajectory 由
-1 → L0（gold=correct → 2 FP）。引擎无研究范围证据时按确认语义**保守判"该做没做"**；
标注（基于研究范围判断"合理省略"）与引擎保守评级的分歧**如实登记**——这正是
B7 判定入口（评测配置层声明谓词事实）存在的原因：任务集未携带 `trajectory_focused`
事实，引擎不猜。评分语义正确化（"声明跳过"不再不可见），非检出能力退化。

### 5.3 其余回归

| 闸 | 结果 |
|---|---|
| golden 重放 | **0 差异**（基线更新后；C4 全记录） |
| pytest 全量 | **269/269**（246 → +23：expected_types 9 + missing/override/词表 14） |
| ruleset-validate 三闸 | manifest PASS（1.7.0）/ conflicts PASS（0）/ golden PASS |
| benchmark-validate 四闸 | taskset 1.1.0 / contamination 0 / coverage（豁免 2 项不变）/ golden PASS |
| reward-validate 五闸 | 映射/确定性/spike-in/消融/golden 全 PASS（-2 mask 语义纳入） |
| validate-ontology | checks 0 / A2 0 / conflicts 0（missing_tier_usage 57/5/14） |
| capture-validate | 签名表校验 + 样例 notebook 冒烟 PASS |
| MCP selfcheck | PASS |
| ruff | **38 < 40 基线**（新代码零新增，实际 -2） |

---

## 6. expected_types 使用说明（供评测者）

1. **默认清单**：`src/bioaudit/data/expected_types.yaml`（10X 11 决策 / Smart-seq2 10 决策，
   来自 L 窗口 A 版实证）；评测者按任务显式追加可选类型（如 trajectory_inference）并
   声明谓词事实（`trajectory_focused: false` 等，见 `capture/expected_types.py` 谓词表）。
2. **接入**：CLI `bio-audit cross-validate --expected <config.yaml>`（或
   `CrossValidator.validate(expected_types=..., expected_context=...)`）；真实评测经
   `analyze_run.py --expected-config`（windowL 先例）。
3. **行为**：缺失预期决策 → 补入 provenance=expected 参与评分（该做没做）；
   optional + 谓词满足 → 豁免（合理省略）；choice 优先取 Agent 已声明值（不伪造）。
4. **清单变更**：走评审（与任务集同门禁风格）；历史分数不追溯重判。

---

## 7. 产物清单与文档同步

| 产物 | 路径 |
|---|---|
| 本报告 | `docs/migration/M1-capture-integrity-report.md` |
| 设计提案（含确认记录） | `docs/migration/M1-design-proposal.md` |
| expected_types 配置 | `src/bioaudit/data/expected_types.yaml` |
| 采集层实现 | `capture/expected_types.py` + `cross_validator.py`（expected_added）+ `models.py`（PROVENANCE_SOURCE_EXPECTED） |
| 引擎实现 | `engine/context_guard.py`（missing 三档）+ `evaluator.py`（-2/override）+ `models/score.py`（missing_keys）+ `aggregator.py`（-2 掩码）+ `reward/{mapping,recipes}.py`（-2 mask） |
| 规则修订 | `rules/data/scRNA/{D2.1-DIMR-001,T1.1-TRAJ-001}.yaml`（词表）+ `ruleset.json`（1.7.0） |
| 本体修订 | `ontology/decision_types/api_data_integrity.yaml`（data_source string）+ 版本 0.1.3 |
| 测试 | `tests/test_expected_types.py`（9）+ `tests/test_m2_missing.py`（14）+ 既有测试更新（cross_validator/k2/declared_eval/ruleset_governance） |
| C4 基线 | `tests/golden/golden_expected_output_after.json` + `docs/specs/2026-08-13-golden-baseline/`（双副本 + asset_manifest change_log） |
| 验证数据 | `data/validation/{validation_dataset.jsonl, full_audit_results.json}` 重生成 + `data/report/ai_error_patterns.md` §2.1/§6.2 同步 |
| L 报告追加 | `docs/migration/L1-broader-eval-report.md` §4.3.1/§6.2/§8（10X-B 闭环，不再标"引擎级补验"） |
| 10X-B 闭环产物 | `cellvoyager-outputs/windowL/reports/windowL_10X_B_expected.json`（本地） |
| README/文档站 | README.md（真实效果口径）+ docs/index.md + site-design §6.2 + migration/index.md + CHANGELOG |
| fix-tracking | A3/A5/B7 排期状态更新（见下） |

**fix-tracking 更新**：A3（override n=0 漏判）→ ✅ 已修（M2.5）；A5（missing 三档
运行时强制 + 类型强制）→ ✅ 已修（M2.4）；B7（跳过可选模块合理省略）→ ✅ 已修
（M2.6，判定入口在评测配置层）；K 遗留①（PCA_arbitrary/no_trajectory 词表缺口）→
✅ 收尾。

---

## 8. 诚实局限

1. **B7 谓词默认保守**：引擎无研究范围证据时按"该做没做"评级 → benchmark 2 任务
   与标注分歧（§5.2 预注册解释）；评测者应在评测配置声明谓词事实消除分歧。
2. **skip 档实际触发面小**：skip-tier 键（3 个）均经 required_context 引用，
   规则本就不匹配——运行时强制为语义完备性（未来约束引用 skip 键时生效），
   当前无行为差异。
3. **L-b/G 窗口未带 expected_types 重跑**（机制自本窗口生效，历史不追溯）；
   复跑排期评估。
4. **10X-B 闭环复用已有产物**（未重新执行黄金脚本）——闭环验证的是采集链路语义，
   执行事实沿用 L 窗口记录。
5. **K3 时代 asset_manifest assets 条目与 change_log 有小不一致**（G1.1/G1.3 条目
   未随 K3 更新）——本窗口按 J1 先例同时更新 assets 与 change_log，既有不一致
   如实登记不追溯。
6. **golden 比较载荷排除 missing_keys 字段**（空数组机械漂移避免；语义变化由
   level/explanation 捕获）——若未来需要 golden 级 missing_keys 断言，需另设机制。

---

## 9. 验收清单对照（execution-plan §六.十七，10 项）

| # | 清单项 | 状态 |
|---|---|---|
| M1.1 | 设计 + 方案交审计中枢确认（expected_types 机制 + 缺失处理语义，B7/G5 保守原则） | ✅ §2（经项目负责人在线确认，实际走通） |
| M1.2 | 实现 + 测试（含 10X-B 闭环：B 版带 expected_types 重跑 → 补入 → D1.1 L0 → **63.7 blocked 走采集链路**） | ✅ §3（测试 9 项 + 真实重跑） |
| M1.3 | G/L 窗口真实评测带 expected_types 复跑（如适用）→ 如实呈现；历史不追溯 | ✅ §3.3（10X-A 不变验证；L-b/G 如实声明不追溯） |
| M2.4 | missing 三档运行时强制（A5 顺序）+ A2 校验（罚分规则引用键禁 fail-open，运行时强制） | ✅ §4.1（Option B；level=-2；A2 断言） |
| M2.5 | override_n2 键映射修复（n_replicates vs n_patients）+ 补测试 | ✅ §4.2（读规则配置键 + n=0 修复 + 候选级 override） |
| M2.6 | B7/G5 合理省略语义 + PCA_arbitrary/no_trajectory 词表补齐 | ✅ §4.3（判定入口评测配置层；L1/L0 评级） |
| M2.7 | 方案（missing 强制后决策状态语义、B7 判定标准、词表条目评级）先交审计中枢确认再落地 | ✅ §2（确认实际走通，报告不称"已批准"） |
| M3.8 | golden 0 差异（或 C4 漂移逐条归因）+ pytest 全量 + 三/四/五闸 + validate-ontology + CI 双矩阵云上绿 + git commit/push（推送纪律） | ✅ §5（C4 4 处全归因；269/269；全闸 PASS；CI 见完成报告） |
| M3.9 | benchmark-run 60 任务集复跑（指标变化留档 + 预注册口径解释）+ reward-validate 五闸复跑 | ✅ §5.2（precision 0.7736→0.7455 预注册解释；FP+2 分歧登记；gap +0.0449 区间内） |
| M3.10 | 报告落盘（本文件）+ execution-plan §六.十七 打勾 + README/文档站口径同步 | ✅ 本文件 + §7 + 完成报告 |

---

## 10. expected_types 机制与引擎语义变更的文档口径（README/文档站同步内容）

- README §真实效果：10X 对照行补"跳过双联体 → 采集链路 63.7 blocked（expected_types
  强制预期决策点，窗口 M）"；工程质量行 pytest 246/246 → 269/269。
- docs/index.md + site-design §6.2：新增 M 窗口行（10X-B 闭环口径：采集链路出 L0，
  不再标注引擎级补验）；版本行 engine 0.3.0 / ruleset 1.7.0。
- migration/index.md：新增 M 报告条目。
- CHANGELOG：0.2.1 后新增 0.3.0 条目（引擎语义变更 + 采集完整性）。

---

*报告完毕。窗口 M 执行计划快照、README/文档站口径、fix-tracking 已同步；
git commit/push 与 CI 云上确认见完成报告。*
