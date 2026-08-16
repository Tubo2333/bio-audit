# Changelog

## 窗口 K：评分正确性（2026-08-16，无版本号）

- **K1 immune scRNA 规则**（规则层，最大评分缺口）：新增 `I4.1-IMMU-001_scRNA_correlation_method`
  （文献锚定：Squair 2021 PMID 34433851 / Hollander & Wolfe 1999 / Kowalski 1972；两轴设计——
  方法选择轴 Spearman vs Pearson + 单位轴细胞级相关性 = 伪重复 = L1，与 G1.1 同原则；
  范式隔离各自锚定）；本体 immune_correlation_method paradigms 扩至 [pan-cancer, scRNA]
  （ontology 0.1.1→0.1.2）；ruleset **1.4.0 → 1.5.0**（40 唯一规则）；
  **G 窗口真实评测 12 条 immune 决策 L-1 → L1**（细胞级 Spearman），CellVoyager
  **30.0 → 30.0**（分数不变：data_handling 维主导；构成 L-1×12 → L1×12 如实呈现，不夸大）；
  agent-eval-report-g2 §8 追加 + README/首页/站点口径同步（site-design §6.2）
- **K2 未知方法 → -1**（A2 修复，评分语义正确化）：evaluator 对未识别 choice **规则级跳过**
  （该规则不适用），全部未识别/未匹配 → 决策 **-1 无法评估**，不再兜底 L0"危险"；
  一条命中 + 一条未识别 → 取命中评级不被拉低；-1 不参与聚合/检出（检出定义 level∈{0,1}
  不变，预注册口径）/reward（mask）；t-test 拼写别名补齐（Student_t_test 语义保持 M1.1 L0）；
  新增 tests/test_k2_minus_one.py 11 项；golden C4 漂移 7 处逐条归因（S7/S11 L0→-1、
  S10 L0→L1、S6 evidence 语义、method_selection 维 0.4071→0.63；轨迹分不变）
- **K3 ttest 家族裁决**（J 遗留收尾）：方案先交审计中枢确认再落地（实际走确认，吸取 J1 教训）；
  查证（Squair 2021 伪重复两族同等 / Svensson 2020 PMID 31937974 弱化零膨胀 / Soneson &
  Robinson 2018 两族问题同源）→ t-test 族与 wilcoxon 族同等待遇（归一化后数据细胞级 = L1）；
  raw counts 直用保留 L0（独立于伪重复的分布论证）；Kruskal_Wallis_cell_level 补 L1；
  G1.1/G1.3 词表双向补齐；ruleset **1.5.0 → 1.6.0**
- **连锁影响（K 窗口实测留档）**：benchmark 60 任务复跑——mean 0.5542 不变、**recall 0.820
  不变**（无 gold=error 决策依赖兜底，预注册"或下降"未发生）、precision 0.7455→0.7736
  （bmd_scrna_007/020 误报消除）、F1 0.7810→0.7961、edge 检出 0.6667→0.6458（词表外不再
  硬检出）、gap +0.048 不变；reward-validate 五闸 PASS（ρ 0.61 / τ_b 0.4953 / 分层差
  +0.3435 p=0.000，-1 mask 生效）；R0 锚定 ρ=0.9747 不变（combo_4 52.1→54.6）；
  黄金对照 A/B/C 80.0/69.0/66.7 零影响
- **回归**：pytest **246/246**；三闸/四闸/五闸 + validate-ontology + capture-validate 全 PASS；
  ruff 40 = 基线零新增；CI 双矩阵全绿；golden 基线 C4 更新（双副本，SHA256 4c4d1b3d…）
- 报告：[K1 评分正确性报告](docs/migration/K1-score-correctness-report.html)

## 文档站化（窗口 H — 2026-08-16，无版本号）

- **站点规范**：`docs/site-design.md`（导航结构 / 目录组织 / 双语策略 / Release 衔接 / 链接与数字口径纪律）
- **Pages 导航升级**：自定义 `_layouts/default.html`（cayman 主题无导航 → 9 项导航覆盖全站）；
  `_config.yml`（lang / github_repo / exclude 代码目录，冻结资产不进 Pages）
- **docs/ 目录组织**：评测报告归入 `docs/migration/`（agent-eval-report / agent-eval-report-g2）；
  宪法协议归入 `docs/protocols/`（agent-eval-protocol / benchmark-protocol）；新增 `docs/environment/`
  （github-pages.md）；`docs/specs/` 与 `docs/migration/` 配 index 索引页；契约/宪法一级文档
  （api-contract / mcp-contract / reward-mapping / reward-protocol）因代码 docstring 与测试锚定保留根级
  （site-design.md §4 决策记录）
- **核心文档双语**（H11 裁决）：README（`README.md` 中文主版 + `README.en.md` 英文版）+ 快速开始
  （`docs/quickstart.md` + `docs/quickstart.en.md`）；其余文档中文为主不翻译（site-design.md §5.1 决策记录）
- **与 Release 衔接**：CHANGELOG 条目引用文档链接；站点导航含 Release 项；v0.2.0 Release body 更新文档链接
- **G-2 遗留 minor 整改**：`src/bioaudit/__init__.py:8` ruff E501（107>100）→ 注释独立成行
- **回归**：golden 20 轨迹 137 决策 0 差异；pytest 234/234；ruff 零新增；CI 双矩阵全绿；
  Pages 构建成功 + HTTP 200 + 导航可达 + 链接无 404

## 0.2.1 — 2026-08-16（窗口 G-2：评测缺口修复 + 窗口 J：规则质量修复）

- **declared 四级可信源落地**（采集层）：call_arg > data_metadata > declared（评测者/数据事实声明）> unverified；
  Agent 上报键永远不进 declared（宪法 §4.1）；12 项测试（test_declared_eval.py）
- **规则平台键审查与放宽**（规则层）：22 条 scRNA 规则 required_context 平台依赖逐条审查
  （过强放宽 17 条 / D1.1 双联体保留 10X 专属）；GSE115978 平台事实查证定案 = **Smart-seq2**
  （GEO Overall design 原文）→ declared 注入 smartseq2；required_context 列表 any-of 语义（engine 0.2.1）；
  ruleset **1.1.1 → 1.2.0**
- **重评（零成本，复用已有 WAL/notebook）**：真实运行有效分数 **30.0 needs_correction（L0=0/L1=7/L3=1/L-1=12）**，
  与 demo 轨迹 **29 分 5 L0** 口径严格区分（禁止混写，教训 #2）；golden **0 差异基线未更新**（纯加性放宽，C4 未触发）
- **J1 wilcoxon 词表对齐**（规则层，窗口 J）：G1.3/G1.1 词表对齐（wilcoxon 家族 5 词条全 L1，
  以 G1.1 语义为准，D2 MAST 同原则）；修复 I 窗口发现①（B 版 L0 来自 G1.3 词表缺口兜底）；
  ruleset **1.2.0 → 1.3.0**；golden 基线 C4 更新 2 决策（L0→L1，轨迹分不变）；
  **B 版黄金对照重评 63.0 blocked → 69.0 needs_correction**（I 报告 §11.5 预警应验）
- **J2 significance_threshold 新规则**（窗口 J）：scRNA 范式新增 **G1.4-DEG-004**（文献锚定
  Conesa 2016 PMID 26813401 等，词表与 M1.3 对齐）；本体扩 scRNA + padj_cutoff/logfc_cutoff 键
  （ontology 0.1.1）；ruleset **1.3.0 → 1.4.0**（39 唯一规则）；三版黄金 Agent 重评
  significance_threshold **L-1 → L3**（聚合分不变）；覆盖豁免登记（D5.12，批 3 补覆盖）
- **J3 annotation L3 签名评估**（窗口 J）：SingleR 无成熟 Python 实现（仅 BiocPy singler 0.1.x
  早期绑定）+ L3 需产物级一致性验证 → **如实声明不硬补签名**，A 版保持 80.0 天花板；backlog 登记
- **连锁影响（J 窗口实测留档）**：benchmark 60 任务检出指标零变化（precision 0.745/recall 0.820/
  F1 0.781）、mean 0.5528→0.5542、gap +0.046→+0.048（区间内，预注册口径解释见 J 报告 §5.2）；
  reward 校准 ρ 0.6179→0.6008、分层差 +0.3614→+0.3434（p=0.000 保持显著）；golden 最终 0 差异
- **回归**：pytest **235/235**；三闸/四闸/五闸/capture-validate/MCP selfcheck 全 PASS；
  CI 双矩阵全绿；**v0.2.1 tag + release notes**（文档站链接见正文）
- 报告：`docs/migration/agent-eval-report-g2.md`（主报告留档：`docs/migration/agent-eval-report.md`）；
  审查报告：`docs/migration/G2b-platform-key-review.md`；宪法：`docs/protocols/agent-eval-protocol.md`（§4.1 修订）；
  窗口 J 报告：`docs/migration/J1-rule-quality-report.md`

## 0.1.6 — 2026-08-16（窗口 F：批 2 任务集 30 → 60 + 校准更新）

- **任务集 v1.1.0（60 条）**：批 2 生成 30 条（scrna 10 / pan 10 / deg 10，
  合计 scrna 22 / pan 20 / deg 18）；批 1 scrna 无 easy 缺口补齐（批 2 新增
  4 条 easy）；难度分布 3 范式 × 3 梯度全非空（easy 24 / medium 27 / hard 9）；
  覆盖审计仍 **34/34 类型 + 38/38 规则**（零触发 = 0）；污染扫描 0 命中；
  bmd_scrna_020 直接使用**真实 CellVoyager 轨迹**（scrna_melanoma_cellvoyager）
  作为错误模式素材（hook 真实运行仍未实测，如实声明）
- **新预注册记录 `benchmark-pr-2026-08-16-02`**：60 条全量重新划分（seed=42，
  public 42 / hidden 18）；gap 区间重评估（保持 [−0.10, +0.10] 保守可比）；
  **批 1 记录 `benchmark-pr-2026-08-16-01` 常量 + 磁盘副本留档**
- **rubric v1.1（annotation.v1.1）**：D 窗口遗留 6 条澄清点全部落地
  （TMM 工具链耦合 / 只评本步 vs 管线衔接 / 报告解释不足归属 / note 与
  choice 矛盾以 choice 为准 / 模板笔误不入罪 / 双细胞去除与下游设计依赖），
  每条锚定批 1 仲裁实证；批 1 标注不追溯重判
- **标注实测**：批 2 校准批 10 条 **κ=0.8694 / α=0.8693 达标放量**；批 2 全量
  275 决策 **κ=0.9336 / α=0.9336**（一致率 97.09%）；**全量 60 合并 623 决策
  κ=0.8336 / α=0.8335**；分歧 8 条全仲裁（strong 583 / medium 40 / weak 0）
- **gap 重评估（如实）**：**Δ=+0.046 ∈ 区间，告警解除**——批 1 Δ=−0.1864
  的"隐藏集小样本组成偏差"判读在 hidden n=9→18 后获收敛证据支持
- **reward 校准重跑（60 条）**：配方 B ρ=0.6179 [0.4042, 0.7830]、
  τ_b=0.5033 [0.3219, 0.6618]；分层 good 0.6775 vs bad 0.3160、
  diff=+0.3614 [0.2291, 0.4719]、**p=0.000 显著分离**；多种子恒定；
  reward-protocol.md §7.1 批 1 旧值留档 + §7.2 新表
- **回归**：golden **20 轨迹 137 决策 0 差异**；benchmark-validate 四闸 +
  reward-validate 五闸 PASS（CI 双矩阵零改动）；pytest **220/220**（206 + 新增 14）
- 报告：`docs/migration/F1-phase3-benchmark-batch2-report.md`；
  协议：`docs/protocols/benchmark-protocol.md`（批 2 扩展）

## 0.2.0 — 2026-08-16（v0.2.0 Release：五阶段重构完成，demo → 可迭代产品）

**里程碑版本**：从"四套分裂演示 demo"升级为"单仓库可迭代产品"，三价值层（lint / benchmark / reward）全部落地。

- **阶段 0 止血**：D5 条件提升 bug 修复（12 决策降级，CellVoyager 41→29）；DEG 双副本去重（43 文件 → 38 唯一规则）；分数口径统一（标签=报告=实测）；R0 重算（Spearman 0.9747 修复后仍成立）；密钥清除
- **阶段 1 地基**：单仓库 `bio-audit`（pyproject/Apache-2.0/路径锚定）；决策类型本体化（34 类型 + context schema + aliases）；API 契约（pydantic 校验 + 错误码 + paradigm 消歧）；轨迹 v2 迁移（provenance）；规则治理三闸 + 三元组快照；CI 双矩阵（pytest + golden + 三闸）
- **阶段 2 采集**：M1 主动上报（CellVoyager hook，异常隔离）+ M3 解析器（signatures 驱动，禁猜规则）+ 交叉验证（四类判定）+ verdict 状态位（provisional/final/revoked）+ MCP server + 事件告警
- **阶段 3 benchmark**：30 条任务集（首批，3 范式 × 难度梯度，348 决策）+ 双标注 IRR（κ=0.81 校准批达标）+ 预注册（gap 区间/划分/门槛）+ 防泄漏三线 + 功效分析（bootstrap CI + Holm）
- **阶段 4 reward**：映射"宪法"（非线性 0/0.30/0.60/0.85/1.00，-1 mask，γ=0.30 硬惩罚）+ 三配方消融 + spike-in 强锚点（三范式 drop ≥0.61）+ 排序一致性验收（分层检验 p=0.001）
- 数字：**pytest 206/206** · CI 双矩阵全绿 · golden 20 轨迹 137 决策 0 差异 · GitHub Pages 上线
- 文档栈：审计报告 / 设计定稿（本体·采集）/ 执行方案 / 各窗口报告 / 里程碑总结（docs/specs/2026-08-16-v2-milestone-summary.md）

## 0.1.5 — 2026-08-16（窗口 E：阶段 4 reward 训练信号）

- **reward 包**（`src/bioaudit/reward/`，外围输出层，评分路径零改动）：
  mapping（E1.2 映射定稿：level→reward 非线性 0/0.30/0.60/0.85/1.00，-1 mask，
  85.0 天花板明确不做微调）/ recipes（A 纯规则分 / B +L0 硬惩罚 γ=0.30 二元 /
  C PRM 预留接口，占位权重均匀）/ api（`reward(trajectory) -> {step_rewards,
  trajectory_reward, meta}`，meta 带三元组快照 C1/P2）/ calibration（E3：
  ρ/τ + bootstrap CI + 分层均值检验 + 多种子 + spike-in）/ validate（五闸）
- **纪律落地**：-1 必须 mask（不参与分子分母，全 mask → None）；只消费 final
  verdict（B4：revoked/provisional/无记录 → mask）；F4 交叉验证四类判定不进
  reward（代码 + 测试双守卫）；**golden 20 轨迹 137 决策 0 差异**
- **校准实测（30 任务冻结）**：配方 B 排序一致性 ρ=0.6091 [0.2894, 0.8335]、
  τ_b=0.4898 [0.2131, 0.7213]；分层均值检验 good 0.6611 vs bad 0.2862，
  diff=+0.375 [0.195, 0.536]，p=0.001（显著分离）；硬惩罚使分离放大 3.4×；
  多种子点估计恒定 + CI 稳定；spike-in 强锚点 scrna_correct + L0 注入
  drop=0.6146 ≥ 0.30（三范式同验）
- **report 集成（E4.10）**：run_audit report 新增 `reward` 块（status=
  experimental_uncalibrated，C3 语义不变）；既有字段零改动
- **CLI**：`reward`（E1 API）/ `reward-calibrate`（E3 校准报告）/
  `reward-validate`（E4 五闸：映射/确定性/spike-in/消融/golden）
- **CI**：双矩阵新增 reward-validate 步骤（E4.13）
- **文档**：`docs/reward-mapping.md`（映射定稿决策记录——"宪法"）、
  `docs/reward-protocol.md`（配方/验收统计量/锚点协议）、api-contract.md §九
- 代码侧 `__version__` 保持 0.1.3（外围层，与快照三元组/任务集快照一致）
- 测试：pytest **206/206**（174 + 新增 32：tests/test_reward.py）；
  报告：`docs/migration/E4-phase4-reward-report.md`

## 0.1.4 — 2026-08-16（窗口 D：阶段 3 benchmark 评测基准）

- **benchmark 包**（`src/bioaudit/benchmark/`，外围层，评分路径零改动）：
  models（Task = v2 轨迹 + gold + difficulty）/ manifest（taskset.json semver）/
  difficulty（E4 预注册 rubric，不依赖审计分数）/ protocol（E1 预注册记录 +
  split 分层随机 seed=42 + gap 容忍区间 [−0.10, +0.10] 负向告警）/
  generator（E6：提示词零规则内容 + 语料变换）/ annotation（E3：κ/α ≥ 0.8 +
  仲裁 + 共识强度）/ runner（D4：批量评测 + bootstrap CI + Holm 校正）/
  contamination（E2 黑盒污染扫描）/ coverage（E5：34 类型 + 38 规则全覆盖）
- **任务集 v1.0.0**：`src/bioaudit/data/tasks/` 首批 30 条（scrna 12 / pan 10 /
  deg 8；批 2 排期补齐至 60）；双标注 + IRR 实测（详见完成报告）；
  taskset.json（semver + 文件哈希 + 快照三元组 + split + 模型信息）
- **CLI**：`benchmark-run`（运行器 + 功效报告）/ `benchmark-validate`
  （四闸：清单 + 污染 + 覆盖 + golden）
- **CI**：双矩阵新增 benchmark-validate 步骤（D6.16）
- golden 回归：**20 轨迹 137 决策 0 差异**；测试全量绿（详见完成报告）
- 报告：`docs/migration/D3-phase3-benchmark-report.md`；
  协议：`docs/protocols/benchmark-protocol.md`

## 0.1.3 — 2026-08-14（B5 规则治理 + B6 回归 CI，阶段 1 窗口 ⑦）

- **B5 ruleset.json 正式启用**：`rules/manifest.py`（加载/校验/生成）——
  `RULESET_VERSION` 从 ruleset.json 读取（不再硬编码，缺失/非 semver fail-closed）；
  清单含 43 文件 SHA256+size / 38 唯一 rule_id / semver / engine+ontology 版本；
  `verify_manifest` 五项检查（哈希篡改守卫测试）
- **B5 三元组快照写全**（C1/P2）：run_audit report 的 engine_version / ruleset_version /
  ontology_version / snapshot 全部非 None（0.1.3 / 1.1.0 / 0.1.0）
- **B5 ruleset-validate 三闸**：`bio-audit ruleset-validate` 一条命令 =
  清单校验 + D2 冲突检查 + golden 重放（D1 变更流程，exit 0/1，CI 门禁）
- **B5 D2 冲突裁决**（裁决书 docs/specs/2026-08-14-d2-adjudication.md）：
  ① deg_method/MAST → G1.3 修订（裸 MAST L2→L1 与 G1.1 对齐；L2 仅保留
  MAST_with_replicate_correction）——评分零变化，golden 0 差异，基线未更新；
  ② multiple_testing_correction/bonferroni → 范式隔离成立（冲突检测器升级为
  范式感知 scope=same-rule-set）；冲突数 2 → 0
- **B5 D4 修复条目映射表**：docs/specs/2026-08-14-fix-tracking.md（audit-report
  全部 78 条 → 已修 52 / 挂账 14 / 排期 12）
- **B6 CI**（.github/workflows/ci.yml）：Python 3.10/3.12 双版本矩阵跑 pytest +
  golden（失败即红）+ ruleset-validate + validate-ontology + R0 锚定；漂移摘要
  golden-summary.json 上传 artifact（人工确认门槛）
- **B6 依赖锁定**：requirements.lock / requirements-dev.lock（pip-tools；
  numpy 2.2.6 / scipy 1.15.3 保 Python 3.10 兼容）
- **B6 R0 脚本迁移**（B1 遗留 1）：scripts/generate_scrna_r0.py 包内锚定
  （bioaudit 导入 + rules_dir_for + VALIDATION_DIR）；异 cwd 重生成与包内
  scrna_r0.json **逐字节一致**（SHA256 16f31ff4…）
- 版本说明：0.1.2（B3/B4）在上一窗口仅记录于 CHANGELOG，代码侧 __version__
  未同步——本窗口对齐为 0.1.3
- golden 回归：**20 轨迹 137 决策 0 差异**；pytest 86/86；asset_manifest.json
  G1.3 条目更新 + change_log

## 0.1.2 — 2026-08-14（B3 API 契约 + B4 轨迹迁移器，阶段 1 窗口 ⑥）

- **B3 API 契约**：三入口（run_audit / audit_decision / match_details）输入全部 pydantic 校验，
  非法输入显式报错（错误码），不静默降级——act 未知不再静默回退全量规则（→ paradigm-not-found）；
  Decision `extra="forbid"`（A15：decisionType 拼错不再静默变"无法评估"）
- **错误码体系**：`bioaudit/errors.py` — bad-request / validation-error / paradigm-not-found /
  rule-not-found / internal-error（+HTTP 映射）；异常统一包装为 `BioAuditError`，不裸抛；
  run_audit 管道内部失败写 `state["error_code"]`；matched 规则缺失 → rule-not-found
- **audit_decision 必填 paradigm**（B2）：deg_method 同名异构消歧（同 choice 不同范式不同评分，
  契约测试守卫）；human_overrides 校验 int 且 -1..4（A7），非法拒绝并记录
  `invalid_override_rejected` 事件
- **契约文档**：`docs/api-contract.md`（三入口 schema + 错误码 + 示例 + 行为变更清单）；
  契约测试 `tests/test_api_contract.py`（24 项）；CLI audit-decision `--act` 必填、错误 JSON 输出
- **B4 轨迹迁移器**：轨迹 v2 schema（version 必填 + trajectory_id/act/provenance/decisions，
  常量经 report/schema.py 再导出）；只读迁移器 `capture/trajectory_migrator.py`
  （只写 `data/trajectories/v2/`，v1 原文件保留 = 备份）；20 条旧轨迹全部迁移，
  `provenance.source=legacy`；schema 校验器缺必填字段显式报错（A15）；
  CLI `migrate-trajectories` / `trajectory-validate`
- golden 回归：**20 轨迹 137 决策 0 差异**（version/provenance 是元数据，不参与评分，基线未更新）；
  pytest 75/75；迁移清单见 `docs/migration/B4-trajectory-migration-report.md`

## 0.1.1 — 2026-08-13（B2 本体落地，阶段 1 核心）

- **本体落地**：`src/bioaudit/ontology/` — paradigms.yaml（3 范式，bulk-DEG 标"骨架待补全"）、
  stages.yaml（6 阶段）、aliases.yaml（3 组同源声明）、topics.yaml（8 主题族）、
  backlog.yaml（G2/G6 待补清单）、decision_types/ 34 个定义文件
- 决策类型定义含 display/stage/paradigms/dimension/optional/depends_on/context_schema；
  missing 三档（fail-closed/skip/fail-open）；A4 design→fail-closed；G3 unit 键（4 类型）；
  G4 batch_correction confound 键；G5 optional+when_not_applicable；G1 一致性族 internal_ref
- **P1 校验器三职责**（`ontology/validator.py` + `bio-audit validate-ontology` CLI）：
  覆盖报告（范式×阶段×类型 / 规则反推 vs 流程正推 / 待补清单）、语义边界（missing 档位、
  A2 罚分规则禁 fail-open、A4/G3/G4/G5、depends_on 不悬空、aliases 对称）、
  冲突完整性（D2：同 choice 不同 level，现存 2 处 finding）
- **引擎接线**（本体为单一事实源）：聚合器删除 TYPE_TO_DIMENSION 硬编码改读 dimension；
  error_tracer 读 depends_on（替代 dependency_graph.yaml，DEG 3 边逐条保留 + scRNA/pan 新增）；
  matcher 读本体 input_synonyms（行为不变）+ 同源注释（homologous_types，非匹配通道）+
  unclassified 标记
- golden 回归：**20 轨迹 137 决策 0 差异**（本体化未改变评分行为）；pytest 38/38
- 资产完整性：72/72 数据文件与 asset_manifest.json 哈希一致（B2 未改动任何冻结资产）

## 0.1.0 — 2026-08-13（B1 阶段 1 骨架）

- 单仓库建立（替代 bio-audit / pancancer-audit / scRNA-audit / fullflow-demo 四项目）
- 引擎迁移（fullflow-demo D5 修复后 + DEG 双副本统一 + mappings 补齐为基准）
- 43 条规则 / 20 轨迹 / validation 数据 / mappings 迁入包内（哈希核对 asset_manifest）
- 路径锚定：所有资源经 `bioaudit.paths` 解析，零 cwd 依赖（F7）
- API 单一入口 `run_audit` / `audit_decision`（B3 契约细化待办）
- UI 薄壳化：只调 api，移除内联管道与演示 sleep（D7），导出 JSON 修正（D1）
- golden 回归：20 轨迹 137 决策 0 差异（`scripts/golden_replay.py` + `tests/test_golden.py`）
- 全新 git 历史（不携带旧仓 13GB 二进制）；Apache-2.0；README/CONTRIBUTING 就位
