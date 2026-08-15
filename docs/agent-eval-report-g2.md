# 窗口 G-2 补充报告：评测缺口修复（declared 注入 + 规则平台键放宽 + 重评）

> **日期**：2026-08-16（窗口 G-2）
> **性质**：对窗口 G 真实评测的修复与重评（零成本——只跑本地审计引擎 + 已有运行产物，
> **不重跑 Agent、不手工编轨迹**）
> **宪法**：`docs/agent-eval-protocol.md`（v1.0，本报告为 G-2 补充）
> **对应验收**：execution-plan-v1 §六.十二 G2-a/b/c/d（13 项，本窗口已冻结）
> **主报告（旧版留档）**：`docs/agent-eval-report.md`（窗口 G，2026-08-16，不修改结论）

---

## 1. 背景与问题

窗口 G 真实评测链路全通（M1×M3 20/20 一致，成本 ¥2.55），但**分数全 L-1 不可用**：
规则 required_context 硬依赖 `sequencing: 10X_scRNA_seq`，采集三级可信源均拿不到
→ 键 unverified → 规则不匹配 → 全部"无法评估"。暴露规则层与采集层的接口缺口
（agent-eval-report.md §7/§8 修复清单：declared 注入 + 规则平台键评估）。

**分水岭事实（G2-b 项 5，查证定案）**：GSE115978（Jerby-Arnon 2018, Cell, PMID 30388455）
为 **Smart-seq2**（GEO 官方 Overall design 原文："profiled with a modified full length
SMART-Seq2 protocol"）——因此 **declared 注入 `10X_scRNA_seq` 是错的**；正确做法 =
declared 注入 `smartseq2` + 规则平台键放宽接受 smartseq2。查证过程与存档见
`docs/migration/G2b-platform-key-review.md` §1。

---

## 2. G2-a：declared 上下文注入（采集层）

**四级可信源定稿**：`call_arg > data_metadata > declared > unverified`。

| 项 | 内容 |
|---|---|
| declared 来源定义 | **只允许来自评测者/数据事实**——运行宪法/评测配置注入（如数据集平台）；**与 Agent claim（M1 声明）严格区分：Agent 上报的键永远不进 declared**（纪律 1） |
| 链路落地 | `M3Parser(declared=...)`（已有参数，语义修订为评测者注入）；`make_cellvoyager_hook(declared=...)`（hook 链路）；CLI `parse-notebook --declared`（已有）+ **`cross-validate --declared`（本次新增）** |
| missing 交互 | declared 提供 schema 键 → 该键进入 context（`context_trust=declared`），**不再 unverified**（G2-a.2） |
| 信任排序守卫 | declared 不能覆盖 call_arg/data_metadata（严格排序，禁止跳级） |
| 声明文件（重评用） | `cellvoyager-outputs/reports/gse115978_declared.json`：`{"sequencing": "smartseq2", "data_category": "raw_counts"}`（含来源注记，评测者署名） |
| 测试 | `tests/test_declared_eval.py` **12 项**：declared→规则匹配（验收项 3 直接测试）、缺键仍 L-1 回归守卫、10X 仍命中、信任排序、unverified 清除、CLI 接线 |

**验收项 3 实测**：`qc_filtering` + declared `sequencing=smartseq2` → Q1.1-QC-001 匹配 → L1
（此前同输入为 L-1 无法评估）。

---

## 3. G2-b：规则平台键审查 + 修订（B5 三闸 + semver）

审查报告（22 条 scRNA 规则逐条判定）：**`docs/migration/G2b-platform-key-review.md`**。
汇总：过强放宽 **17 条**（sequencing 16 条 + N1.1 data_category 1 条）；**D1.1 双联体
保留 10X 专属**（纪律 5：双联体是液滴平台问题，Smart-seq2 板式 FACS 分选无此前提）；
无平台依赖 4 条（A1.1-API + S1.x 一致性族）不动。

| 修订 | 内容 |
|---|---|
| 规则 YAML | 17 个文件：`sequencing: [10X_scRNA_seq, smartseq2]`；N1.1 追加 `data_category: [umi_counts, raw_counts]`（Smart-seq2 全转录本 = raw_counts） |
| 引擎 | `required_context` 列表 = **any-of** 语义（`RuleRegistry`，engine **0.2.0 → 0.2.1**） |
| 采集配套 | `sc.tl.leiden/louvain` 签名 `context_fixed: {graph_type: SNN}`（工具定义语义，C1.1 真实前置条件在采集层可提取） |
| ruleset | **1.1.1 → 1.2.0**（`generate_manifest` 重算 43 文件哈希；17 个规则文件哈希变更记入 golden asset_manifest change_log，18 条） |
| **B5 三闸** | `bio-audit ruleset-validate`：**清单 PASS / 冲突 PASS（0）/ golden PASS（0 差异）** |
| **golden 漂移** | **0 差异，基线未更新，C4 未触发**——放宽是纯加性（20 轨迹 137 决策全用 10X/umi_counts，命中集合逐决策不变）；若未来轨迹用 smartseq2/raw_counts 将从 L-1 变为可评分，属预期行为变化（G2-c 已验证） |

---

## 4. G2-c：重评（用已有真实运行产物，不手工编轨迹）

**方法（零成本）**：`cellvoyager-outputs/scripts/analyze_run.py`（窗口 G 原分析脚本，
新增 `--declared` 与 `--no-verdict-store` 参数）对**既有产物**重跑——
① 重解析运行 notebook（`GSE115978_melanoma_analysis_1.ipynb`，19 cells，未改动）；
② 从 WAL/verdicts 重建 M1 声明（20 条，未改动）；③ 交叉验证（四类判定）；④ 重建
final 轨迹（M3 事实 context + declared）→ `run_audit` 打分。**不重跑 Agent（省钱），
不手工编轨迹（纪律 4）**。原 `final_trajectory_v2.json` 已备份
（`cellvoyager-outputs/backups/final_trajectory_v2_pre_g2.json`，SHA256
C54E76E22321B0A482B41DC9FE410FFCBDE65EB4A35E53209331BBF6AE12F960）。

**结果（报告：`cellvoyager-outputs/reports/windowG_reeval.json`）**：

| 指标 | 窗口 G（修复前） | **G-2 重评（修复后）** |
|---|---|---|
| trajectory_score | **0.0**（全 L-1 占位） | **30.0** |
| eval_verdict | needs_correction（占位） | **needs_correction（有效）** |
| L4/L3/L2/L1/L0/-1 | 0/0/0/0/0/**20** | **0/1/0/7/0/12** |
| 交叉验证 | 一致 20 / 虚报 0 / 漏报 0 | 一致 20 / 虚报 0 / 漏报 0（不变） |
| 维度分 | — | data_handling 0.300 / method_selection 0.575（最低维主导 → 30.0） |

**8 条有效评分逐条（L0/L1 清单）**：

| step | 决策类型 | choice | level | 规则 |
|---|---|---|---|---|
| nb01-clustering_method | clustering_method | Leiden | **L3** | C1.1-CLUS-001 |
| nb01-qc_filtering ×4 | qc_filtering | hard_threshold | **L1** | Q1.1-QC-001 |
| nb01-scRNA_normalization ×2 | scRNA_normalization | LogNormalize | **L1** | N1.1-NORM-001 |
| nb08-annotation_method | annotation_method | manual_marker | **L1** | A1.1-ANNO-001 |

**L-1 清单（12 条，如实归因）**：`immune_correlation_method` ×12（Spearman）——
**规则覆盖缺口**：scRNA 规则集不含该类型（本体 paradigms=[pan-cancer]，范式隔离设计
ontology-design §二.1）；declared 齐全也无法评分。**非 context 缺口、非 Agent 质量结论**。

### 与 demo 时代 CellVoyager 结果对比（29 分 5 L0）

| 口径 | demo 时代（scrna_melanoma_cellvoyager，12 决策） | **G-2 真实运行（20 决策）** |
|---|---|---|
| 分数 | 29.0 | **30.0** |
| L0 | **5**（no doublet / no batch / cell-level DEG 伪重复 / PCA arbitrary / …） | **0** |
| L1 | 有（如 hard_threshold QC） | **7** |
| L3 | 部分（如 Leiden） | **1** |
| verdict | **blocked**（含 L0） | needs_correction |

**差异解读（如实，不夸大）**：
1. **方法学取向不同**：demo 轨迹是"12 步完整管线"（含双联体/批次/DEG 环节），5 个 L0
   全是"跳过关键步骤"；真实运行 max-iterations=5 的 5 步分析聚焦 QC→注释→免疫相关，
   未进入双联体/批次/DEG 环节——**没有 L0 不等于没有风险**，而是决策覆盖范围更窄
   （免疫相关 12 步在 scRNA 范式下无规则可评）。
2. **QC/归一化/注释三处 L1 与 demo 同款**：hard_threshold（固定阈值）与 LogNormalize
   在两代评测中均被评为"有风险"——规则体系跨 demo/真实运行一致（信度证据）。
3. **Leiden 在两侧均为 L3**（当前标准算法），与规则设计一致。
4. **分数相近（29 vs 30）是巧合口径，不可直接比较**：决策数不同（12 vs 20）、
   L-1 占比不同（demo 0 vs 本次 60%）、最低维主导聚合机制不同；唯一可靠对比维度是
   **L0/L1 计数与规则命中**（如上表）。
5. **demo 时代的 5 个 L0 中 3 个（no doublet/no batch/cell-level DEG）在本运行中
   根本不构成决策点**：Smart-seq2 无双联体前提（D1.1 10X 专属）、单样本 FACS 分选
   无批次整合环节、未做 DEG。这是平台事实查证（§1）带来的评测范围差异。

---

## 5. G2-d：回归

| 闸 | 结果 |
|---|---|
| pytest 全量 | **234/234**（222 既有 + 12 新增 declared/平台键测试） |
| golden 重放 | **0 差异**（20 轨迹 137 决策；基线未更新，C4 未触发） |
| ruleset-validate 三闸 | 清单 PASS / 冲突 PASS（0）/ golden PASS |
| validate-ontology | PASS（冲突 0） |
| benchmark-validate 四闸 | taskset / contamination / coverage / golden 全 PASS |
| reward-validate 五闸 | PASS |
| ruff | 新增/修改代码零错误 |

**执行计划快照**：`docs/specs/2026-08-13-execution-plan-v1.md` §六.十二 13 项逐项打勾（G-2 完成标记）。

---

## 6. 产物清单

| 产物 | 路径 |
|---|---|
| G-2 补充报告（本文件） | `bio-audit-v2/docs/agent-eval-report-g2.md` |
| 平台键审查报告 | `bio-audit-v2/docs/migration/G2b-platform-key-review.md` |
| declared 测试 | `bio-audit-v2/tests/test_declared_eval.py`（12 项） |
| 规则修订（17 文件） | `bio-audit-v2/src/bioaudit/rules/data/scRNA/*.yaml`（ruleset 1.2.0） |
| 引擎修订 | `bio-audit-v2/src/bioaudit/storage/rule_registry.py`（any-of）+ `capture/signatures.yaml`（graph_type SNN） |
| 采集链路 | `bio-audit-v2/src/bioaudit/capture/{models,m3_parser,cellvoyager_hook}.py` + `cli.py`（cross-validate --declared） |
| 重评结果 | `cellvoyager-outputs/reports/windowG_reeval.json` + `reports/gse115978_declared.json` |
| 重评轨迹 | `cellvoyager-outputs/runs/GSE115978_winG_20260816_final/final_trajectory_v2.json`（declared context 版；旧版备份 `backups/final_trajectory_v2_pre_g2.json`） |
| 资产变更留痕 | `docs/specs/2026-08-13-golden-baseline/asset_manifest.json` change_log（+17 条） |

## 7. 诚实局限

1. **immune ×12 仍 L-1**：scRNA 范式无 immune_correlation_method 规则（覆盖缺口），
   本轮不过度修（不新增规则）；留待规则库按本体 backlog 生长。
2. **n=1 不变**：LLM 随机性，分数不可复现（宪法 §9）；30.0 仅描述本次运行。
3. **declared 边界靠流程保证**：本窗口以评测者署名声明文件 + 宪法修订落地；
   未来运行需运行配置显式注入，避免任何 Agent 侧回填路径。
4. **双联体/批次/DEG 环节未在本运行覆盖**：与 demo 的对比受决策范围限制（§4 解读 5）。
