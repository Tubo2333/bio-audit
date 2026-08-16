# Bio-Audit

[![CI](https://github.com/Tubo2333/bio-audit/actions/workflows/ci.yml/badge.svg)](https://github.com/Tubo2333/bio-audit/actions)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-Apache--2.0-green)

**一个为生物信息学 AI Agent 设计的"方法学监考系统"：逐步骤审查 Agent 的分析决策，
对照文献锚定的规则打分、给依据、留证据——让黑盒分析变得可审计、可复现、可比较。**

> **English**: [README.en.md](README.en.md) · **文档站**: https://tubo2333.github.io/bio-audit/

---

## 为什么需要它

AI Agent 做生信分析已经相当熟练：代码能跑、输出像样、总结听起来很有道理。但它**不会主动告诉你它的方法学决策对不对**：

- 归一化为什么用 TPM，而不用 raw counts 跑 DESeq2？
- 12 个样本没做批次校正，患者效应和生物学信号分得开吗？
- 把单个细胞当独立样本做差异表达（伪重复），p 值膨胀了多少？
- 多重检验不校正，报告里的显著基因有多少是假的？

这些问题不是 bug——代码没报错，输出也正常。它们是**"选错方法"和"跳过关键步骤"**，传统代码审查抓不到，只有对照"科学方法学共识"逐步骤审才能发现。

我们让 CellVoyager（一个单细胞分析 Agent）在 GSE115978 黑色素瘤真实数据上完整跑了一次分析，然后逐步骤翻开它的决策草稿：**12 步分析中 5 个危险级（L0）决策**——跳过双联体检测、跳过批次校正、用 cell-level 伪重复做 DEG、PCA 维度随意设定、跳过轨迹推断。在传统审查下，这一切"看起来完全正常"。

**Bio-Audit 就是把"科学方法学共识"编码成可执行的规则，在 Agent 分析的每一步实时检查、评分、溯源。**

## 它做什么

| 层 | 白话解释 | 怎么做到的 |
|---|---|---|
| **lint**（运行时验证） | Agent 边跑边被审，说过的和做过的对不上当场暴露 | M1 主动上报 + M3 产物解析 + 交叉验证（虚报/漏报检测）+ verdict 状态位（provisional → final / revoked） |
| **benchmark**（评测基准） | "这个 Agent 到底行不行"变成可重复的数字 | 60 条带真值标注的任务集（双标注 IRR κ=0.83、预注册、防泄漏、功效分析） |
| **reward**（训练信号） | 把审计分数变成能喂给强化学习的信号 | level→reward 映射宪法（-1 屏蔽、L0 硬惩罚 γ=0.30）、三配方消融、spike-in 锚点 |

每个决策的评分都**锚定具体文献**（PMID 直达），不是"我觉得"。Agent 也可以直接通过 **MCP server** 在分析过程中调用审计（`audit_decision`），获得即时反馈。

## 真实效果

我们让 CellVoyager 在 GSE115978 上真实运行（2026-08，总成本 ¥2.55），并用修复后的链路重评：

| 口径 | 结果 |
|---|---|
| demo 轨迹（2026-08-13 D5 修复后重跑，12 步分析） | **29 分 · Blocked · 5 × L0** |
| **G-2 真实运行重评**（GSE115978 · declared 注入 + 规则平台键放宽后） | **30.0 · needs_correction · L0=0 / L1×7 / L3×1 / L-1×12** |

两个口径对象不同、机制不同，**严格区分、禁止混写**（口径纪律见 [site-design §6.2](https://tubo2333.github.io/bio-audit/docs/site-design.html#62-数字口径纪律教训-2-单一事实源)）。报告：[G-2 补充报告](https://tubo2333.github.io/bio-audit/docs/migration/agent-eval-report-g2.html) · [G 主报告（旧版留档）](https://tubo2333.github.io/bio-audit/docs/migration/agent-eval-report.html)。

**高分阳性对照（窗口 I，2026-08）**：为了让"链路能抓错"的证据闭环，我们还用**确定性脚本**（按公开最佳实践编写的"黄金 Agent"，**非 LLM**）在同一个数据集上真实执行、走同一条采集链路——教科书式执行得到 **80.0 · pass**，与 CellVoyager 真实运行 **30.0 · needs_correction** 形成对比度：

| 黄金 Agent 变体（同数据同流程，仅一处方法学差异） | 分数 · verdict | 注入的方法学错误 |
|---|---|---|
| **A 黄金版**（MAD QC → SCTransform → VST HVG → PCA-elbow → Harmony → Leiden → CellTypist → pseudobulk DESeq2 → BH） | **80.0 · pass** | 无 |
| **B 逻辑断裂版**（cell-level DEG 替代 pseudobulk，伪重复） | **69.0 · needs_correction**（J1 修复前 63.0 · blocked） | DEG 把细胞当独立样本（终答照常输出差异基因列表） |
| **C 微妙错误版**（固定硬阈值替代 MAD 自适应 QC） | **66.7 · needs_correction** | QC 固定阈值（该数据恰好一个细胞都没滤掉，结果表面与 A 几乎相同） |

三版终答"表面完成度"相同，仅方法学逻辑不同 → **审计分呈梯度（80.0 → 69.0 → 66.7）**——**审计评的是科学逻辑链，不是只看终答**。报告：[窗口 I 阳性对照报告](https://tubo2333.github.io/bio-audit/docs/migration/I1-positive-control-report.html)。（注 1：A 版 80.0 未达 85.0 目标，偏差归因于注释方法 L3 通道的采集签名缺口，报告 §6 如实记录。注 2：B 版在窗口 J 规则修复（ruleset 1.3.0，wilcoxon 词表对齐）后由 63.0·blocked 改为 69.0·needs_correction——细胞级 wilcoxon 按 G1.1 语义为"有风险"而非"危险"，I 报告 §11.5 预警的"blocked 证据消失"已应验；分数梯度保持。）

引擎自身的可信度也有独立验证（R0-R3）：模拟数据真值锚定下，审计分数与实际 F1 的排序一致性 Spearman ρ=0.9747（D5 修复后重算，结论不变）；权威文献案例 4/4 全部正确判级。

## 快速开始

```bash
pip install -e ".[dev,ui]"          # Python >= 3.10

bio-audit run src/bioaudit/data/trajectories/v2/deg_correct.json   # 审计一条轨迹
bio-audit golden                    # golden 回归（20 轨迹 137 决策，必须 0 差异）
bio-audit ruleset-validate          # 规则集校验（清单/冲突/golden 回归）
```

完整上手（安装 / 常用命令 / API·MCP 接入 / 测试回归）：**[快速开始](https://tubo2333.github.io/bio-audit/docs/quickstart.html)**（[English](https://tubo2333.github.io/bio-audit/docs/quickstart.en.html)）

## 项目状态与路线图

**当前（v0.2.x，2026-08）**：核心体系已闭环——稳定引擎 + 34 类型决策本体 + 规则治理门禁、真实采集链路（M1/M3 交叉验证）、60 条评测任务集、reward 信号层；真实 Agent 评测链路打通并完成首轮修复（G-2），端到端阳性对照（黄金 Agent A/B/C）补齐"链路能认对"证据（窗口 I）。工程质量：pytest 235/235 · CI 双矩阵（Python 3.10/3.12）全绿 · golden 回归 0 差异 · 报告带三元组快照（engine/ruleset/ontology 版本），任何分数可复现。

**接下来**：L3/L4 结论级与一致性级审计（通用实现）、PRM（过程奖励模型）、任务集扩展（批 3，跨模型标注对照）、更多真实 Agent 评测（多数据集/多 Agent）。

## 文档

- [文档中心](https://tubo2333.github.io/bio-audit/docs/) · [快速开始](https://tubo2333.github.io/bio-audit/docs/quickstart.html)
- [API 契约](https://tubo2333.github.io/bio-audit/docs/api-contract.html) · [MCP 契约](https://tubo2333.github.io/bio-audit/docs/mcp-contract.html)
- [规则贡献指南](CONTRIBUTING.md) · [窗口报告索引](https://tubo2333.github.io/bio-audit/docs/migration/) · [Release](https://github.com/Tubo2333/bio-audit/releases)
- 设计依据（本体/采集/执行方案）：`docs/specs/`（仓库外审计内存，不进 Pages）

## 仓库结构

```
src/bioaudit/
├── engine/       # 匹配 / 评分 / 聚合（规则引擎核心）
├── ontology/     # 34 决策类型本体 + 校验器
├── rules/        # 44 条规则 YAML（39 唯一）+ ruleset 版本快照
├── capture/      # 采集：M1 hook / M3 解析 / 交叉验证 / verdict
├── benchmark/    # 任务集 / 难度 / IRR / 运行器 / 污染扫描
├── reward/       # level→reward 映射 / 配方 / 校准
├── api/          # 三入口契约（pydantic + 错误码）
└── data/         # 20 条轨迹 / validation / mappings
```

## 贡献

欢迎贡献规则、任务集与代码——规则改动有自动化校验（清单 / 冲突检测 / golden 回归）兜底，改不坏。见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可

[Apache-2.0](LICENSE)。致谢：设计借鉴 BiomniBench、GeneBench、FlowBench、CoE Audit 等评测框架的发现与方法论。
