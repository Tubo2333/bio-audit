# Bio-Audit

**生信 AI Agent 方法学决策的确定性审计层（Scientific Decision CI）**

把"科学方法学共识"编码为文献锚定的可执行规则，对 Agent 的每个方法学决策实时检查、
评分、溯源——嵌入 Agent 工作流（MCP/SDK），输出三层价值：
**运行时验证（lint）/ 评测数据（benchmark）/ 训练信号（reward）**。

> 本仓库为 **bio-audit-v2**（重构单仓库，阶段 1 B1 骨架完成）。设计依据见
> `docs/` 与上级 `docs/specs/`（refactor-plan-v1 / v1.1、ontology-design-v1、
> trajectory-capture-design-v1、execution-plan-v1）。

## 快速开始

```bash
# 安装（Python >= 3.10）
pip install -e ".[dev,ui]"

# 命令行审计一条轨迹
bio-audit run src/bioaudit/data/trajectories/deg_correct.json

# golden 回归：20 轨迹 137 决策 vs 冻结基线，必须 0 差异
python scripts/golden_replay.py --baseline tests/golden/golden_expected_output_after.json

# 单元 + 回归测试
pytest

# Streamlit 薄壳 UI（只调 bioaudit.api）
streamlit run ui/app.py
```

## 仓库结构（阶段 1 目标形态）

```
bio-audit-v2/
├── pyproject.toml            # Apache-2.0；Python>=3.10；核心依赖 pydantic+pyyaml
├── src/bioaudit/
│   ├── paths.py              # 包内路径锚定（importlib/__file__ 派生，零 cwd 依赖）
│   ├── engine/               # 匹配/评分/聚合/冲突/传播（fullflow-demo D5 修复后迁移）
│   ├── models/               # Decision / Rule / Score / Profile 数据模型
│   ├── storage/              # RuleRegistry（C2 去重告警）+ EventStore
│   ├── api/                  # 单一入口：run_audit / audit_decision（B3 完善契约）
│   ├── ontology/             # 本体（阶段 B2 落地：34 类型 + P1 校验器）
│   ├── capture/              # 采集（阶段 2：M1 hook / M3 解析器 / 交叉验证）
│   ├── rules/                # 43 条规则 YAML（统一后）+ ruleset 快照清单
│   ├── report/               # 报告 schema（C1 三元组快照：ruleset+ontology+engine）
│   └── data/                 # 包内小资产：20 轨迹 / validation / mappings / report
├── mcp/                      # MCP server（阶段 2 骨架）
├── ui/                       # Streamlit 薄壳（只调 api）
├── tests/                    # 单元 + golden 回归（tests/golden/ 冻结基线副本）
├── scripts/                  # golden_replay / 数据下载 / 路径审计
└── docs/                     # 迁移记录、设计引用
```

## 路径锚定（F7 修复）

所有数据资源通过 `bioaudit.paths` 解析（`Path(__file__)` 派生），引擎/UI/脚本
**不依赖当前工作目录**。任意 cwd 下 `import bioaudit` 均可运行（见
`tests/test_path_anchoring.py`）。

## 数据与密钥治理

- **大体积数据不进 git**（h5ad/csv.gz 等）：见 `scripts/download_datasets.py` 与 `.gitignore`
- **密钥仅环境变量注入**：`.env` 全部 gitignore；引擎零密钥逻辑

## 许可

Apache-2.0（拍板 #3，H13）。
