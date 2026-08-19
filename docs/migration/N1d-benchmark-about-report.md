# N1d 子窗口完成报告：评测与奖励 + 关于页（窗口 N · 4/5）

> **窗口**：N-d（execution-plan §六.十八 11-12）｜**日期**：2026-08-19
> **依据**：demo-redesign-design v0.3（§3.4 评测页四 tab / §3.5 关于页 / §4 对照表 /
> §7 素材清单）+ demo-n-window-ledger §12.1（冻结验收清单）+ 台账 §12 引言（demo/data
> 键名钉死）+ 各窗口报告（F1/M1/E4/K1/L1/G-2）+ site-design §6.2（口径纪律）
> **验收方式**：demo 设计中枢独立验收（不轻信自检：独立重算 + AppTest 实跑 + 真实
> 浏览器视觉抽查 + git/CI 检查）

---

## 1. 交付总览

| 项 | 内容 |
|---|---|
| 页面实现 | `demo/pages/03_benchmark.py`（评测与奖励四 tab 完整实现）+ `demo/pages/04_about.py`（关于页完整实现） |
| 数据层增补 | export 脚本新增提炼 `reward_summary.json` / `engineering_summary.json`；`eval_summary.json` 增补成本字段（¥2.55 / ¥0.43）；verify 增补 3 节（成本 / reward / 工程数字） |
| 样式 | `theme.css` 增补 N-d 区块（tabs 深色化 / 统计卡 / 堆叠条 / spike-in 条 / 运行卡 / 关于页样式 / 链接配色修复） |
| 零改动 | `src/`、`tests/`、`ui/`（git diff 确认） |
| 提交 | 单 commit，只含 demo/ + pyproject.toml（S4 注释同步）+ docs/ 报告与登记（推送纪律 §六.7） |

## 2. execution-plan §六.十八 打勾

- [x] **N-d 11** 四 tab：benchmark 摘要（recall 0.820/precision 0.7455/F1 0.7810/
      IRR κ=0.8336 出处 F1 报告/gap 0.046 产物值 + M 后 0.0449 注明）/ 平台对照
      （Smart-seq2 vs 10X 决策集差异）/ reward 映射 + spike-in / 真实评测档案
      （¥2.55/¥0.43 + R0 ρ=0.9747 + 黄金对照定位声明）
- [x] **N-d 12** 关于页：项目一句话 + 三价值层白话 + 工程数字 + 路线图 + MCP 说明
      + takeaway 三句话 + 旧痛点×新手段对照表

## 3. 台账 §12.1 冻结验收清单逐项核对

| # | 验收项 | 结果 | 证据 |
|---|---|---|---|
| 1 | benchmark tab：60 任务摘要 + IRR κ 出处注明 + gap 0.046 + M 后 0.0449 + 层间比较；全部读 demo/data 零硬编码 | ✅ | 页面全部数字来自 `data_index.benchmark_summary()`（stat 卡 recall 0.820 / precision 0.7455 / F1 0.7810 / IRR κ=0.8336·623 决策·一致率 93.58%，n_decisions/n_gold_error/n_tasks_run 数据派生）；gap callout 读 gap.delta / gap.delta_after_m / gap.in_tolerance / gap.tolerance_interval（+0.046 / +0.0449 区间内无告警）；strata 两组（act 3 档 + difficulty 3 档，含 CI/n）+ comparisons 表（bootstrap p + Holm 校正 p，全部校正后 p≥0.05 如实呈现）；κ 出处由摘要 JSON note 注明（irr.note caption 展示，F1 报告） |
| 2 | 平台对照 tab：决策集差异可视化（10X 多双联体/UMI/批次）；63.7/66.7 禁止混写；数字 = golden_summary entries | ✅ | 五份黄金对照表（id/平台/分数·verdict/决策数/维度分/critical issues 全部读 golden_summary）；口径纪律 callout 页首（63.7 仅限 10X-B expected / 66.7 仅限 Smart-seq2-C，site-design §6.2）；决策集差异两栏卡 + 构成表（共享 10 类型 + 高亮 doublet_detection 10X 独有行，出处 L1 §4.3/§5） |
| 3 | reward tab：映射表 {4:1.00,3:0.85,2:0.60,1:0.30,0:0.00} + -1 mask + spike-in 掉分演示 | ✅ | 映射表读 reward_summary.mapping（L-1 mask 行灰显）+ mask 语义 callout（不参与分子分母）+ 聚合 mean/γ=0.30 + status experimental_uncalibrated 警告；spike-in 三范式条（scrna 0.85→0.2354 drop 0.6146 / deg 0.85→0.2125 drop 0.6375 / pan 0.85→0.2400 drop 0.6100），出处 E4 §三.9 + reward-protocol §七.2 |
| 4 | 真实评测档案 tab：两次运行（G 30.0 K1 重评 L1×19/L3×1 / L-b 30.0 L1×4/L2×1）+ 成本 + 定位声明 + R0 | ✅ | 运行卡读 eval_summary runs 条目级 provenance（分数/verdict/level_counts/note/provenance）；成本读 cost 字段（¥2.55 agent-eval-report §2 / ¥0.43 L1 §7.2，均平台余额差权威口径）；定位声明 callout（确定性脚本非 LLM + 真实 LLM n=1 诚实声明）；R0 卡读 r0_summary（ρ=0.9747 · PASS · detail · limit） |
| 5 | 关于页：一句话 + 三价值层 + 工程数字（274 测试/CI 双矩阵/golden 0 差异/三元组快照）+ 路线图 + MCP + takeaway + 对照表 | ✅ | 见 §4 逐项 |
| 6 | 工程纪律：pytest 全绿 + golden 0 差异 + CI 云上绿 + 推送纪律；demo/data 增补走 export | ✅ | 见 §7 |
| 7 | skill：design-taste-frontend + web-design-guidelines 走查（🔴=0）+ code-review 双轴 | ✅ | 见 §5/§6 |
| 8 | 报告 + execution-plan 打勾 | ✅ | 本文件；execution-plan §六.十八 N-d 11-12 已勾 |

## 4. 关于页内容（台账 §12.1 第 5 项逐块）

| 块 | 内容 | 出处 |
|---|---|---|
| 项目一句话 | "把单细胞分析方法学审计自动化：管线拆成一条条决策，逐条对照可执行规则给出等级与依据——分数可复现、结论可追溯、证据可展开" | 设计 §3.5 |
| 三价值层 | 01 lint 层（审得准）/ 02 benchmark 层（信得过）/ 03 reward 层（可训练），白话顺序叙事 | 设计 §3.5 |
| 工程数字 | 274 测试（读 engineering_summary，pytest --collect-only 实测）/ CI 双矩阵 3.10+3.12 / golden 0 差异（20 轨迹 137 决策）/ 三元组快照（current_snapshot 运行时取） | engineering_summary + current_snapshot |
| 路线图 | 已做 G-2~M 七窗口 + N 窗口（8 条）；排期项 6 条（L3/L4 结论级审计、多 Agent 对比、h5ad 在线分析、reward RLHF 校准、PRM、Docker/线上部署）——如实声明 | execution-plan + E4 §七 + L1 §8 |
| MCP 说明 | 文字（bio-audit-mcp v1.0.0，三工具 audit_decision/audit_trajectory/report）+ JSON-RPC 代码示例；不作演示页 | docs/mcp-contract.md |
| takeaway | 三句话（逐条标错 + 可追溯可复现 + 系统自身被评测） | 设计 §2 观众③ |
| 对照表 | 旧痛点×新手段 5 行（白底平铺→深色分层 / 默认控件→定制组件 / 一条条跑→多选对比 / 无来源→快照徽章 / 口径混乱→分列纪律） | 设计 §4 |
| 链接 | 文档站 / 仓库 / 快速开始（青色可点击链接，修复 Streamlit 默认深蓝覆盖） | site-design §3 |

## 5. 数字核对表（独立重算：verify_demo_data.py 11 节全 [OK] + AppTest 渲染核对）

| 口径 | 页面显示 | demo/data 摘要 | 源报告/产物重读 | 一致 |
|---|---|---|---|---|
| recall | 0.820 | 0.82 | benchmark_run_baseline.json aggregate | ✅ |
| precision | 0.7455 | 0.7454545454… | 同上 | ✅ |
| F1 | 0.7810 | 0.7809523809… | 同上 | ✅ |
| IRR κ / α | 0.8336 / 0.8335 | κ=0.8336 · α=0.8335 | F1 报告锚点（623 决策 · 一致率 93.58%） | ✅ |
| gap | +0.046 → M 后 +0.0449 | delta 0.046 / delta_after_m 0.0449 | benchmark_run_baseline.json gap + M1 报告 +0.0449 锚点 | ✅ |
| 决策构成 | correct 477 / edge 96 / error 50 / 合计 623 | n_gold_correct/n_gold_error/n_decisions | benchmark 摘要 + F1 报告 | ✅ |
| strata | deg 0.4431 / pan 0.6264 / scrna 0.5757；难度 0.6335/0.5373/0.3844（含 CI·n） | strata.act / strata.difficulty | benchmark_run_baseline.json | ✅ |
| 黄金对照 ×5 | 80.0 / 69.0（原始 63.0 并存）/ 66.7 / 80.0 / 63.7（含维度分、critical issues、口径 note） | golden_summary entries | windowI/L 报告重读 | ✅ |
| 成本 G | ¥2.55 | eval_summary cost 2.55 | agent-eval-report.md §2 锚点（余额 39.53→36.98） | ✅ |
| 成本 L-b | ¥0.43 | eval_summary cost 0.43 | L1 §7.2 锚点（余额 22.53→22.10） | ✅ |
| reward 映射 | 4:1.00 / 3:0.85 / 2:0.60 / 1:0.30 / 0:0.00 + L-1 mask | reward_summary.mapping/mask | reward-mapping.md §2/§3 逐行锚点 | ✅ |
| spike-in | scrna 0.85→0.2354（drop 0.6146）/ deg 0.85→0.2125（0.6375）/ pan 0.85→0.2400（0.6100） | reward_summary.spike_in | E4 §三.9 + reward-protocol §七.2 锚点 + drop 数值自洽（=0.85−after） | ✅ |
| 真实评测 ×2 | G 30.0（L1×19/L3×1，K1 重评）/ L-b 30.0（L1×4/L2×1） | eval_summary runs 条目级 | windowK1_reeval / windowLb_analysis 重读 | ✅ |
| R0 | ρ=0.9747 · PASS | r0_summary.key_metric | scrna_r0.json（K/M 后版本） | ✅ |
| 工程数字 | 274 测试 | engineering_summary.n_tests | pytest --collect-only 实测 274 | ✅ |

**口径分列**（site-design §6.2）：63.7 仅限 10X-B expected 口径（页面 callout + 摘要
note）；66.7 仅限 Smart-seq2-C 口径；29/30 双口径注沿用 N-b 实现；成本双口径
（余额差权威 vs usage 换算 ¥0.90）以余额差为准并留档说明。

## 6. skill 应用记录

### 6.1 design-taste-frontend 执行（页面生成）
- 评测页四 tab：统计卡网格（等宽大数字）+ gap/口径 callout + 决策构成堆叠条 +
  strata 进度条 + 比较表 + 决策集差异两栏（等高 274/274 实测）+ spike-in 掉分条 +
  运行卡 + R0 卡——全数据驱动，克制无装饰；
- 关于页：非对称价值层行（64px 编号列 + 1fr 文本）+ 工程数字四卡 + 路线图两栏 +
  MCP 代码块 + takeaway + 对照表；
- AI 模板感自检：无渐变/彩虹文字/emoji 堆砌/对称三卡复制/无意义动画；圆角 8-10px；
  动效 150ms ease-out + prefers-reduced-motion。

### 6.2 web-design-guidelines 走查（🔴=0）
走查方式：真实浏览器（Playwright headless Chrome）+ 全页/元素级截图 + AppTest
DOM 断言交叉验证。五维结果与问题闭环：

| 维度 | 结果 |
|---|---|
| 字体排版 | ✅ 等宽数字 + 三层字重层级；中文混排行高 1.6；无 <14px 正文（最小 0.66rem 仅徽章） |
| 间距节奏 | ✅ 8px 网格一致；卡片 10px 圆角；组间距一致 |
| 交互反馈 | ✅ tabs hover/active 态（琥珀下划线）；链接 hover 变色；无新增按钮 |
| 色彩对比 | ✅ token 一致；正文 #e5e7eb on #0f1115 ≈ 13:1；链接青 #22d3ee |
| 布局层级 | ✅ 主次分明；两栏等高；窄屏 1100px 表格纵堆叠 |

问题闭环（全部修复后复验）：
- 🟡 关于页三元组快照卡大字号折行（0.3.0 · 1.7.0 · 0.1.3 断成两行）→ **已修**：
  新增 `ba-stat-value-sm`（1.05rem）单行显示，四卡等高复验通过；
- 🟡 关于页底部链接被 Streamlit 默认样式覆盖为深蓝 rgb(0,84,163)（对比度不足）
  → **已修**：选择器特定性提升（`[data-testid="stMarkdownContainer"] a` 等）+ 青色
  + 1px 下划线，computed style 实测 rgb(34,211,238)；
- 全页 OCR 疑点逐项元素级核实：两栏卡片等高 274/274、callout 完整无截断、
  高亮行可见——**均为误报，无真实问题**。

🔴 = 0。

### 6.3 code-review 双轴审查（Standards vs Spec 分开展示）

> 审查员 A（Standards 轴）与审查员 B（Spec 轴）独立子代理并行、分开展示、不合并
> 裁决；意见闭环如下（采纳/驳回逐条记录）。报告见 §8。

（§8 填写闭环记录）

## 7. 工程纪律核对

- [x] **golden 0 差异**：`bio-audit golden` → `"diffs": []`（137 决策）
- [x] **pytest 全绿**：274 passed（102.68s；含 test_demo_smoke 5 项）
- [x] **ruff**：demo/ 0 错误
- [x] **数据增补走 export**：成本/reward/工程数字全部经 export 提炼（带 provenance
      锚点断言）；verify_demo_data.py 增补 3 节全 [OK]（**默认调用、中文 GBK 控制台
      实测**，F3 修复后）；demo/data 旧摘要重生成仅 exported_at 变化（数值零漂移，
      git diff 逐文件核对）；manifest 指纹自检通过
- [x] **自包含性**：demo 运行时只读 demo/data + 包内资产；全输出无 Windows 绝对路径
      （verify §8 扫描 NONE）
- [x] **推送纪律**：只 add demo/ + pyproject.toml + docs/ 报告与登记；src/、tests/、
      ui/ 零改动（git diff 确认）；push 前三查
- [x] **CI 云上绿**：见 §7.1

### 7.1 推送与 CI 云上结果

- **commit** `3a4738d`（2026-08-19）：19 文件（demo/ 16 + pyproject.toml + docs 2 报告 + index.md 登记）；
  push 前四查——git status 无预期外文件、diff 边界干净（src/tests/ui 零改动）、
  `git ls-files demo/` 无大文件、commit 边界单 commit；
- **push 插曲（如实）**：本机代理（127.0.0.1:7892，SSH over HTTPS proxy 配置）不在线
  → 首推失败（errno=10061）；实测直连 GitHub SSH 认证成功 → 一次性
  `-c core.sshCommand="ssh -o ProxyCommand=none"` 推送成功（不改配置文件）；
- **CI 云上绿**：run `32270653462`（push 3a4738d）**success**——双矩阵
  `pytest+golden (Python 3.10)` 与 `pytest+golden (Python 3.12)` 均绿（含 pytest
  全套 274 passed + smoke 5 项真跑、golden replay 137 决策 0 diff、本体/规则/采集/
  benchmark/reward/MCP 闸门、数据管线锚定、ruff 含 demo/）；Pages build
  `32270649324` success（docs 站重建，登记 N1d）。

## 8. 双轴代码审查闭环记录

> 审查员 A（Standards 轴，构建质量）与审查员 B（Spec 轴，需求符合性）独立子代理
> 并行审查（各自实跑 verify/ruff/collect-only 佐证）、分开展示、不合并裁决；
> 意见闭环如下（采纳/驳回逐条记录）。

### 8.1 Standards 轴 findings 与闭环（🔴=0）

| # | 严重度 | finding | 闭环决议 |
|---|---|---|---|
| S1 | 🟠 | Tab 4 L 分布渲染含 ×0 空档（cellvoyager_g level_counts 含 0 档），与全 demo「0 档省略」约定冲突 | **采纳**：`03_benchmark.py` L 分布加 `int(v) > 0` 过滤（与 result_view.level_counts_label 同约定）；页面实测 G 显示 L3×1 · L1×19 |
| S2 | 🟠 | R0 状态徽章类名笔误：`ba-flow-chip ba-flow-final` 不存在（theme.css 只有 `ba-flow-chip-final`），绿色最终态样式丢失 | **采纳**：改 `ba-flow-chip ba-flow-chip-final` |
| S3 | 🟠 | export/verify 的 subprocess（pytest --collect-only）未检查 returncode，失败会静默吞或裸 traceback | **采纳**：两脚本补 `if proc.returncode != 0: raise/check(带 stderr 尾巴)` |
| S4 | 🟠 | export/verify 新增 pytest 硬依赖，与 pyproject「纯 stdlib」注释冲突 | **采纳**：pyproject.toml:35 注释同步更新（pytest 属 dev extra，构建 demo/data 需已装） |
| S5 | 🟠 | 平台对照卡硬编码分数（80.0/69.0/66.7/63.7 等）与「零硬编码」承诺冲突 | **采纳**：卡片 prose 改为「分数·verdict 见上表」，仅保留决策集事实（审查前已先行修复） |
| S6 | 🟡 | 锚点正则双份复制（export vs verify，散弹式修改） | **驳回**（说明）：verify 是 N1a 定稿的**独立重读核对**（S4/S5 决议），共享锚点模块会耦合两脚本、丧失独立核对价值；verify 用更严的 `:.4f` 精确锚是对 export 的交叉校验，属设计特性 |
| S7 | 🟡 | cost 键防御不对称（页面 `r.get("cost", {})` 后直接 `cost["amount"]` → KeyError） | **驳回**（说明）：demo/data 由 manifest 指纹钉死，缺 cost = 数据缺陷，应响亮失败而非静默降级 |
| S8 | 🟡 | 页面无除零/结构兜底（n_total=0、ci 缺键） | **驳回**（说明）：数据被 manifest 钉死（623 决策等锚点断言），强耦合即防漂移设计 |
| S9 | 🟡 | `_LEVEL_SEMANTICS` 与 result_view.LEVEL_META 文案重复 | **驳回**（说明）：前者是 reward 映射语义（reward-mapping.md §2 宪法），后者是 level 徽章语义，职责不同；宪法变更走评审流程 |
| S10 | 🟡 | 死 CSS `.ba-about-links`（改链接后无使用） | **采纳**：theme.css 移除 |
| S11 | 🟡 | 关于页 CI/golden 卡显示值硬编码（3.10+3.12 / 0 差异） | **采纳**：export 增补结构化字段 `ci_matrix_versions`（ci.yml 锚点解析）+ `golden_diff`，页面派生显示 |
| S12 | 🟡 | st.code JSON 示例含 `//` 注释（JSON 不支持） | **采纳**：移除注释行 |
| S13 | 🟡 | 性能：四 tab 全执行 + 六份 JSON 重读 | **驳回**（说明）：文件均 <10KB，与既有页面同构；数据量增长时再上 cache_data |

### 8.2 Spec 轴 findings 与闭环（1 🔴 + 2 🟠 + 5 🟡，全部闭环）

| # | 严重度 | finding | 闭环决议 |
|---|---|---|---|
| F1 | 🔴 | benchmark tab 硬编码 623/50/60（台账 §12.1 第 1 项原话「零硬编码」） | **采纳**：`bm["n_decisions"]` / `bm["n_gold_error"]` / `bm["n_tasks_run"]` 派生（审查前已先行修复，机制违规非数据错误） |
| F2 | 🟠 | 平台对照卡重复硬编码分数与决策数 | **采纳**：同 S5（卡片去字面量，主表已全读 entries） |
| F3 | 🟠 | verify/export 默认调用在中文 Windows（GBK）崩溃：¥ 消息 UnicodeEncodeError，§9-11 无法执行（独立实跑复现） | **采纳**：两脚本 main() 开头 `sys.stdout.reconfigure(encoding="utf-8", errors="replace")`；修复后**默认调用（无环境变量）** 11 节全 [OK] 实测通过 |
| F4 | 🟡 | 数据集元数据硬编码（7,186 cells × 22,454 genes · 32 患者 等，L1 §3.1/§5 出处） | **驳回**（说明）：spec 未规定这些叙事性数据进 demo/data（台账 §12.1 第 2 项只要求 platform/n_decisions/维度分/critical_issues 读 entries）；页面 caption 已注出处；如需入数据走 export 后续窗口 |
| F5 | 🟡 | gap callout 硬编码 ±0.10 | **采纳**：读 `gap.tolerance_interval`（数据现成） |
| F6 | 🟡 | 「κ 出处 F1 报告 §F2」chip 冗余硬编码 | **采纳**：移除 chip，出处由 provenance note + irr.note caption 承担（摘要 JSON 内已注明） |
| F7 | 🟡 | 关于页工程卡显示值硬编码 | **采纳**：同 S11（ci_matrix_versions / golden_diff 结构化） |
| F8 | 🟡 | level 语义文案硬编码（_LEVEL_SEMANTICS） | **驳回**（说明）：同 S9（宪法文案，非数字；变更走评审） |
| F9 | 🟡 | export 新增 pytest 子进程强依赖 + 台账状态未更新 | **部分采纳**：S4（pyproject 注释同步）；台账状态表更新归 demo 设计中枢（N1a C3 裁决，不属执行窗口） |

### 8.3 闭环后最终验证

- ruff check demo/ → 0 错误
- export + verify **默认调用（GBK 控制台）** 全绿（11 节 [OK]）
- pytest 274 passed（102.68s）+ `bio-audit golden` diffs=[]（0 差异）
- test_demo_smoke 5/5（四页冒烟含评测页四 tab 渲染 + golden 守卫 + 63.7 断言）
- 页面关键渲染 AppTest 断言核对（strata CI/比较表 p 值/provenance chips/关于页全块）

**双轴结论**：Standards 🔴=0（5 🟠 + 6 🟡 全部闭环，1 驳回说明）；Spec 符合度高，
F1-F8 全部闭环（3 驳回均附理由）。无阻塞项，意见闭环率 100%。

## 9. 遗留与说明（给 N-e）

1. **demo/data 由 9 → 11 文件**（新增 reward_summary / engineering_summary）；
   N-e 全站走查时按新清单核对。
2. **成本口径双记录**（G 报告 §2 权威余额差 vs usage 换算；L1 §7.2 同款）——页面以
   余额差权威口径展示，usage 换算留档于 eval_summary cost.source 注。
3. **工程数字 274 为 pytest 实收集**（export 时实测）——若后续窗口新增测试，重跑
   export 即自动更新，页面无硬编码。
4. **「未验证」节点色**等跨窗口待办延续（台账 §5），N-e 收口。
5. 走查截图存于本机临时目录（不入仓库）；N-e 的 image-to-code 预览页将重截。

---

*报告完毕。窗口 N-d 执行计划快照与 execution-plan 打勾完成；git commit/push 与
CI 云上确认见 §7/§7.1。*
