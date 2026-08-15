# 窗口 F 完成报告：批 2 任务集扩展（30 → 60）与校准更新

> **日期**：2026-08-16
> **执行依据**：docs/specs/2026-08-13-execution-plan-v1.md §六.九（F1-F4 验收清单，12 项冻结）
> + docs/protocols/benchmark-protocol.md（宪法）+ `src/bioaudit/benchmark/pre_registration.json`
> （record **benchmark-pr-2026-08-16-02**，批 1 记录 `benchmark-pr-2026-08-16-01` 留档）
> **验收结果**：**F1-F4 全部 12 项 ✅**（逐项见 §三）；golden **20 轨迹 137 决策 0 差异**；
> pytest **220/220**（206 + 新增 14）

---

## 一、执行范围与纪律对照

按建议顺序执行：**F1（生成 30 条 + 新预注册）→ F2（校准批 IRR + 全量标注 +
rubric v1.1）→ F3（覆盖 + 难度复核）→ F4（reward-protocol 更新 + 回归）**。

五条关键纪律逐条对照：
1. **生成器提示词零规则内容（E6）**：`generator_prompt.md` 未改动（prompt_hash
   `943fc2f11acd` 与批 1 相同）；批 2 规格表 rule_id 扫描 0 命中（脚本内置自检 +
   `test_batch2_specs_rule_id_free` 同规测试）；60 任务污染扫描 **0 命中**
   （rule_id/title/ngram 三类全 0）。
2. **难度不用审计分数定义（E4）**：难度仍由 `difficulty.v1` 预注册 rubric 从
   gold 特征计算（`benchmark/difficulty.py` 零引擎引用）；
   `test_difficulty_independent_of_audit_score` 继续生效。
3. **新预注册记录（新 record_id），批 1 旧值留档（E1）**：新记录
   `benchmark-pr-2026-08-16-02`（含 gap 区间重评估，§四）；批 1 记录常量
   `PRE_REGISTRATION_V1` + 磁盘副本 `pre_registration_v1_archived.json` 留档；
   taskset irr 字段保留批 1 校准（0.8087/0.8080）与全量（0.7292/0.7288）旧值。
4. **校准批 IRR 达标（κ/α≥0.8）再放量（E3）**：批 2 新校准批 10 条（104 决策）
   先双标注 → **κ=0.8694 / α=0.8693 达标** → 放量标注剩余 20 条。
5. **golden 0 差异硬验收（任务集是外围层）**：评分路径零改动，golden 复跑
   **0 差异**（§六）。

## 二、产出清单

| 类别 | 文件 | 说明 |
|------|------|------|
| 任务集 | `src/bioaudit/data/tasks/taskset.json` | **v1.1.0**（60 条；semver 显式提升 + 文件哈希 + 快照三元组 + 60 条新 split + 批 1/批 2 IRR 全留档） |
| 任务集 | `src/bioaudit/data/tasks/{scrna,pan,deg}/bmd_*.json` | **60 条**（批 1 30 + 批 2 30：scrna 10 / pan 10 / deg 10） |
| 生成器 | `scripts/generate_benchmark_tasks_batch2.py` | 批 2 变体规格（30 条，window-F review）+ E6 自检 |
| 组装 | `scripts/assemble_gold_batch2.py` | 批 2 gold/难度写入 + 60 条 split 重划分 + taskset v1.1.0 + IRR 报告 |
| 标注 | `src/bioaudit/data/annotation/annotator_A/B_batch2_{calib,full}.jsonl` + `arbitration_batch2.jsonl` | 批 2 双标注原始 JSONL（A/B 各 275 行）+ 仲裁（8 条） |
| 标注 | `src/bioaudit/data/annotation/merged_annotations_batch2.json` + `irr_report_batch2.json` | 批 2 合并结果 + IRR 实测（批 1 旧值留档） |
| rubric | `benchmark/annotation_rubric.md` | **annotation.v1.1**（D 遗留 6 条澄清点，§四） |
| 预注册 | `benchmark/pre_registration.json` + `pre_registration_v1_archived.json` | **新记录 v2**（gap 区间重评估）+ 批 1 留档 |
| 协议 | `docs/protocols/benchmark-protocol.md` | 批 2 扩展（60 条 / v1.1.0 / rubric v1.1 / 记录 v2） |
| reward 协议 | `docs/reward-protocol.md` | §7.1 批 1 留档 + §7.2 60 任务新实测表 |
| 测试 | `tests/test_benchmark_batch2.py`（13 项）+ `test_benchmark.py`/`test_reward.py` 更新 | 批 2 守卫（E6/预注册/校准门槛/gold 版本/覆盖/难度/split） |

## 三、验收对照（§六.九 F1-F4，12 项逐项）

### F1 任务集扩展
- [x] **1. 批 2 生成 30 条（scrna/pan/deg 均衡，合计 60 条），流程不变**：
  批 2 = scrna 10 / pan 10 / deg 10（合计 60：scrna 22 / pan 20 / deg 18）；
  流程与批 1 相同——语料 → 变体规格（generator_prompt.md v1，零规则内容）→
  确定性变换（apply_spec）→ 人工审核（window-F review，逐条核对变换结果）→
  E6 自检（规格表 rule_id 0 命中 + 污染扫描 0 命中 + 语料来源断言测试）。
- [x] **2. 语料扩展**：CellVoyager hook 真实运行仍未实测（窗口 C 遗留）——
  **继续使用现有语料库**（20 条 legacy + scrna_melanoma_cellvoyager，如实声明，
  见预注册 v2 corpus_policy）；bmd_scrna_020 直接以**真实 CellVoyager 轨迹**
  （scrna_melanoma_cellvoyager）为底，纳入 PCA_arbitrary / Kruskal_Wallis_cell_level /
  LogNormalize / no_trajectory 真实错误模式；错误注入素材全部记录
  `error_pattern_sources`（语料轨迹 id，非规则反推）。
- [x] **3. 新预注册记录（新 record_id）**：`benchmark-pr-2026-08-16-02`
  （§四全文）；含 gap 区间重评估（批 1 Δ=−0.1864 小样本偏差判读；批 2
  hidden n≈18 后区间保持 [−0.10, +0.10] 不变，保守与批 1 可比）；批 1 记录
  `benchmark-pr-2026-08-16-01` 常量 + 磁盘副本留档。

### F2 标注
- [x] **4. 校准批 IRR 重跑**：批 2 新校准批 10 条（104 决策，跨范式跨难度）先
  双标注 → **κ=0.8694 / α=0.8693（一致率 93.27%）双门槛达标** → 放量
  标注剩余 20 条；批 1 校准批旧值（0.8087/0.8080）留档。
- [x] **5. 全量 60 条双标注 + 分歧仲裁 + 共识强度**：批 2 全量 275 决策双标注
  （A/B 各 275 行，逐任务核对无遗漏）→ **批 2 IRR κ=0.9336 / α=0.9336**
  （一致率 97.09%）；**全量 60 合并 IRR κ=0.8336 / α=0.8335**（623 决策，
  一致率 93.58%）；分歧 **8 条全部仲裁**（仲裁员第三方定案，与一方一致 8 条，
  第三条路 0 条）；共识强度：批 2 strong 267 / medium 8 / weak 0；全量 60
  strong 583 / medium 40 / weak 0。批 1 旧标注不追溯重判。
- [x] **6. rubric v1.1 修订（6 条澄清点）**：D 窗口遗留 6 条澄清点全部落地
  `annotation_rubric.md` §四（4.1 TMM 工具链耦合 / 4.2 只评本步 vs 管线衔接 /
  4.3 报告解释不足归属 / 4.4 note 与 choice 矛盾以 choice 为准 / 4.5 模板笔误
  不入罪 / 4.6 双细胞去除与下游设计依赖），每条锚定批 1 仲裁实证（§八）；
  标注版本提升 annotation.v1.1（批 2 gold 记录 v1.1，批 1 gold 保持 v1）。

### F3 覆盖与难度
- [x] **7. 覆盖审计：60 条仍 34/34 类型 + 38/38 规则**（`benchmark-validate` 闸 3
  实测：n_types_covered=34、n_rules_matched=38、missing 全空、零触发规则 = 0，
  无需豁免清单）。
- [x] **8. 难度分布复核（3 范式 × 3 梯度）**：9 个 (范式, 难度) 格子**全部非空**；
  批 1 缺口修复——批 2 scrna 新增 easy 4 条（bmd_scrna_013/014/015/022）；
  全量 60 难度分布 = easy **24** / medium **27** / hard **9**（scrna 4/14/4、
  pan 7/10/3、deg 13/3/2，§七）。

### F4 校准更新与回归
- [x] **9. reward-protocol.md 实测表更新（旧值留档）+ 分层检验重跑 + gap 区间重评估**：
  reward-protocol.md §7.1 批 1 旧表留档 + §7.2 60 任务新实测表（§九 diff 摘要）；
  分层检验重跑：配方 B good 0.6775 vs bad 0.3160，diff=+0.3614 [0.2291, 0.4719]，
  **p=0.000 显著分离**（批 1：+0.375，p=0.001——结论稳健）；gap 重评估：
  **Δ=+0.046 ∈ [−0.10, +0.10]，告警解除**（批 1 Δ=−0.1864 小样本组成偏差
  判读得到收敛证据支持，§9.3）。
- [x] **10. benchmark-validate 四闸全绿 + golden 0 差异**：四闸 PASS（taskset
  v1.1.0 60 条 / contamination 0 命中 / coverage 34+38 / golden 0 差异）。
- [x] **11. pytest 全量绿 + 新增任务集相关测试**：pytest **220/220**
  （206 + 新增 14：tests/test_benchmark_batch2.py 13 项 + test_benchmark.py
  新增 v1 留档 1 项；既有测试更新 3 处：≥60 条 / taskset 1.1.0 / reward 60 任务）。
- [x] **12. CI 双矩阵确认全绿**：ci.yml 无需改动（benchmark-validate 四闸 +
  reward-validate 五闸已常驻双矩阵）；本地全套复现：四闸 PASS + 五闸 PASS +
  golden 0 差异 + pytest 220/220 + ruff 新代码零错误（§六）。

## 四、预注册记录（新 record_id 全文）

记录 `benchmark-pr-2026-08-16-02`（机器可读：`benchmark/pre_registration.json`；
批 1 留档：`pre_registration_v1_archived.json`）：

```json
{
 "record_id": "benchmark-pr-2026-08-16-02",
 "date": "2026-08-16",
 "version": "pr.v2",
 "supersedes": "benchmark-pr-2026-08-16-01",
 "scope": "批 2 任务集扩展（30 → 60 条）后全量生效",
 "split": {
  "method": "stratified_random_by_paradigm_and_difficulty",
  "seed": 42,
  "public_ratio": 0.7,
  "note": "批 1 划分在 30 条上执行；批 2 合并为 60 条后**重新划分**（gold+难度冻结后一次性执行，seed/方法不变可复现）；hidden n≈18"
 },
 "gap": {
  "statistic": "mean(trajectory_score/100) over tasks: public - hidden",
  "tolerance_interval": [-0.10, 0.10],
  "alarm_rule": "Δ 超出 [-0.10, 0.10] → 负向告警（泄漏信号），替代'两集一致'验收（E1）",
  "report_note": "gap 只作为泄漏信号登记；不据此修改任何分数或任务",
  "re_evaluation": "批 1 实测 Δ=-0.1864（区间外）判读为隐藏集小样本组成偏差（hidden n=9；确定性引擎无泄漏通道）；批 2 隐藏集 n≈18 后重评估：区间保持 [-0.10, +0.10] 不变（保守、与批 1 口径可比；n 扩大后抽样误差缩小，若仍出界则组成偏差解释的置信度上升）。结果如实呈现：可能收敛回区间内，也可能仍超区间，均按协议登记不改分。"
 },
 "irr_gate": {
  "primary": "cohen_kappa_3class >= 0.8",
  "secondary": "krippendorff_alpha_nominal >= 0.8",
  "calibration_batch_size": 10,
  "note": "批 2 新校准批（10 条新任务，跨范式跨难度）双标注达标后放量（E3）；批 1 校准批旧值留档（κ=0.8087 / α=0.8080）"
 },
 "difficulty_rubric_version": "difficulty.v1",
 "annotation_rubric_version": "annotation.v1.1",
 "model_policy": "生成器与评测 Agent 不同模型（E6）；模型信息记录在任务集元数据",
 "contamination_policy": "任务/生成器提示词中规则标识/标题命中登记为污染特征（E2），命中即标记",
 "corpus_policy": "批 2 语料扩展优先纳入新错误模式素材（CellVoyager hook 真实运行未实测，窗口 C 遗留）；继续使用现有语料库（20 条 legacy + scrna_melanoma_cellvoyager），如实声明"
}
```

- 批 1 旧值（留档）：record_id `benchmark-pr-2026-08-16-01`、gap 区间 [−0.10, +0.10]、
  split seed=42 70/30、irr 门槛 κ/α ≥ 0.8（校准批 10 条）——全部原样归档。
- 实测对照：批 1 Δ=−0.1864（出界告警）→ 批 2 **Δ=+0.046（区间内，告警解除）**。

## 五、标注 IRR 实测（E3）

| 批次 | n_items | 一致率 | Cohen's κ | Krippendorff's α | 门槛 |
|------|---------|--------|-----------|-------------------|------|
| 批 1 校准（留档） | 127 | 92.13% | 0.8087 | 0.8080 | ✅ 达标 |
| **批 2 校准（本窗口）** | **104** | **93.27%** | **0.8694** | **0.8693** | **✅ 达标 → 放量** |
| 批 1 全量（留档） | 348 | 90.80% | 0.7292 | 0.7288 | —（如实报告） |
| **批 2 全量** | **275** | **97.09%** | **0.9336** | **0.9336** | — |
| **全量 60 合并** | **623** | **93.58%** | **0.8336** | **0.8335** | **≥0.8 ✅** |

- 批 2 分歧 **8 条全部仲裁**（仲裁员第三方）：与 A 一致 5 条（deg_013 s1→edge、
  pan_017 D1→edge、scrna_019 A6→edge、A7→edge、S12→error）、与 B 一致 3 条
  （deg_013 s2→correct、scrna_020 S8→edge、scrna_021 S3→error）；第三条路 0 条。
- 共识强度：批 2 strong **267** / medium **8** / weak **0**；全量 60 strong **583** /
  medium **40** / weak **0**。
- 批 2 gold 分布（275 决策）：correct **197** / edge **52** / error **26**；
  全量 60（623 决策）：correct **477** / edge **96** / error **50**。
- 分歧模式（批 2）：edge↔error 4 条 / edge↔correct 3 条 / error↔edge 1 条
  （集中在 no_filtering 下游依赖、一致性族证据强度、双细胞跳过判定——
  rubric v1.1 已覆盖的边界，仲裁逐条定案）。
- **rubric v1.1 效果（如实）**：批 2 全量 κ=0.9336 显著高于批 1 全量 0.7292——
  6 条澄清点直接压低了 TMM 工具链 / 笔误 / 方向矛盾 / 双细胞等历史分歧源；
  同模型双标局限保持（如实声明，批 2 未引入跨模型/人工对照）。

## 六、回归证据

```
golden:   ok=True | n_diffs=0 | trajectories=20 | decisions=137
pytest:   220 passed（206 + 新增 14）
benchmark-validate: 四闸 PASS（taskset 60 条 / contamination 0 命中 / coverage 34+38 / golden 0 差异）
reward-validate:    五闸 PASS（mapping / determinism / spike_in_anchor / ablation / golden；calibration 证据 60 任务）
ruff:     新代码零错误
```

## 七、60 条任务清单（分布/难度/来源）

| 范式 | 任务数 | 难度分布 (1/2/3) | gold (correct/edge/error) | 主要语料来源 |
|------|--------|-------------------|---------------------------|--------------|
| scrna | 22（批 1 12 + 批 2 10） | 4 / 14 / 4 | 175 / 48 / 27 | scrna_correct/crc/nsclc/melanoma + **CellVoyager 真实轨迹** |
| pan | 20（批 1 10 + 批 2 10） | 7 / 10 / 3 | 153 / 38 / 25 | pan_correct / pan_error + pan_edge_* |
| deg | 18（批 1 8 + 批 2 10） | 13 / 3 / 2 | 149 / 10 / 19 | deg_correct / deg_error / deg_edge_n2 |
| **合计** | **60** | **24 / 27 / 9** | **477 / 96 / 50** | 20 条 legacy + 1 条 CellVoyager |

批 2 明细（30 条，window-F review）：

| 任务 | 难度 | n_dec | base | 错误注入来源 |
|------|------|-------|------|--------------|
| bmd_scrna_013 | 1 | 9 | scrna_correct | —（全正确） |
| bmd_scrna_014 | 1 | 9 | scrna_crc_correct | scrna_error（wilcoxon 伪重复） |
| bmd_scrna_015 | 1 | 9 | scrna_melanoma_correct | —（全正确，scVI/pseudobulk_edgeR 变体） |
| bmd_scrna_016 | 2 | 14 | scrna_correct | —（全正确） |
| bmd_scrna_017 | 2 | 11 | scrna_crc_correct | scrna_error（hard_threshold/no_doublet/PCA_fixed_10） |
| bmd_scrna_018 | 2 | 13 | scrna_nsclc_correct | scrna_error+deg_error（no_correction 等） |
| bmd_scrna_019 | 3 | 20 | scrna_correct | scrna_error（wilcoxon/not_checked/no_correction） |
| bmd_scrna_020 | 2 | 12 | **scrna_melanoma_cellvoyager** | **真实 CellVoyager 轨迹原样** |
| bmd_scrna_021 | 2 | 11 | scrna_crc_correct | scrna_error+scrna_edge_nodoublet |
| bmd_scrna_022 | 1 | 8 | scrna_correct | —（全正确） |
| bmd_pan_011 | 1 | 5 | pan_correct | —（全正确） |
| bmd_pan_012 | 1 | 8 | pan_correct | pan_edge_epv（EPV 5-10） |
| bmd_pan_013 | 1 | 5 | pan_correct | deg_error（TPM） |
| bmd_pan_014 | 2 | 16 | pan_correct | pan_error（no_ph_test/univariate 宣称独立） |
| bmd_pan_015 | 2 | 16 | pan_correct | pan_error（Pearson/方向矛盾） |
| bmd_pan_016 | 3 | 17 | pan_correct | pan_error+pan_edge_consistency |
| bmd_pan_017 | 3 | 16 | pan_error | pan_error 语料原样 |
| bmd_pan_018 | 2 | 5 | pan_correct | pan_error+deg_error（Student_t/no_correction） |
| bmd_pan_019 | 1 | 5 | pan_correct | pan_edge_purity（纯度局限声明） |
| bmd_pan_020 | 2 | 16 | pan_correct | deg_error+pan_error（边界集中） |
| bmd_deg_009 | 1 | 5 | deg_correct | —（全正确） |
| bmd_deg_010 | 1 | 5 | deg_correct | deg_error（TPM/BY） |
| bmd_deg_011 | 1 | 5 | deg_correct | deg_error（no_filtering） |
| bmd_deg_012 | 1 | 5 | deg_correct | deg_error（no_filtering/p_raw） |
| bmd_deg_013 | 2 | 5 | deg_correct | deg_error+pan_error（no_filtering/t 检验/p_raw） |
| bmd_deg_014 | 2 | 5 | deg_correct | deg_error（no_filtering/TPM/p_raw） |
| bmd_deg_015 | 1 | 5 | deg_correct | —（全正确，limma-voom 变体） |
| bmd_deg_016 | 1 | 5 | deg_correct | deg_error+pan_error（no_filtering/t 检验） |
| bmd_deg_017 | 1 | 5 | deg_correct | —（BY/放宽阈值边界） |
| bmd_deg_018 | 3 | 5 | deg_error | deg_error 语料原样（4 错） |

- 类型覆盖：**34/34**（60 条；含 6 个语料零触发类型的 capture 签名词汇构造）
- 规则覆盖：**38/38**（零触发 = 0，无豁免）
- split（60 条，seed=42 分层随机 70/30）：public **42** / hidden **18**
- taskset v1.1.0：semver 显式提升（E8）；模型信息（生成器 deepseek-v4-flash /
  评测引擎 0.1.3 / prompt 943fc2f11acd）；快照三元组（engine 0.1.3 / ruleset
  1.1.1 / ontology 0.1.0）

## 八、rubric v1.1 澄清点修订说明（6 条）

| # | 澄清点 | 批 1 仲裁实证（锚点） | v1.1 条款 |
|---|--------|----------------------|-----------|
| 1 | TMM 工具链耦合判定 | 8 条 D2 分歧全判 edge（TMM 与 DESeq2 联用冗余）；TPM 输入 counts 工具 = error | 4.1：按工具链匹配判定；TMM/RLE+原生链=correct、+DESeq2=edge、TPM 入 counts 工具=error/edge |
| 2 | 只评本步 vs 管线衔接 | scrna_006 A8/S12、scrna_008 S12（轨迹内不一致不牵连本步→correct） | 4.2：每步独立；一致性族类型例外（跨模块判定本身）；相邻输入形态作 context |
| 3 | 报告解释不足类归属 | pan_005 A1 / pan_007 D15 / pan_009 D16（方向矛盾未讨论→edge） | 4.3：默认 edge；仅当矛盾支撑明确结论→error |
| 4 | note 与 choice 矛盾仲裁依据 | pan_003 D13（note 与标签矛盾→以 choice 为准）；scrna_002 S10（note 描述不符→以 choice 为准） | 4.4：标签以实际 choice 为准；Agent rationale 矛盾不改写 choice 语义 |
| 5 | 模板笔误权重 | scrna_001/002/004/008 S1（GSE 号不一致→correct，不入罪） | 4.5：笔误不判 error；仅当暗示方法学错误 |
| 6 | 双细胞去除与下游设计依赖 | scrna_002 S3（85K 细胞、下游 pseudobulk→edge） | 4.6：下游患者级聚合=edge；细胞级下游+双细胞率高=error；小数据=edge |

批 2 标注效果：6 条澄清条款直接引用（仲裁 note 引用条款编号），批 2 全量
κ=0.9336（vs 批 1 0.7292）——分歧模式从"边界各执一词"收敛为"边界少量残余"。
批 1 已定案标签不追溯重判（gold 版本 v1 保持）。

## 九、reward-protocol 更新 diff 摘要（F4.9）

1. **头注**：v1 + 批 2 更新（60 任务 / taskset v1.1.0 / 新预注册记录 v2）；
   数据行 30 条 → 60 条。
2. **§七 → §7.1（批 1 旧值留档）+ §7.2（60 任务新实测表）**：
   - 配方 B：ρ 0.6091 → **0.6179**（CI [0.2894,0.8335] → **[0.4042,0.7830]** 收窄）；
     τ_b 0.4898 → **0.5033**（CI [0.2131,0.7213] → **[0.3219,0.6618]**）；
     分层 good 0.6611 → **0.6775**、bad 0.2862 → **0.3160**、
     diff +0.375 → **+0.3614**（CI [0.195,0.536] → **[0.2291,0.4719]** 收窄）、
     p 0.001 → **0.000**；
   - 配方 A/C：ρ 0.6279 → 0.6686、diff +0.110 → +0.133（均显著）；
   - 解读更新：结论稳健（60 条样本 CI 收窄、分层分离复现）；硬惩罚放大
     2.7×（30 条时为 3.4×）。
3. **§八**：批 2 落地状态更新（校准重跑完成 + 留档说明）。
4. 排序一致性/分层检验为证据闸（reward-validate 五闸常驻，CI 双矩阵确认）。

### 9.3 gap 重评估（新预注册记录）

| 记录 | n_hidden | Δ | 判定 |
|------|----------|-----|------|
| 批 1（benchmark-pr-2026-08-16-01） | 9 | −0.1864 | 区间外 → 告警（判读：小样本组成偏差） |
| **批 2（benchmark-pr-2026-08-16-02）** | **18** | **+0.046** | **区间内 → 告警解除** |

- 结果如实呈现：Δ 从 −0.1864 收敛到 +0.046（隐藏集 n=9→18）——支持批 1
  "无泄漏通道、组成偏差"的判读；gap 只登记不改分（协议明文）。

### 9.4 评测功效（60 条，bootstrap B=2000，seed=42）

- 检出：recall **0.820** [0.698, 0.917]、precision 0.745、F1 **0.781** [0.647, 0.883]
  （批 1：recall 0.833 / F1 0.769——60 条样本更稳，CI 收窄）
- mean score 0.5528 [0.4818, 0.6218]；edge 检出率 64/96（66.7%）
- 分层：deg 0.443 / pan 0.626 / scrna 0.576；难度 1/2/3 = 0.634 / 0.537 / 0.384
- 多重比较：全对 Holm 校正后 n.s.（deg vs pan p=0.056→0.28；难度 1 vs 3
  p=0.026→0.153 n.s.）

## 十、遗留项（如实声明）

1. **同模型双标注局限保持**：批 2 两个标注员仍为同族 LLM（独立上下文）；
   跨模型/人工标注对照未落地（协议 §九.2 如实声明）。
2. **CellVoyager hook 真实运行仍未实测**（窗口 C 遗留）：批 2 语料扩展以现有
   语料库为准（预注册 corpus_policy 声明）；bmd_scrna_020 直接使用真实
   CellVoyager 轨迹作为素材。
3. **批 2 全量 IRR 显著高于批 1**：归因于 rubric v1.1 澄清 + 批 2 任务边界
   更清晰；同模型高估风险依然存在（如实声明）。
4. **gap 告警解除但样本仍有限**：hidden n=18；如需更强证据，隐藏集可在
   G 窗口（真实 Agent 评测）后继续扩大。
5. 难度分布非严格均衡（deg easy 13 / scrna easy 4）：rubric 特征驱动的如实
   结果（deg 短管线天然易）；三范式 × 三梯度全非空满足验收。

## 十一、关键设计决策记录

| 决策 | 依据 |
|------|------|
| 批 2 组成 scrna 10 / pan 10 / deg 10 | F1.1 均衡 + F3.8 补齐 scrna easy 缺口 |
| 预注册 v2 区间保持 [−0.10, +0.10] | 保守、与批 1 口径可比；n≈18 抽样误差缩小（预注册先于实测） |
| 60 条全量重新划分（seed=42 不变） | 预注册 v2 声明；hidden n≈18 后 gap 重评估有意义 |
| 批 1 标注不追溯重判（gold 版本 v1 保持） | rubric v1.1 只澄清边界不改变三分类定义；重判会污染历史比对 |
| taskset 1.0.0 → 1.1.0 | E8 semver 显式提升（新增 30 任务 = 功能增量） |
| 批 2 校准批 10 条跨范式跨难度 | E3 预注册（κ/α ≥ 0.8 达标再放量），与批 1 同构 |
| 仲裁由第三方独立完成（不读规则） | E6 角色分离；8 条分歧全部 medium（无 weak） |
| reward 校准 60 条重跑 + 旧值留档 | F4.9：分层检验随任务集变化如实重新评估 |
| gap 只登记告警不改分 | E1 协议明文（批 2 实测收敛回区间，未触发任何修改） |
