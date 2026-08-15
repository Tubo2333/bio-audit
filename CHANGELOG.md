# Changelog

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
  协议：`docs/benchmark-protocol.md`

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
