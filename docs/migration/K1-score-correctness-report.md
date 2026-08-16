# 窗口 K 报告：评分正确性（K1 immune 规则 + K2 未知方法→-1 + K3 ttest 裁决）

> **日期**：2026-08-16（窗口 K）
> **对应验收**：execution-plan-v1 §六.十五（K1–K4，9 项，2026-08-16 冻结）
> **启动消息**：docs/specs/2026-08-16-handoff-design-hub.md §七.K
> **背景**：三个让评分"不完整/不准确"的机制问题——① immune_correlation_method 无 scRNA 规则
> （G 窗口真实评测 20 决策中 12 条全 L-1，最大评分缺口）；② 未知方法兜底 L0（A2，fix-tracking
> 挂最久）；③ ttest 家族词表不一致（J1 遗留观察）。
> **报告**：`bio-audit-v2/docs/migration/K1-score-correctness-report.md`（本文件）

---

## 1. 结论摘要（直给）

| 任务 | 结果 | 关键数字 |
|---|---|---|
| **K1 immune scRNA 规则** | ✅ 落地（文献锚定 + 范式隔离各自锚定） | 新增 `I4.1-IMMU-001_scRNA_correlation_method`；ruleset 1.4.0→**1.5.0**（40 唯一规则）；ontology 0.1.1→**0.1.2**；**G 窗口 12 条 immune L-1 → L1**（细胞级伪重复），CellVoyager **30.0 → 30.0**（分数不变，构成变化，如实呈现） |
| **K2 未知方法 → -1** | ✅ 落地（规则级跳过语义，A2 修复） | 不再兜底 L0；golden C4 漂移 3 决策 L0→-1 + 1 决策 L0→L1 + 3 决策 evidence 语义；benchmark **recall 0.820 不变 / precision 0.7455→0.7736 / F1 0.7810→0.7961**（误报消除，预注册口径解释成立） |
| **K3 ttest 家族裁决** | ✅ 审计中枢确认后落地 | t-test 族与 wilcoxon 族同等待遇（细胞级 = L1）；raw counts 直用保留 L0（独立分布论证）；Kruskal 补 L1；ruleset 1.5.0→**1.6.0** |
| **K4 回归与报告** | ✅ 全闸绿 | pytest **246/246**；三/四/五闸 + validate-ontology + capture-validate PASS；ruff 零新增（40 = 基线）；CI 云上绿；git 已推送 |

**一句话**：最大评分缺口闭合（G 窗口 immune 12 条从"无法评估"变为"有风险"）、评分语义正确化
（不认识 ≠ 错误，不再兜底 L0）、t-test 家族遗留裁决落地（先交审计中枢确认再实施）——
连锁影响全部实测留档：golden 漂移走 C4、benchmark 检出指标如实呈现（recall 不变、误报减少）、
R0 锚定 ρ 不变、黄金对照零影响。

---

## 2. K1 immune_correlation_method 规则（scRNA 范式，最大评分缺口）

### 2.1 文献锚定与词表设计（清单 K1.1）

- 文件：`src/bioaudit/rules/data/scRNA/I4.1-IMMU-001_scRNA_correlation_method.yaml`
- **两个独立风险轴**（范式隔离各自锚定，与 pan I4.1-IMMU-001 不共享评级）：
  1. **方法选择轴**：Pearson 要求双变量正态（免疫评分与基因表达常非正态），Spearman 秩相关
     对单调关系/离群值稳健；
  2. **单位轴**：细胞级相关性检验把细胞当独立观察 = 伪重复，与 G1.1-DEG-001 同原则
     （Squair 2021 PMID 34433851：细胞级检验 FPR 膨胀）→ **L1 有风险**。
- **level 词表**：
  - L3：`Spearman_on_samples` / `Spearman_sample_level` / `Spearman_patient_level` /
    `Kendall_tau_on_samples`（样本/患者级秩相关，正确处理单位）
  - L2：`Pearson_with_normality_test` / `Pearson_after_transformation`（Pearson + 正态性验证）
  - L1：`Spearman` / `Spearman_rank_correlation` / `rank_correlation` / `Kendall_tau` /
    `Spearman_cell_level` / `Kendall_cell_level` / `Pearson_cell_level` / `Pearson_default` /
    `Pearson_no_normality_check`（① 细胞级 = 伪重复 = L1；② scRNA 下 choice 未声明样本单位
    按保守默认细胞级处理——裸 Spearman/Kendall 评 L1；③ Pearson 未检验正态性 = L1）
  - L0：`Pearson_on_clearly_non_normal` / `linear_regression_R2_on_ranks`
- **条件门**：`required_context: {}`——G1.4 先例（M3 签名对 immune_correlation_method 只产出
  choice，无事实 context），以 decision_type 为唯一门 + per-paradigm registry 隔离
  （与 pan I4.1 的 analysis_type 门不冲突）。
- **证据**（evidence 逐条）：Squair 2021 PMID 34433851（L-Confirmed，伪重复原则）、
  Hollander & Wolfe 1999（Spearman 稳健性）、Kowalski 1972 PMID 5043289（Pearson 非正态不可靠）。

### 2.2 本体扩展（清单 K1.2）

- `ontology/decision_types/immune_correlation_method.yaml`：paradigms `[pan-cancer]` →
  **[pan-cancer, scRNA]**
- `ontology/paradigms.yaml` + `ontology/__init__.py`：ontology **0.1.1 → 0.1.2**
- `validate-ontology`：0 错误 / 0 冲突 / 34 类型全覆盖（immune_correlation_method 进入 scRNA
  覆盖矩阵，interpretation 阶段）

### 2.3 ruleset + B5 三闸（K1 阶段）

- `ruleset.json` 重新生成：**1.4.0 → 1.5.0**（45 文件 / 40 唯一规则；清单 1.5.0 备注 K1）
- **B5 三闸实测**：清单 PASS / 冲突 PASS（0）/ golden PASS（**0 差异**——golden 无 scRNA 范式
  immune 决策；pan_correct/pan_error 的 immune 决策由 pan I4.1 覆盖，不受影响）
- 覆盖豁免登记（D5.12）：`I4.1-IMMU-001_scRNA_correlation_method` 在 60 条任务集零触发 →
  `benchmark/coverage.py` `DEFAULT_EXEMPTIONS` 追加（理由：任务集冻结后新增规则；批 3 扩展时
  补覆盖并移除豁免；G 窗口真实评测 12 条 immune 决策已实际覆盖 scRNA 侧）

### 2.4 G 窗口 12 条 immune 重评（清单 K1.2，如实呈现）

**方法（零成本）**：既有 final 轨迹（`final_trajectory_v2.json`，未改动，重评前备份
`final_trajectory_v2_pre_K1.json`，SHA256 58A48116ECE9F519F6A29B9760980F0950AFD459BB8072752578EC49054CEB79）
仅重跑本地审计引擎（脚本 `cellvoyager-outputs/scripts/audit_recheck_K1.py`，输出
`cellvoyager-outputs/reports/windowK1_reeval.json`）。**不重跑 Agent、不手工编轨迹**。

**结果（ruleset 1.5.0 / ontology 0.1.2）**：

| 指标 | G-2 重评（ruleset 1.2.0） | **K1 重评（ruleset 1.5.0）** |
|---|---|---|
| trajectory_score | **30.0** | **30.0（不变）** |
| eval_verdict | needs_correction | needs_correction（不变） |
| L3/L2/L1/L0/-1 | 1/0/7/0/**12** | **1/0/19/0/0** |
| 维度分 | data_handling 0.300 / method_selection 0.575 | data_handling 0.300 / method_selection **0.339** |
| critical_issues | 7 | **19** |

**如实呈现（不夸大）**：
1. **分数不变（30.0 → 30.0）**：最低维主导聚合下 data_handling 0.300 仍是瓶颈维
   （hard_threshold ×4 + LogNormalize ×2 全 L1）——**覆盖缺口闭合 ≠ 分数提升**；
   12 条 immune 从"无法评估"变为"有风险（细胞级伪重复）"，构成如实变化
   （method_selection 维 0.575 → 0.339 反映新增 12 条 L1）。
2. **L1 而非 L3 的归因**：本运行 Spearman 为**细胞级**相关性（Step 4/5：1,787 个肿瘤细胞
   为观察单位）——按 K1 规则细胞级 = 伪重复 = L1（与 G1.1 对细胞级 wilcoxon 同原则）；
   Spearman 本身作为方法选择是对的（L3 通道保留给样本/患者级秩相关）。
3. **K2/K3 对本运行零影响**：20 决策 choice 全部命中词表（无兜底 L0），不涉及 t-test 族——
   K 窗口最终状态（ruleset 1.6.0）下重评数字保持（§6 复核）。
4. **口径同步（site-design §6.2 纪律）**：agent-eval-report-g2.md §8 追加（本报告 §8）；
   README.md 真实效果表 + docs/index.md 数字口径速查 + docs/site-design.md §6.2 口径表
   均新增 K1 重评行（30.0 · L0=0 / L1×19 / L3×1 / L-1×0），禁止与 demo 29 分/G-2 30.0 混写。

---

## 3. K2 未知方法 → -1（A2 修复，评分语义正确化）

### 3.1 语义与实现（清单 K2.3）

- **规则级跳过语义**：`RuleEvaluator._check_level` 对未识别 choice 返回 `None`
  （该规则不适用），不再兜底 L0"危险"；`evaluate()` 汇总——**一条命中 + 一条未识别 →
  取命中评级（不被拉低）**；**全部规则未识别/未匹配 → 决策 -1 无法评估**。
- `matched_rules` 保留全部 condition 命中规则（溯源"被考虑但未适用"）；evidence/alternatives
  仅来自实际评级规则（被跳过规则不再贡献证据——S6 evidence 语义变化即此）。
- `evaluate_all_rules`（冲突检测）跳过未识别规则（该规则无评级可冲突）。
- **-1 决策语义**：不参与聚合（aggregator 已跳过）/ 不参与检出（benchmark 检出定义
  level∈{0,1} 不变，协议预注册口径）/ reward mask（level_reward(-1) → None，F1 定死）。
- **t-test 拼写别名补齐**（B6 归一化语义）：`Student_t_test`/`student's t-test` →
  `ttest_equal_variance`、`Welch's t-test` → `ttest_unequal_variance`——pan_error D3
  （Student_t_test）语义保持 M1.1 L0（词表命中，非兜底），**不列为漂移**。
- **范围声明**：本窗口只做 A2（未知方法→-1）；missing 三档运行时强制（A1-A5 组）不同批，
  不做（B7 跳过可选模块语义仍在排期）。

### 3.2 测试覆盖（清单 K2.4）

新增 `tests/test_k2_minus_one.py`（11 项）：
1. 未识别 choice + 匹配规则 → **-1**（不误判 L0；matched_rules 保留溯源）
2. 未识别 choice 不在检出集合（-1 不参与检出，预注册口径）
3. 多规则混合：命中规则评级不被未识别规则拉低
4. 全部规则未识别 → -1（G1.1+G1.3 双规则场景）
5. 无规则匹配 → -1（既有语义保持）
6. `evaluate_all_rules` 跳过未识别（冲突检测不参与）
7. override_n2（D4）仍生效（n≤2 → L0，即使 choice 未识别）
8. t-test 拼写别名（Student_t_test → M1.1 L0 语义保持）
9. 归一化映射断言
10-11. golden 兜底决策 K2 现状端到端（S7/S11 → -1，S10 ∈ {-1, L1}，词表内 L0 不误伤）

同步更新：`test_api_contract.py`（scRNA 裸 DESeq2 由 L0 → -1，paradigm 消歧语义保持）、
`test_engine.py`（规则计数 39→40，docstring 更新）。

### 3.3 golden 漂移 C4 记录（清单 K2.4，逐条不静默）

**漂移全貌（基线 1.4.0 → 最终 1.6.0，7 处 diff，2 条轨迹）**：

| # | 轨迹 | 决策 | 变化 | 归因 |
|---|---|---|---|---|
| 1 | scrna_melanoma_cellvoyager | S7 dim_reduction `PCA_arbitrary` | **L0 → -1** | K2：D2.1 词表无此条目（任意维度不构成词表内判定）→ 无法评估，不再兜底 L0 |
| 2 | scrna_melanoma_cellvoyager | S11 trajectory_inference `no_trajectory` | **L0 → -1** | K2：T1.1 词表无此条目 → 无法评估（"跳过可选模块"合理省略 vs 该做没做归 missing 三档批次，B7 排期） |
| 3 | scrna_melanoma_cellvoyager | S10 deg_method `Kruskal_Wallis_cell_level` | **L0 → L1** | K3：词表补齐（秩检验细胞级 = 伪重复 = L1，与 wilcoxon 族同原则，审计中枢确认） |
| 4-6 | scrna_melanoma_cellvoyager / scrna_crc_error / scrna_error | S6 batch_correction `no_integration` | evidence_citations 语义 | K2：B1.2-BATC-002 规则级跳过（词表未含 no_integration），不再贡献证据；B1.1 评级 L0 不变 |
| 7 | scrna_melanoma_cellvoyager | dimension_scores | method_selection 0.4071 → **0.63** | K2+K3 组合（S7/S11 排除、S10 L1） |

**不变项（如实声明）**：trajectory_score 29.0 / verdict blocked（S3/S6 词表内 L0 仍主导）；
pan_error D3（Student_t_test）保持 L0（别名归一 → M1.1 t-test 家族词表，非兜底）；
其余 19 条轨迹 0 变化。

**C4 执行**：双副本基线同步更新（`tests/golden/golden_expected_output_after.json` +
`docs/specs/2026-08-13-golden-baseline/golden_expected_output_after.json`，逐字节一致，
SHA256 **4c4d1b3d72d8373c46380e85fc8b7344e1d3181e3335294ef157497a15cd6abb**）；
`asset_manifest.json` change_log **+8 条**（K1 新规则 / K3 G1.1 / K3 G1.3 / golden 基线 /
validation_dataset / full_audit_results / scrna_r0 / ai_error_patterns，均附原因）。

### 3.4 benchmark 连锁（清单 K2.5，60 任务集复跑，如实留档）

**预注册口径解释**：检出定义 = level ∈ {0,1} **不变**；K2 使部分"靠兜底 L0 检出"的决策变
-1 → 属**评分语义正确化**（不认识的词表外 choice 不再冒充"危险"），非检出能力退化。

| 指标 | 基线 1.4.0（HEAD 实测复跑） | **1.6.0（K 后）** | 变化 |
|---|---|---|---|
| mean_score | 0.5542 [0.4837, 0.6232] | **0.5542** [0.4837, 0.6232] | 不变 |
| precision | 0.7455 | **0.7736** | **+0.028** |
| recall | 0.820 | **0.820** | **不变**（预期"或下降"未发生：无 gold=error 决策依赖兜底） |
| F1 | 0.7810 | **0.7961** | +0.015 |
| edge_detection_rate | 0.6667（64/96） | **0.6458**（62/96） | −0.021（语义正确化代价，见下） |
| gap（public − hidden） | +0.048（区间内） | **+0.048**（区间内，无告警） | 不变 |

**受影响任务（2 个，逐条归因）**：`bmd_scrna_007` / `bmd_scrna_020`（gold 标注：
S7=edge、S10=edge、S11=correct）——
- S11 `no_trajectory`（gold=correct）：兜底 L0（FP 误报）→ -1（TN）→ **precision 上升
  （减少 2 个误报）**——"跳过轨迹推断"在该任务被标注为合法省略，K2 不再误报为危险；
- S7 `PCA_arbitrary`（gold=edge）：L0（检出）→ -1（未检出）→ edge 检出率下降
  （词表缺口如实呈现为无法评估，而非硬检出）；
- S10 `Kruskal_Wallis_cell_level`（gold=edge）：L0 → L1（仍检出，edge 计数不变）；
- 轨迹分 29.0 / verdict blocked 均不变。
- **无 gold=error 决策受 K2 影响** → recall 0.820 不变（预注册口径的最强实证：
  检出集合零损失）。

### 3.5 reward 连锁（清单 K2.5，五闸复跑）

`reward-validate` 五闸全 PASS（mapping / determinism / spike-in / ablation / calibration /
golden）。校准证据（60 任务，B=2000，seed=42）：

| 项 | 基线 1.4.0（J 窗口） | **1.6.0（K 后）** |
|---|---|---|
| 排序一致性 ρ | 0.6008 [0.3818, 0.7708] | **0.61** [0.392, 0.7768] |
| Kendall τ_b | 0.4884 | **0.4953** [0.3128, 0.6582] |
| 分层均值差（good − bad） | +0.3434 [0.2091, 0.4601] p=0.000 | **+0.3435** [0.21, 0.4592] **p=0.000 显著保持** |

- 变化来源：bmd_scrna_007/020 的 S7/S11 由 L0（reward 0.0）→ -1（mask，None）——-1 mask
  语义（F1）生效：不注入虚假信号；S10 L0→L1（0.0→0.3）。
- 分离结论（good/bad 显著分离）稳健保持——如实报告为证据（拍板 #2：不做点估计门槛）。

---

## 4. K3 ttest 家族词表裁决（J 登记遗留）

### 4.1 查证（清单 K3.6，落地前完成）

| 论证 | 结论 |
|---|---|
| 伪重复（Squair 2021 PMID 34433851） | 对 t-test 族与 wilcoxon 族**同等成立**（细胞级检验 FPR 膨胀主因）→ 同等待遇基础 |
| 正态性/零膨胀独立论证 | **不构成独立于伪重复的决定性论证**：Svensson 2020 PMID 31937974（液滴 scRNA 并非零膨胀，传统"零膨胀"论点弱化）；CLT 提供中等样本量稳健性；Soneson & Robinson 2018（Nat Methods, doi 10.1038/nmeth.4612）显示 t 与秩和族细胞级 FPR 问题同源 |
| raw counts 直用独立论证 | **成立**：counts 为离散、非负、均值-方差相关数据，t-test 连续正态假设在任何单位（含样本级）下都不成立；标准做法为 log/CPM 变换或负二项模型——独立于伪重复的分布违背 |

### 4.2 方案提交与审计中枢确认（清单 K3.6，吸取 J1 流程教训）

方案经 **ask_user_question 实际走确认流程**（2026-08-16，审计中枢在线确认，非自拟自批）：
**批准方案（含 Kruskal 附加项）**——① t-test 族与 wilcoxon 族同等待遇（归一化后数据细胞级
= L1）；② raw counts 直用保留 L0；③ Kruskal_Wallis_cell_level 补 L1（wilcoxon 族同原则
直接延伸，修复 demo/任务轨迹 S10 兜底）。

### 4.3 落地（清单 K3.7）

- `G1.1-DEG-001_pseudobulk.yaml`：`ttest_equal_variance`/`ttest_on_cells` **L0 → L1**；
  补 `ttest_on_normalized`/`Kruskal_Wallis_cell_level` → L1；L0 补
  `ttest_on_raw_counts`/`anova_on_cells`（独立分布违背，note 注明 K3 裁决出处）
- `G1.3-DEG-003_method.yaml`：双向补齐 `ttest_equal_variance`/`ttest_on_cells`/
  `Kruskal_Wallis_cell_level` → L1；`ttest_on_raw_counts`/`anova_on_cells` 保留 L0
- 结果：**t-test 家族 5 词条两规则全对齐**（ttest_on_normalized/ttest_equal_variance/
  ttest_on_cells = L1；ttest_on_raw_counts/anova_on_cells = L0），Kruskal 双规则 L1
- ruleset **1.5.0 → 1.6.0** + B5 三闸（清单 PASS / 冲突 PASS / golden 按 C4 记录，§3.3）
- **连锁零影响确认**：60 任务集无 ttest 族 choice（预扫描 + 复跑实证）；I 窗口黄金对照
  三版无 ttest/Kruskal/immune 决策 → 80.0/69.0/66.7 不变（§6 实测复核）

---

## 5. 连锁影响汇总（全部实测留档）

| 资产 | 变化 | 状态 |
|---|---|---|
| golden 基线（双副本） | C4 更新（§3.3，SHA256 4c4d1b3d…） | 0 差异复验 |
| validation_dataset.jsonl | 137 行重生成（S7/S11 → -1、S10 → L1，3 行变化） | 与 golden 一致 |
| full_audit_results.json | cellvoyager danger 5→2 / risk 3→4 / unevaluable 0→2、avg_score 35.8→46.0（-1 不参与）；deg_method danger 3→2 / risk 2→3；level_dist 增 unevaluable 桶 | 重生成 |
| scrna_r0.json | 确定性重生成（ruleset 1.6.0 / 24 规则）：combo_4 S10 ttest_on_cells L0→L1 → audit 52.1→54.6；**Spearman ρ=0.9747 / τ_b=0.9487 / 单调性 / PASS 不变**；meta 更新（含 K3 变化注记） | CI 锚定一致 |
| ai_error_patterns.md | §2.1 level 分布（L0 26→23、L1 21→22、L-1 0→2）、§3.1 deg_method 行、§7.4 CellVoyager 表（K 口径 + 明细更新） | 同步 |
| asset_manifest.json | change_log +8 条 | 留痕 |
| I 窗口黄金对照 A/B/C | **80.0 / 69.0 / 66.7 不变**（K 规则下实测复核，§6） | 零影响 |
| 覆盖豁免 | +I4.1 scRNA（D5.12，理由附注） | benchmark-validate PASS |

---

## 6. K 最终状态复核（ruleset 1.6.0 / ontology 0.1.2 / engine 0.2.1）

- **CellVoyager G 窗口重评**（final_trajectory_v2.json，未改动）：30.0 · needs_correction ·
  L0=0 / L1×19 / L3×1 / L-1×0（与 K1 阶段一致——K2/K3 对本轨迹零影响）
- **demo 轨迹**（scrna_melanoma_cellvoyager）：29.0 · blocked（S3/S6 L0、S10 L1、S7/S11 -1）
- **I 窗口黄金对照**：A 80.0 pass / B 69.0 needs_correction / C 66.7 needs_correction
- **R0 锚定**：ρ=0.9747（combo_4 评分变化后排序不变）
- **benchmark 60 任务**：mean 0.5542 / recall 0.820 / precision 0.7736 / F1 0.7961 / gap +0.048
- **reward**：ρ 0.61 / τ_b 0.4953 / 分层差 +0.3435（p=0.000）

---

## 7. 门禁矩阵（K 窗口最终状态）

| 闸 | 结果 |
|---|---|
| pytest 全量 | **246/246**（235 基线 + 11 新增 K2 测试；含规则计数 40/45、覆盖豁免、ontology 0.1.2 断言更新） |
| ruleset-validate 三闸 | manifest PASS（1.6.0）/ conflicts PASS（0）/ golden PASS（0 差异） |
| validate-ontology | 0 错误 / 0 冲突 / 34 类型全覆盖（immune_correlation_method scRNA 已覆盖） |
| benchmark-validate 四闸 | taskset / contamination / coverage（含 I4.1 豁免）/ golden 全 PASS |
| reward-validate 五闸 | mapping / determinism / spike-in / ablation / calibration 全 PASS + golden PASS |
| capture-validate | PASS（0 错误 0 警告，34 类型 / 23 有签名） |
| ruff | **40 = HEAD 基线 40，零新增**（新代码零错误；ontology/__init__.py E501 已修） |
| R0 锚定（scrna_r0） | 确定性重生成与打包文件逐字节一致（脚本 meta 同步） |
| **CI 云上**（教训 #5） | GitHub Actions 双矩阵（3.10/3.12）**全绿**（见完成报告） |
| git（教训 #4） | commit + push 完成（见完成报告） |

---

## 8. 产物清单与文档同步

| 产物 | 路径 |
|---|---|
| 本报告 | `bio-audit-v2/docs/migration/K1-score-correctness-report.md` |
| 新规则（K1） | `src/bioaudit/rules/data/scRNA/I4.1-IMMU-001_scRNA_correlation_method.yaml` |
| 规则修订（K3） | `src/bioaudit/rules/data/scRNA/{G1.1-DEG-001_pseudobulk,G1.3-DEG-003_method}.yaml` |
| 引擎修订（K2） | `src/bioaudit/engine/evaluator.py`（规则级跳过 + t-test 拼写别名） |
| ruleset | `src/bioaudit/rules/ruleset.json`（**1.6.0**，45 文件 / 40 唯一规则） |
| 本体 | `ontology/decision_types/immune_correlation_method.yaml` + `paradigms.yaml` + `__init__.py`（**0.1.2**） |
| K2 测试 | `tests/test_k2_minus_one.py`（11 项）+ test_api_contract/test_engine 更新 |
| 覆盖豁免 | `src/bioaudit/benchmark/coverage.py`（DEFAULT_EXEMPTIONS + I4.1 scRNA） |
| golden 基线（双副本） | `tests/golden/golden_expected_output_after.json` + `docs/specs/2026-08-13-golden-baseline/golden_expected_output_after.json` |
| 验证数据 | `src/bioaudit/data/validation/{validation_dataset.jsonl, full_audit_results.json, scrna_r0.json}` |
| 报告数据 | `src/bioaudit/data/report/ai_error_patterns.md`（§2.1/§3.1/§7.4 同步） |
| 资产清单 | `docs/specs/2026-08-13-golden-baseline/asset_manifest.json`（change_log +8 条） |
| G 窗口重评追加 | `bio-audit-v2/docs/migration/agent-eval-report-g2.md`（§8 追加） |
| 口径同步 | `README.md` / `docs/index.md` / `docs/site-design.md`（§6.2 口径表 + K1 重评行） |
| 追踪表 | `docs/specs/2026-08-14-fix-tracking.md`（A2 收尾 + K 更新记录） |
| execution-plan | `docs/specs/2026-08-13-execution-plan-v1.md` §六.十五 打勾（9/9） |
| CHANGELOG | `CHANGELOG.md` Unreleased 条目（K 窗口变更） |
| 重评脚本/结果 | `cellvoyager-outputs/scripts/audit_recheck_K1.py` + `reports/windowK1_reeval.json`（仓库外） |

---

## 9. 诚实局限与遗留

1. **词表缺口如实登记为 -1**（K2 语义的直接后果）：`PCA_arbitrary`（D2.1）、
   `no_trajectory`（T1.1）不在词表 → 无法评估；`Kruskal_Wallis_cell_level` 已由 K3 补齐为
   L1。**遗留候选**：D2.1 补"任意维度"条目、T1.1 补"未做轨迹推断"条目（后者与 B7
   "跳过可选模块"裁决联动，随 missing 三档批次 A1-A5 处理，本窗口不做）。
2. **scRNA 裸 DESeq2 词表缺口**：G1.1/G1.3 仅收 `pseudobulk_DESeq2` 形式，裸 DESeq2 →
   -1（K2 语义）；语义上细胞级 DESeq2 = 伪重复 = L1 候选，登记为词表扩展候选
   （批 3 任务集扩展时一并处理）。
3. **override_n2 键映射遗留**：evaluator D4 override 硬编码检查 `n_replicates`，而
   G1.1 override 条件文本为 `n_patients <= 2`——scRNA 范式 n_patients≤2 不会触发 override
   （K 前既有状态，K 未改语义，仅测试注明）。登记为引擎层遗留（随 A1-A5 语义强制批次处理）。
4. **scrna_r0 audit_min/max 范围陈旧**：`generate_scrna_r0.py` COMBOS 的预期范围
   （combo_2 40-70 / combo_3 20-50 / combo_4 0-25）与 D5 修复+J/K 时代评分不符
   （`all_in_expected_range: False`）——**J2 时代既有状态，K 未恶化**；登记清理候选。
5. **n=1 数据与确定性脚本定位**：G 窗口重评仍为单数据集（GSE115978）；黄金对照为确定性
   脚本（非 LLM）——排期不变（批 3 语料、多数据集多 Agent 评测）。
6. **K1 规则的单位轴依赖上下文/词表声明**：M3 签名当前只产出 `Spearman`（未区分单位），
   样本级使用需显式 choice 后缀或 unit 上下文——签名表扩展登记为采集层候选。
7. **benchmark edge 检出率 -0.021**：S7（gold=edge，词表外）不再硬检出——语义正确化代价，
   预注册口径下如实呈现（检出定义不变，无 gold=error 损失）。

---

## 10. 验收清单对照（execution-plan §六.十五，9 项全勾）

| # | 清单项 | 状态 |
|---|---|---|
| K1.1 | 文献锚定设计 scRNA 版免疫相关性检验规则（level 词表 + 细胞级伪重复语义 + 证据） | ✅ §2.1 |
| K1.2 | 本体 paradigms 扩 [pan-cancer, scRNA]（semver 0.1.2）+ G 窗口 12 条重评（L-1→L1）+ CellVoyager 30.0→30.0 如实呈现 + g2 追加 + README/首页/站点口径同步 | ✅ §2.2/§2.4/§8 |
| K2.3 | evaluator 未识别 choice 规则级跳过；全部未识别/未匹配 → -1；不再兜底 L0；检出定义不变；A2 与 missing 三档不同批 | ✅ §3.1 |
| K2.4 | 测试（未识别→-1 不误判 L0；混合取 L1 不被拉低）；golden 漂移 C4 逐条记录 | ✅ §3.2/§3.3 |
| K2.5 | benchmark 60 任务复跑如实留档 + 预注册口径解释；reward-validate 五闸复跑（-1 mask） | ✅ §3.4/§3.5 |
| K3.6 | 预置裁决原则查证；方案**先交审计中枢确认再落地**（实际走确认） | ✅ §4.1/§4.2 |
| K3.7 | G1.1/G1.3 词表双向补齐 + ruleset semver（1.6.0）+ B5 三闸 + golden C4 | ✅ §4.3/§3.3 |
| K4.8 | golden 0 差异（C4 后）+ pytest 全量绿 + 三/四/五闸 + validate-ontology + CI 双矩阵云上绿 + git commit/push | ✅ §7 |
| K4.9 | 报告落盘（本文件）+ execution-plan §六.十五 打勾 | ✅ 本文件 |

---

*报告完毕。execution-plan §六.十五 9 项打勾；git commit/push 与 CI 云上确认见完成报告。*
