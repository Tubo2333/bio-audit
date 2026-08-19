# N1a 子窗口完成报告：骨架 + 数据层（窗口 N · 1/5）

> **窗口**：N-a（execution-plan §六.十八 1-3）｜**日期**：2026-08-19
> **依据**：demo-redesign-design v0.3（§1.3/§4/§5/§6/§7/§10）+ demo-n-window-ledger
> §2.1/§3（冻结验收清单）+ handoff-design-hub §六.7（推送纪律）
> **验收方式**：demo 设计中枢独立验收（不轻信自检：实跑 + 数字独立重算 + git 检查）

---

## 1. 交付总览

| 项 | 内容 |
|---|---|
| 新目录 | `demo/`（app.py / theme.css / components.py / data_index.py / pages×4 / data×9 / scripts×2） |
| 修改文件 | `pyproject.toml`（ui extra 锁 `<2`；新增 demo extra；ruff exclude demo/data） |
| 零改动 | `src/`、`tests/`、`ui/`（git diff 确认） |
| 数据层 | `demo/data/` 9 个文件，全部带 provenance，全库无 Windows 绝对路径 |
| 提交 | 单 commit，只含上述文件（推送纪律 §六.7） |

## 2. execution-plan §六.十八 打勾

- [x] **N-a 1** demo/ 目录（app.py 侧边栏导航 + 条件渲染、theme.css 深色主题、
      pages/ 四页空壳、components.py、data_index.py）；ui/ 薄壳并存零改动
- [x] **N-a 2** scripts/export_demo_data.py：从 cellvoyager-outputs 提炼摘要 JSON
      到 demo/data/（provenance: source/sha256/generated_at；剥离 Windows
      绝对路径）；素材数字与 §1.3 表格钉死出处一致
      （80.0/69.0/66.7/63.7/30.0×2/85.0×6/60.0/29.0）
- [x] **N-a 3** 空壳可启动：`streamlit run demo/app.py` 四页路由通
      （AppTest 实测 + headless 服务器 200 + 截图确认）

## 3. 台账 §3 冻结验收清单逐项核对

| # | 验收项 | 结果 | 证据 |
|---|---|---|---|
| 1 | 结构齐全 + ui/ 零改动 | ✅ | demo/ 树见 §4；`git status` 仅 `M pyproject.toml` + `?? demo/` |
| 2 | pyproject 落 `streamlit>=1.31,<2` | ✅ | pyproject.toml:31-34（ui + demo 两 extra） |
| 3 | 提炼脚本可运行 → provenance + 无绝对路径 + 63.7 基准副本 | ✅ | `python demo/scripts/export_demo_data.py` exit 0；verify §5.4 扫描无命中；windowL_10X_B_expected.json provenance.source=windowL_10X_B_expected.json |
| 4 | 数字核对（独立重算） | ✅ | `python demo/scripts/verify_demo_data.py` 全 [OK]，核对表见 §5 |
| 5 | 可启动：四页路由 + 启动校验中文提示不崩溃 | ✅ | AppTest 四页切换无异常；缺 manifest/指纹不匹配两场景均中文提示（含 export_demo_data.py）不崩溃；服务器 HTTP 200；截图确认单组导航 + 深色主题 + 无 Deploy |
| 6 | pytest 全绿 + golden 0 差异 + 推送纪律 | ✅ | pytest 269 passed；`bio-audit golden --json` diffs=[]；push 前四查见 §8 |
| 7 | skill 应用：design-taste-frontend + code-review 双轴 | ✅ | 设计语言见 §6.1；双轴审查闭环见 §7（报告落盘本节） |
| 8 | N1a 报告 + execution-plan 打勾 | ✅ | 本文件；execution-plan §六.十八 N-a 1-3 已勾 |

## 4. 交付文件清单

```
demo/
├── app.py                      # 入口：主题注入 + 启动数据校验 + 侧边栏导航 + 条件渲染
├── theme.css                   # 深色审计台（§4 token；data-testid 注入；隐藏自动导航/Deploy）
├── components.py               # Cascader/GroupSelect/Multi-select/SplitButton 骨架签名（N-b 实现）
├── data_index.py               # demo/data 索引 + verify_data_ready 启动校验
├── pages/                      # 四页空壳（render() + 标题占位 + N-b~N-d 填充注释）
│   ├── 01_workshop.py          # 审计工坊（N-b）
│   ├── 02_capture.py           # 采集演示（N-c）
│   ├── 03_benchmark.py         # 评测与奖励（N-d）
│   └── 04_about.py             # 关于（N-d）
├── scripts/
│   ├── export_demo_data.py     # 提炼脚本（cellvoyager-outputs → demo/data/，provenance 化）
│   └── verify_demo_data.py     # 独立数字核对脚本（源重读 vs 摘要比对）
└── data/                       # 提炼摘要（export 生成；运行时唯一数据源）
    ├── manifest.json           # 指纹 + 来源登记（启动校验依据）
    ├── golden_summary.json     # 黄金对照 ×5（windowI A/B/C + windowL 10X A/B_expected）
    ├── eval_summary.json       # 真实评测 ×2（G 30.0 K1 重评 / Lb 30.0）
    ├── benchmark_summary.json  # benchmark 摘要（recall/precision/F1/gap/IRR κ）
    ├── r0_summary.json         # R0 锚定（ρ=0.9747）
    ├── trajectories_index.json # 20 条轨迹索引（golden 基线分数）
    ├── verdicts_10X_B.jsonl    # M1 声明重建输入（N-c）
    ├── golden_agent_10X_B_executed.py  # M3 解析输入（N-c，sanitize 后副本）
    └── windowL_10X_B_expected.json    # 63.7 断言基准（N-c，provenance 保留 source）
```

## 5. 数字核对表（独立重算：verify_demo_data.py 从源报告重读 vs demo/data）

| 口径 | 设计 §1.3 钉死值 | demo/data 摘要 | 源报告重读 | 一致 |
|---|---|---|---|---|
| 黄金 A（Smart-seq2，I） | 80.0 · pass | 80.0 · pass（10 决策） | windowI_A.json audit | ✅ |
| 黄金 B（Smart-seq2，I；J 后重评） | 63.0 → 69.0 · needs_correction | 69.0 · needs_correction（原始 63.0·blocked 并存） | windowI_B.json = 63.0·blocked；J1 报告锚点 69.0·needs_correction | ✅ |
| 黄金 C（Smart-seq2，I） | 66.7 · needs_correction（仅限 Smart-seq2-C 口径） | 66.7 · needs_correction（10 决策） | windowI_C.json audit | ✅ |
| 黄金 A（10X，L） | 80.0 · pass（11 决策含双联体） | 80.0 · pass（11 决策） | windowL_10X_A.json audit | ✅ |
| 黄金 B（10X，expected_types 后） | **63.7 · blocked**（仅限 10X-B expected 口径） | 63.7 · blocked（11 决策） | windowL_10X_B_expected.json audit | ✅ |
| CellVoyager 真实评测（G，K 后重评） | 30.0 · needs_correction（L1×19/L3×1） | 30.0 · L1×19/L3×1（K1 重评）+ 注 G-2 版 L1×7/L3×1/L-1×12 | windowK1_reeval.json level_counts | ✅ |
| CellVoyager 短评测（L-b） | 30.0 · needs_correction（L1×4/L2×1） | 30.0 · L1×4/L2×1（5 决策） | windowLb_analysis.json audit | ✅ |
| demo 轨迹 20 条 | 85.0×6 / 60.0·pass / 29.0 等 | 索引 20 条，85.0×6、scrna_edge_singleanno 60.0·pass、scrna_melanoma_cellvoyager 29.0·blocked | golden 基线（tests/golden）逐条比对 + 抽查 3 条 | ✅ |
| benchmark | recall 0.820 / precision 0.7455 / F1 0.7810 / gap +0.046（M 后 0.0449 注明） | 0.82 / 0.7455 / 0.7810 / 0.046 + delta_after_m 0.0449 | benchmark_run_baseline.json aggregate/gap（utf-8-sig）| ✅ |
| IRR | κ=0.8336（出处 F1 报告） | κ=0.8336 / α=0.8335 / 623 决策 / 93.58% | F1 报告锚点正则解析（"全量 60 合并 IRR κ="） | ✅ |
| R0 | ρ=0.9747（scrna_r0.json K/M 后版本） | key_metric 含 0.9747 · PASS | scrna_r0.json | ✅ |

**口径分列注释**（防混写）：golden_summary.json 条目 note 字段——63.7 条目标注
"仅限 10X-B expected 口径（静默跳过双联体被补入），禁止与 66.7 混写"；66.7 条目
标注"仅限 Smart-seq2-C 口径（QC 硬阈值），禁止与 63.7 混写"；eval_summary 标注
"29/30 双口径页内注释见 N-b（demo-redesign-design §3.2）"。

## 6. 关键实现说明

### 6.1 设计语言（design-taste-frontend 执行记录）
- **配色**：深蓝黑底 #0f1115 + 面板 #1a1d24 + 细边框 #2a2f3a；琥珀 #f59e0b 仅作
  选中态/焦点（面积 <10%）；青 #22d3ee 作版本徽章；verdict 绿/黄/红有语义。
- **字体**：等宽栈（JetBrains Mono → Windows 落 Consolas）用于分数/徽章/品牌；
  中文混排行高 1.6 + word-break。
- **布局**：侧边栏固定导航（radio 定制为块级按钮，选中态 = 琥珀左边条，无发光
  无放大）+ 顶部横幅（品牌 + 三元组版本徽章 + 当前页名）+ 主区流式；8px 网格、
  圆角 10px。
- **AI 模板感自检**：无渐变/彩虹文字、无 emoji 堆砌、无对称三栏复制、圆角克制、
  动效 150ms ease-out + prefers-reduced-motion。

### 6.2 导航与条件渲染（1.31 兼容）
- 侧边栏 `st.radio` 页级导航（key="page" 持久化）+ `if/elif` 条件渲染调用
  pages 模块 `render()`；**不用 st.tabs 承载整页**（设计 §3.1）。
- Streamlit 自动 multipage 导航（pages/ 扫描）与默认 Deploy 按钮由 theme.css
  隐藏（data-testid 选择器——正是版本锁定 `>=1.31,<2` 的动机）。
- pages/ 文件双模：被 app.py import 时提供 render()；被 multipage 直接执行时
  `__main__` guard 自渲染（兜底）。

### 6.3 数据层（provenance 化）
- 全部分数从源产物读取提炼；数字锚点断言仅作防漂移护栏（源值变化 → 脚本报错
  退出，不静默写坏数据）。
- 剥离 Windows 绝对路径：提炼只取白名单字段 + 递归 sanitize + `_final_scan`
  全输出扫描（含 `D:\`/`C:\` 即失败）；executed.py 副本中 2 处路径替换为
  `<absolute-path-stripped>` 占位（不影响 M3 正则解析）。
- 自包含性：demo 运行时只读 demo/data/ + bioaudit 包内资产；启动校验 manifest
  指纹，缺失给中文提示（"请先运行 `python demo/scripts/export_demo_data.py`"）
  不崩溃。

### 6.4 provenance 字段示例（windowL_10X_B_expected.json 提炼副本）
```json
{
  "provenance": {
    "source": "windowL_10X_B_expected.json",
    "source_sha256": "87b3f0ca65f0b8c14117aa84609ee21b677ed768139b85d6398cf7eec69f8dba",
    "generated_at": "2026-08-16T23:05:11",
    "exported_at": "2026-08-19T12:31:24+00:00",
    "note": "63.7 断言基准提炼副本（demo-redesign-design §6；N-c 断言读本副本）"
  }
}
```

## 7. 双轴代码审查（code-review skill，两轴独立子代理并行）

> 审查员 A（Standards 轴，构建质量）与审查员 B（Spec 轴，是否做了该做的）
> 独立运行、分开展示、不合并裁决；意见闭环如下（采纳/驳回逐条记录）。

### 7.1 Standards 轴 findings 与闭环

| # | 严重度 | finding | 闭环决议 |
|---|---|---|---|
| S1 | 建议-高 | 设计文档悬空引用：demo docstring 引用的 docs/specs/2026-08-16-demo-redesign-design.md 不在仓库内 | **驳回**（与仓库惯例一致）：src/ 的 regression.py、ontology/__init__.py、capture/models.py 等均以 docs/specs/*.md 引用外部审计内存文档（site-design §1.2 明示外部文档不进 Pages 不动路径）；docstring 引用是既有模式 |
| S2 | 建议-中 | benchmark 摘要 n_decisions=623 / agreement=0.9358 硬编码无防漂移锚点 | **采纳**：export 改为从 F1 报告正则解析（"全量 60 合并…（623 决策，一致率 93.58%）"）+ 锚点断言；verify 同步核对 |
| S3 | 建议-中 | sanitize 内容破坏：expected_types.config 引用身份被抹；executed.py 副本不可执行；错误消息被吞截 | **采纳**：config 改为包内相对引用 `src/bioaudit/data/expected_types.yaml`（保留身份）；executed 副本 manifest 注明"解析专用副本（M3 输入，不执行）"；正则收紧为 ≥2 级反斜杠路径——`failed:\n` 不再误判（L222 错误消息完好） |
| S4 | 建议-中 | verify 未核对变换最大的两个 N-c 副本（verdicts jsonl / executed.py） | **采纳**：verify 增补逐字节/逐行与源比对（verdicts 25 行语义一致；executed == 源剥离后逐字节一致；占位符 1 处） |
| S5 | 建议-低-中 | verify 是"独立重读"而非"独立重算"，与 export 共享锚点；缺源时裸 FileNotFoundError | **部分采纳**：docstring 措辞改"独立重读核对"并说明护栏语义；补 src.exists() 显式报错（exit 2） |
| S6 | 建议-低 | _WIN_PATH 盲区（正斜杠/UNC）+ 护栏共用同一正则"自己验证自己" | **部分采纳**：正则升级覆盖 UNC；**正斜杠形态刻意不支持**——`https://` 的 `s://` 与盘符正斜杠无法区分（实测曾误毁 PubMed URL，已回滚；源产物实测无正斜杠路径形态，留档 §9） |
| S7 | 建议-低 | 输出非确定性（exported_at 每次变化 → git 噪声） | **驳回**（provenance 语义）：exported_at 时间戳是台账要求的 provenance 字段（source/sha256/generated_at/exported_at）；重复导出产生新时间戳是预期行为，manifest 同步更新；N 窗口只导出一次 |
| S8 | 吹毛求疵 | _report_anchor 死代码；Counter 函数内导入；app.py next() 无默认值 + main() 无 guard；data_index manifest 损坏裸崩/缺指纹静默放行；pyproject 注释误导；双份清单漂移；f-string 无插值；eval level 键类型不一致；verify 跳过 windowI_B 决策数；groups_for_paradigm(None) 未文档化；精度断言不一致 | **全部采纳**：逐一修复（删死代码 / 顶部导入 / next 默认值 + `__main__` guard / manifest JSONDecodeError 容错 + 缺 sha256 报问题 / 注释修正 / OUT_FILES 与 REQUIRED_FILES 共享单一事实源 / 去 f 前缀 / level 键统一字符串 / 补决策数核对 / docstring 补未选态语义 / 统一 1e-9） |

### 7.2 Spec 轴 findings 与闭环

| # | 严重度 | finding | 闭环决议 |
|---|---|---|---|
| A1 | 建议 | 台账 §3.7 冻结项：code-review 双轴审查报告未闭环落盘 | **采纳**：本节（7.1/7.2/7.3）即闭环记录，报告随本次提交落盘 |
| B1 | 建议 | export 的 manifest 来源登记为死代码（capture 键无扩展名 vs files 键有扩展名，永不命中） | **采纳**：capture 返回键改为文件名；manifest 实测含 N-c 三副本的 source/source_sha256 |
| B2 | 建议 | 报告 commit/push 表述超前 + CI 云上绿未验证 | **采纳**：push 后按三查复核 + 记录 CI 云上绿（见 §8） |
| B3 | 建议 | export/verify 脚本含 DEFAULT_SOURCES 绝对路径，台账 §3.3"全库"字面不满足 | **驳回**（口径说明）：台账"全库 grep 无 Windows 绝对路径"指**提炼产物**（demo/data，扫描 NONE）；脚本默认源路径是 dev 工具输入参数（--sources 可覆盖、docstring 明示），非数据内容 |
| C1 | 吹毛求疵 | pages 引用的 .ba-page-title/.ba-page-sub 未在 theme.css 定义（空挂类名） | **采纳**：theme.css 补定义（标题/副标题排版） |
| C2 | 吹毛求疵 | 报告 §6.4 provenance 示例时间戳过期 | **采纳**：刷新为最新导出值（2026-08-19T12:31:24+00:00） |
| C3 | 吹毛求疵 | 台账 §1 状态表仍标 N-a ⏳ 未开工 | **转交**：台账状态由 demo 设计中枢验收后更新（职责归中枢，不属执行窗口） |
| C4 | 吹毛求疵 | 清单外附加文件 pages/__init__.py 与 verify_demo_data.py | **说明**：均已列入报告 §4 交付清单；pages/__init__.py 为 importlib 包导入所需，verify_demo_data.py 为独立核对工具 |

### 7.3 闭环后最终验证

- ruff check demo/ → 0 错误（data/ 生成产物 exclude）
- export_demo_data.py 幂等重跑 exit 0 → verify_demo_data.py 全 [OK] exit 0
- AppTest 四页回归通过；verdicts 副本 PubMed URL 完好（正则误伤已回滚）
- pytest 269 passed；`bio-audit golden --json` diffs=[]（见 §8）

## 8. 工程纪律核对

- [x] **golden 0 差异**：`bio-audit golden --json` → `"diffs": []`（137 决策）
- [x] **pytest 全绿**：269 passed（99.8s）
- [x] **ruff**：demo/ 源码 0 错误（data/ 生成产物 exclude，理由：executed.py
      副本保持源原样供 M3 解析）；src 历史 E501 与本窗口无关（CI ruff 非门禁
      `|| true`，且纪律不碰 src/）
- [x] **推送纪律**：commit `3400ca3`（仅 demo/ + pyproject.toml +
      docs/migration/N1a-skeleton-data-report.md + index.md 登记）；
      push 前三查——① git status 无预期外文件（干净）② git log origin/main..HEAD
      仅 1 commit ③ git ls-files demo/ 无大文件（最大 38.8KB verdicts jsonl）；
      `git push origin main` 成功（b1739e8..3400ca3）
- [x] **CI 云上绿**：见 §8.1
- [x] **零改动**：src/、tests/、ui/ 未触碰（git diff 仅 pyproject.toml）

### 8.1 CI 云上结果

- run `32253399493`（push 3400ca3）**success**：双矩阵 `pytest+golden (Python 3.10)` +
  `pytest+golden (Python 3.12)` 均绿（含 pytest 全套、golden replay 137 决策 0 diff、
  本体/规则/benchmark/reward 闸门、scrna_r0 数据管线锚定）；ruff 非门禁（`|| true`）
- Pages build `32253398916` 随 push 触发（docs 站重建，index.md 登记 N1a）

## 9. 遗留与说明（给后续子窗口）

1. **冷启动耗时**：N-a 实测——AppTest 全流程（含 import bioaudit + 规则加载）
   单次 run ~1-2s 内完成，`streamlit run` 冷启动含服务器启动 ~5s；满足设计
   §3.2 冷启动 ≤10s 预算，加载态按台账 §5 待 N-e 收口实测记录。
2. **components.py** 为签名骨架（N-b 实现）：Cascader 三级联动 / Multi-select
   ≤3 / Split Button；占位方法显式 NotImplementedError，不允许静默占位混入。
3. **CI streamlit 依赖**：N-c 的 test_demo_smoke 上 CI 前需同步 CI 依赖
   （台账 §2.2：CI 不装 streamlit；demo extra 已就绪）。
4. **69.0 重评分**：源 windowI_B.json 现值为 63.0·blocked（I 窗口实测），
   69.0·needs_correction 为 J 窗口重评（J1 报告，K1 复核不变）——摘要中
   双值并存 + provenance note 说明，防第三套数字。
5. **G 评测 30.0 双版本**：G-2 版（L1×7/L3×1/L-1×12，ruleset 1.2.0）与 K1 版
   （L1×19/L3×1，ruleset 1.5.0）同分；摘要以 K1 后重评为准并注明差异（台账
   §2.1 口径）。
6. **正斜杠盘符形态不支持**：`_WIN_PATH` 刻意不匹配 `C:/dir` 形态——`https://`
   的 `s://` 与正斜杠盘符无法用正则区分（实测曾误毁 PubMed URL 后回滚）；
   源产物实测无反斜杠以外形态（N1a 验证 §8 扫描 NONE）。若未来源数据出现
   正斜杠盘符路径，需改用结构化解法（白名单字段剥离）而非扩展正则。
7. **executed.py 副本为解析专用**：仅 1 处占位符（`--rscript` 默认值），
   副本不执行（N-c 仅 M3Parser.parse_code 正则解析）；manifest 已注明。
8. **execution-plan 打勾**：§六.十八 N-a 1-3 已勾（仓库外文档
   D:\C-file\docs\specs\2026-08-13-execution-plan-v1.md，不随本仓库 push）。
9. **台账状态表**（demo-n-window-ledger.md §1）：N-a ⏳ → ✅ 由 demo 设计
   中枢验收后更新（验收记录归中枢职责）。
