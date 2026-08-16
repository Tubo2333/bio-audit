# 窗口 I 报告：端到端高分阳性对照「黄金 Agent」（A/B/C 三版）

> **日期**：2026-08-16（窗口 I）
> **性质**：端到端阳性对照 + 逻辑链敏感性对照——**确定性脚本**（非 LLM）在
> GSE115978 上真实执行，走真实采集链路（M1→M3→交叉验证→verdict→run_audit），
> 验证"链路能认对"；B/C 为同一脚本的参数化错误注入（错误开关），验证
> "审计对科学逻辑链敏感，而非只看终答表面完成度"。
> **对应验收**：execution-plan-v1 §六.十三 I1–I4（9 项，本窗口已冻结）
> **宪法**：`docs/protocols/agent-eval-protocol.md`（G 窗口；declared 语义 §4.1）
> **同族产物**：`D:\C-file\cellvoyager-outputs\windowI\`（不入仓库）
> **报告**：`bio-audit-v2/docs/migration/I1-positive-control-report.md`（本文件）

---

## 1. 结论摘要（直给）

| 版本 | 注入的方法学差异 | trajectory_score | verdict | L4/L3/L2/L1/L0/-1 | 交叉验证（一致/虚报/漏报/未验证） |
|---|---|---|---|---|---|
| **A 黄金版** | 无（教科书式：MAD QC → SCTransform → VST HVG → PCA-elbow → Harmony → Leiden → CellTypist → pseudobulk DESeq2 → BH） | **80.0** | **pass** | 0/7/1/0/0/1 | **10 / 0 / 0 / 0** |
| **B 逻辑断裂** | cell-level DEG（`rank_genes_groups` wilcoxon）替代 pseudobulk（伪重复） | **63.0** | **blocked** | 0/6/1/0/1/1 | **10 / 0 / 0 / 0** |
| **C 微妙错误** | QC 硬阈值（`filter_cells(min_genes=200)`）替代 MAD 自适应 | **66.7** | **needs_correction** | 0/6/1/1/0/1 | **10 / 0 / 0 / 0** |

**一句话**：同一条采集链路、同一份数据、同一流程、终答表面完成度相同（三版都
正常产出细胞类型与 DEG 列表），**仅一处方法学差异 → 审计分与 verdict 呈梯度**
（80.0 pass → 63.0 blocked → 66.7 needs_correction）——"审计对逻辑链敏感"
获得端到端量化证据；与 CellVoyager 真实 LLM 运行（30.0 / L1×7）同链路对比，
"链路能认对正确执行、也能抓出真实风险"两侧证据齐备。

**如实声明**：黄金 Agent = **确定性脚本，不是 LLM**（定位：端到端阳性对照，
不是"真实 LLM 高分"）。A 版 80.0 未达预期 85.0，偏差归因见 §6（注释方法
A1.1 的 L3 通道无 M3 可验证签名——**签名表缺口，非方法学错误**）；B 版 L0
机制与预期措辞略有出入（G1.1 判 L1，L0 来自 G1.3 词表缺口兜底）；C 版 66.7
低于预期 70-80（data_handling 维度组成所致）。全部如实归因，不掩盖、不硬凑。

---

## 2. 背景与定位

- **缺口**：G/G-2 已验证"采集链路能抓错"（CellVoyager 真实运行 30.0 / L1×7，
  交叉验证 20/20 一致），但从未验证"链路能给正确执行高分"——阳性对照缺失；
  R0/benchmark 是引擎级与构造轨迹级验证，不覆盖"真实执行 → M1/M3 → 交叉验证
  → verdict → 评分"的端到端高分路径（execution-plan §六.十三 背景）。
- **本窗口补**：(1) 端到端高分证据（A 版）；(2) 逻辑链敏感性证据（B/C 版——
  同数据同流程、终答表面完成度相同、仅方法学差异 → 审计分梯度）。
- **防"设计高分"纪律（E6 精神）**：黄金脚本按公开最佳实践文献编写，**不引用
  规则库内容**（无 rule_id、无 required_context、无 level 提及）；方法选择本身
  是文献推荐方法（§3），分数由系统独立评分产生——脚本作者无法保证高分
  （A 版 80.0 就是真实例证：任何"设计"都无法让注释拿到 L3）。

---

## 3. 黄金 Agent 设计（I1.1）

### 3.1 方法学依据（文献，全部公开最佳实践）

| 步骤 | 方法 | 文献 |
|---|---|---|
| QC | MAD 自适应阈值（median ± 3×scaled MAD，scater 风格） | McCarthy 2017 (PMID 28212749)；Luecken & Theis 2019 (PMID 31841116) |
| 归一化 | SCTransform（正则化负二项回归） | Hafemeister & Satija 2019 (PMID 31870423) |
| HVG | Seurat VST（flavor=seurat_v3） | Stuart 2019 (PMID 31178118) |
| 降维 | PCA + elbow（累计方差 ≥75% 选维；UMAP 仅可视化） | Luecken & Theis 2019 (PMID 31841116) |
| 批次整合 | Harmony（患者为批次变量） | Korsunsky 2019 (PMID 31740819) |
| 聚类 | Leiden（SNN 图） | Traag 2019 (PMID 30914743) |
| 注释 | CellTypist（参考库逻辑回归 + majority voting） | Domínguez Conde 2022 (PMID 35649401) |
| DEG | 患者级 pseudobulk + DESeq2（患者为生物学重复） | Squair 2021 (PMID 34433851)；Love 2014 (PMID 25516281) |
| 多重检验 | Benjamini-Hochberg FDR | Benjamini & Hochberg 1995；Conesa 2016 (PMID 26813401) |

方法选择与规则高分词表可匹配（SCTransform/Leiden/CellTypist/pseudobulk_DESeq2/
BH/MAD5_adaptive_threshold/PCA_elbow_selection/Harmony/vst）——这些本身就是
文献推荐方法，非应试；词表匹配情况由系统在报告期独立确认（§5 逐决策表）。

### 3.2 脚本-规则隔离（纪律 1）

- 产物：`cellvoyager-outputs/windowI/golden_agent_{A,B,C}.py`，由单一模板
  `golden_agent_template.py` + 变体生成器 `make_variants.py`（错误开关）生成；
  每版为自包含脚本，产物文本 = 实际执行代码逐字一致（无死分支污染 M3）。
- 脚本内容核查：全文无 rule_id、无 required_context/level 字样、无规则 YAML
  读取；仅含文献依据与 API 契约词汇（choice 词表是审计 API 的接口语言）。
- 隔离证据：A 版 80.0 而非 85.0——若脚本"设计"了高分，注释一步（CellTypist
  只有 L2 通道）就是不可绕过的天花板，脚本作者在编写时无从得知评分细节
  （编写顺序：文献 → 脚本 → 运行 → 系统评分）。

### 3.3 错误注入（I2.4，B/C 变体）

- **B 版·逻辑断裂**：DEG 步骤替换为 `sc.tl.rank_genes_groups(..., method="wilcoxon")`
  （细胞级，伪重复——把细胞当独立样本）；终答（差异基因列表）照常输出
  （366 个显著基因，表面完成度与 A 版一致）。
- **C 版·微妙错误**：QC 步骤替换为 `sc.pp.filter_cells(min_genes=200)` +
  `sc.pp.filter_genes(min_cells=3)`（固定硬阈值）；结果照常输出
  （有趣事实：该数据集中硬阈值恰好一个细胞都没滤掉，656 个显著基因——
  结果表面与 A 版几乎相同，但方法学逻辑被独立降级）。
- 注入点全部落在**现有规则覆盖内**（qc_filtering → Q1.1；deg_method → G1.1/G1.3），
  非覆盖外类型（那只会 L-1，无对比价值）——注入点选择依据规则覆盖审计
  （benchmark D5 产物），非规则内容引用。

---

## 4. 真实执行（I1.2 前半）

### 4.1 数据与事实

| 项 | 值 |
|---|---|
| 数据 | `GSE115978_raw.h5ad`（7186 cells × 22454 genes，raw counts，485.5MB） |
| 平台 | **Smart-seq2**（GEO Overall design 原文，G-2 已查证定案；declared 注入 smartseq2/raw_counts，评测者署名文件 `windowI/declared.json` = G-2 同款） |
| 患者数 | **32**（obs.sample_id 为单一类别 "GSE115978"，患者 ID 编码于 cell_barcode 前缀如 cy79/MGH00478/merck，大小写归一化去重；真实读取，见 `reports/metadata_GSE115978.json`） |
| 数据元数据 | n_cells=7186 / n_genes=22454 / n_patients=32 / has_batch=true（build_metadata.py 真实读取） |

### 4.2 环境（只装本地，不进仓库）

- venv：`D:\C-file\cellvoyager-env`（Python 3.12.10；scanpy 1.12.3 / anndata 0.13.2 /
  pydeseq2 0.5.4 / celltypist 1.7.1 + Immune_All_High v2 模型 / harmonypy 0.0.10 /
  statsmodels 0.14.6 / scikit-misc 0.5.2 / bio-audit 0.2.1 editable）
- **R 4.6.1 + Bioconductor sctransform 0.4.3**（`C:\R\R-4.6.1`）：SCTransform 无
  Python 实现（PyPI 无 sctransform/scranpy Windows 轮子，scranpy 构建失败，
  sctransform GitHub 源不存在）→ 归一化步骤经 Rscript 子进程真实调用参考实现
  `sctransform::vst`（方法为文献推荐方法，执行真实；混合管线如实声明）
- 采集存储：`BIOAUDIT_WAL_DIR/BIOAUDIT_VERDICT_DIR` → `cellvoyager-outputs/data/{wal,verdicts}`
  （与 G 窗口同族）

### 4.3 执行耗时（每版独立真实执行）

| 步骤 | A | B | C |
|---|---|---|---|
| 加载+患者标注 | 0.4s | 0.4s | 0.3s |
| QC | 1.1s | 0.9s | 1.4s |
| HVG | 3.2s | 3.2s | 2.9s |
| SCTransform（R） | 85.0s | 80.8s | 78.2s |
| PCA | 0.7s | 0.7s | 0.7s |
| Harmony | 65.0s | 20.2s | 17.9s |
| Leiden | 11.7s | 10.8s | 10.5s |
| CellTypist | 6.1s | 5.8s | 5.7s |
| DEG | 5.8s | 1.0s | 5.4s |
| BH | 0.1s | 0.1s | 0.1s |
| **合计（步骤和）** | **~179s** | **~124s** | **~123s** |

产出（每版 runs/<V>/）：`analysis_summary.json` / `analyzed.h5ad` /
`deg_significant_top200.csv` / `golden_agent_<V>_executed.py`（执行后逐字副本，
M3 解析对象）/ `work/`（sctransform 中间产物）。

---

## 5. 采集链路与评分结果（I1.2/I1.3）

### 5.1 链路（三版完全一致，零代码改动）

- **M1**：脚本每步经 `M1Reporter.report()` 上报（paradigm=scrna，白名单注册，
  WAL + verdict provisional 落盘）→ 每版 **10 条声明**。
- **M3**：`M3Parser(act="scrna", metadata=数据元数据, declared=评测者声明)`
  解析 `golden_agent_<V>_executed.py` → 每版 74-78 个候选命中（多实例为
  注释/文档字符串重复命中，同 choice 无害），4 类 uncertain
  （api_data_integrity / clustering_resolution / dim_reduction(pca 调用) /
  pca_dimension——签名表"禁猜"设计的预期行为）。
- **CrossValidator**：**三版均为 consistent 10 / false_positive 0 /
  false_negative 0 / unverified 0**——声明与执行证据逐决策对齐（正反两面：
  G 窗口 20/20 一致是"链路一致"，本窗口是"教科书式声明+教科书式执行"的一致）。
- **verdict**：10/10 provisional → final（无 revoked——无虚报）。
- **final-only 轨迹 → run_audit**：10 决策，context 为 M3 事实 context
  （调用参数 + 数据元数据 + declared），逐决策规则匹配见下。

### 5.2 A 版（黄金，80.0 pass）

| decision_type | choice | L | matched_rules |
|---|---|---|---|
| qc_filtering | MAD5_adaptive_threshold | **3** | Q1.1-QC-001 |
| scRNA_normalization | SCTransform | **3** | N1.1-NORM-001 |
| hv_gene_selection | vst | **3** | H1.1-HVG-001 |
| dim_reduction | PCA_elbow_selection | **3** | D2.1-DIMR-001_reduction |
| batch_correction | Harmony | **3** | B1.1-BATC-001_integration + B1.2-BATC-002_requirement |
| clustering_method | Leiden | **3** | C1.1-CLUS-001_method |
| annotation_method | CellTypist | **2** | A1.1-ANNO-001_method |
| deg_method | pseudobulk_DESeq2 | **3** | G1.1-DEG-001_pseudobulk + G1.3-DEG-003_method |
| multiple_testing_correction | BH | **3** | G1.2-DEG-002_multiple_testing |
| significance_threshold | padj <= 0.05, \|logFC\| >= 1.0 | **-1** | （无 scRNA 规则——覆盖缺口，§8.3） |

- **trajectory_score = 80.0**（min 维 = method_selection 0.80 =
  (0.85×4 + 0.60)/5，其中 0.60 为 CellTypist L2）；data_handling 0.85；
  statistical_rigor 0.85；**verdict = pass**（无 L0/L1，≥60）。
- 执行事实：7186 → 7180 cells（MAD QC），1997 HVG genes，elbow 20 PCs，
  19 clusters，12 cell types（T cells 3488 / Endothelial 1144 / B 893 /
  Macrophages 503 / Epithelial 473），pseudobulk DEG（32 患者 × 2 细胞类型）
  641 个显著基因（padj<0.05 & |logFC|>1）。

### 5.3 B 版（逻辑断裂，63.0 blocked）

- 唯一差异：deg_method = wilcoxon_rank_sum（细胞级，伪重复）。
- **deg_method → L0**（matched G1.1 + G1.3）→ verdict **blocked**；
  method_selection 0.63 = (0.85×3 + 0.60 + 0.00)/5 → **63.0**。
- **L0 机制如实拆解（重要）**：预期"G1.1 判 L0"，实际 **G1.1 判 L1**
  （wilcoxon_rank_sum 在 G1.1 词表 = L1）；**L0 来自 G1.3 词表缺口**——
  `wilcoxon_rank_sum` 不在 G1.3 词表（G1.3 用的是 `Seurat_wilcoxon_default`），
  evaluator 对未识别 choice 兜底 L0（"未知方法 → 危险"）。两规则取最严 → L0。
  → 这是 G1.1 与 G1.3 之间真实的**词表不一致缺陷**（D2 裁决对齐了 MAST，
  未对齐 wilcoxon 家族），本窗口作为发现登记（§8.2）。
- 执行事实：366 个显著基因（细胞级 wilcoxon），终答照常输出。

### 5.4 C 版（微妙错误，66.7 needs_correction）

- 唯一差异：qc_filtering = hard_threshold（min_genes=200 / min_cells=3）。
- **qc_filtering → L1**（Q1.1）→ verdict **needs_correction**；
  data_handling 0.667 = (0.30 + 0.85 + 0.85)/3 → **66.7**。
- 执行事实：硬阈值恰好滤掉 **0 个细胞**（7186 → 7186；Smart-seq2 FACS 分选
  数据质量高），656 个显著基因——**结果表面与 A 几乎相同，但方法学逻辑被
  独立降级**（审计评的是方法，不是结果）。

---

## 6. 梯度解读与预估偏差归因（I2.5，如实）

**梯度成立**：同数据（GSE115978）、同流程、终答表面完成度相同（三版均产出
细胞类型 + 显著 DEG 列表），仅一处方法学差异 → 分数与 verdict 均变化：
80.0 pass → 63.0 blocked → 66.7 needs_correction。"审计对逻辑链敏感"获得
端到端量化证据（此前只有 R0 引擎级与 benchmark 构造轨迹级证据）。

**预估偏差（3 项，全部如实归因，均为有效发现而非掩盖）**：

1. **A 版 80.0 < 预期 85.0**——归因：annotation_method 的 L3 通道
   （`SingleR_with_CellTypist_cross_validation` / `multi_method_consensus` /
   `reference_based_with_marker_validation`）**无 M3 确定性签名**，单一
   CellTypist 只能被验证为 L2；且 SingleR 无 Python 实现、无法真实执行
   双方法交叉验证 → 教科书式注释在采集层天花板 = L2。**签名表缺口**，非
   方法学错误（§8.2）。若未来签名表为"多方法交叉验证"增加可验证签名，
   A 版预期可达 85.0。
2. **B 版 L0 机制与预期措辞不符**——预期"G1.1 判 L0"；实际 G1.1 判 L1、
   L0 来自 G1.3 词表缺口兜底（§5.3）。分数 63.0 ∈ 预期区间 [60,75] ✓，
   verdict blocked ✓，但**机制归因必须写对**：G1.1 的语义本来就是
   "细胞级 wilcoxon = L1（有风险）"，L0 是词表不一致的副产物。
3. **C 版 66.7 < 预期 70-80**——归因：data_handling 维度仅 3 个决策
   （qc/norm/batch），QC 降级后均值 0.667；预期 70-80 建立在更大的维度
   组成假设上（若管线含更多 data_handling 决策，如双联体/API 完整性——
   但 Smart-seq2 无双联体前提、API 完整性无 M3 签名，均不可行）。
   verdict needs_correction ✓ 与预期一致。

**分数排序说明**：B（63.0）< C（66.7）但 B 是 blocked、C 是 needs_correction——
分数口径是最低维度均值×100，verdict 由 L0/L1 存在性决定；**严重性判断
（blocked > needs_correction）与数值排序不完全一致是评分模型的已知特性**
（C1 最低维主导 + 均值稀释），如实呈现，不圆场。

---

## 7. 与 CellVoyager 真实运行对比（I3.6，同链路同数据）

| 维度 | CellVoyager（真实 LLM，G-2 重评） | **黄金 A（确定性脚本）** | B | C |
|---|---|---|---|---|
| 对象 | LLM Agent（deepseek-chat，max-iterations 5） | **确定性脚本（非 LLM）** | 同左（注入逻辑断裂） | 同左（注入微妙错误） |
| 数据 | GSE115978（同） | GSE115978（同） | 同 | 同 |
| 采集链路 | M1 hook（20 声明）→ M3 → 交叉验证 20/20 一致 | M1Reporter（10 声明）→ M3 → 交叉验证 10/10 一致 | 同 | 同 |
| trajectory_score | **30.0** | **80.0** | 63.0 | 66.7 |
| verdict | needs_correction | **pass** | blocked | needs_correction |
| L 分布 | 0/1/0/7/0/12 | 0/7/1/0/0/1 | 0/6/1/0/1/1 | 0/6/1/1/0/1 |
| 主要问题 | hard_threshold×4、LogNormalize×2、manual_marker×1（L1）；immune×12 L-1 | 无（唯一非 L3 = CellTypist L2 签名表天花板） | DEG 伪重复（L0） | QC 硬阈值（L1） |

**解读**：同一条链路，教科书式执行 80.0 pass vs 真实 LLM 30.0 needs_correction，
对比度成立；且两者的问题类型可交叉印证（CellVoyager 的 hard_threshold/
LogNormalize 被 C 版/A 版对照确认——C 版证明 hard_threshold 确实判 L1，
A 版证明 LogNormalize 不是唯一可选归一化）。**口径纪律**：黄金 Agent 分数
只与 CellVoyager 分数同列呈现，不与 demo 时代 29 分混写（site-design §6.2）；
黄金 Agent 定位 = 端到端阳性对照（确定性脚本），不是"真实 LLM 高分"。

---

## 8. 发现清单（本窗口的真实产出）

### 8.1 采集组件缺陷（修复 + 回归，纪律 2 允许路径）

- **缺陷**：`M3Parser._resolve_choice` 的 `choice_ranges` 分支对**非字面量
  kwarg**（如 `n_comps=n_comps` 变量间接——真实脚本的常见写法）直接
  `TypeError` 崩溃（str vs int 比较），违反"禁猜 → uncertain"设计
  （F6）：无法确定性取值时应进 uncertain，绝不崩溃；此前 `_build_candidate`
  的 `_coerce` 已处理该情形，`choice_ranges` 漏了。
- **修复**（最小改动）：`choice_ranges` 分支先 `_coerce(kwargs.get(arg_name), "float")`，
  失败 → `(None, False)` → uncertain。
- **回归测试**：`tests/test_m3_parser.py::test_non_literal_kwarg_choice_ranges_uncertain_not_crash`
  （变量 n_comps/resolution → uncertain 不崩溃；字面量 0.8 路径行为不变）。
- **回归**：pytest **235/235**（234 + 1）、golden **0 差异**、ruleset-validate 三闸
  PASS（评分路径零改动——解析器修复只影响 uncertain 判定）。

### 8.2 采集签名表缺口（登记，不改代码——外围层缺口，非缺陷）

| 类型 | 缺口 | 影响 |
|---|---|---|
| annotation_method | A1.1 的 L3 通道（多方法交叉验证/参考+marker 验证）无确定性签名；SingleR 无 Python 实现 | 教科书式注释最高只能被验证为 L2 → A 版 80.0 天花板 |
| pca_dimension | 签名仅支持 n_comps ∈ {30-50, 10, 15, <5} 区间映射；elbow 选择（20 PCs）→ uncertain | 合理选维不进 final 轨迹（不扣分，也不得分） |
| clustering_resolution | 仅 0.8 → default_0_8；1.0/其他 → uncertain | 同上 |
| qc_mito_threshold | 仅固定阈值 25/50 有签名；MAD 自适应 mito → 无签名 | MAD mito 决策不进轨迹 |
| api_data_integrity | read_h5ad 为 context-only 签名 | 完整性检查无法被确定性验证 |
| **deg_method（G1.1 vs G1.3 词表不一致）** | `wilcoxon_rank_sum`（M3 签名输出）不在 G1.3 词表（其词表为 `Seurat_wilcoxon_default`） | B 版 L0 的直接机制；规则层词表缺陷（D2 裁决漏项），登记建议修复 —— **已修复（窗口 J1，2026-08-16）：G1.3 词表对齐 G1.1（wilcoxon 家族全 L1），ruleset 1.3.0，重评见 §12** |

### 8.3 规则覆盖缺口（如实登记，不在本窗口补规则）

- `significance_threshold`：scRNA 范式**无规则**（M1.3 仅在 DEG/pan 范式），
  三版该决策均 L-1（与 G 窗口 immune_correlation ×12 同类缺口）；本体
  34 类型含此类型，规则库按本体 backlog 生长（G2 同类处理，不过度修）。
  **（已修复——窗口 J2，2026-08-16：新增 G1.4-DEG-004，三版重评 L-1 → L3，见 §12.3。）**
- `qc_mito_threshold` 的 MAD 通道、`clustering_resolution` 的多分辨率通道：
  同上（规则有、签名无 → 采集层缺口，§8.2）。

### 8.4 环境缺口（如实声明）

- SCTransform/scran 无 Python 3.12 可用实现（PyPI 无包 / scranpy 无 Windows
  轮子且源码构建失败 / sctransform GitHub 源不存在）→ 归一化经 Rscript 真实
  执行 Bioconductor 参考实现（混合管线）；若未来出现 Python 原生实现，
  可去掉 R 依赖（方法不变，分数不变）。

---

## 9. 回归（I4.8/I4.9）

| 闸 | 结果 |
|---|---|
| pytest 全量（仓库根） | **235/235**（234 既有 + 1 新增 M3 解析器回归测试） |
| golden 重放 | **0 差异**（20 轨迹 137 决策；基线未更新，C4 未触发） |
| ruleset-validate 三闸 | 清单 PASS / 冲突 PASS（0）/ golden PASS |
| 评分路径 | **零改动**（仅 `capture/m3_parser.py` 解析器修复 + 1 测试；golden 0 差异证实） |
| ruff | 新增/修改代码零错误（修复行短，无新告警） |
| CI | GitHub Actions 双矩阵（3.10/3.12）确认（见执行计划快照） |
| 仓库外 | `D:\C-file\docs\specs\2026-08-13-execution-plan-v1.md` §六.十三 9 项打勾 |

---

## 10. 产物清单

| 产物 | 路径 |
|---|---|
| 本报告 | `bio-audit-v2/docs/migration/I1-positive-control-report.md` |
| 黄金脚本模板 + 变体生成器（错误开关） | `cellvoyager-outputs/windowI/golden_agent_template.py` + `make_variants.py` |
| 三版执行产物（脚本/摘要/h5ad/DEG 表/executed 副本） | `cellvoyager-outputs/windowI/runs/{A,B,C}/` |
| 三版采集链路分析报告 | `cellvoyager-outputs/windowI/reports/windowI_{A,B,C}.json` |
| 数据元数据（真实读取） | `cellvoyager-outputs/windowI/reports/metadata_GSE115978.json` |
| declared（评测者署名，G-2 同款） | `cellvoyager-outputs/windowI/declared.json` |
| verdict/WAL（三版会话） | `cellvoyager-outputs/data/{verdicts,wal}/golden_winI_{A,B,C}_20260816.jsonl` |
| 组件修复 | `bio-audit-v2/src/bioaudit/capture/m3_parser.py`（choice_ranges 防崩溃） |
| 回归测试 | `bio-audit-v2/tests/test_m3_parser.py::test_non_literal_kwarg_choice_ranges_uncertain_not_crash` |
| README 真实效果更新 | `bio-audit-v2/README.md`（§真实效果，高分对照 + 逻辑链梯度） |

---

## 11. 诚实局限

1. **黄金 Agent 是确定性脚本，非 LLM**——端到端阳性对照定位；"真实 LLM
   高分"不在本窗口证据范围（排期：更多真实 Agent 评测）。
2. **A 版 80.0 ≠ 85.0**——annotation L2 是签名表天花板（§6.1），非方法学
   错误；85.0 目标未达成已如实归因。
3. **n=1 数据**——仅 GSE115978（Smart-seq2）；结论推广需更多数据集
   （排期：多数据集/多 Agent 评测）。
4. **确定性近似**——Harmony/Leiden 为迭代求解器，seed 固定可复现到浮点
   噪声级（每次运行聚类数一致，见 §4.3 三版 n_clusters 均为 19）。
5. **B 版 L0 机制依赖 G1.3 词表缺口**——若规则库修复该词表（§8.2），
   B 版将变为 L1/needs_correction（~69.0），梯度仍成立但"blocked"证据
   消失；本窗口按当前规则版本如实报告。**（2026-08-16 窗口 J 已修复并应验：
   ruleset 1.3.0 重评 B 版 = 69.0 needs_correction，见 §12。）**
6. **hard_threshold 在 C 版滤掉 0 个细胞**——结果面与 A 几乎相同，恰好
   强化"审计评方法不评结果"的论证，但该巧合不可外推。
7. **sctransform 丢弃 8 个极稀疏基因**（参考实现行为，≤4 细胞表达）——
   已如实记录（A/B/C 均 1997 genes）；对评分零影响（HVG/基因集不参与评分）。

---

## 12. 窗口 J 追加记录：B 版重评（2026-08-16，ruleset 1.2.0 → 1.3.0）

> 本窗口登记发现①（§8.2：G1.1 vs G1.3 wilcoxon 词表不一致）已由窗口 J 修复
> （J1 方案：以 G1.1 语义为准，与 D2 MAST 裁决同原则——细胞级 wilcoxon = L1 有风险；
> G1.3 L1 词表补 wilcoxon_rank_sum/wilcoxon_sc/Seurat_FindMarkers，G1.1 对称补
> Seurat_wilcoxon_default；方案经执行窗口提交用户在线确认后落地，裁决内容审计中枢事后
> 追认合理——过程记录见 J 报告 §8.6）。本附录记录修复后三版黄金 Agent 重评结果。

### 12.1 重评结果（同一 final_trajectory 重跑 run_audit，零采集链路改动）

| 版本 | 窗口 I 实测（ruleset 1.2.0） | **J1 重评（ruleset 1.3.0）** | L 分布（L4/L3/L2/L1/L0/-1） |
|---|---|---|---|
| **A 黄金版** | 80.0 · pass | **80.0 · pass（不变）** | 0/8/1/0/0/1 |
| **B 逻辑断裂** | 63.0 · blocked | **69.0 · needs_correction** | 0/7/1/1/0/1 |
| **C 微妙错误** | 66.7 · needs_correction | **66.7 · needs_correction（不变）** | 0/7/1/1/0/1 |

- **B 版**：deg_method（wilcoxon_rank_sum）L0 → **L1**（两规则词表对齐后均评 L1），
  method_selection 维度 0.63 → 0.69 = (0.85×3 + 0.60 + 0.30)/5 → **69.0**；
  verdict blocked → **needs_correction**（无 L0，有 L1）。
  → §11.5 诚实局限 5 的预警**应验**："B 版将变为 L1/needs_correction（~69.0），
  梯度仍成立但 'blocked' 证据消失"——修复后 blocked 证据确实消失，如当时声明。
- **A/C 版**：无 wilcoxon 决策，分数/verdict 不变（80.0 pass / 66.7 needs_correction）。
- **梯度结论更新**：同数据同流程仅一处方法学差异 → 审计分梯度 80.0 → 69.0 → 66.7
  保持成立；verdict 梯度由 pass/blocked/needs_correction 变为 pass/needs_correction/
  needs_correction——B 版严重性证据从"危险级 L0"修正为"有风险级 L1"（与 G1.1
  科学语义一致：伪重复 = 有风险，L0 保留给 t-test 族），"审计对逻辑链敏感"的
  量化证据不依赖该 L0，仍成立（分数梯度 + 严重性排序）。

### 12.2 连锁影响（J1，如实留档）

| 项 | ruleset 1.2.0（修复前） | ruleset 1.3.0（修复后） |
|---|---|---|
| golden（20 轨迹 137 决策） | 基线 L0×2（scrna_crc_error/scrna_error S10） | **基线更新**（C4）：该 2 决策 L0→L1；轨迹分/verdict 不变（其他 L0 主导，29.0/40.0 blocked） |
| benchmark 60 任务 | mean 0.5528 / recall 0.820 / F1 0.781 / gap +0.046 | mean **0.5542** / 检出指标**不变** / gap **+0.048**（区间内，无告警）；bmd_scrna_005 67.7→70.0、bmd_scrna_014 68.0→74.0（→needs_correction） |
| reward 校准 | ρ 0.6179 / τ_b 0.5033 / 分层差 +0.3614（p=0.000） | ρ **0.6008** / τ_b **0.4884** / 分层差 **+0.3434**（p=0.000 保持显著） |
| pytest | 235/235 | 235/235（评分路径零代码改动，仅规则数据 + 基线） |

### 12.3 J2 追加：significance_threshold 覆盖缺口修复后重评（2026-08-16，ruleset 1.3.0 → 1.4.0）

> 本窗口登记发现③（§8.3：scRNA 范式无 significance_threshold 规则，三版均 L-1）已由
> 窗口 J2 修复：新增 `G1.4-DEG-004_significance_threshold`（文献锚定 Conesa 2016
> PMID 26813401 等；level 词表与 DEG/pan 范式 M1.3-DEG-001 对齐——阈值科学范式无关）；
> 本体 significance_threshold 扩至 scRNA + context_schema 增 padj_cutoff/logfc_cutoff 键
> （ontology 0.1.0 → 0.1.1）。golden 0 差异（无 scRNA 轨迹含该类型决策，C4 未触发）；
> benchmark 60 任务 0 变化（无任务含该类型）；新规则覆盖豁免登记（D5.12）。

| 版本 | J1 重评（ruleset 1.3.0） | **J2 重评（ruleset 1.4.0）** | significance_threshold 决策 |
|---|---|---|---|
| **A 黄金版** | 80.0 · pass（L-1×1） | **80.0 · pass（L-1×0）** | L-1 → **L3**（padj<=0.05, \|logFC\|>=1.0，G1.4 命中） |
| **B 逻辑断裂** | 69.0 · needs_correction（L-1×1） | **69.0 · needs_correction（L-1×0）** | L-1 → **L3**（同 A） |
| **C 微妙错误** | 66.7 · needs_correction（L-1×1） | **66.7 · needs_correction（L-1×0）** | L-1 → **L3**（同 A） |

- **维度分如实呈现**：三版 statistical_rigor 维度均 0.85（BH L3 与 significance L3
  均值），**聚合分无变化**（80.0/69.0/66.7）——覆盖缺口闭合（L-1 → L3）不改变
  A 版 80.0 天花板结论（天花板仍来自 annotation L2 签名表缺口，§6/§8.2）。
- golden/benchmark/reward 全链路 0 变化（无既有资产含 scRNA significance_threshold
  决策）；pytest 235/235；规则集 1.4.0（39 唯一规则）。

详细报告：`bio-audit-v2/docs/migration/J1-rule-quality-report.md`（窗口 J）。

详细报告：`bio-audit-v2/docs/migration/J1-rule-quality-report.md`（窗口 J）。

---

*报告完毕。窗口 I 执行计划快照与 README 同步更新；git commit/push 与 CI
确认见执行计划快照。*
