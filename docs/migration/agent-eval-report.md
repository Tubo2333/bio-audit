# 窗口 G 公开报告：CellVoyager 真实 Agent 评测（第一次真实评测）

> **日期**：2026-08-16
> **性质**：真实 LLM Agent 评测（DeepSeek anthropic 端点，真实 API 花费）
> **宪法**：`docs/protocols/agent-eval-protocol.md`（v1.0，含冒烟修订记录）
> **对应验收**：execution-plan-v1 §六.十 G1-G4；docs/protocols/benchmark-protocol.md
>
> **▶ 窗口 G-2 补充**（2026-08-16，评测缺口修复 + 重评，本报告旧版留档）：
> `docs/migration/agent-eval-report-g2.md`——declared 注入 + 规则平台键放宽（ruleset 1.2.0）
> 后重评得有效分数 **30.0（needs_correction，L0=0/L1=7/L3=1/L-1=12）**；
> 本报告 §4 的"分数 0.0（全 L-1 占位）"为修复前口径，结论部分（评分基础设施缺口
> 而非 Agent 质量结论）由 G-2 重评闭环。

---

## 1. 运行环境

| 项 | 值 |
|---|---|
| 评测对象 | CellVoyager（`D:\C-file\scRNA-audit\CellVoyager`，只读参考，零源码修改；wrapper 接入） |
| venv | `D:\C-file\cellvoyager-env`（Python 3.12.10，独立 venv，不进仓库） |
| 关键依赖 | scanpy 1.12.3 / anndata 0.13.2 / litellm 1.96.2 / claude-agent-sdk 0.2.139 / bio-audit 0.2.0 (editable) |
| 数据集 | `GSE115978_raw.h5ad`（485.5MB，7,186 cells × 22,454 genes，csr float32，31.6M nnz；预检 0 issues） |
| 数据平台 | GSE115978 摘要标注 "Smart-seq2 or 10X"（平台未在数据中可确认） |
| 模型 | hypothesis：`deepseek/deepseek-chat`（litellm 原生路径）；执行：`deepseek-chat`（anthropic 兼容端点 `https://api.deepseek.com/anthropic`，Claude Code CLI 打 `unrecognized_model` 警告但实测可用） |
| 运行参数 | num-analyses=1、max-iterations=5（宪法 §2 预算决策）、--no-deepresearch、non-interactive |
| 执行日期 | 2026-08-15 22:00–22:12（正式运行，10-12 分钟） |

## 2. API 成本与耗时

| 项 | 值 |
|---|---|
| **总花费（窗口 G）** | **¥2.55**（平台余额 39.53 → 36.98，权威口径） |
| 正式运行（第 5 次，采集完整） | 约 ¥1.51（usage 换算：输入 64,736 + 缓存读 2,263,680 + 输出 30,492 tokens，按 deepseek-chat ¥2/¥0.5/¥8 每 M 假设） |
| 前 4 次部署尝试（含冒烟） | 约 ¥1.05（如实计入；失败原因见 §7） |
| 预算 | ¥5 硬上限，**未超支**（余额差口径 ¥2.55） |
| 正式运行耗时 | 约 10-12 分钟（22:00:20–22:12，WAL 活跃窗口；agent 完成 5 步分析并写出 final summary 后人工停止 session-close 尾流） |
| 全窗口耗时 | 约 3 小时（环境搭建/预检/冒烟/部署修复/分析/回归；超出计划 2-3.5h 内） |

## 3. 采集链路结果（M1 × M3 × 交叉验证）

| 通道 | 结果 |
|---|---|
| **M1 hook 上报**（真实 NotebookSession，MCP 子进程内） | **20 条声明**（原始 40 条 = 双 attach 双份，按 (step_id, type, choice) 去重；见 §7） |
| M1 类型分布 | immune_correlation_method 12、qc_filtering 4、scRNA_normalization 2、annotation_method 1、clustering_method 1 |
| **M3 解析**（notebook 6 个代码 cell） | **14 候选 + 4 未定**（未定=UMAP 投影≠聚类降维等，禁猜规则正确触发） |
| **交叉验证四类判定** | **一致 20 / 虚报 0 / 漏报 0 / 未验证 0** —— M1 声明全部被 M3 事实证实，无虚报无漏报 |
| verdict 联动 | 20/20 provisional → final（一致路径）；revoked 0（本运行无虚报样本，生命周期 revoked 分支未实测） |

**解读**：hook 上报的决策与 notebook 实际执行代码逐条对齐一致——M1/M3 双通道在真实运行中验证通过（C 窗口遗留闭环达成）。Agent 的 5 步分析（QC→注释→免疫程序评分→Spearman 相关→DEG→UMAP 共表达）产生的决策类型集中在 5 个本体类型（本次运行未涉及 HVG 选择/批次校正/DEG 工具选择等）。

## 4. 分数与 verdict（如实呈现）

| 指标 | 值 |
|---|---|
| trajectory_score | **0.0**（全部 20 决策 L-1 占位） |
| eval_verdict | needs_correction |
| L4/L3/L2/L1/L0/-1 计数 | 0 / 0 / 0 / 0 / 0 / **20** |
| critical_issues | 0 |

**为什么是 0.0（诚实归因）**：audit 规则 Q1.1-QC-001 等对 qc_filtering 等类型要求 `required_context: sequencing: 10X_scRNA_seq`；采集链路中该键**三级可信源均不可得**——代码调用参数无、h5ad 元数据无（uns 空、obs 无 sequencing 列）、agent 未声明平台 → 键标 unverified → 规则不匹配 → 引擎按设计返回"无法评估"占位分（L-1）。**这不是 Agent 表现差或好，而是评测输入（context）不完整导致的"无法评估"**——本运行如实呈现为分数不可用。

附带发现：GSE115978 摘要写 "Smart-seq2 or 10X"，即便声明平台也不一定命中 `10X_scRNA_seq` 硬条件——规则对测序平台假设可能过强（见 §7 建议）。

## 5. 检出 vs 任务集表现（benchmark-run 对比，描述性）

| 口径 | 任务集（60 条，623 决策） | 真实 Agent 运行（1 次，20 决策） |
|---|---|---|
| 决策量 | 623 | 20 |
| 检出精度/召回/F1 | 0.745 / 0.820 / 0.781 | 20/20 声明全部获 M3 证实（一致率 100%，n=20 无统计意义） |
| mean trajectory_score | 0.5528 [0.40…] | 0.0（全部 L-1 占位，context 缺键所致） |
| L0-L1 计数 | （见 benchmark_run_baseline.json） | L-1×20（占位），L0-L1 均 0 |
| edge 检出率 | 0.667 | 不适用（本运行无 edge 样本） |

**纪律遵守**：n=1 真实运行与任务集**不做统计检验**（预注册，benchmark-protocol §9）；仅描述性对比。任务集的 recall/F1 反映确定性引擎对理想轨迹的检出能力，与真实 LLM 运行不可直接比较。

## 6. 检出的科学内容（notebook 最终摘要）

Agent 完成 5 步分析并产出可复现结论（notebook `GSE115978_melanoma_analysis_1.ipynb`，19 cells）：
1. QC（宽松过滤保留 7,177/7,186 cells；25 Leiden clusters）→ 2. 标记基因注释（T 3,500 / Melanoma 1,787 / B 878 / Myeloid 456 / Fibroblast 453 / Endothelial 103）→ 3. T 细胞耗竭评分（66.8% 高于背景）→ 4. 邻域检验（kNN 图因 FACS 分选区室分离而功效不足——如实记录方法学墙）→ 5. PCA 空间最近邻检验：**配体阳性肿瘤细胞邻近的 T 细胞耗竭更高（0.333 vs 0.285，Mann-Whitney p=0.012）；CD274 ρ=+0.056 p=0.017、CD86 ρ=+0.097 p=3.8e-5**。结论：假设部分成立（真实但温和、配体特异性）。这些方法学决策与结论全部进入 M3 采集。

## 7. 部署过程与诚实局限

**部署 5 次尝试（全部计入成本，如实记录）**：
1. stdout GBK 编码崩溃（零 token 损失）→ 修：`PYTHONIOENCODING=utf-8`；
2-3. hook 主进程 patch 无效——NotebookSession 由 **MCP server 子进程**创建执行（C 窗口部署脚本 attach agent.executor 亦无效）→ 修：sitecustomize 注入（约 ¥1.05 损失）；
4. FastMCP 工具以**关键字参数**调用 `execute_cell(index=...)`，`_CODE_EXTRACTORS` 只处理位置参数 → 提取 IndexError 被隔离吞掉（C 窗口测试盲区，FakeExecutor 仅位置调用）→ 修：extractors 支持 args+kwargs + 2 项回归测试；
5. sitecustomize 与 `_server_command` 引导**双 attach** → 每条决策双份上报 → 修：模块级 attach 标记；本次数据按 (step_id, type, choice) 去重。

**其他局限**：
- **DecisionScore 快照不携带输入 context**（C 窗口设计缺陷）→ `final_trajectory` 重建轨迹 context 全空 → 审计失真；已修复 M1Reporter（快照并入 context）+ 测试；本次分析从交叉验证对齐重建轨迹（M1 choice + M3 事实 context）；
- **评测 n=1**：LLM 随机性，结果不可复现（宪法 §9），不做任何统计推断；
- **sequencing 键缺口**：采集链路无法自动获取测序平台；规则 Q1.1 强依赖 `10X_scRNA_seq` 声明。建议：① 运行宪法支持 declared 注入（agent 声明平台）；② 规则层评估 required_context 对平台键的依赖是否过强（GSE115978 为 Smart-seq2/10X 混合来源）；
- M3 有 4 条 uncertain（UMAP/PCA 等）——禁猜规则正确触发，非缺陷；
- 本次无虚报样本 → verdict revoked 分支未在真实运行中实测（C 测试已覆盖）；
- agent 完成分析后出现与评测无关的 "session-close 协议" 尾流（Claude Code 遵循 D:\C-file\CLAUDE.md 的行为）——已人工及时停止；后续运行应设完成信号自动停止；
- `unrecognized_model` 警告：Claude Code CLI 不识别 deepseek-chat 模型名但实际使用（冒烟+正式运行双重验证）；`cache_read_input_tokens` 显示 DeepSeek 上下文缓存生效（占成本大头，¥0.5/M 计价）；
- 双 attach 去重后 M1 声明 20 条与 verdict 文件记录数一致（40 原始 → 20 唯一决策）。

## 8. 结论与后续

- **G2.5 达成**：M1 hook 上报 + M3 解析 + 交叉验证（四类判定）在真实运行中端到端跑通，20/20 一致；
- **评分不可用（如实）**：context 缺 sequencing 键 → 全 L-1 占位；这是评测基础设施缺口，不是 Agent 质量结论；
- **本次评测为窗口 G 的"链路验证 + 第一次真实采样"**：科学产物（notebook 结论）完整且可复现；分数体系待 context 注入能力就绪后重评；
- 修复清单：m1_reporter 快照 context（已修+测试）/ hook kwargs（已修+测试）/ 双 attach 标记（已修）/ 建议 rules required_context 平台键评估 / 建议 declared 注入通道。

## 9. 产物清单

| 产物 | 路径 |
|---|---|
| 宪法 | `bio-audit-v2/docs/protocols/agent-eval-protocol.md` |
| 本报告 | `bio-audit-v2/docs/migration/agent-eval-report.md` |
| 正式运行 notebook（19 cells） | `cellvoyager-outputs/runs/GSE115978_winG_20260816_final/GSE115978_melanoma_analysis_1.ipynb` |
| 运行备份 | `cellvoyager-outputs/backups/GSE115978_winG_20260816_final_backup/` |
| M1 声明（WAL） | `cellvoyager-outputs/data/wal/cv_gse115978_winG_20260816.jsonl` |
| verdicts | `cellvoyager-outputs/data/verdicts/cv_gse115978_winG_20260816.jsonl` |
| 分析报告 | `cellvoyager-outputs/reports/windowG_analysis.json` |
| final 轨迹 | `cellvoyager-outputs/runs/GSE115978_winG_20260816_final/final_trajectory_v2.json` |
| 预检/冒烟/余额 | `cellvoyager-outputs/reports/{h5ad_precheck_GSE115978,phase0_smoke_endpoint,phase0_smoke_hook,balance_before,balance_after}.json` |
| benchmark 基线 | `cellvoyager-outputs/reports/benchmark_run_baseline.json` |
| 运行脚本套件 | `cellvoyager-outputs/scripts/`（预检/冒烟/运行入口/分析/余额） |
