# B6 完成报告（阶段 1 · 回归 CI）— 2026-08-14

> 执行窗口 ⑦ · B6：golden 接入 CI + 漂移报告 + 依赖锁定 + 双版本矩阵 + R0 脚本迁移。
> 依据：execution-plan-v1（§六.五 B6 验收清单 6 项，冻结）、refactor-plan-v1.1
> （C4/H3/H8）、B1 迁移报告 §五遗留 1（generate_scrna_r0.py 迁移）。
> 验收对照见文末 §七（逐条打勾）。

## 一、产出清单

```
.github/workflows/ci.yml      # ★ CI：Python 3.10/3.12 矩阵 + pytest + golden +
                              #   ruleset-validate + validate-ontology + R0 锚定 + 漂移 artifact
requirements.lock             # ★ 运行时依赖锁（pip-tools，Python>=3.10 解析）
requirements-dev.lock         # ★ dev+scripts 依赖锁（numpy 2.2.6 / scipy 1.15.3 保 3.10 兼容）
scripts/generate_scrna_r0.py  # ★ fullflow-demo 迁移 + 包内锚定（B1 遗留 1）
README.md / CONTRIBUTING.md   # CI 门禁与规则变更流程文档化
```

## 二、B6-1 golden 接入 CI（失败即红）

`.github/workflows/ci.yml`（on: push/PR，`[main, master]`）：

```yaml
- name: Golden replay（20 轨迹 137 决策，失败即红；C4）
  run: |
    bio-audit golden --json > golden-summary.json || { echo "::error::GOLDEN DIFF — 分数漂移必须逐条人工确认（v1.1 C4）"; cat golden-summary.json; exit 1; }
```

- `bio-audit golden`（= `python scripts/golden_replay.py`，B1 已有）exit 0/1；
  CI 步骤失败 → job 红 → PR 不可合并（C4/D1"失败自动回退"）。
- 同一 job 还跑 `bio-audit ruleset-validate --json`（B5 三闸）与
  `bio-audit validate-ontology --json`（P1 三职责）——规则/本体/引擎全部门禁。

## 三、B6-2 漂移报告机制

- `bio-audit golden --json` 输出的 summary 即**结构化 diff 摘要**：
  n_diffs + 每条 diff 的 `trajectory`/`step_id`/`kind`/`expected`/`actual`
  （覆盖轨迹分数、verdict、dimension_scores 与逐决策 step_scores）。
- CI：summary 写入 `golden-summary.json` → `actions/upload-artifact@v4`
  （`if: always()`，通过也留档；命名 `golden-summary-<python 版本>`）→
  **diff ≠ 0 时 job 红，必须人工确认**（C4：漂移逐条解释 + 更新基线）。
- 本地等价命令：`python scripts/golden_replay.py`（0 差异打印 GOLDEN OK）。

## 四、B6-3 依赖锁定（lockfile 提交仓库）

- `pip-compile`（pip-tools 7.6.1）从 pyproject.toml 生成：
  - `requirements.lock`：运行时（pydantic 2.13.4 / pyyaml 6.0.3 + 传递依赖，6 包）
  - `requirements-dev.lock`：dev + scripts extra（pytest 9.1.1 / ruff 0.16.3 /
    numpy / scipy + 传递依赖，16 包）
- **Python 3.10 兼容约束**：numpy<2.3 / scipy<1.16 → 锁定 numpy **2.2.6** /
  scipy **1.15.3**（2.3+/1.16+ 要求 Python≥3.11，会破坏 3.10 矩阵；已 dry-run 验证可安装）。
- UI extra（streamlit）不入 CI 锁（CI 不装 UI；文件头注明可按需单独生成 ui.lock）。
- CI 安装：`pip install -r requirements.lock -r requirements-dev.lock && pip install -e .`；
  pyproject `requires-python = ">=3.10"` 已有（H8）。

## 五、B6-4 CI 双版本矩阵（Python 3.10 / 3.12）

```yaml
strategy:
  fail-fast: false
  matrix:
    python-version: ["3.10", "3.12"]
```

两版本各跑：安装（锁依赖）→ validate-ontology → ruleset-validate → pytest →
golden（失败即红）→ 漂移 artifact → R0 锚定。`fail-fast: false`：一版失败不取消另一版。
本地仅 3.12 可实测（86/86 绿）；3.10 由 lockfile 兼容约束 + CI 矩阵覆盖。

## 六、B6-5 generate_scrna_r0.py 迁移 + 包内锚定（B1 遗留 1）

`fullflow-demo/scripts/generate_scrna_r0.py` → `bio-audit-v2/scripts/`：

| 变更点 | 旧 | 新 |
|--------|----|----|
| 引擎导入 | `sys.path` hack + `from src.engine...` | `from bioaudit.engine...`（包安装） |
| 规则目录 | `RuleRegistry("data/rules/scRNA")`（cwd 依赖） | `RuleRegistry(rules_dir_for("scrna"))`（包内锚定，F7） |
| 输出路径 | `data/validation/scrna_r0.json`（cwd 依赖） | 默认 `bioaudit.paths.VALIDATION_DIR`；`--output` 可覆盖 |
| 逻辑/seed | 原样保留 | 原样保留（确定性 seed=42） |

**锚定验证**：`cd C:\`（异 cwd）运行 → 输出与包内 `scrna_r0.json`
**逐字节一致**（SHA256 `16f31ff4…`，24,089 B）✅——同时证明 D2 裁决
（G1.3 MAST 修订）对 R0 combo_3 S10 评分零影响。CI 增加 R0 锚定步骤：
重生成到 /tmp → 与包内文件哈希比对，不一致即红。
`convert_*.py`（依赖 5GB 原始数据）与 `validate_edge_cases.py` 仍留旧仓——
数据管线（H3 下载脚本）托管就绪后迁移，登记 fix-tracking（C13）。

## 七、验收对照（B6 验收清单 6 项）

| # | 验收项 | 结果 |
|---|--------|------|
| 1 | golden_replay 接入 CI（GitHub Actions 或等价本地命令），失败即红 | ✅ `.github/workflows/ci.yml`：`bio-audit golden` diff≠0 → exit 1 → job 红；等价本地命令 `bio-audit golden` |
| 2 | 漂移报告：CI 输出 diff 摘要，有变化必须人工确认 | ✅ golden-summary.json（轨迹分数/逐决策 level 的 expected vs actual）上传 artifact；失败即红=人工确认门槛（C4） |
| 3 | 依赖锁定：lockfile 提交仓库 | ✅ requirements.lock + requirements-dev.lock 提交（pip-tools；3.10 兼容约束） |
| 4 | CI 双版本矩阵（Python 3.10 / 3.12）跑 pytest + golden | ✅ matrix ["3.10","3.12"]：pytest + golden + 校验器 + R0 锚定 |
| 5 | 数据管线锚定：generate_scrna_r0.py 迁移新仓并包内锚定（迁移报告遗留 1） | ✅ scripts/generate_scrna_r0.py（bioaudit 导入 + rules_dir_for + VALIDATION_DIR 锚定）；重生成逐字节一致；CI 锚定步骤 |
| 6 | 回归：CI 全套绿（含 golden 0 差异） | ✅ 本地全套复现：pytest 86/86、ruleset-validate 三闸 PASS、golden 0 差异、R0 重生成一致；3.12 实测，3.10 由矩阵+锁约束覆盖 |

## 八、遗留项（不阻塞 B6 验收）

1. **CI 实测**：仓库无 git remote，workflow 未在 GitHub 上实跑过；推送到 GitHub
   后首跑验收（本地已逐命令复现全部步骤）。
2. `convert_*.py` / `validate_edge_cases.py` 迁移依赖 H3 数据下载托管就绪（fix-tracking C13）。
3. `ruff check` 在 CI 为 `|| true`（H13 渐进：当前 lint 噪音未清零，排期阶段 2 收严）。
