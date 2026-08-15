# Bio-Audit

**生信 AI Agent 方法学决策的确定性审计层（Scientific Decision CI）**

把"科学方法学共识"编码为文献锚定的可执行规则，对 Agent 的每个方法学决策实时检查、
评分、溯源——嵌入 Agent 工作流（MCP/SDK），输出三层价值：
**运行时验证（lint）/ 评测数据（benchmark）/ 训练信号（reward）**。

> **English**: [README.en.md](README.en.md) · **文档站**: https://tubo2333.github.io/bio-audit/

## 当前状态（v0.2.x，2026-08-16）

五阶段重构（止血 → 地基 → 采集 lint → benchmark → reward）已全部完成，真实 Agent 评测链路打通：

- **真实评测（G-2 重评）**：CellVoyager 在 GSE115978 上真实运行，重评有效分数
  **30.0 needs_correction（L0=0 / L1×7 / L3×1 / L-1×12）**，总成本 ¥2.55；
  报告见 [docs/migration/agent-eval-report-g2.md](https://tubo2333.github.io/bio-audit/docs/migration/agent-eval-report-g2.html)
- **数字口径纪律**（教训 #2）：demo 轨迹 29 分 5×L0 ≠ 真实运行 30.0，两者口径严格区分
  （[site-design §6.2](https://tubo2333.github.io/bio-audit/docs/site-design.html#62-数字口径纪律教训-2-单一事实源)）
- **工程质量**：pytest 234/234 · CI 双矩阵（3.10/3.12）全绿 · golden 20 轨迹 137 决策 0 差异 ·
  ruleset 1.2.0 / engine 0.2.1 / taskset 60 条（IRR κ=0.8336）

## 快速开始

```bash
pip install -e ".[dev,ui]"          # Python >= 3.10

bio-audit run src/bioaudit/data/trajectories/v2/deg_correct.json   # 审计一条轨迹
bio-audit golden                    # golden 回归（20 轨迹 137 决策，必须 0 差异）
bio-audit ruleset-validate          # 规则治理三闸（清单/冲突/golden）
```

完整上手（安装 / 常用命令 / API·MCP 接入 / 测试回归）：**[快速开始](https://tubo2333.github.io/bio-audit/docs/quickstart.html)**（[English](https://tubo2333.github.io/bio-audit/docs/quickstart.en.html)）

## 三价值层

| 层 | 能力 | 关键产物 |
|---|---|---|
| **lint** | 运行时验证：M1 主动上报 + M3 产物解析 + 交叉验证（虚报/漏报）+ verdict 状态位（provisional/final/revoked） | `capture/` + MCP server |
| **benchmark** | 评测基准：60 条任务集（3 范式×难度梯度）、双标注 IRR、预注册 gap、防泄漏、功效分析 | `benchmark/` + 协议 |
| **reward** | 训练信号：level→reward 映射宪法（-1 mask、γ=0.30 硬惩罚）、三配方消融、spike-in 锚点 | `reward/` |

## 仓库结构

```
bio-audit-v2/
├── pyproject.toml            # Apache-2.0；Python>=3.10
├── src/bioaudit/
│   ├── paths.py              # 包内路径锚定（零 cwd 依赖，F7）
│   ├── engine/               # 匹配/评分/聚合/冲突/传播（D5 修复后基线）
│   ├── ontology/             # 本体：34 决策类型 + P1 校验器三职责
│   ├── rules/                # 43 条规则 YAML（38 唯一）+ ruleset 快照（semver）
│   ├── capture/              # 采集（M1 hook / M3 解析 / 交叉验证 / verdict）
│   ├── benchmark/            # 任务集 + 难度 + IRR + 运行器 + 污染扫描
│   ├── reward/               # 映射/配方/校准（外围输出层，评分路径零改动）
│   ├── api/ + errors.py      # 三入口契约（pydantic + 错误码 + paradigm 必填）
│   ├── report/               # 报告 schema（engine/ruleset/ontology 三元组快照）
│   └── data/                 # 包内资产：20 轨迹 / validation / mappings
├── mcp/                      # MCP server（stdio JSON-RPC）
├── ui/                       # Streamlit 薄壳（只调 api）
├── tests/                    # 234 项（tests/golden/ 冻结基线副本）
├── docs/                     # 文档站（导航/目录规范见 docs/site-design.md）
└── .github/workflows/ci.yml  # 双矩阵 + golden + 三/四/五闸
```

## 文档导航

- [文档中心](https://tubo2333.github.io/bio-audit/docs/) · [快速开始](https://tubo2333.github.io/bio-audit/docs/quickstart.html)
- [API 契约](https://tubo2333.github.io/bio-audit/docs/api-contract.html) · [MCP 契约](https://tubo2333.github.io/bio-audit/docs/mcp-contract.html)
- [规则贡献](CONTRIBUTING.md) · [窗口报告](https://tubo2333.github.io/bio-audit/docs/migration/) · [Release](https://github.com/Tubo2333/bio-audit/releases)
- 站点规范：docs/site-design.md（导航/目录/双语/Release 衔接）；设计依据在仓库外审计内存 docs/specs/
  （refactor-plan-v1/v1.1、ontology-design-v1、trajectory-capture-design-v1、execution-plan-v1）

## 路径锚定与数据治理

- 所有数据资源经 `bioaudit.paths` 解析（`Path(__file__)` 派生），任意 cwd 可运行（F7）；
- 大体积数据不进 git（h5ad/csv.gz 等）；密钥只环境变量注入，`.env` 全部 gitignore，引擎零密钥逻辑。

## 许可

Apache-2.0。
