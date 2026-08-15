# 窗口 E 完成报告：阶段 4 reward 训练信号

> **日期**：2026-08-16
> **执行依据**：docs/specs/2026-08-13-execution-plan-v1.md §六.八（E1-E4 验收清单，13 项冻结）
> + refactor-plan-v1.1（F1-F7 方法论裁决）+ 拍板 #1（F4：交叉验证判定不进 reward）
> + 拍板 #2（F7：验收 = 排序一致性 + 分层均值检验，放弃 Spearman 点估计门槛）
> **验收结果**：**E1-E4 全部 13 项 ✅**（逐项见 §三）；golden **20 轨迹 137 决策 0 差异**；
> pytest **206/206**（174 + 新增 32：tests/test_reward.py）

---

## 一、执行范围与纪律对照

按建议顺序执行：**E1（API + 映射定稿）→ E2（配方 + 消融）→ E3（校准 + 验收）
→ E4（集成 + 回归）**。

五条关键纪律逐条对照：

| # | 纪律 | 落地 |
|---|------|------|
| 1 | reward 是外围输出层，**不得改变评分路径**（golden 0 差异硬验收） | matcher/evaluator/aggregator/registry **零改动**；reward 只消费 step_scores；report 新增 `reward` 块（纯函数，既有字段不变）；golden 复跑 **0 差异**（§三.11） |
| 2 | **-1 必须 mask**，不参与聚合 | `level_reward(-1)=None`；不参与分子与分母；全 mask → `trajectory_reward=None`（不给 0 虚假信号）；测试 `test_minus_one_masked_in_aggregation` |
| 3 | **只消费 final verdict**（阶段 2 状态位 B4） | revoked → mask(revoked)、provisional → mask(provisional_not_final)、无记录 → mask(no_verdict_record)；revoked 的 L0 不触发硬惩罚；verdict_store 集成测试 |
| 4 | 交叉验证四类判定（虚报/漏报/未验证）**不进 reward**（F4 拍板） | reward 包零引用交叉验证器（源码级守卫）+ 输出 schema 无四类判定字段（输出级守卫），双守卫测试 |
| 5 | 验收用**排序一致性 + 分层均值检验**（F7 拍板），不用 Spearman 点估计当门槛 | ρ/τ + bootstrap CI **如实报告**；主判据 = good/bad 分层显著分离（diff>0 且 p<0.05，预注册分组）；ρ 不做阈值 |

## 二、产出清单

| 类别 | 文件 | 说明 |
|------|------|------|
| 包 | `src/bioaudit/reward/`（6 模块） | mapping（映射定稿）/ recipes（配方 A/B/C + 硬惩罚 + PRM 接口）/ api（E1.1 入口 + report 集成）/ calibration（E3 统计 + 锚点）/ validate（E4 五闸） |
| CLI | `reward` / `reward-calibrate` / `reward-validate` | E1 API / E3 校准报告 / E4 自检五闸 |
| 决策记录 | `docs/reward-mapping.md` | **E1.2 映射定稿"宪法"**（数值 + 等距/非线性论证 + min/mean + 饱和 + -1 mask + γ 依据 + PRM 接入点） |
| 协议 | `docs/reward-protocol.md` | 配方定义 / mask 语义 / 预注册统计量与分组 / 锚点阈值依据 / 实测表 |
| 契约 | `docs/api-contract.md` §九 | reward 入口请求/响应 schema + 契约要点 |
| report 集成 | `src/bioaudit/api/audit.py` Step 7 | report.reward 块（`experimental_uncalibrated`，C3 语义不变；失败降级不拖垮报告） |
| CI | `.github/workflows/ci.yml` | 双矩阵新增 reward-validate 步骤（E4.13） |
| 测试 | `tests/test_reward.py`（**32 项**） | 映射/mask/时序/消融/锚点/确定性/报告集成/CLI |
| 报告 | `docs/migration/E4-phase4-reward-report.md` | 本文件 |

## 三、验收对照（§六.八 E1-E4，13 项逐项）

### E1 reward API 与映射定稿

- [x] **1. reward API：`reward(trajectory) -> {step_rewards, trajectory_reward, meta}`，
  带三元组快照（ruleset/ontology/engine，C1/P2 复用）→ 可复现**：
  `reward()`（E1.1 定稿签名：trajectory/act/recipe/session_id/verdicts/prm_weights/
  snapshot）；meta.snapshot 携带三元组（默认 `current_snapshot()`，可显式传入）；
  report 集成复用纯函数 `report_reward_block`；测试 `test_reward_api_structure_and_snapshot`。
- [x] **2. Level→reward 映射定稿（决策记录 docs/reward-mapping.md）**：
  **映射表** `{4:1.00, 3:0.85, 2:0.60, 1:0.30, 0:0.00}`（非线性/严重性凸：底部
  严重性 > 顶部区分度，论证见文档 §2）；**-1 mask**（不参与聚合，文档 §3）；
  **85.0 天花板饱和：明确不做 evidence 微调**（理由：证据质量未校准 + 确定性
  底线 + L4 是预留出口；扩展点 `EVIDENCE_ADJUSTMENT_HOOK=None` 显式记录，文档 §4）；
  **min vs mean：选 mean**（credit assignment：mean 稠密每步可归因，min 塌缩；
  稀释问题由硬惩罚显式解决，min 的保守语义由引擎审计分数承担，文档 §5）。
- [x] **3. 时序化（F2）：per-step reward 序列；M1 声明时序为准、M3 补漏按阶段
  末尾聚合；只消费 final（B4 状态位，revoked 步骤 reward 置 mask）**：
  step_rewards 带 order（0-based，M1 声明顺序）+ source（declared/backfilled）；
  M3 补漏条目在轨迹文件阶段末尾 = "阶段末尾聚合"语义；verdict 映射
  （revoked/provisional/无记录 → mask，三种 reason 区分）；无会话 = all_final
  模式（legacy/benchmark，meta.verdict_mode 如实标注）；测试
  `test_temporal_order_and_sources` / `test_final_only_verdict_masking` /
  `test_final_only_via_verdict_store_session`。

### E2 配方与消融

- [x] **4. F4 遵守：交叉验证四类判定不进 reward（代码与测试双重守卫）**：
  源码级守卫（reward 包无 cross_validator/CrossValidator/M3 解析器引用）+
  输出级守卫（输出无 false_report/missed/unverified 等字段）；
  `test_f4_reward_does_not_consume_cross_validation_stats` /
  `test_f4_reward_output_has_no_four_judgment_stats`。
- [x] **5. 配方定义：基线 = 纯规则分；硬惩罚阈值（任一 L0 → 轨迹级惩罚系数，
  数值与依据记录）；PRM 加权接口预留**：
  A = mean（纯规则分）；B = A × **γ=0.30**（任一未 mask L0，二元不复利）——
  γ 依据（docs/reward-mapping.md §6）：L0 语义 = "将导致错误结论"/verdict=blocked；
  n≥2 时含 L0 轨迹 reward ≤ 0.246 < 0.60（L2-only 地板）< 0.85（全对），
  "显著低于全对"数学保证；实测佐证：B 的分层分离 = A 的 3.4 倍（0.375 vs 0.110）；
  **PRM 预留**：recipe C 权重接口（默认 1.0 均匀占位 → C≡A 诚实声明；
  非均匀权重改变输出 = 接口生效测试证明；接入点文档 §7）。
- [x] **6. 三组消融可运行：A/B/C 同一输入三组输出可比**：
  `ablate()` / `bio-audit reward-calibrate`——同一 30 条任务、同一引擎
  step_scores、同 schema；实测 summary：A 0.7069 / B 0.4487 / C 0.7069
  （n_evaluable 全 30）；测试 `test_ablation_three_recipes_comparable_on_same_input`。

### E3 校准与验收

- [x] **7. 排序一致性验收（F5/F7，拍板 #2）：30 任务 reward 排序 vs gold 排序，
  报告 Spearman/τ + 分层均值检验（好/坏任务组显著分离）+ CI；放弃点估计门槛**：
  预注册分组 good = n_gold_error==0 / bad = n_gold_error≥1；实测（配方 B）：
  **Spearman ρ = 0.6091 [0.2894, 0.8335]、Kendall τ_b = 0.4898 [0.2131, 0.7213]**
  （任务级重采样 percentile bootstrap，B=2000，seed=42）；**分层均值检验：
  good 0.6611 [0.5159, 0.7914] vs bad 0.2862 [0.2009, 0.3939]，
  diff = +0.375 [0.1954, 0.5355]，置换 bootstrap p = 0.001 → 显著分离 ✅**。
  如实解读：ρ≈0.61 中等强度符合 F7 预期（gold 评结果含未检出错误 FN、
  reward 评方法，非单调映射），验收判据是分层分离显著 + 排序一致有正证据。
- [x] **8. 多种子复跑 + 确定性（F6）**：reward 无随机源（确定性测试：同输入
  两次逐字节一致）；多种子 {42, 1, 7, 123, 2026}：ρ/τ 点估计完全恒定
  （0.6091/0.4898），bootstrap CI 边界跨种子偏差 ≤ 0.05（稳定）——
  `test_reward_determinism` / `test_multi_seed_stability` / reward-validate 闸 2。
- [x] **9. 校准锚点（F7）：weak anchor = benchmark gold；strong anchor =
  spike-in 合成数据（注入已知 L0 → reward 显著下降）——落地 + 测试**：
  弱锚点 = §7 排序一致性/分层检验（gold 质量 q = correct/(correct+error)）；
  **强锚点**（spike-in，drop 阈值 0.30 预注册，依据 = (n−1)/n·0.85·γ 最坏
  情形 n=2 时 0.2975，取保守 0.30）：
  - scrna_correct + `no_doublet_detection`（引擎实测 L0 自校验）→ **0.85 → 0.2354，drop = 0.6146** ✓
  - deg_correct + `no_correction` → **0.85 → 0.2125，drop = 0.6375** ✓
  - pan_correct + `no_ph_test` → **0.85 → 0.2400，drop = 0.6100** ✓
  三范式全部 drop ≥ 0.30 且注入步骤 level==0（L1 注入对照：drop 远小于 L0，
  惩罚针对性测试）；测试 `test_spike_in_known_l0_drops_reward` /
  `test_spike_in_anchor_works_all_paradigms` / `test_spike_in_l1_injection_smaller_drop_than_l0`。

### E4 集成与回归

- [x] **10. report 集成：reward 字段进 report（标注 experimental/未校准，
  C3 语义不变），CLI 暴露**：
  run_audit report 新增 `reward` 块：`status=experimental_uncalibrated` +
  reward_schema=reward.v1 + 全量 step_rewards/trajectory_reward/meta；
  失败降级块（不拖垮主报告，测试证明）；CLI `bio-audit reward <轨迹>
  [--act] [--recipe A|B|C] [--session] [--prm-weights]`（E4.10）+ 
  `reward-calibrate` + `reward-validate`；contract 文档 §九。
- [x] **11. golden 0 差异（评分路径零改动）**：`bio-audit golden` **20 轨迹
  137 决策 0 差异**（reward-validate 闸 5 常驻守卫；评分路径文件零改动）。
- [x] **12. 测试全量绿 + 新增 reward 测试（映射/mask/时序/消融/锚点）**：
  pytest **206/206**（174 → +32：tests/test_reward.py——映射定稿 3 /
  聚合语义 1 / API 结构 3 / 时序与 final-only 4 / mask 2 / 配方与惩罚 4 /
  PRM 接口 2 / F4 守卫 2 / 消融与确定性 3 / 排序一致性 2 / 分层检验 1 /
  spike-in 3 / 报告集成 2 / CLI 3）；ruff 新代码零错误。
- [x] **13. CI 步骤更新（reward 自检纳入双矩阵，离线可运行）**：
  ci.yml 双矩阵新增 `bio-audit reward-validate --json`（五闸：映射健全 /
  确定性 / spike-in 锚点 / 三组消融 / golden 0 差异 + 校准证据输出，全部
  离线，只消费包内资产）。

## 四、消融与校准实测汇总（30 任务冻结，docs/reward-protocol.md §七）

| 配方 | ρ [CI] | τ_b [CI] | good | bad | diff [CI] | p |
|------|--------|----------|------|-----|-----------|-----|
| A | 0.6279 [0.2916, 0.8380] | 0.4949 [0.2099, 0.7182] | 0.7692 | 0.6592 | +0.110 [0.036, 0.183] | 0.007 |
| **B** | **0.6091 [0.2894, 0.8335]** | **0.4898 [0.2131, 0.7213]** | **0.6611** | **0.2862** | **+0.375 [0.195, 0.536]** | **0.001** |
| C | 0.6279 [0.2916, 0.8380] | 0.4949 [0.2099, 0.7182] | 0.7692 | 0.6592 | +0.110 [0.036, 0.183] | 0.007 |

- 三组消融同输入可比：A 0.7069 / B 0.4487 / C 0.7069（C 占位权重 → ≡A，预期）；
- **B 是默认配方的实证依据**：硬惩罚把分层分离放大 3.4 倍且不扭曲排序
  （ρ 0.628→0.609，CI 重叠）；
- 多种子：点估计恒定（确定性）、CI 稳定（偏差 ≤ 0.05）；
- spike-in：三范式 drop 0.610–0.638，全部 ≥ 0.30 强锚点通过。

## 五、映射决策记录摘要（完整论证见 docs/reward-mapping.md）

| 决策点 | 定稿 | 核心论证 |
|--------|------|----------|
| 映射对象 | level（非 numeric_score） | 与评分路径解耦；numeric 是展示口径 |
| 等距 vs 非线性 | 非线性（0.00/0.30/0.60/0.85/1.00） | level 语义间距不等；惩罚错误的边际价值 > 奖励锦上添花 |
| -1 | mask（不参与分子分母） | 无好坏信息；给值 = 注入虚假信号 |
| 85.0 饱和 | 明确不做微调（扩展点显式记录） | 证据质量未校准；L4 是预留出口 |
| min vs mean | **mean**（+ 硬惩罚组合） | mean 稠密 credit assignment；min 塌缩且与引擎 C1 冗余 |
| 硬惩罚 | γ=0.30，二元 | L0="将导致错误结论"；n≥2 时含 L0 轨迹 ≤ 0.246 < 0.60 < 0.85 |
| PRM | 接口预留（占位权重 1.0 均匀） | PRM 未实现；接口先通，诚实标注 C≡A |

## 六、experimental 标注说明（E4.10 / C3 语义）

- report.reward.status = **`experimental_uncalibrated`**——reward 是训练信号
  候选，**未经过 RLHF 校准**；任何消费方不得把 reward 当校准信号用于生产决策；
- 与既有 C3 语义的关系：报告 schema 版本不变（新增可选字段，非破坏性变更）；
  引擎/规则/本体版本与快照三元组不受影响；golden 基线未更新（评分零变化，
  C4 未触发）；
- 内部纪律：映射定稿（docs/reward-mapping.md）为"宪法"，数值变更走评审 +
  reward-validate 全闸 + golden 0 差异（文档 §10 变更流程）。

## 七、遗留与排期（如实声明）

1. **批 2 任务集（30→60）落地后校准重跑**：本文档 §四 表格更新 + 新预注册
   记录（旧值留档）；分层检验随任务集变化如实重新评估（reward-protocol.md §八）；
2. **PRM 未实现**：配方 C 占位权重（均匀）持续生效；PRM 落地后替换权重并走
   映射变更流程；
3. **report 集成已含降级保护**：reward 块失败不拖垮报告（外围层纪律测试）；
   未来若 reward 转为生产信号，需先完成 RLHF 校准（超出本窗口范围）；
4. 映射/统计代码 numpy-only（不引 scipy 核心依赖），与 B6 锁依赖一致。
