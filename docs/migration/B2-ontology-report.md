# B2 完成报告（阶段 1 · 本体落地）— 2026-08-13

> 执行窗口 B · B2：34 决策类型定义 + P1 校验器三职责 + aliases + internal_ref + 引擎接线。
> 依据：ontology-design-v1（定稿）、refactor-plan-v1.1（A/G/D/P 组裁决）、
> diagrams/2026-08-13-decision-type-ontology.md（34 类型图）、execution-plan-v1（§五 快照）。
> 验收：ontology 目录完整 + 校验器三职责可运行 + 引擎读本体 + **golden 0 差异**（137 决策）。

## 一、产出清单

```
src/bioaudit/ontology/                  # ★ 本体（单一事实源，包内锚定）
├── paradigms.yaml                      # 3 范式；bulk-DEG 标注"骨架待补全"（§二.4）
├── stages.yaml                         # 6 阶段（data-acquisition→conclusion）
├── aliases.yaml                        # 3 组同源声明（filtering↔qc_filtering、
│                                       #   normalization↔scRNA_normalization、
│                                       #   deg_method 仅 homology_note）
├── input_synonyms.yaml                 # 匹配通道同义映射（原 type_aliases.yaml 移入）
├── topics.yaml                         # 8 主题族（一致性/QC/注释/预后/富集/免疫/轨迹/聚类）
├── backlog.yaml                        # 待补清单（G6 DEG 方向性 + G2 基因组/注释/marker 版本）
├── loader.py                           # Ontology 加载/查询（加载期结构校验）
├── validator.py                        # ★ P1 校验器三职责
└── decision_types/                     # ★ 34 个决策类型定义（样板 = deg_method）
    ├── filtering / normalization / deg_method / multiple_testing_correction /
    │   significance_threshold          # bulk-DEG 5（pan-cancer 超集共享）
    ├── cbioportal_projection / gsea_background / enrichment_correction /
    │   immune_correlation_method / purity_confounding / cox_ph_assumption /
    │   events_per_variable / independent_prognostic_claim / ic50_sample_size /
    │   expression_survival_consistency / immune_expression_consistency   # pan-cancer +11
    └── api_data_integrity / qc_filtering / qc_mito_threshold / doublet_detection /
        scRNA_normalization / hv_gene_selection / batch_correction / dim_reduction /
        pca_dimension / clustering_method / clustering_resolution / trajectory_inference /
        trajectory_validation / annotation_method / annotation_validation /
        cluster_annotation_consistency / annotation_deg_consistency /
        trajectory_annotation_consistency                                # scRNA +18

引擎接线（本体化，行为等价）：
├── engine/aggregator.py                # 删 TYPE_TO_DIMENSION 硬编码 → 本体 dimension
├── engine/error_tracer.py              # 默认依赖图 → 本体 depends_on（兼容旧文件参数）
├── engine/matcher.py                   # 归一化 → 本体 input_synonyms；同源注释
│                                       #   homologous_types + unclassified 标记
├── models/decision.py                  # ParsedStep + homologous_types / unclassified
├── cli.py                              # + bio-audit validate-ontology
└── scripts/validate_ontology.py        # CLI 薄包装
```

## 二、决策类型定义要点（v1.1 裁决逐项落地）

| 裁决 | 落地 |
|------|------|
| A4 | deg_method 样板 `design` 键 `missing: fail-closed`（样板原 skip 已改） |
| A2 | 罚分规则（level_0/1 非空）引用的键一律 fail-closed/skip；`analysis_type`/`integration_type`/`data_source`/`has_batch` 等均按此定档；校验器对 fail-open 键 × 罚分规则做交叉检查（合成违例测试证明可检出） |
| A5 | missing 三档全部使用：fail-closed ×57 / skip ×5 / fail-open ×12（三档语义已声明，引擎运行时强制属 H7 重补轨迹后阶段，不在 B2 改变评分） |
| G1 | 一致性族 5 成员全部带 `internal_ref`（联合上游决策评分，机制阶段 2+ 落地） |
| G2/G8 | 校验器"流程正推 vs 规则反推"对比：范式声明阶段 vs 类型推导阶段（发现并修正 pan-cancer 声明含 data-acquisition 的不一致）；bulk-DEG 骨架标记持续对照；待补清单 backlog.yaml |
| G3 | `unit` 键（cell/sample/pseudobulk/生物·技术重复）覆盖 4 个分析单位敏感类型：deg_method（伪重复之根）、scRNA_normalization、batch_correction、doublet_detection |
| G4 | batch_correction 增加 `confound` 键（none/batch/patient/library_prep/site） |
| G5 | 16 个可选类型全部带 `when_not_applicable` 适用性谓词（含一致性族 claim_not_made、batch_correction single_sample_or_no_batch 等） |
| D2 | 冲突完整性检测运行：**现存 2 处 finding**（见 §五遗留） |
| P1 | 校验器三职责可运行（覆盖报告 / 语义边界 / 冲突完整性） |

## 三、P1 校验器三职责（验收项 2）

`bio-audit validate-ontology`（或 `python scripts/validate_ontology.py [--json]`）：

1. **覆盖报告**：34 类型 × 3 范式 × 6 阶段矩阵；范式声明阶段 vs 类型推导阶段；
   规则反推（38 唯一规则的全部 decision_type ∈ 本体，**0 缺失**）；
   本体→规则（34 类型全部有规则覆盖，0 待补）；backlog 待补清单展示。
2. **语义边界**：missing 三档合法性与使用分布；A4 design fail-closed；
   A2 罚分规则禁 fail-open（含合成违例检出测试）；G3 unit / G4 confound / G5 谓词；
   depends_on / aliases / internal_ref 不悬空；aliases 对称性（per-type ↔ aliases.yaml）。
3. **冲突完整性**：同 decision_type + 同 choice（归一化）不同 level 检出——
   现存 2 处：`deg_method/mast`（G1.1 L1 vs G1.3 L2，scRNA 内真实不一致）、
   `multiple_testing_correction/bonferroni`（G1.2 L2 vs M1.2 L1，跨范式）。
   运行时不受影响（strictest 取分 + 按范式 registry 隔离），作为规则库评审条目挂账。

校验结果：**0 错误 / 1 警告**（bulk-DEG 骨架待补全，预期内）。

## 四、引擎接线（验收项 3）与 golden 回归（验收项 4）

- 聚合器：`TYPE_TO_DIMENSION` 硬编码（34 条）删除，dimension 从本体读取；
  **34 类型维度逐一与旧硬编码相同**（tests/test_ontology.py 冻结守卫）。
- error_tracer：依赖图从本体 `depends_on` 组合；旧 dependency_graph.yaml 3 条 DEG 边
  逐条保留（superset 守卫测试）；scRNA/pan 新增边（如 qc_filtering→deg_method），
  修复旧图"缺失"问题（ontology-design-v1 §五），仅影响错误链报告，不影响评分。
- matcher：归一化映射从本体 input_synonyms 读取（与旧 type_aliases.yaml 8 条目
  一一对应，行为不变）；同源声明仅作注释（`ParsedStep.homologous_types`），
  明确**不是匹配通道**（§二.1，防 qc_filtering→filtering 误归一化）；未知类型
  → `unclassified: true`（§五，评分仍走 -1 无法评估，不改评分）。
- **golden 重放：20 轨迹 / 137 决策 / 0 差异**（权威基线 + 仓库副本；无需更新基线，
  无漂移）。pytest **38/38 通过**（原 12 + 新增 26）；异 cwd 路径锚定测试通过；
  72/72 数据文件与 asset_manifest.json 哈希一致（B2 未改动任何冻结资产）。

## 五、遗留项（挂账，不阻塞 B2 验收）

1. **D2 冲突 2 处修复**：deg_method/mast（G1.1 vs G1.3）、
   multiple_testing_correction/bonferroni（G1.2 vs M1.2）。~~建议随 B5 规则治理窗口
   一并裁决（改规则文本或声明 paradigm 隔离理由）。~~
   ✅ **已在 B5 窗口裁决（2026-08-14）**：裁决 1 = G1.3 修订（裸 MAST L2→L1，与 G1.1 对齐）；
   裁决 2 = 范式隔离成立（检测器升级为范式感知 same-rule-set）。冲突数归零，golden 0 差异。
   裁决书：docs/specs/2026-08-14-d2-adjudication.md。
2. **missing 三档运行时强制**（A1-A5 交互规则）未接入 evaluator：本体已声明语义，
   引擎强制需配合 H7 重补轨迹（部分决策会转"未验证"）——排期阶段 1 后半段，
   届时 golden 基线按 v1.1 C4/H1 流程更新并记录漂移原因。
3. **unclassified 待补清单登记**：matcher 已标记未知类型，写入规则库待补清单的
   自动化接线留待 B5 规则治理。
4. **校验器进 CI**（v1.1 D1）：`validate-ontology` 已可脚本化（--json 输出），
   CI 门槛接线排期 B6 回归体系。
5. 一致性族 internal_ref 联合评分机制（G1）阶段 2+ 落地（当前仅 schema 声明）。

## 六、验收对照

| 验收项 | 结果 |
|--------|------|
| ontology 目录完整（paradigms/stages/34 定义/aliases/校验器） | ✅ 34/34 定义，必填键全齐，ID 唯一 |
| 校验器三职责可运行 | ✅ `validate-ontology` exit 0；覆盖/语义/冲突三节输出 |
| 引擎读本体（dimension/depends_on/aliases） | ✅ 硬编码删除；接线测试 + 等价性守卫 |
| golden 0 差异（137 决策） | ✅ 0 差异，无需更新基线（无漂移） |
