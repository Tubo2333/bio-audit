# 窗口 M 设计提案（M1.1 expected_types 语义 + M2.7 missing 强制/B7/词表评级）

> **日期**：2026-08-16（窗口 M）
> **性质**：~~设计提案~~ **已确认**——本文件为设计记录；确认经 ask_user_question
> 实际走通（**项目负责人在线确认，2026-08-16，5 项全确认**：D1 expected_types 语义 /
> D2 Option B 规则引用驱动 / D3 level=-2 独立编码 / D4 B7 判定与词表评级 /
> D5 10X-B 闭环重跑方式）。报告措辞一律用"经项目负责人确认"，不称"已批准"。
> **依据**：execution-plan §六.十七 M1.1/M2.7 + handoff-design-hub §七.M（审计中枢待裁决 2 处）
> + ontology-design-v1 §四（missing 三档定稿）+ refactor-plan-v1.1 A1-A5 + fix-tracking A3/A5/B7
> + L1-broader-eval-report §6.2/§4.3（阴性声明不可验证 + 10X-B 引擎级补验先例）
> **影响面实测**（2026-08-16，只读脚本，见下）：为裁决提供量化依据。

---

## 0. 影响面实测（设计输入）

| 方案 | golden 20 轨迹 137 决策 | benchmark 60 任务 623 决策 | 说明 |
|---|---|---|---|
| **Option A**：schema 全键严格强制（任何 fail-closed 键缺失 → 未验证） | **45 决策**变未验证（含 scrna_edge_nodoublet E7 L0→未验证、scrna_correct S3/S4/S6/S10 L3→未验证） | **197 决策**变未验证 | 符合 ontology-design §四字面（"代价已确认接受"），但大量键无任何规则引用（如 doublet 的 `unit`、multiple_testing_correction 的 `sequencing`）——缺失不影响任何评分正确性，标未验证属凭空降级；且 10X-B 闭环需额外合成 unit 才能出 L0 |
| **Option B（推荐）**：规则引用驱动——fail-closed 键缺失 **且被该类型候选规则引用**（required_context ∪ context_constraints）→ 未验证 | **0 决策**受影响 | **13 决策**受影响（全部为 pca_dimension 缺 `n_genes`，D2.2 约束引用） | 精确闭合 A1 洞（约束键缺失 fail-open 静默通过 → 未验证）与 required_context 静默不匹配（fail-closed 键缺失 → 未验证而非"规则不匹配"）；不误伤无规则依赖的键 |

- skip 档键（仅 3 个：`reference_based`/`graph_type`/`method`）规则引用极少：golden **0**、任务 **0** 受影响。
- 类型强制（A5 TypeError）：golden 上下文**0 处**类型不匹配。
- override_n2 键映射修复：golden 中 scRNA n_patients 均 ≥10、deg/pan 用 n_replicates——**0 漂移**；deg_edge_n2 E1（n_replicates=2）继续触发 override（修复后从规则配置读键，行为保持）。
- 词表补齐：golden 2 决策受影响（scrna_melanoma_cellvoyager S7 PCA_arbitrary -1→L1、S11 no_trajectory -1→L0）；任务 4 决策（bmd_scrna_007/020 的 S7/S11）。

---

## 1. M1.1 expected_types 处理语义（提案）

### 1.1 配置位置（清单放评测配置，不放引擎硬编码）

新增 `src/bioaudit/data/expected_types.yaml`（包内锚定，`paths.py` 加锚点；CLI 与 capture 共用）：

```yaml
# 预期决策点清单（评测配置，per 范式×平台）；变更走评审（与任务集同门禁风格）
version: 1
defaults:
  scrna_10x:        # 10X scRNA 标准管线（L 窗口 A 版 11 决策实证）
    - api_data_integrity
    - qc_filtering
    - doublet_detection
    - scRNA_normalization
    - hv_gene_selection
    - dim_reduction
    - batch_correction
    - clustering_method
    - annotation_method
    - deg_method
    - multiple_testing_correction
    - significance_threshold
  scrna_smartseq2:  # Smart-seq2 标准管线（无双联体前提，平台查证实证）
    - api_data_integrity
    - qc_filtering
    - scRNA_normalization
    - hv_gene_selection
    - dim_reduction
    - batch_correction
    - clustering_method
    - annotation_method
    - deg_method
    - multiple_testing_correction
    - significance_threshold
  # pan / deg：按范式 optional:false 类型 + 评测者显式声明（骨架，先不启用强制）
```

- 说明：execution-plan M1.1 举例"10X 10 决策、Smart-seq2 9 决策"为冻结清单时的预估；
  默认清单以 L 窗口 A 版最终轨迹实证为准（**11/10 决策**）；**实施修正 1 处**：
  初稿含 api_data_integrity（12/11），实测 A 版最终轨迹 11/10 不含该类型
  （M3 无确定性签名，属 uncertain 类）→ 已从默认清单移除（10X-B 闭环重跑验证
  仅 doublet_detection 补入，符合预期）。
- 可选类型（optional:true，如 trajectory_inference/batch 批次的谓词类）**不进默认清单**；
  评测者按任务显式追加（配谓词事实）。

### 1.2 缺失预期决策的补入语义（B7/G5 保守原则）

对每个预期类型，交叉验证后仍无 final 决策（M1/M3 均无，或 M1 声明被虚报撤销）时：

1. **豁免判定**：类型 `optional: true` **且** `when_not_applicable` 谓词满足（谓词事实由评测配置/declared 声明，如 `trajectory_focused: false`）→ **不补入、不评分**（合理省略，报告记录 exempt 原因）。
2. **否则补入**（该做没做）：
   - `choice`：优先取 M1 已撤销声明中的 choice（如 10X-B 的 `skip_doublet`——Agent 自己的声明，不伪造）；无声明 → 哨兵 `not_performed`；
   - `provenance.source = "expected"`（新增来源常量，与 M1/M3 区分）；
   - `context`：会话事实（declared + 数据元数据 + M1 声明 context 并集）；
   - verdict：新建 **final** 记录（来源 expected，reason 注明"预期决策缺失补入"）；
   - 之后走正常 run_audit 评分（含 M2.7 missing 强制）。
3. 补入决策**参与评分**（L0 威慑落点）；报告/统计单列 `expected_added` 计数，交叉验证 stats 新增该类别。

### 1.3 生效范围与历史口径

- 生效入口：`CrossValidator.validate(expected_types=...)`（参数已存在，语义扩展）；CLI `cross-validate --expected <yaml>`；新增辅助函数 `load_expected_types()`。
- **历史分数不追溯重判**；新机制从本窗口起生效。
- G/L 窗口真实评测带 expected_types 复跑（如适用）→ 如实呈现（如 L-b 的 qc_filtering"执行了但未捕获"可被补入）。

---

## 2. M2.7 missing 三档强制决策状态语义（提案）

### 2.1 决策状态：新增 `level = -2`（未验证）

| 状态 | level | 语义 | 聚合/reward/检出 |
|---|---|---|---|
| 无法评估 | -1 | 有匹配规则但 choice 未识别（K2），或无规则 | mask（现状） |
| **未验证（新增）** | **-2** | **关键上下文缺失（fail-closed 键缺失且被候选规则引用），评估前提不成立** | 与 -1 同掩码：不进维度分、reward mask、不进检出（检出定义 level∈{0,1} 不变） |

- `LEVEL_LABELS[-2]` = "未验证 — 关键上下文缺失，无法评估（missing 三档强制，M 窗口）"；`LEVEL_TO_SCORE` 不加 -2（不给数值，防误导）。
- 报告/UI：`step_scores[].level=-2` + `explanation` 列出缺失键；`DecisionScore` 加 `missing_keys: list[str]` 字段（兼容：默认空）。
- verdict：-2 不触发 blocked/needs_correction（与 -1 同）；全部决策 -2/-1 的轨迹维持现状聚合（A6 挂账语义不变，本窗口不动）。

### 2.2 强制顺序与触发（A5：先最严档位定决策状态，再规则求值）

对每条决策，按决策类型的 `context_schema` 与**该类型候选规则引用**（required_context ∪ context_constraints 键）解析：

1. **fail-closed**（最严）：缺失键 ∈ 候选规则引用键 → **决策 = 未验证（-2）**，跳过规则求值（含 override）；
2. **skip**：缺失键 ∈ 候选规则引用键 → **跳过依赖该键的规则**（不匹配；`matched_rules_skipped` 溯源，A1 交互规则：最严规则被跳过时等级可能抬高，以 skipped 列表如实呈现）；
3. **fail-open**：视为满足（仅无害键）；
4. **类型强制（A5/A3）**：context 值按 schema type 校验；非法/不可强转 → 该键标 unverified → 按档位处理（枚举外值 → 警告 + 该键 unverified）；
5. **A2 运行时断言**：evaluator 匹配到罚分规则（level_0/1 方法命中）时，校验其引用的键无 fail-open（静态校验器已有，运行时再断言，防未来规则改动绕过）。

### 2.3 影响面（实测，Option B）

- golden **0 差异**（现有上下文均规则充足）→ 本项不触发 C4；
- benchmark 任务 **13 决策**（pca_dimension 缺 n_genes）→ 复跑留档 + 预注册解释。

---

## 3. M2.5 override_n2 键映射修复（提案）

- evaluator `_check_overrides` 不再硬编码 `n_replicates`：解析 `rule.scoring.override_n2.condition`（`"key op value"` 正则，与 rule_registry 约束解析同款）取键名 → 查 `parsed.normalized_context[key]`；
- **n=0 falsy 漏判修复**（fix-tracking A3）：显式 `key in ctx` 判定 + 数值强转比较（`int(ctx[key]) <= 2`），0 正确触发；
- 键缺失 → 不触发（若该键 fail-closed 且被引用，已由 2.2 未验证层拦截）；
- 影响：golden 0 漂移（scRNA n_patients 均 >2；deg/pan n_replicates 行为保持）。

---

## 4. B7/G5 合理省略判定 + 词表条目评级（提案）

### 4.1 合理省略判定入口（B7）

- **判定入口 = expected_types 补入路径（评测配置层）**：optional:true + when_not_applicable 谓词满足 → 豁免（§1.2-1）。谓词事实由评测者声明（declared/评测配置），**引擎层不猜测研究范围**。
- 引擎层对**已声明跳过**决策（choice=no_trajectory 等）：按词表评级；谓词证据存在于上下文（如 `trajectory_focused: false`）且满足时 → 该规则级跳过（K2 同款，决策 -1，不误伤合理省略）；**无证据 → 保守按该做没做评级**。

### 4.2 词表条目评级（提案，文献/规则语义锚定）

| 条目 | 规则 | 评级 | 理由 |
|---|---|---|---|
| `PCA_arbitrary` | D2.1-DIMR-001_reduction | **L1（有风险）** | 任意选维（无 elbow/JackStraw/方差解释依据）与 PCA_fixed_10/15 同原则（D2.1 level_1 note："仅用 10 个 PC 可能捕获不到稀有群体变异"）；主观固定维度无法保证信号捕获，方法学上不构成正确/可接受 |
| `no_trajectory` | T1.1-TRAJ-001_inference | **L0（危险）** | "该做没做"：研究需轨迹推断（谓词不满足/无证据）时跳过 → 结论缺失时间维度证据，与 T1.1 level_0（no_validation/wrong_topology）同档"未验证轨迹语义"；B7 豁免（谓词满足）在 §4.1 判定，不改变词表评级 |

### 4.3 已知连锁（实测预估，实施时如实留档）

- golden：scrna_melanoma_cellvoyager **S7 -1→L1、S11 -1→L0** → C4 基线更新（2 决策 + 轨迹分重算），change_log 逐条归因；
- benchmark：bmd_scrna_007/020 的 S7/S11 由 -1 → L1/L0；S11 gold=correct → 引擎 L0 = **2 FP**（预注册口径解释：引擎无研究范围证据时保守判"该做没做"；与标注"合理省略"判断的分歧如实登记，不追溯改标注）；
- reward：-2 mask 语义纳入 reward-validate。

---

## 5. 待确认决策点（ask_user_question 实际走通）

| # | 决策点 | 提案（Recommended） | 备选 |
|---|---|---|---|
| D1 | expected_types 配置与补入语义 | §1（配置 data/expected_types.yaml；默认清单 11/10；缺失补入 provenance=expected；optional+谓词满足才豁免） | 清单/豁免规则的调整 |
| D2 | missing 强制触发范围 | §2 **Option B（规则引用驱动）**：golden 0 漂移、任务 13 决策 | Option A（schema 全键）：golden 45、任务 197 |
| D3 | 未验证状态表示 | §2.1 **level=-2**（与 -1 区分、同掩码、报告列缺失键） | 复用 -1 + 附加字段 |
| D4 | B7 判定与词表评级 | §4：判定在评测配置层 + 无证据保守评级（PCA_arbitrary→L1、no_trajectory→L0）+ benchmark 差异预注册留档 | 调整评级或豁免策略 |
| D5 | 10X-B 闭环重跑方式 | 复用 windowL 已有 WAL/verdict/notebook 数据 + expected_types 配置重跑采集链路（零新执行成本），不再标注"引擎级补验" | — |
