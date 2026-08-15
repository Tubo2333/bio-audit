# Bio-Audit Benchmark 协议（阶段 3 / 窗口 D + F）

> **版本**：v1（2026-08-16，与任务集 taskset v1.0.0 绑定）+ **批 2 扩展
> （窗口 F，2026-08-16）**：taskset v1.1.0（60 条），预注册记录升级为
> `benchmark-pr-2026-08-16-02`（批 1 记录 `benchmark-pr-2026-08-16-01` 留档，
> 见 `benchmark/protocol.py` 与 `pre_registration_v1_archived.json`）。
> **依据**：refactor-plan-v1.1 E1-E8（评测方法论裁决）+ audit-report E 组 +
> execution-plan §六.七（D1-D6）+ §六.九（F1-F4）
> **预注册记录**：`src/bioaudit/benchmark/pre_registration.json`（机器可读副本）
> **数据**：`src/bioaudit/data/tasks/`（60 条，批 1 30 + 批 2 30）+
> `src/bioaudit/data/annotation/`

---

## 一、目标与范围

benchmark 是**外围层**：评测确定性审计引擎（engine 0.1.3）对带已知错误注入的
Agent 轨迹（gold）的**错误检出能力与分数行为**。它不改变任何评分路径
（golden 20 轨迹 137 决策 0 差异为硬验收，D6.14）。

评测对象口径（预注册）：
- **检出**（positive）= 引擎 level ∈ {0, 1}（危险/有风险）；
- gold `error` → 检出 = TP；未检出 = FN；
- gold `correct` → 检出 = FP；未检出 = TN；
- gold `edge` → 不参与 TP/FP，单独报告 edge 处理率（被检出的 edge 比例）。

## 二、任务集（D1）

- **规模**：目标 ≥60 条（3 范式 × 难度梯度 × 类型覆盖）。**已落地 60 条**
  （批 1：scrna 12 / pan 10 / deg 8；批 2：scrna 10 / pan 10 / deg 10；
  合计 scrna 22 / pan 20 / deg 18）。
- **格式**：每条 = v2 轨迹（version/trajectory_id/provenance/decisions）+
  `gold`（E3 双标注产物）+ `difficulty`（E4 特征 rubric 产物）。
- **版本管理**（E8）：`taskset.json` semver（**当前 1.1.0**，批 2 显式提升）+
  文件级 SHA256 + 快照三元组（engine/ruleset/ontology，C1/P2）；任务/标注变更走
  `bio-audit benchmark-validate` 三闸（清单 + 污染 + 覆盖）+ golden 回归。

## 三、生成器与防泄漏（D1.2/D1.3；E6）

管线：**变体规格（LLM，generator_prompt.md）→ 确定性变换
（generator.transform.v1）→ 人工审核 → 任务草稿 → 独立标注管线**。

| E6 要求 | 落地 |
|---------|------|
| 生成器提示词不含规则内容 | `generator_prompt.md` 为纯过程性指令；测试守卫（规则标识/标题扫描 0 命中） |
| 生成器与评测 Agent 不同模型 | 生成器 LLM（deepseek-v4-flash）vs 评测 Agent = 确定性引擎（模型信息记录在 taskset.model_info） |
| 标注者与规则作者角色分离 | 标注者只读 `annotation_rubric.md` + 任务文件；**禁止读取规则库**（标注提示词明确纪律） |
| 错误注入素材来自真实 Agent 语料 | 每条任务 provenance 记录 `base_trajectories` + `error_pattern_sources`（20 条 legacy 轨迹 + CellVoyager 轨迹 scrna_melanoma_cellvoyager）；**禁止规则反推** |

错误注入示例（全部有语料先例）：`no_integration`/`no_doublet_detection`/
`wilcoxon_rank_sum`（11 患者，伪重复）/`PCA_fixed_10`/`manual_marker`/
`not_checked`（scrna_error）；`no_ph_test`/`univariate_Cox_claiming_independent`/
`EPV_less_than_5`/`GO_all_genes_no_filter`（pan_error）；`no_correction`/
`p_raw <= 0.05`（deg_error）；`PCA_arbitrary`/`Kruskal_Wallis_cell_level`/
`LogNormalize`（CellVoyager 真实轨迹）。
6 个语料零触发类型的决策（qc_mito_threshold/pca_dimension/annotation_validation/
trajectory_validation/annotation_deg_consistency/trajectory_annotation_consistency）
以 capture 签名词汇（阶段 2 真实代码模式）构造；其中正确样例无语料先例
（诚实声明：新类型仅含"未验证/跳过"类错误模式，来自语料 neglect 模式迁移）。

## 四、难度分层（D2.5；E4）

**难度标签不得由审计分数定义**（防循环）。预注册 rubric `difficulty.v1`
（`benchmark/difficulty.py`，有测试守卫：难度计算代码不引用引擎分数路径）：

1. hard（3）：n_decisions ≥ 17 或 n_errors ≥ 3 或 n_subtle_errors ≥ 2；
2. easy（1）：n_decisions ≤ 10 且 n_errors ≤ 1；
3. 其余 → medium（2）。

特征 = {n_decisions, n_errors, n_edge, n_subtle_errors, n_consistency_family}
（subtle = 一致性族 + 方法学细节类型，预注册定义）。难度在 gold 冻结后由
特征确定性计算并写入任务文件；审计分数**不参与**任何一步。

## 五、公开/隐藏集与 gap 容忍区间（D2.6；E1）

- **划分**（预注册）：按 范式×难度 分层随机，seed=42，public:hidden = 70:30；
  在 gold+难度冻结后一次性执行，划分固化在 taskset.json split 字段
  （同输入可复现）。**批 2（窗口 F）**：任务集合并 60 条后**全量重新划分**
  （方法/seed 不变，hidden n≈18；预注册记录 `benchmark-pr-2026-08-16-02`）。
- **gap 统计量**：Δ = mean(trajectory_score/100)public − mean(hidden)。
- **容忍区间**：**[−0.10, +0.10]**（归一化分数单位）。|Δ| 超出区间 →
  **负向告警（泄漏信号）**，替代原"两集一致"验收；gap 只登记告警，不修改
  任何分数或任务。
- **批 2 区间重评估（预注册）**：批 1 实测 Δ=−0.1864（区间外）判读为隐藏集
  小样本组成偏差（hidden n=9）；批 2 hidden n≈18 后**区间保持不变**（保守、
  与批 1 口径可比），结果如实呈现（可能收敛回区间内，也可能仍超区间）。
- 实测：见 `benchmark-run` 输出的 `gap` 字段与完成报告。

## 六、真值标注（D3；E3）

- **双标注**：两个独立标注员（只读 rubric + 任务文件，不同任务顺序）对每条
  决策三分类：`correct / error / edge`（rubric：error=方法学不当致结论失真；
  edge=可辩护但非最优；correct=主流标准做法）。
- **rubric 版本**：批 1 = annotation.v1；**批 2 = annotation.v1.1**
  （窗口 F：D 遗留 6 条澄清点——TMM 工具链耦合 / 只评本步 vs 管线衔接 /
  报告解释不足归属 / note 与 choice 矛盾以 choice 为准 / 模板笔误不入罪 /
  双细胞去除与下游设计依赖，见 `benchmark/annotation_rubric.md` §四）。
  批 1 已定案标签不追溯重判。
- **IRR 门槛**：校准批 10 条先双标注 → Cohen's κ（主）与 Krippendorff's α
  （次）**均 ≥ 0.8 才放量**（预注册）。批 1 校准批旧值留档；批 2 新校准批
  （10 条新任务）另行达标后放量。
- **仲裁**：分歧条目由第三名仲裁者定案；共识强度：strong（双标一致）/
  medium（仲裁 2:1）/ weak（仲裁与双方均不一致）。
- **绑定**（D3.8）：gold 记录标注版本 + 批次 IRR + 快照三元组
  （engine/ruleset/ontology 版本）。
- 实测：见 `data/annotation/irr_report.json`（批 1）/ `irr_report_batch2.json`
  （批 2 + 全量 60）与完成报告。

## 七、评测运行与功效分析（D4；E7）

- **运行器**：`bio-audit benchmark-run` —— 批量审计 → 结果表
  （trajectory_score / verdict / L0-L4/-1 计数 / 决策类型错误率），
  随机源全部固定 seed（默认 42）→ 可重复。
- **功效分析**：
  * bootstrap CI（percentile，B=2000，任务级重采样）：mean score /
    recall / precision / F1；
  * 多重比较协议：范式×难度层间均值比较 = 两样本置换 bootstrap 检验，
    p 值经 **Holm-Bonferroni** 校正（协议在报告 method 字段声明）。
- **黑盒**（E2）：运行器只消费任务 JSON；规则文本不可见；
  规则字符串命中由 `contamination` 模块登记为污染特征（命中即标记）。

## 八、覆盖审计与评审（D5；E5/E8）

- **覆盖审计**（`benchmark-validate` 闸 3）：34 决策类型 + 38 唯一规则
  全覆盖；零触发 = 0 或显式豁免（附理由）。
- **评审机制**（E8，与 B5 规则治理同门禁风格）：任务集/标注变更 =
  PR + `benchmark-validate` 三闸（taskset 清单 + 污染扫描 + 覆盖审计）
  + golden 回归，全部通过才可合并；taskset semver 显式提升；
  仲裁/署名/版本追溯记录在任务 provenance 与标注产物。

## 九、排期与遗留

1. **批 2（30 条 → 60 条）**：**已完成（窗口 F，2026-08-16）**；流程不变
   （语料扩展 + generator_prompt.md v1 规格 → 校准批 IRR → 放量）；
   新预注册记录 `benchmark-pr-2026-08-16-02`（批 1 旧值留档）。
2. **同模型双标注局限**：两个标注员为同族 LLM（独立上下文）——IRR 可能
   高估；跨模型标注（如人工 + LLM）仍未落地（批 2 保持同族双标，如实声明）。
3. CellVoyager 真实运行语料随阶段 2 遗留（hook 未实测）；批 2 语料扩展
   以现有语料库为准（如实声明），bmd_scrna_020 直接使用真实 CellVoyager
   轨迹（scrna_melanoma_cellvoyager）作为错误模式素材。
