# G-2b 规则平台键审查报告（22 条 scRNA 规则 required_context 逐条审查）

> **日期**：2026-08-16（窗口 G-2）
> **对应验收**：execution-plan-v1 §六.十二 G2-b 项 4/5/6/7
> **触发背景**：窗口 G 真实评测分数全 L-1——规则 required_context 硬依赖
> `sequencing: 10X_scRNA_seq`，采集三级可信源均拿不到 → 键 unverified → 规则不匹配。
> **关键纪律**：只放宽"确实过强"的平台依赖，保留 10X 专属规则合理性（如双联体检测）；
> 修订走 B5 三闸 + ruleset semver 提升；golden 漂移记录原因不静默。

---

## 1. 分水岭事实：GSE115978 平台查证（G2-b 项 5，不凭 summary 猜）

**结论：GSE115978（Jerby-Arnon et al. 2018, Cell, PMID 30388455）实测为 Smart-seq2，不是 10X。**

| 证据层级 | 内容 |
|---|---|
| GEO 官方记录（Overall design 原文） | *"Individual cells were dissociated from fresh tumor resections, isolated immune and non-immune cells by FACS based on CD45 staining, and profiled with a **modified full length SMART-Seq2 protocol**."*（https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE115978，2026-08-16 直接抓取存档） |
| 文献 | Jerby-Arnon L et al., "A Cancer Cell Program Promotes T Cell Exclusion and Resistance to Checkpoint Blockade", Cell 2018（GEO Citation PMID 30388455）；Smart-seq2 全转录本（plate-based，FACS 分选 CD45±） |
| 数据形态佐证 | GEO 补充文件为 counts.csv + tpm.csv（全转录本基因计数，非 UMI 计数）；7,186 cells 与窗口 G 运行一致 |
| 之前的摘要歧义 | GSE115978 摘要曾标注 "Smart-seq2 or 10X"——**已由 GEO 官方 Overall design 澄清为 Smart-seq2**；窗口 G 报告 §4 的"附带发现"据此定案 |

**分水岭推论（G2-b 项 5 定案）**：
1. declared 注入 `10X_scRNA_seq` 是**错误**的（违背数据事实）——正确 declared 值 = `smartseq2`；
2. 规则修订方向 = **平台键放宽接受 smartseq2**（不是硬塞 10X）；
3. 数据类别：Smart-seq2 全转录本 → `data_category = raw_counts`（非 umi_counts），
   N1.1 归一化规则的 `umi_counts` 硬依赖同为"过强"，一并放宽。

---

## 2. 22 条 scRNA 规则 required_context 平台依赖逐条清单（G2-b 项 4）

判定标准：
- **合理（保留）**：平台前提有生物学/方法学实质（如双联体检测仅液滴平台有意义）；
- **过强（放宽）**：规则科学内容与平台无关，仅因编写时以 10X 为例而硬编码；
- **无平台依赖**：不涉及 sequencing 键。

| # | rule_id | 决策类型 | required_context 平台相关键 | 判定 | 修订 |
|---|---|---|---|---|---|
| 1 | A1.1-ANNO-001_method | annotation_method | sequencing: 10X_scRNA_seq | **过强**：注释方法（SingleR/CellTypist/marker）与平台无关 | 放宽 → `[10X_scRNA_seq, smartseq2]` |
| 2 | A1.1-API-001_data_integrity | api_data_integrity | —（required_context 空） | 无平台依赖 | 不动 |
| 3 | A1.2-ANNO-002_marker_validation | annotation_validation | sequencing: 10X_scRNA_seq | **过强**：marker 验证与平台无关 | 放宽 |
| 4 | B1.1-BATC-001_integration | batch_correction | sequencing: 10X_scRNA_seq + has_batch: true | **过强**（sequencing）：批次整合适用一切 scRNA 平台；has_batch 保留 | sequencing 放宽 |
| 5 | B1.2-BATC-002_requirement | batch_correction | sequencing: 10X_scRNA_seq | **过强**：批次必要性判断与平台无关 | 放宽 |
| 6 | C1.1-CLUS-001_method | clustering_method | sequencing: 10X_scRNA_seq + graph_type: SNN | **过强**（sequencing）；graph_type=SNN 为真实前置条件（图聚类），**保留** | sequencing 放宽；采集层补 graph_type 工具语义（见 §3.3） |
| 7 | C1.2-CLUS-002_resolution | clustering_resolution | sequencing: 10X_scRNA_seq | **过强**：分辨率选择与平台无关 | 放宽 |
| 8 | D1.1-DOUB-001_detection | doublet_detection | sequencing: 10X_scRNA_seq | **合理（保留 10X 专属）**：双联体是液滴共捕获产物；板式 FACS 分选（Smart-seq2）无双联体问题，规则前提不成立 | **不动**（纪律 5） |
| 9 | D2.1-DIMR-001_reduction | dim_reduction | sequencing: 10X_scRNA_seq + method: PCA | **过强**（sequencing）；method: PCA 保留 | sequencing 放宽 |
| 10 | D2.2-DIMR-002_pca_dimension | pca_dimension | sequencing: 10X_scRNA_seq | **过强**：PCA 维度选择与平台无关 | 放宽 |
| 11 | G1.1-DEG-001_pseudobulk | deg_method | sequencing: 10X_scRNA_seq | **过强**：pseudobulk 伪重复原则普适（Squair 2021） | 放宽 |
| 12 | G1.2-DEG-002_multiple_testing | multiple_testing_correction | sequencing: 10X_scRNA_seq | **过强**：多重检验校正普适 | 放宽 |
| 13 | G1.3-DEG-003_method | deg_method | sequencing: 10X_scRNA_seq | **过强**：DEG 方法统计假设与平台无关 | 放宽 |
| 14 | H1.1-HVG-001_selection | hv_gene_selection | sequencing: 10X_scRNA_seq | **过强**：HVG 选择（VST/dispersion）适用一切 scRNA 计数数据 | 放宽 |
| 15 | N1.1-NORM-001_normalization | scRNA_normalization | sequencing: 10X_scRNA_seq + **data_category: umi_counts** | **过强（双平台假设）**：Smart-seq2 全转录本为 raw_counts；LogNormalize/SCTransform 均适用 | sequencing + data_category 均放宽 → `data_category: [umi_counts, raw_counts]` |
| 16 | Q1.1-QC-001_filtering | qc_filtering | sequencing: 10X_scRNA_seq | **过强**：QC 过滤（MAD/硬阈值）与平台无关 | 放宽 |
| 17 | Q1.2-QC-002_mito | qc_mito_threshold | sequencing: 10X_scRNA_seq | **过强**：线粒体比例阈值与平台无关 | 放宽 |
| 18 | S1.1-CONS-001_cluster_annotation | cluster_annotation_consistency | integration_type: cross_module | 无平台依赖 | 不动 |
| 19 | S1.2-CONS-002_annotation_deg | annotation_deg_consistency | integration_type: cross_module | 无平台依赖 | 不动 |
| 20 | S1.3-CONS-003_trajectory_annotation | trajectory_annotation_consistency | integration_type: cross_module | 无平台依赖 | 不动 |
| 21 | T1.1-TRAJ-001_inference | trajectory_inference | sequencing: 10X_scRNA_seq | **过强**：轨迹推断（monocle3/slingshot）与平台无关 | 放宽 |
| 22 | T1.2-TRAJ-002_annotation_precondition | trajectory_validation | sequencing: 10X_scRNA_seq | **过强**：注释前置条件与平台无关 | 放宽 |

**汇总**：22 条中 —— 过强放宽 **17 条**（sequencing 16 条 + N1.1 的 data_category 1 条）；
保留 10X 专属 **1 条**（D1.1 双联体）；无平台依赖 **4 条**（A1.1-API + S1.1/S1.2/S1.3 一致性族）。

---

## 3. 修订落地（G2-b 项 6，B5 三闸 + semver）

### 3.1 规则修订 diff（17 个文件，均为 required_context 值放宽）

```
- sequencing: 10X_scRNA_seq
+ sequencing: [10X_scRNA_seq, smartseq2]      # 16 条通用规则
- sequencing: 10X_scRNA_seq                   # N1.1 专属
- data_category: umi_counts
+ sequencing: [10X_scRNA_seq, smartseq2]
+ data_category: [umi_counts, raw_counts]
```

涉及文件（scRNA/ 下）：A1.1-ANNO-001 / A1.2-ANNO-002 / B1.1-BATC-001 / B1.2-BATC-002 /
C1.1-CLUS-001 / C1.2-CLUS-002 / D2.1-DIMR-001 / D2.2-DIMR-002 / G1.1-DEG-001 /
G1.2-DEG-002 / G1.3-DEG-003 / H1.1-HVG-001 / N1.1-NORM-001 / Q1.1-QC-001 /
Q1.2-QC-002 / T1.1-TRAJ-001 / T1.2-TRAJ-002。
**未改动**：D1.1-DOUB-001（10X 专属保留，纪律 5）。

### 3.2 引擎修订（required_context 列表 any-of 语义）

`RuleRegistry._condition_matches` / `_evaluate_condition`：required_context 值为列表时
按 **any-of（任一命中即通过）** 判定（engine 0.2.0 → **0.2.1**）。既有标量值语义不变
（全部 38 条规则中 37 条为标量，唯一列表来自本次放宽）。

### 3.3 采集层配套（G2-b 项 6 的接口缺口）

- `signatures.yaml`：`sc.tl.leiden` / `sc.tl.louvain` 增加 `context_fixed: {graph_type: SNN}`
  ——graph_type=SNN 是工具定义语义（scanpy 图聚类运行在 neighbors SNN 图上），
  与既有 `method: PCA` / `reference_based: true` 同一级别（call_arg 可信源）；
  解决 C1.1 的真实前置条件在采集层无法提取的接口缺口。
- `cli.py cross-validate` 增加 `--declared`（与 parse-notebook 对齐）。

### 3.4 semver 与三闸结果

- `ruleset.json`：**1.1.1 → 1.2.0**（minor：规则行为加性扩展——放宽接受集，不破坏既有匹配）；
  engine_version 0.2.0 → 0.2.1；43 文件哈希重算（17 个规则文件哈希变更）。
- **B5 三闸（`bio-audit ruleset-validate`）实测：清单 PASS / 冲突 PASS（0 冲突）/ golden PASS（0 差异）**。

---

## 4. golden 漂移记录（G2-b 项 7，C4 流程）

**结论：golden 0 差异，基线未更新，C4 未触发。**

原因（如实记录）：放宽是**纯加性**的——20 条 golden 轨迹 137 决策的 context 全部使用
`sequencing: 10X_scRNA_seq` / `data_category: umi_counts`，这些值在新规则下仍被接受，
规则命中集合与评分逐决策不变（`bio-audit golden` 实测 n_diffs=0）。

若未来轨迹使用 smartseq2/raw_counts，将从"无法评估（L-1）"变为可评分——这正是本窗口
重评（G2-c）要验证的行为变化，不属于 golden 漂移。

---

## 5. 残留风险与诚实声明

1. **immune_correlation_method ×12（真实运行）**：scRNA 规则集不含该类型规则
   （本体 paradigms: [pan-cancer]）——即使 declared 注入齐全，scrna 范式下仍为
   L-1"没有适用的规则"。这是**规则覆盖缺口**（范式隔离设计使然，ontology-design §二.1），
   不是平台键问题；本轮不新增规则（不过度修），在 G2-c 报告中如实呈现。
2. **D1.1 双联体对 Smart-seq2 的 L-1**：平台专属规则的诚实代价——Smart-seq2 运行
   中 doublet 决策"无法评估"是正确语义（规则前提不成立），而非缺陷。
3. **N1.1 data_category 放宽的边界**：仅放宽到 raw_counts（全转录本基因计数）；
   TPM/FPKM 等仍不匹配（归一化规则的 L0 词表已覆盖 TPM_norm 惩罚路径，门禁不变）。
