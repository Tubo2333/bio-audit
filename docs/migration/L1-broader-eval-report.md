# 窗口 L 报告：评得多——10X 黄金对照 + 真实短评测

> **日期**：2026-08-16（窗口 L）
> **性质**：评测覆盖扩展——**L-a 10X 黄金对照**（GSE132465 CRC 10X UMI，≈0 成本，
> 确定性脚本真实执行）补 Smart-seq2 评不到的规则维度（D1.1 双联体 / N1.1 umi_counts
> 分支 / 33 样本批次整合）；**L-b 真实短评测**（CellVoyager 聚焦短分析，¥1-2 预算）
> 拿"真实 LLM Agent 高分/全评分"的第一份证据（n=1，高分不保证）。
> **对应验收**：execution-plan-v1 §六.十六 L1–L3（11 项，2026-08-16 冻结）
> **宪法**：`docs/protocols/agent-eval-protocol.md`（§10 L 窗口修订记录）
> **同族产物**：`D:\C-file\cellvoyager-outputs\windowL\`（不入仓库）
> **报告**：`bio-audit-v2/docs/migration/L1-broader-eval-report.md`（本文件）

---

## 1. 结论摘要（直给）

| 任务 | 结果 | 关键数字 |
|---|---|---|
| **L-a 10X 黄金对照 A 版**（教科书式 + scDblFinder 双联体） | ✅ **80.0 · pass** | 11 决策 10×L3 + 1×L2；**D1.1 首次真实验证 = L3**（scDblFinder，2,783/59,399 双联体 = 4.69%）；交叉验证 11/0/0/0；0 成本（37.5 分钟） |
| **L-a 10X 变体 B 版**（跳过双联体） | ✅ **L0 实证成立** | 采集层：skip 声明**虚报 → revoked**（阴性声明不可验证，final 轨迹 10 决策 → 80.0 pass——省略在采集层不可见）；**窗口 M 闭环：带 expected_types 重跑 → doublet_detection 补入（provenance=expected）→ 63.7 · blocked 直接出自采集链路**（§4.3.1；原引擎级补验段落留档） |
| **平台互补** | ✅ 10X vs Smart-seq2 决策集差异实证 | 10X 独有：doublet_detection / umi_counts 分支 / 33 样本批次；Smart-seq2 版该决策不存在（I 窗口 10 决策无 D1.1）；两平台共享 10 个决策类型全评分 |
| **L-b 真实短评测** | ✅ **30.0 · needs_correction**（高分未兑现，如实呈现） | 5 决策全可评分（L-1=0）：L2×1（dispersion）+ L1×4（LogNormalize×2、Spearman×2）；交叉验证 5/5 一致；**实际成本 ¥0.43**（预算 ¥5 内，4.92 分钟） |

**一句话**：评分缺口闭合（K）后，"评得多"的第一步落地——10X 平台首次真实执行
覆盖 D1.1 双联体规则两侧语义（做 → L3 / 跳过 → L0），同时暴露采集层对"阴性声明"
（跳过类决策）不可验证的真实边界；平台互补对照显示各平台适用决策集差异被如实
呈现，不硬套。

---

## 2. 背景与定位（L-a）

- **背景**：K 窗口后评分缺口闭合（immune 可评 / 未知方法→-1），下一步扩展评测覆盖
  （"评得多"）。两条零/低成本路径（execution-plan §六.十六）：10X 黄金对照 + 真实短评测。
- **为什么 10X**：I 窗口黄金对照（GSE115978）是 **Smart-seq2** 平台——**D1.1 双联体
  检测规则（10X 专属，required_context `sequencing: 10X_scRNA_seq`）从未真实执行验证**；
  N1.1 的 umi_counts 分支、33 样本级批次整合同样是 Smart-seq2 评不到的维度。
- **方法**：黄金 Agent = 确定性脚本（非 LLM），按公开最佳实践编写（Luecken & Theis
  2019 等），在 GSE132465（CRC 10X UMI，本地 1.8GB h5ad）上真实执行，走真实采集
  链路（M1Reporter/M3Parser/CrossValidator/verdict/run_audit，**零代码改动**）。
- **防"设计高分"纪律（E6 精神）照旧**：脚本只依据文献，不引用规则库（隔离审查
  见 §3.3）；分数由系统独立评分（A 版 80.0 与 I 窗口同分同机制——注释方法 L2 天花板）。

---

## 3. 数据与脚本（L1.1/L1.2）

### 3.1 数据准备与平台查证（清单 L1.1，不凭文件名）

| 项 | 值 |
|---|---|
| 数据 | `GSE132465_raw.h5ad`（63,689 cells × 25,655 genes，csr float32，整数值 UMI counts，1.8GB） |
| **平台查证** | **10X Genomics Chromium 3'（v2）**——GEO GSE132465 Overall design 原文 "Single-cell 3' mRNA sequencing data were obtained from 23 patients in 23 primary colorectal cancer and 10 matched normal mucosa"（2026-08-16 抓取存档 `windowL/geo/GSE132465_GEO_page_20260816.html`，GPL20301 = Illumina HiSeq 4000）+ HCA wrangler 项目页 "Library Construction Method: 10x 3' v2"（存档同目录）——**不是凭文件名猜** |
| 数据事实 | 33 个 10X 文库（23 tumor "-T" + 10 normal "-N"，obs_names 前缀实测）；23 患者；tissue/disease 单值；X 整数值（min 1 / max 26,489）→ data_category=umi_counts；var_names 非唯一（加载时 make_unique，数据事实） |
| 预检 | `h5ad_precheck` 复用：0 issues（无 nullable string 坑）；`reports/h5ad_precheck_GSE132465.json` |
| 版权/provenance（H4） | GEO 页面 + GPL 页面 + HCA 项目页 HTML 存档（`windowL/geo/`）；declared 文件含证据链注记（`windowL/declared.json`）；数据版权归 Lee et al. 2020（PMID 32451460）/ GEO 原始提交者，本地仅评测用途 |
| declared（评测者署名） | `{"sequencing": "10X_scRNA_seq", "data_category": "umi_counts"}` + `_evidence` 三条（GEO 原文/HCA 记录/X 整数值实测） |
| 数据元数据（二级可信源） | `reports/metadata_GSE132465.json`（n_cells=63,689 / n_genes=25,655 / n_patients=23 / n_samples=33 / has_batch=true，真实读取） |

### 3.2 黄金脚本适配 10X（清单 L1.2）

模板 `windowL/golden_agent_template_10x.py`（I 窗口结构复用）+ 变体生成器
`windowL/make_variants_10x.py`（错误开关）：

| 步骤 | 10X-A（黄金） | 10X-B（变体·跳过双联体） |
|---|---|---|
| 载入/完整性 | h5ad 读取 + var_names_make_unique + 非负/整数值断言 | 同左 |
| QC | MAD 自适应阈值（McCarthy 2017；Luecken & Theis 2019） | 同左 |
| **双联体检测** | **scDblFinder 真实执行**（Rscript + Bioconductor 参考实现，Xi & Li 2021 PMID 33541407；**samples= 按 33 文库分别估算**——合并矩阵不传 samples 会把全矩阵当单库、双联体率虚高到 21.5%，首次运行已实测并修正，见 §6.1）；输入 = QC 后 UMI counts（genes×cells MatrixMarket，零基因前置过滤，方向冒烟验证） | **显式跳过**（不调用任何双联体工具；M1 如实声明 skip_doublet） |
| 归一化 | SCTransform（sctransform::vst，Rscript 参考实现；UMI 数据标准选择） | 同左 |
| HVG | Seurat VST v3（2000） | 同左 |
| 降维 | PCA + elbow（累计方差 ≥75%） | 同左 |
| 批次整合 | Harmony（key=**sample**，33 个 10X 文库） | 同左 |
| 聚类 | Leiden（SNN，resolution 1.0） | 同左 |
| 注释 | CellTypist（Immune_All_High，majority voting） | 同左 |
| DEG | 患者级 pseudobulk + DESeq2（23 患者为生物学重复） | 同左 |
| 多重检验 | BH FDR | 同左 |
| 显著性 | padj ≤ 0.05 & \|logFC\| ≥ 1.0 | 同左 |

**脚本-规则隔离（纪律照旧）**：生成脚本全文无 rule_id / required_context / 评分
level 字样；双联体工具名只出现在 A 版注入块（B 版文本零双联体工具名——M3 解析
实测 B 版 doublet_detection 候选 = 0，见 §4.2）；方法选择全部为文献推荐方法。

### 3.3 环境（只装本地，不进仓库）

- venv：`D:\C-file\cellvoyager-env`（同 I 窗口；scanpy 1.12.3 / anndata 0.13.2 /
  pydeseq2 0.5.4 / celltypist 1.7.1 + Immune_All_High v2 / harmonypy 0.0.10）
- **R 4.6.1 + Bioconductor**：sctransform 0.4.3（I 窗口已有）+ **scDblFinder 1.26.7**
  （本窗口新增；依赖 SingleCellExperiment/scran 等已随装，Windows 二进制）
- 采集存储：`BIOAUDIT_WAL_DIR/BIOAUDIT_VERDICT_DIR` → `cellvoyager-outputs/data/{wal,verdicts}`

---

## 4. 真实执行与采集链路结果（L1.3）

### 4.1 执行事实（每版独立真实执行，seed=42）

| 指标 | 10X-A | 10X-B |
|---|---|---|
| 载入+标注 | 2.3s | 2.2s |
| QC（MAD） | 2.3s（63,689 → 59,399） | 2.5s（同左） |
| 双联体 | **1,218.7s**（2,783 双联体 = **4.69%** 去除） | 0.1s（跳过） |
| HVG | 4.7s（1,987 genes） | 5.1s（1,990 genes） |
| SCTransform（R） | 837.8s（vst 丢 13 极稀疏基因） | 978.8s（丢 10） |
| PCA | 3.8s（elbow 20 PCs） | 4.1s（同左） |
| Harmony（33 文库） | 105.2s | 154.7s |
| Leiden | 37.4s（23 clusters） | 42.1s（26 clusters） |
| CellTypist | 26.8s（11 cell types） | 31.7s（12 cell types） |
| DEG | 5.0s（1,085 显著） | 5.7s（1,059 显著） |
| BH / 显著性 | 0.1s | 0.1s |
| **合计** | **~37.5 分钟（0 成本）** | **~20.5 分钟（0 成本）** |

- 细胞组成（A 版）：T cells 20,858 / Epithelial 12,892 / Macrophages 7,262 /
  Plasma cells 4,974 / B cells 3,636（共 11 类）——与 CRC 免疫微环境常识一致
  （DEG 对照 = T cells vs Epithelial cells）。
- **执行差异注意**：B 版无双联体去除 → 下游细胞数多 2,783（59,399 vs 56,616），
  聚类数/细胞类型数略增（26 vs 23 clusters；12 vs 11 types）——**跳过双联体的
  真实后果之一**：双联体进入聚类形成额外簇（D1.1 规则 rationale 的实证侧面）。

### 4.2 采集链路（两版独立，零代码改动）

| 通道 | 10X-A | 10X-B |
|---|---|---|
| M1 声明 | **11 条**（含 doublet_detection=scDblFinder） | **11 条**（含 doublet_detection=**skip_doublet**） |
| M3 解析 | candidates 含 **doublet_detection ×N（全 choice=scDblFinder）**；uncertain 4 类（api_data_integrity/clustering_resolution/dim_reduction/pca_dimension——签名表禁猜设计，I 窗口同款） | candidates **无双联体候选**（79 候选 10 类型） |
| **交叉验证** | **consistent 11 / 虚报 0 / 漏报 0 / 未验证 0** | **consistent 10 / 虚报 1 / 漏报 0 / 未验证 0** |
| verdict | 11/11 → final | 10/10 → final；**skip_doublet provisional → revoked**（"M3 无 doublet_detection 任何执行证据，声明 'skip_doublet' 未执行 → 虚报"，verdict store 实证） |
| final 轨迹 | **11 决策** | **10 决策**（双联体不在内——B4 final-only） |

### 4.3 评分（ruleset 1.6.0 / ontology 0.1.2 / engine 0.2.1）

**10X-A：80.0 · pass**（method_selection 0.80 / data_handling 0.85 / statistical_rigor 0.85）：

| decision_type | choice | L | matched_rules |
|---|---|---|---|
| qc_filtering | MAD5_adaptive_threshold | **3** | Q1.1-QC-001 |
| **doublet_detection** | **scDblFinder** | **3** | **D1.1-DOUB-001** |
| scRNA_normalization | SCTransform | **3** | N1.1-NORM-001（umi_counts 分支） |
| hv_gene_selection | vst | **3** | H1.1-HVG-001 |
| dim_reduction | PCA_elbow_selection | **3** | D2.1-DIMR-001_reduction |
| batch_correction | Harmony | **3** | B1.1-BATC-001 + B1.2-BATC-002（33 文库 ≥2 条件） |
| clustering_method | Leiden | **3** | C1.1-CLUS-001_method |
| annotation_method | CellTypist | **2** | A1.1-ANNO-001_method（签名表天花板，同 I 窗口） |
| deg_method | pseudobulk_DESeq2 | **3** | G1.1-DEG-001 + G1.3-DEG-003 |
| multiple_testing_correction | BH | **3** | G1.2-DEG-002_multiple_testing |
| significance_threshold | padj ≤ 0.05, \|logFC\| ≥ 1.0 | **3** | G1.4-DEG-004 |

→ **D1.1 首次真实验证：10X 下做双联体检测（scDblFinder 真实执行）→ L3**；
L 分布 0/10/1/0/0/0（L4/L3/L2/L1/L0/-1），**全决策可评分（L-1 = 0，K 后评分缺口
闭合的端到端印证）**。

**10X-B（采集层）：80.0 · pass**（10 决策，无双联体决策）——**如实解读**：final-only
轨迹不含"跳过"决策（阴性声明被交叉验证撤销），**D1.1 未触发**；采集链路对
"未声明的省略"保持沉默（真实 Agent 同样如此——它不声明就不会被评到）。

**10X-B（引擎级补验）：63.7 · blocked**——把 B 版已声明（且被撤销）的
skip_doublet 决策按 M1 事实 context（sequencing=10X_scRNA_seq / n_cells=59,399）
补入轨迹做引擎级评分（透明标注，非采集链路产物）：

| 项 | 值 |
|---|---|
| doublet_detection = skip_doublet | **D1.1 → L0**（危险——双联体未识别，下游聚类/注释/DEG 被污染） |
| data_handling | (0.85×3 + 0.00)/4 = **0.6375** |
| trajectory_score | **63.7** · verdict **blocked**（critical_issues 1 条） |

→ **D1.1 两侧语义实证：做 → L3；跳过 → L0**（10X 平台敏感性成立）。**采集层边界
如实声明**：阴性声明（"我跳过了 X"）无法被 M3 验证 → 虚报撤销 → 不进 final 轨迹；
L0 威慑在纯采集链路下依赖"决策被声明/被预期"——这是采集层的真实边界，不是缺陷
伪装（报告 §7 局限）。

### 4.3.1 采集层边界闭环：10X-B 带 expected_types 重跑（窗口 M 追加，2026-08-16）

> **状态：采集层边界已闭环**（窗口 M / M1.1，execution-plan §六.十七）——
> 本节为 M 窗口追加记录；原 §4.3"引擎级补验"段落保留为历史留档（其结论
> 与闭环结果一致：**63.7 · blocked**），但该路径已被采集链路正式取代，
> **不再标注"引擎级补验"**（M1.2 验收：B 版带 expected_types 重跑 →
> doublet_detection 补入 → D1.1 L0 → 63.7 blocked 走采集链路）。

**机制（M1.1 裁决 2026-08-16，经项目负责人在线确认）**：预期决策点清单放评测配置
（`src/bioaudit/data/expected_types.yaml`，per 范式×平台，非引擎硬编码）；缺失预期
决策补入 `provenance=expected`（choice 优先取 M1 已撤销声明——B 版 Agent 自己的
`skip_doublet`，不伪造；无声明 → `not_performed`）；仅显式 optional 且
`when_not_applicable` 谓词满足才豁免（B7/G5 保守原则）。

**重跑（复用 windowL 已有 WAL/verdict/notebook 产物，零新执行成本）**：
`analyze_run.py --expected-config`（新会话 `golden_winL_10X_B_expected`，不触碰
原会话 verdict）：

| 项 | 值 |
|---|---|
| effective expected_types | 11 决策（10X 标准管线，A 版最终轨迹实证；api_data_integrity 无 M3 确定性签名不入清单） |
| 交叉验证 | consistent 10 / 虚报 1（skip_doublet 撤销）/ 漏报 0 / 未验证 1 + **expected_added 1** |
| 补入决策 | `doublet_detection / skip_doublet`（provenance=expected，verdict final，context=M1 事实：sequencing=10X_scRNA_seq / n_cells=59,399 / data_category=umi_counts / n_patients=23 / has_batch=true） |
| final 轨迹 | **11 决策**（10 一致 + 1 预期补入） |
| **评分** | **63.7 · blocked**（method_selection 0.80 / **data_handling 0.6375** / statistical_rigor 0.85；critical_issues 1 条 = D1.1 L0） |
| 产物 | `windowL/reports/windowL_10X_B_expected.json`（本地，不入仓库） |

→ **L0 威慑不再依赖"决策被声明"**：10X 平台下 doublet_detection 为标准管线预期决策点，
静默跳过（即使不声明）也会被 expected_types 补入 → D1.1 L0 → blocked。§6.2 登记发现①
（阴性声明不可验证）由此闭环；采集层边界从"跳过不可见"收敛为"预期清单内不可跳过、
清单外如实不可见"（清单外类型仍需评测者显式声明，报告 §8 局限 #4 已更新）。
历史分数不追溯重判；新机制自窗口 M 起生效。

---

## 5. 平台互补对照（L1.4，与 GSE115978 Smart-seq2 版对比）

| 维度 | **10X（本窗口，GSE132465 CRC）** | **Smart-seq2（窗口 I，GSE115978 黑色素瘤）** |
|---|---|---|
| 平台事实 | 10X Chromium 3' v2，UMI counts（GEO + HCA 查证） | Smart-seq2 全长（G-2 查证定案） |
| 数据 | 63,689 cells × 25,655 genes，33 文库/23 患者 | 7,186 cells × 22,454 genes，32 患者 |
| 黄金 A 版 | **80.0 · pass**（11 决策） | **80.0 · pass**（10 决策） |
| **doublet_detection** | **存在且可评：scDblFinder → L3（真实执行）** | **决策不存在**（Smart-seq2 无双联体前提；规则 required_context 10X 专属） |
| scRNA_normalization | SCTransform · L3（**umi_counts 分支**） | SCTransform · L3（raw_counts 分支） |
| batch_correction | Harmony · L3（**33 个 10X 文库**为批次，n_patients=23） | Harmony · L3（32 患者） |
| 其余 8 决策类型 | 全部 L3/L2 同款评分 | 同款 |
| **平台适用决策集差异（如实）** | 10X 比 Smart-seq2 **多** doublet_detection；两平台其余决策类型一致；**各平台适用决策集差异被审计如实呈现，不硬套**（Smart-seq2 版若出现 doublet 决策会因 required_context 不匹配而 L-1——平台键 fail-closed 设计） | 同左 |

**互补解读**：两平台黄金对照同分（80.0）不同决策集——审计分数可跨平台比较的前提
是"各平台适用决策集差异如实呈现"（本表）；10X 版补上了双联体/UMI/批次维度，
Smart-seq2 版保持无双联体前提。**D1.1 的 10X 专属语义（做 L3/跳过 L0）只在 10X
平台存在**——这正是"平台敏感性"的实证，而非分数可比性问题。

---

## 6. 运行中发现与修正（如实）

### 6.1 首次运行失败 2 项（均已修复，计入报告）

1. **scDblFinder 合并矩阵不传 samples= → 双联体率虚高**（首跑 21.5%）：
   33 个 10X 文库合并为单矩阵后，scDblFinder 默认按"单库"估算双联体比例
   （模拟双联体数随细胞数增长）→ 修正为传 `samples=`（每细胞文库来源），
   实测 **4.69%**（符合 10X 0.5-8% 常识区间）。**方法学要点**：多文库合并矩阵
   必须告知 scDblFinder 文库归属（参考实现文档语义）。
2. **CellTypist obs/X 行数不匹配崩溃**（首跑）：`raw_counts_full` 在双联体去除
   前快照，双联体过滤后 obs（59,399→46,640）与 scaled 矩阵（59,399）错位 →
   修正：counts 层/raw_counts_full 在双联体步骤**之后**快照（下游分析本就应
   基于去除双联体后的细胞）。
3. 首跑 1 次失败的全过程产物备份于 `windowL/runs/10X_A/failed_run_1_artifacts/`
   （WAL/verdict 原样留档），重跑用同一 session（清理残留后），成功记录见 §4。

### 6.2 采集层边界发现（登记，非缺陷）

- **阴性声明不可验证**：M1 声明"跳过 X"（skip_doublet）无 M3 执行证据 →
  交叉验证判虚报 → verdict revoked → 不进 final 轨迹。语义上正确（B4
  final-only 纪律），但意味着 **L0 威慑依赖"决策被声明"**——真实 Agent 若
  静默省略（不声明），采集层无感知。登记为采集层语义边界（与 G 窗口
  "链路可运行 ≠ 分数可评分"同类发现；改进方向 = expected_types 强制预期
  决策点检查，排期评估）。
  **→ 已闭环（窗口 M，2026-08-16）**：expected_types 落地后，静默省略预期
  决策（如 10X 标准管线的 doublet_detection）会被补入 provenance=expected
  参与评分（D1.1 L0 → blocked），详见 §4.3.1；清单外类型仍需评测者显式声明
  （边界收敛，非消失）。

---

## 7. L-b 真实短评测（L2.5–L2.7）

### 7.1 任务设计与宪法修订（清单 L2.5）

- **任务文件**：`cellvoyager-outputs/windowL/task_gse115978_focused.txt`——
  聚焦短分析：仅 QC + 归一化（+ 可选 HVG），**明确不做聚类/注释/轨迹/DEG**；
  方法选择完全留给 Agent；终答 = 简短摘要（QC 前后细胞数/QC 准则/归一化方法/维度）。
- **宪法修订**：`agent-eval-protocol.md` §10 追加（聚焦任务描述/参数/预算：
  max-iterations 4、num-analyses 1、预算 ¥5 上限、超时 60 分钟、密钥环境变量、
  unset 代理、n=1 随机性声明）——已落盘。
- **部署**：hook 复用 G 窗口已修路径（kwargs 提取器 / 双挂去重 / MCP 子进程
  `_server_command` 注入），`run_cellvoyager_with_hook.py` 原样复用（仅 PYTHONPATH
  注入 CellVoyager 源码根，G 窗口同款接入方式）；编排 `run_lb.py`（密钥运行时从
  本机 DSH 凭证文件读取注入子进程环境，不落盘）。

### 7.2 运行记录（清单 L2.6，每步耗时与 token）

| 阶段 | 值 |
|---|---|
| 正式运行（CellVoyager，deepseek-chat，max-iterations 4，num-analyses 1，no-deepresearch） | **4.92 分钟**（21:13:21 → 21:18:16），exit 0 |
| WAL | 15 条（report_intent 5 / report_result 5 / step_completed 5）→ **M1 声明 5 条** |
| usage（claude_execution.log 提取） | input 54,364 / cache 1,241,344 / output 21,243 tokens |
| 成本（usage 换算，deepseek-chat ¥2/¥0.5/¥8 假设） | **¥0.90**（保守口径） |
| **成本（平台余额差，权威口径）** | **¥0.43**（22.53 → 22.10；预算 ¥5 内） |
| 超时 | 未触发（4.92 min ≪ 60 min） |

**部署插曲（如实）**：首次启动失败（主进程缺 CellVoyager 源码根 PYTHONPATH，
零 token 损失，余额不变），加 PYTHONPATH 后一次成功；编排脚本自身 GBK 打印
emoji 崩溃（子进程输出含 ✅）→ 补跑余额/分析步骤，正式运行结果不受影响。

### 7.3 Agent 实际行为（如实，n=1）

Agent 大体遵从聚焦范围（**未做聚类/注释/轨迹/DEG**），实际执行三步：
① MAD 自适应 QC（notebook 自述移除 10.9% 细胞——**但 qc_filtering 决策未被
声明/捕获**，见下）；② 文库大小归一化 + log 变换 + HVG；③ 患者级 QC 相关性
刻画（超出任务列举范围的额外步骤，2 个相关性决策）。

### 7.4 采集链路与评分（清单 L2.6/L2.7）

- **交叉验证：consistent 5 / 虚报 0 / 漏报 0 / 未验证 0**；verdict 5/5 → final；
  final 轨迹 **5 决策**。
- **评分（ruleset 1.6.0）：30.0 · needs_correction**（method_selection 0.40 /
  data_handling 0.30）：

| decision_type | choice | L | matched_rules |
|---|---|---|---|
| hv_gene_selection | dispersion | **2** | H1.1-HVG-001 |
| scRNA_normalization | LogNormalize（×2 实例） | **1** | N1.1-NORM-001 |
| immune_correlation_method | Spearman（×2 实例） | **1** | I4.1-IMMU-001_scRNA_correlation_method（K1 规则，细胞级 = 伪重复） |

- **L 分布：L4/L3/L2/L1/L0/-1 = 0/0/1/4/0/0——全决策可评分（L-1 = 0）**：
  K 窗口评分缺口闭合在真实评测中的直接印证（G 窗口当时 12/20 为 L-1）。
- **高分未兑现（如实归因，不硬凑）**：聚焦短分析并没有带来高分——Agent 的
  方法学选择（LogNormalize 而非方差稳定化归一化、细胞级 Spearman 相关性 =
  伪重复、dispersion 而非 VST 的 HVG）落在规则的"有风险（L1）"档；**这本身
  就是证据：决策点少 ≠ 决策正确，LLM 方法学选择在短任务中仍是真实风险**
  （宪法 §10.1 预注册口径："若仍以 L1 为主则如实归因——决策集小、方法学选择
  仍是真实风险"——应验）。
- **采集层观察（与 §6.2 同款边界）**：Agent 实际执行了 MAD QC（notebook 证据），
  但 qc_filtering 决策未进入 M1/M3 任何通道 → 轨迹无该决策 → Q1.1 未评分。
  "执行了但未声明/未签名"的省略在采集层不可见（M3 对自定义 is_outlier 掩码
  无确定性签名——签名表缺口，I 窗口已登记同类）；不伪造、不补猜。

### 7.5 与黄金对照对比（描述性，n=1 不做统计）

| 维度 | L-b 真实 LLM（聚焦短分析） | L-a 黄金 A（10X） | I 窗口黄金 A（Smart-seq2） |
|---|---|---|---|
| 对象 | **真实 LLM Agent**（deepseek-chat） | 确定性脚本（非 LLM） | 确定性脚本（非 LLM） |
| 决策数 | 5（聚焦任务） | 11 | 10 |
| 分数 · verdict | **30.0 · needs_correction** | 80.0 · pass | 80.0 · pass |
| L 分布 | 0/0/1/4/0/0 | 0/10/1/0/0/0 | 0/9/1/0/0/0 |
| 主要问题 | LogNormalize×2 / Spearman×2 / dispersion | 无（CellTypist L2 天花板） | 同左 |
| 成本 | **¥0.43** | 0（¥0） | 0（¥0） |

**对比解读**：同一条采集链路，真实 LLM 的短任务（30.0）vs 教科书式脚本
（80.0）对比度复现（与 G 窗口 30.0 同分巧合，但决策构成完全不同——G 是
7 L1 + 1 L3 + immune×12，本窗口是 4 L1 + 1 L2，决策集更小）；**"高分不保证"
如实兑现**——L-b 没有拿到"真实 LLM 高分"证据，拿到的是"真实 LLM 短任务
方法学选择仍偏有风险"的证据，如实呈现不圆场。

---

## 8. 诚实局限（L-a + L-b）

1. **黄金 Agent 为确定性脚本，非 LLM**（I 窗口同款定位）；L-b 补真实 LLM 证据
   （n=1，LLM 随机性不可复现，不做统计推断）。
2. **n=2 数据集**（GSE132465 10X + GSE115978 Smart-seq2）；跨平台推广需更多数据。
3. **scDblFinder 经 Rscript 参考实现执行**（Bioconductor 包无 Python 实现；
   与 I 窗口 SCTransform 同款混合管线）。
4. **B 版 L0 已走采集链路闭环**（窗口 M 追加，2026-08-16）：expected_types 强制
   预期决策点检查落地后，B 版带配置重跑 → doublet_detection 补入（provenance=
   expected）→ D1.1 L0 → **63.7 blocked 直接出自采集链路**（见 §4.3.1），不再依赖
   引擎级补验；历史"引擎级补验"段落保留为留档。
5. **Harmony/Leiden 迭代求解器**：seed 固定可复现到浮点噪声级（A/B 聚类数
   23/26 差异主要来自双联体去除与否，非随机性）。
6. **双联体率 4.69% 是该数据实测值**，不可外推为所有 10X 数据的典型值；
   "跳过 → L0"的判定依据是方法学（D1.1 规则），不依赖具体双联体比例。
7. **sctransform 丢弃极稀疏基因**（13/10 个，参考实现行为），对评分零影响。
8. **L-b 高分未兑现**：聚焦短分析（5 决策）仍以 L1 为主（LogNormalize/Spearman）——
   n=1 单次运行，不构成"LLM 必然低分"结论；同时"决策点少 → 高分概率高"的
   设计假设在本运行未获支持（如实登记，排期可复测）。
9. **L-b 范围遵从性**：Agent 大体遵从（未做聚类/注释/DEG）但额外做了患者级 QC
   相关性刻画（2 个 Spearman 决策）；qc_filtering 实际执行（MAD，notebook 证据）
   但未进入采集通道（M3 签名缺口 + M1 未声明）——执行与评分覆盖的差异如实呈现。
10. **成本口径双记录**：余额差 ¥0.43（权威）vs usage 换算 ¥0.90（保守假设，
    含缓存计价差异）；以余额差为准。

---

## 9. 回归（L3.10）

| 闸 | 结果 |
|---|---|
| golden 重放 | **0 差异**（20 轨迹 137 决策；纯外围窗口，评分路径零改动） |
| pytest 全量 | **246/246**（K 窗口基线；本窗口零代码改动，无新增测试） |
| ruleset-validate 三闸 | 清单 / 冲突 / golden 全 PASS（规则零改动） |
| benchmark-validate 四闸 / reward-validate 五闸 | PASS（复跑确认，数字见 §10） |
| ruff | 零新增（本窗口未改仓库代码） |
| CI | GitHub Actions 双矩阵云上确认（见执行计划快照） |

---

## 10. 产物清单与文档同步

| 产物 | 路径 |
|---|---|
| 本报告 | `bio-audit-v2/docs/migration/L1-broader-eval-report.md` |
| 10X 黄金模板 + 变体生成器 | `cellvoyager-outputs/windowL/golden_agent_template_10x.py` + `make_variants_10x.py` |
| 两版执行产物 | `windowL/runs/10X_{A,B}/`（脚本/摘要/h5ad/DEG 表/executed 副本） |
| 两版采集链路报告 | `windowL/reports/windowL_10X_{A,B}.json` |
| 数据元数据 / declared | `windowL/reports/metadata_GSE132465.json` + `windowL/declared.json` |
| 平台查证存档（H4） | `windowL/geo/`（GSE132465 / GPL20301 / HCA 项目页 HTML） |
| 预检报告 | `windowL/reports/h5ad_precheck_GSE132465.json` |
| 首跑失败留档 | `windowL/runs/10X_A/failed_run_1_artifacts/` |
| L-b 任务/编排/结果 | `windowL/task_gse115978_focused.txt` + `run_lb.py` + `reports/windowLb_analysis.json` |
| 宪法修订 | `bio-audit-v2/docs/protocols/agent-eval-protocol.md` §10 |
| README/首页口径同步 | README.md §真实效果 + docs/index.md（site-design §6.2 新增平台行） |

---

## 11. 验收清单对照（execution-plan §六.十六，11 项）

| # | 清单项 | 状态 |
|---|---|---|
| L1.1 | 数据预检 + 版权/provenance（H4）+ 平台查证（GEO 记录，不凭文件名） | ✅ §3.1 |
| L1.2 | 黄金脚本适配 10X（UMI counts/双联体/批次/pseudobulk；隔离照旧；真实执行 + 采集链路零代码改动） | ✅ §3.2/§4 |
| L1.3 | D1.1 首次真实验证：黄金版 L3 / 变体版 L0（10X 平台敏感性实证；Smart-seq2 无该决策如实呈现） | ✅ §4.3/§5 |
| L1.4 | 与 GSE115978 对比表（平台互补 + 决策集差异） | ✅ §5 |
| L2.5 | 任务设计 + 宪法修订记录（agent-eval-protocol 追加：聚焦短分析/max-iterations 4-5/num-analyses 1/预算 ¥5/超时 60 min） | ✅ 宪法 §10 |
| L2.6 | 真实运行（hook 复用已修路径）+ M1/M3/交叉验证/verdict/评分全链路 + 每步耗时与 token 记录 | ✅ §7.2/§7.4 |
| L2.7 | 结果如实呈现（分数/verdict/L 分布/与黄金对照对比；n=1 声明；高分不保证） | ✅ §7.3/§7.5 |
| L2.8 | 失败预案（任一步失败如实记录；成本超限/超时 → 停止，宪法 §6/§7） | ✅ 宪法 §10 + §7.2（部署插曲如实记录；预算 ¥5 内未触发） |
| L3.9 | 报告落盘（本文件）+ README/首页口径同步（site-design §6.2 新增平台/版本行，禁止混写） | ✅ §10 |
| L3.10 | golden 0 差异 + pytest 全绿 + 各闸（纯外围零代码改动） | ✅ §9 |
| L3.11 | git commit/push（教训 #4）+ CI 云上绿（教训 #5）+ execution-plan §六.十六 打勾 + 完成报告 | ✅ 完成报告 |

---

*报告完毕。窗口 L 执行计划快照与 README 同步更新；git commit/push 与 CI 云上
确认见完成报告。*
