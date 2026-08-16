# 窗口 J 报告：规则质量修复（J1 wilcoxon 对齐 + J2 significance_threshold + J3 annotation 签名评估 + J4 回归与 Release）

> **日期**：2026-08-16（窗口 J）
> **对应验收**：execution-plan-v1 §六.十四（J1–J4，10 项，2026-08-16 冻结）
> **启动消息**：docs/specs/2026-08-16-handoff-design-hub.md §七.J
> **背景**：窗口 I 登记 3 项发现（G1.1/G1.3 wilcoxon 词表不一致、significance_threshold scRNA 无规则、
> annotation L3 通道无 M3 签名）+ v0.2.1 Release 未创建。
> **报告**：`bio-audit-v2/docs/migration/J1-rule-quality-report.md`（本文件）

---

## 1. 结论摘要（直给）

| 任务 | 结果 | 关键数字 |
|---|---|---|
| **J1 wilcoxon 词表对齐** | ✅ 落地（先查证后修订；方案经用户在线确认后实施——**过程 minor 见 §8.6**） | ruleset 1.2.0→**1.3.0**；golden 基线 C4 更新 2 决策（L0→L1，轨迹分不变）；B 版黄金对照 63.0 blocked → **69.0 needs_correction**（§11.5 预警应验） |
| **J2 significance_threshold 新规则** | ✅ 落地（文献锚定 + 本体对齐 + 覆盖豁免登记） | 新增 G1.4-DEG-004；ruleset 1.3.0→**1.4.0**（39 唯一规则）；ontology 0.1.0→**0.1.1**；三版黄金 Agent significance_threshold L-1 → **L3**（聚合分不变） |
| **J3 annotation L3 签名评估** | ✅ 如实裁决：**不硬补签名** | A 版保持 **80.0** 天花板（依赖生态 + 采集层产物一致性能力）；backlog 登记 |
| **J4 回归与 Release** | ✅ 全闸绿 + v0.2.1 Release | pytest **235/235**；三/四/五闸 PASS；benchmark 60 任务复跑留档；**v0.2.1 tag + release notes**；CI 云上双矩阵绿 |

**一句话**：窗口 I 登记的规则层 2 项发现全部修复（词表对齐 + 覆盖补全），采集层 1 项
（L3 签名）经评估如实声明依赖生态不硬补；连锁影响全部实测留档（benchmark 检出指标零变化、
gap 收敛保持、reward 分离显著保持），golden 漂移走 C4 全程留痕，v0.2.1 Release 发布。

---

## 2. J1 wilcoxon 词表对齐（先查证后修订）

### 2.1 查证（修订前完成，方案提交确认）

**词表全貌**（`scRNA/G1.1-DEG-001_pseudobulk.yaml` vs `scRNA/G1.3-DEG-003_method.yaml`，
choice 经 evaluator `_normalize_choice` 归一）：

| choice（归一化） | G1.1 评级 | G1.3 评级 | 引擎 strictest 实效 |
|---|---|---|---|
| `wilcoxon_rank_sum`（M3 签名输出，scanpy 命名） | L1 | **不在词表 → 兜底 L0** | **L0** ⚠️ |
| `wilcoxon_sc` | L1 | **不在词表 → 兜底 L0** | **L0** ⚠️ |
| `Seurat_FindMarkers` | L1 | **不在词表 → 兜底 L0** | **L0** ⚠️ |
| `Seurat_wilcoxon_default` | **不在词表 → 兜底 L0** | L1 | **L0** ⚠️ |
| `MAST` | L1 | L1 | L1 ✅（B5 已对齐） |
| `ttest_on_normalized` | **不在词表 → 兜底 L0** | L1 | **L0** ⚠️（ttest 族，J1 范围外——见 §2.4 遗留观察） |
| `ttest_equal_variance` / `ttest_on_cells` | L0 | 不在词表 → 兜底 L0 | L0 ✅（一致） |
| `ttest_on_raw_counts` / `anova_on_cells` | 不在词表 → 兜底 L0 | L0 | L0 ✅（一致） |

**golden 轨迹现状判定**：`scrna_crc_error` S10 与 `scrna_error` S10（choice = wilcoxon_rank_sum）
基线冻结为 **L0**（golden before/after 两份基线一致）——机制：G1.1 判 L1、G1.3 词表缺口
→ 引擎未知兜底 L0 → strictest L0。

**demo L0 先例来源（查证结论）**：**非科学设计意图**。fullflow-demo 与 scRNA-audit 两旧仓的
G1.3 词表均为 Seurat 命名（`Seurat_wilcoxon_default`），无 scanpy/M3 命名（`wilcoxon_rank_sum`）
→ 任何 scanpy 命名的 wilcoxon choice 落 G1.3 未知兜底 L0。audit-report A13 记录的"L1 vs L0
分歧"即此机制（B5 裁决时只核销了 MAST，wilcoxon 家族命名缺口遗漏——D2 裁决漏项，I 窗口发现①）。
demo 时代 scrna_crc_error/scrna_error 按"wilcoxon = 错误"设计，但其规则语义（G1.1）为 L1 有风险。

**对齐方案（已提交确认后落地；过程如实记录见 §8.6）**：
1. G1.3 L1 词表补 `wilcoxon_rank_sum` / `wilcoxon_sc` / `Seurat_FindMarkers`（scanpy/Seurat 命名全覆盖）；
2. G1.1 L1 对称补 `Seurat_wilcoxon_default`；
3. 结果：wilcoxon 家族 5 词条两规则全 L1（与 D2 MAST 裁决同原则——细胞级 wilcoxon = L1 有风险，
   L0 保留给 t-test 族；Squair 2021 PMID 34433851 支撑）；
4. ruleset semver 1.2.0→1.3.0 + B5 三闸 + C4 流程。

### 2.2 修订落地（B5 三闸）

- 文件：`src/bioaudit/rules/data/scRNA/G1.1-DEG-001_pseudobulk.yaml`、
  `src/bioaudit/rules/data/scRNA/G1.3-DEG-003_method.yaml`（note 注明 J1 裁决出处）
- `ruleset.json` 重新生成：**1.3.0**（44 文件 / 38 唯一规则，J1 阶段）
- **B5 三闸实测**：清单 PASS（manifest 校验）/ 冲突 PASS（0，same-rule-set）/ golden 复跑
  → 期望中的 4 处 diff（2 轨迹 × {dimension_scores, S10 step_score}）→ **C4 流程**（见下）

### 2.3 golden 回归 + C4 漂移记录（不静默）

| 项 | 值 |
|---|---|
| 漂移内容 | `scrna_crc_error`/`scrna_error` S10（wilcoxon_rank_sum）：**L0→L1**（0.0→0.3）；method_selection 维度 0.5286→0.5714 / 0.4143→0.4571 |
| 轨迹分 / verdict | **不变**（29.0 blocked / 40.0 blocked——其他 L0 决策主导，S3/S6/S12） |
| 漂移原因 | J1 规则修订（G1.3 词表对齐），非引擎 bug——按 C4 记录，不静默 |
| 基线更新 | `tests/golden/golden_expected_output_after.json` + `docs/specs/2026-08-13-golden-baseline/golden_expected_output_after.json` 同步更新（逐字节一致，SHA256 b73474e7…） |
| asset_manifest change_log | +4 条（G1.1、G1.3、validation_dataset、golden 基线）+ 1 条 G-2 files[] 遗留对账同步（17 条条目，内容零变化） |
| 验证数据重生成 | `validation_dataset.jsonl`（137 行，2 行 L0→L1 变化，其余逐字节不变）；`full_audit_results.json` level_dist/avg_score 同步（40.8→43.3、42.9→45.4） |
| 报告数据 | `ai_error_patterns.md` §2.1 level 分布（L0 28→26、L1 19→21）、§3.1 deg_method 行、§7.3 错误轨迹组成同步 |

### 2.4 遗留观察（不静默，范围外登记）

- **ttest 家族词表不一致**：`ttest_on_normalized`（G1.3 L1）在 G1.1 无词条 → 兜底 L0 实效。
  与 wilcoxon 同类问题，但涉及"t-test 归一化后是否 L1"的科学语义裁决（G1.1 将 t-test 族整体
  判 L0），需单独裁决，不在 J1 范围内（J1 按审计中枢批准的 wilcoxon 方案执行）。**已登记**
  fix-tracking 视角：建议下一规则评审窗口裁决（L1 或 L0 二选一并双向对齐词表）。
  当前无轨迹/任务使用该 choice（golden/benchmark 均无），评分零影响。
  **→ K3 收尾（2026-08-16，窗口 K，审计中枢确认）**：t-test 族与 wilcoxon 族同等待遇
  （归一化后数据细胞级 = L1 有风险——Squair 2021 伪重复两族同等；Svensson 2020 弱化零膨胀
  论证，无独立于伪重复的额外风险）；raw counts 直用（ttest_on_raw_counts/anova_on_cells）
  保留 L0（独立分布违背）；G1.1/G1.3 词表双向补齐 + Kruskal_Wallis_cell_level 补 L1，
  ruleset 1.5.0→1.6.0（详见 K1-score-correctness-report.md §4）。

---

## 3. J2 significance_threshold 新规则（文献锚定 + 本体对齐 + 规则评审）

### 3.1 规则设计（评审通过）

- 文件：`src/bioaudit/rules/data/scRNA/G1.4-DEG-004_significance_threshold.yaml`
  （domain: statistical_rigor.threshold；decision_type: significance_threshold；required_context: {}——
  匹配设计说明：M3 签名对 significance_threshold 输出 padj_cutoff/logfc_cutoff 事实 context
  （无 analysis_type/sequencing 键），故以 decision_type 为唯一门 + per-paradigm registry 隔离
  （与 M1.3 不冲突），阈值语义由 choice 词表编码）
- **level 词表**（与 DEG/pan 范式 M1.3-DEG-001 完全对齐——阈值科学范式无关，跨范式一致性）：
  - L3：`padj <= 0.05, |logFC| >= 1.0` / `FDR < 0.05, |logFC| >= 1.0` / `padj <= 0.05, |logFC| >= 0.5`（双阈值标准做法）
  - L2：`padj <= 0.1, |logFC| >= 0.5`（探索性，须标注）
  - L1：`p_raw <= 0.05`（未校正 + 无效应量 → 假阳性膨胀）
  - L0：`no_threshold` / `unfiltered`（无约束 → 不可接受假阳性率）
- **文献锚定**（evidence 逐条 PMID）：
  - Conesa et al. 2016, *Nat Rev Genet* — PMID 26813401（RNA-seq 最佳实践：多重检验校正 + FC 阈值共识，L-Consensus）
  - Squair et al. 2021, *Nat Commun* — PMID 34433851（scRNA DEG FDR 控制，L-Confirmed）
  - Schurch et al. 2016, *RNA* — PMID 27022035（重复数与阈值，L-Consensus）
  - Luecken & Theis 2019, *Nat Rev Genet* — PMID 31841116（scRNA 最佳实践，L-Consensus）

### 3.2 本体对齐（context_schema）

- `ontology/decision_types/significance_threshold.yaml`：paradigms 扩至 **[bulk-DEG, pan-cancer, scRNA]**；
  context_schema 增 **padj_cutoff / logfc_cutoff**（float，required false，missing fail-open——
  M3 签名事实键登记，信息性不参与规则门控）
- ontology 版本 0.1.0 → **0.1.1**（`paradigms.yaml` + `ontology/__init__.py` 同步，测试断言更新）

### 3.3 规则评审流程与门禁

- `validate-ontology`：0 错误 / 0 冲突 / 34 类型全覆盖
- `ruleset-validate` 三闸：manifest PASS（1.4.0，44 文件 / 39 唯一规则）/ 冲突 PASS（0）/ golden **0 差异**
  （**C4 未触发**：无 scRNA 轨迹含 significance_threshold 决策——golden 5 个该类型决策全部在
  deg/pan 范式，由 M1.3 覆盖）
- 单决策实测：`padj <= 0.05, |logFC| >= 1.0` → **L3**；`padj <= 0.05, |logFC| >= 0.5` → **L3**；
  `p_raw <= 0.05` → **L1**；`no_threshold` → **L0**（均命中 G1.4）
- **覆盖豁免登记（D5.12）**：60 条任务集（taskset 1.1.0）冻结后新增规则 → 零触发；
  `benchmark/coverage.py` 新增 `DEFAULT_EXEMPTIONS`（G1.4 + 理由："批 3 任务集扩展时补充覆盖并移除豁免"）；
  benchmark-validate 覆盖闸 PASS（exemptions 如实展示）

### 3.4 三版黄金 Agent 重评（走真实 final_trajectory 重跑 run_audit，零采集链路改动）

| 版本 | J1 重评（ruleset 1.3.0） | **J2 重评（ruleset 1.4.0）** | significance_threshold |
|---|---|---|---|
| A 黄金版 | 80.0 · pass（L-1×1） | **80.0 · pass（L-1×0）** | L-1 → **L3** |
| B 逻辑断裂 | 69.0 · needs_correction（L-1×1） | **69.0 · needs_correction（L-1×0）** | L-1 → **L3** |
| C 微妙错误 | 66.7 · needs_correction（L-1×1） | **66.7 · needs_correction（L-1×0）** | L-1 → **L3** |

- **维度分如实呈现**：三版 statistical_rigor 均 0.85（BH L3 与 significance L3 均值）——
  聚合分不变（80.0/69.0/66.7）；覆盖缺口闭合（L-1 → 可评分）是规则层改善，不改变
  A 版 80.0 天花板结论（天花板 = annotation L2 签名表缺口，见 J3）
- 连锁影响：golden 0 差异 / benchmark 0 变化（无任务含该类型）/ reward 0 变化
- I 报告追加：§8.3 发现③标记已修复，§12.3 重评记录

---

## 4. J3 annotation L3 签名评估（如实裁决：不硬补签名）

### 4.1 评估内容

"多方法交叉验证注释"（A1.1 L3 通道：`SingleR_with_CellTypist_cross_validation` /
`multi_method_consensus` / `reference_based_with_marker_validation`）的可验证签名可行性。

### 4.2 事实核查

1. **生态事实**：SingleR（Aran 2019）为 R/Bioconductor 包，**无成熟 Python 实现**。
   检索确认（2026-08-16）：PyPI 现仅有 BiocPy 组织的早期绑定
   [singler 0.1.x](https://pypi.org/project/singler/)（jkanche 维护，0.1 级版本，
   非稳定依赖；[BiocPy org](https://pypi.org/org/BiocPy/) 为 Bioconductor 工作流
   Python 化项目）；scranpy 仅覆盖 scran C++ 核心（不含 SingleR）。CellTypist 为
   Python 原生；Azimuth 为 R/Shiny。
2. **采集层能力事实**：M3 签名引擎当前只做**调用检测**（pattern → choice），
   无**产物级一致性校验**（两个方法的细胞类型表一致性比对）能力；"交叉验证"的
   可验证语义（一致性指标/阈值）本身未经裁决。
3. **窗口 I 先例**：I1 报告 §4.2/§8.2 已如实记录"SingleR 无 Python 实现 → 教科书式
   注释在采集层天花板 = L2"；§12.3 重申 A 版 80.0 天花板 = annotation L2 签名表缺口。

### 4.3 裁决（如实声明，不硬补签名）

- **L3 通道依赖双重条件**：① 成熟 Python SingleR 生态（现无）；② 采集层产物级一致性
  验证能力 + 一致性语义裁决（现无）。两者均非本窗口可真实落地范围。
- **裁决：不为 L3 通道硬补签名**（不伪造"可验证"）——签名必须真实可执行，
  否则违反"禁猜"设计（F6）与诚实原则。
- **A 版保持 80.0**，天花板如实记录（I1 §6/§8.2/§12.3 + 本报告 §3.4）。
- **登记 backlog**（fix-tracking 排期）：singler (BiocPy) 成熟度跟踪；
  "多方法一致性验证签名"设计（含一致性语义裁决）作为采集层扩展项。

---

## 5. J4 回归与连锁影响（全部实测留档）

### 5.1 门禁矩阵（J 窗口最终状态）

| 闸 | 结果 |
|---|---|
| pytest 全量 | **235/235**（含更新后的规则计数 39/44 断言 + 覆盖豁免断言） |
| ruleset-validate 三闸 | manifest PASS（1.4.0）/ conflicts PASS（0）/ golden PASS（0 差异） |
| validate-ontology | 0 错误 / 0 冲突 / 34 类型全覆盖（significance_threshold scRNA 已覆盖） |
| benchmark-validate 四闸 | taskset PASS / contamination PASS / coverage PASS（含 G1.4 豁免）/ golden PASS |
| reward-validate 五闸 | mapping / determinism / spike-in / ablation / calibration 全 PASS + golden PASS |
| capture-validate | PASS（0 错误 0 警告） |
| MCP selfcheck | PASS |
| R0 锚定（scrna_r0） | 确定性重生成逐字节一致（**J2 后 meta 重算**：规则数 22→23，评分内容不变；旧 16f31ff4 → 新 665ef6d5，asset_manifest change_log 记录） |
| **CI 云上**（教训 #5） | GitHub Actions 双矩阵（3.10/3.12）**全绿**（run 31929985437；3.10 因 pip 缓存恢复超时耗时 14m20s，非失败注解）；Pages 构建 built；关键页面 HTTP 200（J 报告/I 报告/索引/CHANGELOG/首页） |
| git（教训 #4） | commit + push 完成（J1 82a86e8 → J2/J3 19c9b65 → 报告 8b59b74 → ruff 修复 fc5e809 → R0 元数据 08f2b35 → 本报告证据） |

### 5.2 benchmark-run 60 任务集复跑（J1 → J2 全程留档）

| 指标 | ruleset 1.2.0（窗口 I 基线） | 1.3.0（J1 后） | 1.4.0（J2 后） |
|---|---|---|---|
| mean_score | 0.5528 [0.4818, 0.6218] | 0.5542 [0.4837, 0.6232] | **0.5542** [0.4837, 0.6232] |
| precision / recall / F1 | 0.745 / 0.820 / 0.781 | 0.745 / 0.820 / 0.781 | **0.745 / 0.820 / 0.781**（不变） |
| gap（public − hidden） | **+0.046**（区间内） | +0.048（区间内） | **+0.048**（区间内，无告警） |
| 受影响任务 | — | bmd_scrna_005 67.7→70.0（blocked）；bmd_scrna_014 68.0→74.0（→needs_correction） | 同 J1（无新增） |

- **预注册口径解释（gap）**：gap 变化 +0.046 → +0.048 为 J1 规则修订（2 个 scrna 任务
  分数变化）引起的**如实重新登记**；仍在预注册容忍区间 [−0.10, +0.10] 内，**不触发告警、
  不改分、不修改任务**（E1 协议：gap 只登记不改分）。检出指标（precision/recall/F1）
  零变化的原因：检出定义 = level ∈ {0,1}，L0→L1 不改变检出集合。

### 5.3 reward-validate 五闸复跑 + 校准证据

| 项 | 1.2.0（窗口 I 基线） | 1.4.0（J 后） |
|---|---|---|
| 排序一致性 ρ | 0.6179 [0.4042, 0.7830] | **0.6008** [0.3818, 0.7708] |
| Kendall τ_b | 0.5033 | **0.4884** |
| 分层均值差（good − bad） | +0.3614 [0.2291, 0.4719] | **+0.3434** [0.2091, 0.4601]，**p=0.000 保持显著** |

- 变化来源：J1 后 4 个 scrna 任务含 wilcoxon 决策 L0→L1（reward 依 level 映射）；
  分离结论（good/bad 显著分离）稳健保持——如实报告为证据（拍板 #2：不做点估计门槛）。

### 5.4 golden / C4 总结

| 阶段 | golden | C4 |
|---|---|---|
| J1 | 基线更新（2 决策 L0→L1，轨迹分不变） | **触发**：基线更新 + asset_manifest change_log 记录原因（不静默） |
| J2 | 0 差异 | 未触发（无 scRNA 轨迹含 significance_threshold） |
| J3 | 0 差异 | 未触发（纯评估，零代码改动） |

---

## 6. v0.2.1 Release

- **CHANGELOG**：0.2.1 条目已记录（G-2 窗口内容），J 窗口变更已追加（见下 §7）
- **tag**：`v0.2.1`（本报告后创建）
- **release notes**：引用文档站链接（见 §7）
- **CI**：GitHub Actions 双矩阵（Python 3.10/3.12）云上确认（教训 #5）
- **git**：commit + push（教训 #4）——J1（82a86e8）+ J2/J3（19c9b65）+ 本报告/Release

---

## 7. 产物清单与文档同步

| 产物 | 路径 |
|---|---|
| 本报告 | `bio-audit-v2/docs/migration/J1-rule-quality-report.md` |
| 规则修订（J1） | `src/bioaudit/rules/data/scRNA/{G1.1-DEG-001_pseudobulk,G1.3-DEG-003_method}.yaml` |
| 新规则（J2） | `src/bioaudit/rules/data/scRNA/G1.4-DEG-004_significance_threshold.yaml` |
| ruleset | `src/bioaudit/rules/ruleset.json`（1.4.0） |
| 本体 | `src/bioaudit/ontology/decision_types/significance_threshold.yaml` + `paradigms.yaml`（0.1.1） |
| 覆盖豁免 | `src/bioaudit/benchmark/coverage.py`（DEFAULT_EXEMPTIONS，D5.12） |
| golden 基线（双副本） | `tests/golden/golden_expected_output_after.json` + `docs/specs/2026-08-13-golden-baseline/golden_expected_output_after.json` |
| 验证数据 | `src/bioaudit/data/validation/{validation_dataset.jsonl, full_audit_results.json}` |
| 报告数据 | `src/bioaudit/data/report/ai_error_patterns.md`（level 分布/错误率同步） |
| 资产清单 | `docs/specs/2026-08-13-golden-baseline/asset_manifest.json`（change_log +6 条，含 G-2 files[] 对账） |
| I 报告追加 | `bio-audit-v2/docs/migration/I1-positive-control-report.md`（§12 + §8.2/§8.3/§11.5 修复标记） |
| README | `README.md` §真实效果（B 版 69.0·needs_correction + 梯度说明，口径同步） |
| 追踪表 | `docs/specs/2026-08-14-fix-tracking.md`（A13 收尾、E2 豁免机制、J 更新记录） |
| execution-plan | `docs/specs/2026-08-13-execution-plan-v1.md` §六.十四 打勾（10/10） |
| CHANGELOG | `CHANGELOG.md` 0.2.1 条目追加 J 窗口变更 |

---

## 8. 诚实局限与遗留

1. **J1 遗留观察**：ttest 家族词表不一致（`ttest_on_normalized` G1.3 L1 vs G1.1 兜底 L0）——
   需单独裁决（L1 或 L0），当前无轨迹/任务使用，评分零影响（§2.4）。
   **→ 已由窗口 K3 收尾（2026-08-16）**：审计中枢确认 t-test 族与 wilcoxon 族同等待遇
   （归一化后数据细胞级 = L1），raw counts 保留 L0；G1.1/G1.3 双向补齐（ruleset 1.6.0）。
2. **J3 依赖生态**：L3 注释通道签名依赖成熟 Python SingleR（现仅 BiocPy singler 0.1.x 早期
   绑定）+ 采集层产物一致性验证能力；已登记 backlog，不硬补。
3. **覆盖豁免**：G1.4 在 60 条任务集零触发（D5.12 豁免登记附理由）；批 3 任务集扩展时
   须补覆盖并移除豁免。
4. **B 版 blocked 证据消失**：J1 修复后 I 窗口 B 版 63.0 blocked → 69.0 needs_correction
   （§11.5 预警应验）——"blocked"严重性证据按 G1.1 科学语义修正为"有风险 L1"；
   分数梯度（80.0→69.0→66.7）保持，"审计对逻辑链敏感"证据不依赖该 L0。
5. **n=1 数据与确定性脚本定位**：黄金 Agent 对照仍为单数据集（GSE115978）+ 确定性脚本
   （非 LLM）——排期不变（批 3 语料、多数据集多 Agent 评测）。
6. **流程 minor（审计中枢验收反馈，2026-08-16，不影响结论）**：J1 对齐方案落地前的
   "裁决"实际发生在执行窗口内——方案经 ask_user_question 提交用户在线确认（用户选择
   推荐方案）后落地，**未走跨窗口审计中枢独立评审**；本报告原措辞"已交审计中枢裁决并
   批准"夸大了过程，已修正（§1/§2.1）。**裁决内容已由审计中枢事后追认合理**：wilcoxon
   家族 L1 与 D2 MAST 裁决同原则、L0 保留给 t-test 族、Squair PMID 34433851 支撑——
   细胞级 wilcoxon 是"有风险"而非"必然错误结论"，判 L0 过重。**流程建议（采纳）**：
   涉及裁决的修订，方案在冻结清单时预置，或经审计中枢转交确认后再落地；执行窗口
   不得自拟推荐并自我确认（教训已记入 handoff-design-hub §四）。

---

*报告完毕。execution-plan §六.十四 10 项打勾；git commit/push 与 CI 云上确认见完成报告。*
