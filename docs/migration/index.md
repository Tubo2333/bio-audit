# 窗口报告索引

各执行窗口的完成报告（验收清单见执行方案 execution-plan-v1，仓库外审计内存）。

## 阶段 1 地基（窗口 B）

| 报告 | 内容 |
|---|---|
| [B1 单仓库骨架与迁移](B1-migration-report.html) | 单仓库建立、72/72 资产哈希一致、路径锚定、golden 0 差异 |
| [B2 本体落地](B2-ontology-report.html) | 34 决策类型 + P1 校验器三职责 + 引擎接线 |
| [B3 API 契约](B3-api-contract-report.html) | 三入口 schema + 错误码体系 + 契约测试 |
| [B4 轨迹迁移器](B4-trajectory-migration-report.html) | 20 条 v1 → v2 轨迹迁移（只读迁移器 + 双哈希清单） |
| [B5 规则治理](B5-ruleset-governance-report.html) | ruleset v1.1.0 + 三闸 + D2 冲突裁决 |
| [B6 回归 CI](B6-regression-ci-report.html) | 双版本矩阵 + 漂移报告 + 依赖锁定 + R0 锚定 |

## 阶段 2 采集（窗口 C）

| 报告 | 内容 |
|---|---|
| [C2 阶段 2 采集 lint 完成报告](C2-phase2-capture-report.html) | M1 hook / M3 解析器 / 交叉验证 / verdict 状态位 / MCP / 可观测 |

## 阶段 3 benchmark（窗口 D / F）

| 报告 | 内容 |
|---|---|
| [D3 阶段 3 benchmark 完成报告](D3-phase3-benchmark-report.html) | 首批 30 条任务集 + IRR + 预注册 + 功效 |
| [F1 批 2 任务集 30→60 完成报告](F1-phase3-benchmark-batch2-report.html) | 任务集 v1.1.0 + rubric v1.1 + gap 收敛 |

## 阶段 4 reward（窗口 E）

| 报告 | 内容 |
|---|---|
| [E4 阶段 4 reward 完成报告](E4-phase4-reward-report.html) | 映射定稿 + 三配方消融 + 校准验收 |

## 真实评测（窗口 G / G-2）

| 报告 | 内容 |
|---|---|
| [G2b 规则平台键审查](G2b-platform-key-review.html) | 22 条 scRNA 规则 required_context 平台依赖逐条审查 |
| [G-2 补充报告（重评 30.0）](agent-eval-report-g2.html) | declared 注入 + 规则放宽 + 真实运行重评 |
| [G 主报告（旧版留档）](agent-eval-report.html) | 第一次真实 Agent 评测（分数 0.0 为修复前口径，见 G-2） |

## 阳性对照与规则质量（窗口 I / J）

| 报告 | 内容 |
|---|---|
| [I1 端到端阳性对照（黄金 Agent A/B/C）](I1-positive-control-report.html) | 80.0/63.0/66.7 三版梯度 + 逻辑链敏感性证据 + 3 项发现登记 |
| [J1 规则质量修复（wilcoxon 对齐 + significance_threshold + L3 签名评估）](J1-rule-quality-report.html) | ruleset 1.4.0 + C4 漂移记录 + 连锁影响留档 + v0.2.1 Release |

## 评分正确性（窗口 K）

| 报告 | 内容 |
|---|---|
| [K1 评分正确性（immune 规则 + 未知方法→-1 + ttest 裁决）](K1-score-correctness-report.html) | ruleset 1.6.0 + G 窗口重评（immune 12 条 L-1→L1）+ A2 修复 + C4 漂移记录 + benchmark/reward 连锁留档 |

## 评测覆盖扩展（窗口 L）

| 报告 | 内容 |
|---|---|
| [L1 更广评测（10X 黄金对照 + 真实短评测）](L1-broader-eval-report.html) | GSE132465 10X 黄金对照（D1.1 双联体规则首次真实执行验证：做→L3 / 跳过→L0）+ 平台互补对照 + CellVoyager 聚焦短评测（30.0 · L-1=0，实际成本 ¥0.43） |

## 采集完整性（窗口 M）

| 报告 | 内容 |
|---|---|
| [M1 采集完整性（expected_types + missing 三档强制 + override/词表）](M1-capture-integrity-report.html) | 10X-B 闭环（63.7 blocked 走采集链路，不再引擎级补验）+ 未验证状态（level=-2）+ override_n2 键映射修复 + PCA_arbitrary/no_trajectory 词表补齐（ruleset 1.7.0）+ C4 漂移记录 + benchmark/reward 连锁留档 |
| [M 设计提案（确认记录）](M1-design-proposal.html) | expected_types 语义 / Option B 规则引用驱动 / B7 判定与词表评级——经项目负责人在线确认（2026-08-16） |

## 新 Demo 重建（窗口 N）

| 报告 | 内容 |
|---|---|
| [N1a 骨架 + 数据层](N1a-skeleton-data-report.html) | demo/ 目录（侧边栏导航+条件渲染+深色主题+四空壳）+ export_demo_data.py 提炼（provenance 化 + 剥离绝对路径）+ 四页路由通 + 数字独立核对（80.0/69.0/66.7/63.7/30.0×2） |
| [N1b 审计工坊](N1b-workshop-report.html) | Cascader 三级联动 + 轨迹对比（≤3 并排、ontology 对齐、无此决策）+ Split Button + 结果页全元素（大卡/verdict 色点/快照徽章/维度条/五档徽章/证据卡 PMID/时间轴推导）+ expected_types 现象演示（63.7 实时重算与断言一致）+ 缓存与演示恢复 + 走查 🔴=0 |

---

报告中的验收清单依据执行方案冻结（`docs/specs/2026-08-13-execution-plan-v1.md`，仓库外）；分数口径纪律见 [site-design §6.2](../site-design.html#62-数字口径纪律教训-2-单一事实源)。
