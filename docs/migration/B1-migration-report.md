# B1 迁移报告（阶段 1 骨架）— 2026-08-13

> 执行窗口 B · B1：单仓库骨架 + 资产迁移 + golden 0 差异 + 路径锚定 + git 重建。
> 依据：execution-plan-v1（§一 窗口 B / §五 快照）、refactor-plan-v1（目标形态）、
> refactor-plan-v1.1（C/D/P 组）、audit-report（F 组工程卫生）、asset_manifest.json（H1）。

## 一、产出清单

```
bio-audit-v2/
├── pyproject.toml            # Apache-2.0 / Python>=3.10 / pydantic+pyyaml 核心依赖
├── LICENSE                   # Apache-2.0 全文（拍板 #3 / H13）
├── README.md                 # 快速开始 + 结构 + 路径锚定 + 数据治理（F4 修复）
├── CONTRIBUTING.md           # 规则贡献指南（H13，D1 治理流程）
├── CHANGELOG.md              # v0.1.0 B1 条目
├── .gitignore                # .env / **/__pycache__ / data 大文件 / 二进制
├── src/bioaudit/
│   ├── __init__.py           # ENGINE_VERSION 0.1.0 / ONTOLOGY_VERSION 0.0.0（C1 三元组）
│   ├── paths.py              # ★ 包内路径锚定（F7：零 cwd 依赖）
│   ├── engine/               # evaluator / matcher / aggregator / conflict_detector / error_tracer
│   ├── models/               # decision / rule / score / profile
│   ├── storage/              # rule_registry（C2 去重）/ event_store（日志锚定）
│   ├── api/                  # run_audit / audit_decision / match_details（B3 契约前置）
│   ├── rules/                # data/{DEG,pancancer,scRNA}/ 43 规则 + ruleset.json 快照
│   ├── ontology/             # 骨架（B2 落地）
│   ├── capture/              # 骨架（阶段 2 落地）
│   ├── report/               # SnapshotTriple（C1）+ REPORT_SCHEMA_VERSION（C3）
│   ├── regression.py         # golden 重放引擎（包内锚定）
│   ├── cli.py                # bio-audit run / golden / audit-decision
│   └── data/                 # trajectories(20) / mappings(4) / validation(5) / report(1)
├── mcp/                      # MCP server 骨架（阶段 2）
├── ui/                       # Streamlit 薄壳（只调 api；D1/D7/D12 修复）
├── tests/                    # 12 项：golden 回归 / 引擎 sanity / 路径锚定（异 cwd）
│   └── golden/               # golden_expected_output_after.json 副本（哈希与权威一致）
├── scripts/                  # golden_replay / check_no_cwd_paths / download_datasets(H3)
└── docs/migration/           # 本报告
```

## 二、迁移核对（H1 / asset_manifest.json）

| 资产 | 源（4 旧项目） | 目标 | 数量 | 哈希核对 |
|------|--------------|------|------|---------|
| 规则（A3 统一后 DEG 血统） | fullflow-demo/data/rules/ | src/bioaudit/rules/data/ | **43** 文件（DEG 5 + pancancer 16 + scRNA 22） | 43/43 ✅ |
| 轨迹 | fullflow-demo/data/trajectories/ | src/bioaudit/data/trajectories/ | **20** | 20/20 ✅ |
| validation 数据 | fullflow-demo/data/validation/ | src/bioaudit/data/validation/ | **5**（full_audit_results / edge_case_validation / scrna_r0 / scrna_r0_pre_d5fix / validation_dataset） | 5/5 ✅ |
| mappings | fullflow-demo/data/mappings/ | src/bioaudit/data/mappings/ | **4** | 4/4 ✅ |
| 报告数据 | fullflow-demo/data/report/ | src/bioaudit/data/report/ | 1（ai_error_patterns.md） | ✅ |
| 引擎代码 | fullflow-demo/src（D5 修复后） | src/bioaudit/{engine,models,storage,api} | 12 模块 | 逻辑逐行核对，仅 import/路径变更 |

**合计 72/72 数据文件与 asset_manifest.json 的 SHA256 逐字节一致**（2026-08-13 验证）。
规则集快照：43 文件 → 38 唯一 rule_id（C2 去重，DEG 与 pancancer 5 同名文件内容全同）。

## 三、验收结果

| 验收项 | 结果 |
|--------|------|
| 新仓库独立运行引擎 | ✅ `pip install -e .` 后任意 cwd 可运行（CLI / API / pytest 异 cwd 验证） |
| golden 0 差异 | ✅ `scripts/golden_replay.py`：20 轨迹 / 137 决策 / **0 差异**（权威基线 + 仓库副本双跑） |
| 无相对 cwd 路径 | ✅ `scripts/check_no_cwd_paths.py` 0 命中；tests/test_path_anchoring.py 异 cwd 运行 12/12 通过 |
| UI 薄壳 | ✅ 只调 bioaudit.api；移除内联管道/sleep（D7）/script 注入（D12）；导出合法 JSON（D1） |
| git 全新 init | ✅ 不携带旧仓 13GB 历史（H2）；.gitignore 覆盖 .env/__pycache__/大文件 |

## 四、路径锚定变更点（F7 逐点）

| 旧（相对 cwd） | 新（包内锚定） |
|---------------|---------------|
| RuleRegistry("data/rules") | `RuleRegistry()` → `bioaudit.paths.RULES_DIR`（__file__ 派生） |
| RuleMatcher 读 "data/mappings/type_aliases.yaml" 等 | `MAPPINGS_DIR / "type_aliases.yaml"` |
| ErrorPropagationTracer("data/mappings/dependency_graph.yaml") | `MAPPINGS_DIR / "dependency_graph.yaml"` |
| EventStore("logs/events") | `~/.bioaudit/logs/events`（`$BIOAUDIT_LOG_DIR` 可覆盖） |
| UI sys.path.insert(ROOT) 四条 | 包安装，直接 `import bioaudit` |
| gen_golden.py 硬编码 D:\C-file 绝对路径 | `bioaudit.regression`（包内锚定，--baseline 可指定） |

## 五、遗留项（不阻塞 B1 验收，排期后续窗口）

1. **generate_scrna_r0.py / convert_* 脚本未迁移**：依赖 numpy/scipy 与 5GB 数据；
   留旧仓，B6（CI 数据管线）迁移并锚定
2. **API 契约（B3）**：pydantic 输入 schema + 错误码 + paradigm 参数细化
3. **本体落地（B2）**：34 类型定义 + P1 校验器三职责
4. **轨迹迁移器（B4）**：20 条旧轨迹 schema 加 version + legacy provenance（C2）
5. **规则治理（B5）**：semver 校验脚本 + 冲突检查（D1/D2）+ CI
6. **规则引擎 A2 修复**：未知方法 L0→-1（评估器层面，engine 0.2.0 变更，需 golden 重放）
7. **ruleset.json 版本写死进报告**（report.ruleset_version 目前 None，B5 接通）
8. **generate_scrna_r0 / 数据下载**：H3 下载脚本 URL/SHA 待外部托管就绪
9. 旧仓库归档（验收通过后按执行方案执行）
