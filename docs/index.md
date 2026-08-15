# 文档中心

Bio-Audit 文档站目录（站点规范见 [site-design](site-design.html)）。按分类浏览：

## 入门

| 文档 | 说明 |
|---|---|
| [快速开始（中文）](quickstart.html) | 安装、CLI 审计、golden 回归、三闸/四闸/五闸、API/MCP 接入 |
| [Quick Start (English)](quickstart.en.html) | English version of the quick start |
| [README](https://github.com/Tubo2333/bio-audit#readme) | 项目总览（GitHub 渲染；[英文版](https://github.com/Tubo2333/bio-audit/blob/main/README.en.md)） |
| [规则贡献指南](https://github.com/Tubo2333/bio-audit/blob/main/CONTRIBUTING.md) | 规则/任务集变更流程（三闸/四闸）、代码规范 |

## 契约与宪法（一级文档）

| 文档 | 说明 |
|---|---|
| [API 契约](api-contract.html) | 三入口（run_audit / audit_decision / match_details）请求/响应 schema + 错误码 + reward 入口 |
| [MCP 契约](mcp-contract.html) | MCP server 工具说明、请求/响应示例、错误码映射、握手 |
| [reward 映射宪法](reward-mapping.html) | level→reward 非线性映射定稿、-1 mask、γ=0.30 硬惩罚、PRM 预留接口 |
| [reward 协议](reward-protocol.html) | 配方定义、mask 语义、预注册统计量、锚点阈值、实测表 |

## 协议与设计

| 文档 | 说明 |
|---|---|
| [benchmark 协议](protocols/benchmark-protocol.html) | 任务集生成/标注/难度/split/gap/功效/黑盒/覆盖/评审 |
| [Agent 评测协议（宪法）](protocols/agent-eval-protocol.html) | 真实 Agent 评测宪法（含 §4.1 declared 修订） |
| [设计文档](specs/index.html) | 站点规范与设计定稿索引 |

## 窗口报告与评测

- [窗口报告索引](migration/index.html)：B1-B6 / C2 / D3 / E4 / F1 / G2b 完成报告 + G、G-2 真实评测报告

## 环境与部署

| 文档 | 说明 |
|---|---|
| [GitHub Pages 部署说明](environment/github-pages.html) | 站点构建机制、导航实现、发布与排障流程 |

## 数字口径速查（教训 #2，禁止混写）

| 口径 | 数值 |
|---|---|
| demo 轨迹（D5 修复后引擎重跑） | 29 分 · 5 × L0 |
| G-2 真实运行重评（GSE115978，declared + 规则放宽后） | **30.0 needs_correction** · L0=0 / L1×7 / L3×1 / L-1×12 |

完整口径规则见 [site-design §6.2](site-design.html#62-数字口径纪律教训-2-单一事实源)。
