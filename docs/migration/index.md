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

---

报告中的验收清单依据执行方案冻结（`docs/specs/2026-08-13-execution-plan-v1.md`，仓库外）；分数口径纪律见 [site-design §6.2](../site-design.html#62-数字口径纪律教训-2-单一事实源)。
