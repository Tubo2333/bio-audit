# N1b 子窗口完成报告：审计工坊（窗口 N · 2/5）

> **窗口**：N-b（execution-plan §六.十八 4-7）｜**日期**：2026-08-19
> **依据**：demo-redesign-design v0.3（§3.1/§3.2/§4/§5/§8/§10）+ demo-n-window-ledger
> §8.1（冻结验收清单 9 项）+ handoff-design-hub §六.7（推送纪律）
> **验收方式**：demo 设计中枢独立验收（不轻信自检：实跑 + 数字独立核对 + git 检查）

---

## 1. 交付总览

| 项 | 内容 |
|---|---|
| 实现文件 | `demo/components.py`（Cascader/Multi-select/Split Button 完整实现）、
  `demo/result_view.py`（新增：结果页全元素渲染模块）、
  `demo/pages/01_workshop.py`（工坊页完整实现）、`demo/theme.css`（样式增量）、
  `pyproject.toml`（streamlit 下限 1.31 → 1.33——st.popover 首发版本，双轴
  审查实证；上限 <2 不变） |
| 零改动 | `src/`、`tests/`、`ui/`、`demo/data/`、`demo/app.py`、`demo/data_index.py`
  （git diff 确认） |
| 数据真实性 | 分数全部实时 run_audit 或 demo/data 产物读取，零硬编码；63.7 链路
  实时重算并与断言基准一致 |
| 验证 | pytest 269 passed / golden 0 差异 / AppTest 冒烟 8 项全过 /
  Playwright 视觉 10+ 状态截图 / ruff 0 错误 |

## 2. execution-plan §六.十八 打勾

- [x] **N-b 4** Cascader（范式→案例类型→轨迹，上级变更清空下级）+ Multi-select
      对比（≤3 条，空状态 + 窄屏堆叠）+ Split Button（运行 + 导出 JSON /
      复制证据链 / 匹配明细 popover）
- [x] **N-b 5** 结果页全元素：总分大卡 + verdict 色点 + 快照徽章
      （engine/ruleset/ontology/generated_at）+ 维度进度条 + 决策状态点 +
      证据卡（PMID）+ 时间轴（decisions + ontology stages 推导）
- [x] **N-b 6** expected_types 现象演示（黄金 B 跳过双联体 → 补入 → 63.7 blocked
      提示，与断言基准一致）
- [x] **N-b 7** 实时出分与 golden/报告一致（20/20 轨迹全量核对 + 黄金 B 链路
      断言）+ 缓存生效（cache_resource 预热 + (trajectory, act) 结果缓存）

## 3. 台账 §8.1 冻结验收清单逐项核对

| # | 验收项 | 结果 | 证据 |
|---|---|---|---|
| 1 | 组件：Cascader 三级联动上级清空下级 + Group Select 只整理轨迹 + DEG/pan 引导文案 + Multi-select ≤3（空状态 + 窄屏堆叠）+ Split Button 四动作 | ✅ | §5.1-5.4 |
| 2 | 结果页全元素（大卡/色点/快照徽章/维度条/决策点五档徽章/证据卡 PMID 悬停/时间轴推导）+"未验证"节点色决策留档 | ✅ | §5.2 + §6.2 |
| 3 | expected_types 现象演示：黄金 B → 补入提示 → L0 → blocked | ✅ | §5.5（63.7 与 windowL_10X_B_expected.json 断言一致） |
| 4 | 实时出分 + 缓存：run_audit 与 golden 一致（抽查 ≥3）+ cache_resource/cache_data 生效 | ✅ | §6.1（20/20 全量核对；缓存命中实测） |
| 5 | 演示恢复：session_state 持久化 + "恢复演示默认态" 2 次点击回讲稿起点 | ✅ | §5.6（AppTest 实测 2 次点击回默认态） |
| 6 | 口径纪律：29/30 双口径页内注释 + 63.7/66.7 不混写 + 每页结果快照徽章 | ✅ | §5.7 + §6.3 |
| 7 | 工程纪律：pytest 全绿 + golden 0 差异 + CI 云上绿 + 推送纪律 | ✅ | §8 |
| 8 | skill：design-taste-frontend（无 AI 模板感）+ web-design-guidelines 走查（🔴=0，报告落盘）+ code-review 双轴（意见闭环） | ✅ | §4 + §7 |
| 9 | 报告 + execution-plan 打勾 | ✅ | 本文件 |

## 4. 设计走查（web-design-guidelines，🔴=0）

完整走查报告见 §4.1（本报告内落盘）。结论：**🔴 严重问题 0 项**；🟡 2 项
（已修 1 项、接受 1 项）；🟢 其余全部通过。走查方式 = Playwright 真实浏览器
10+ 状态截图（默认态/对比结果/决策点/时间轴/证据卡/引导文案/黄金卡/63.7 链路/
窄屏 1024px/popover 菜单）+ 逐维核对。

### 4.1 走查明细（按 web-design-guidelines 五维）

| 维度 | 结论 | 备注 |
|---|---|---|
| 字体与排版 | ✅ 层级清晰（1.75rem 标题 / 0.82rem 分区 / 0.92rem 正文 / 0.7rem 徽章下限）；等宽字体用于分数/徽章/时间戳；中文混排行高 1.6 + word-break | 对比表 choice 省略号补 title（🟡 已修）；快照徽章 0.68rem → 0.7rem（🟡 已修） |
| 间距与节奏 | ✅ 8px 网格一致、卡片圆角 10px、分区节奏 18px；结果区非对称两栏（1:1.6） | — |
| 交互与反馈 | ✅ hover（卡片边框青/按钮琥珀）、disabled 态（无选择禁用运行）、空状态引导文案（未选/未运行/deg 引导）、focus 保留 Streamlit 默认环、动效 150ms ease-out + prefers-reduced-motion | — |
| 色彩与对比 | ✅ 正文 #e5e7eb on #0f1115（≈14:1）；次要 #9ca3af（≈5.5:1）；弱化 #6b7280 仅装饰性辅助文字（≈3.6:1，🟡 接受——非关键信息）；语义色受控（verdict 圆点 vs level 徽章形态区分） | — |
| 布局与层级 | ✅ 第一眼锚点 = 大分数卡；对比表前置、完整结果后置；窄屏 1024px 无溢出、对比表纵向堆叠 | — |

**🟡 接受项（1）**：弱化灰 #6b7280 对比度 3.6:1——仅用于 caption/单位/时间戳等
非关键装饰文本，不承载关键信息，与设计 §4 token 一致。

## 5. 关键实现说明

### 5.1 Cascader 三级联动（components.py）
- 第一级范式（DEG/Pan-Cancer/scRNA，selectbox）；
  第二级案例类型 = **Group Select 语义**（只整理轨迹、永不改变范式）；
  第三级轨迹（按范式×组经 resolver 从 demo/data 构建，组件不碰数据层）。
- **上级变更清空下级**：`{prefix}_paradigm_base/_group_base` 派生基线——
  值变化 → 显式 pop 下级控件键（防 selectbox 旧值静默回落）；首次渲染
  基线随默认值同步初始化（预置态不被误清）。
- **DEG/pan 引导文案**：范式 ∈ {deg, pan} 时第二级下渲染
  "黄金对照与真实评测仅 **scRNA** 范式提供"（不出现空列表）。
- 交互键独占 `cascader_*` 命名空间，st.session_state 持久化（刷新不丢）。

### 5.2 结果页全元素（result_view.py）
- 总分大卡：等宽 `ba-score` 3rem + verdict 色点（10px 圆点，**与 level 徽章
  视觉形态区分**——圆点 vs 圆角徽章）；
- 快照徽章：engine/ruleset/ontology/generated_at/来源 chip 行
  （`report.current_snapshot()` + 审计运行时间戳；产物读取卡用 provenance
  generated_at + "产物读取 · 来源文件"）；
- 维度进度条：data_handling/method_selection/statistical_rigor，语义色
  （≥70% 绿 / ≥40% 黄 / <40% 红）；
- 决策状态点：auto-fill 网格卡（level 五档徽章 L3 绿/L2 青/L1 黄/L0 红/L-1 灰
  + choice + 规则数 + 悬停摘要 explanation）；
- 证据卡：每决策 expander（L≤1 默认展开），文献证据 **PMID 转悬停徽章**
  （正则替换 markdown 链接/裸 PMID → `<span title="PMID n">`，**零 `<a>` 标签**，
  断网演示纪律）；备选方案、未验证键提示；
- 时间轴：见 §6.1 推导说明。

### 5.3 Multi-select 对比（≤3 条并排）
- `st.multiselect(max_selections=3)`（≥1.24 API，1.31 兼容）钉死上限；
  空状态引导；范式变更 → 对比区清空（防跨范式残留）；级联所选经典轨迹
  自动加入对比（≤3、去重、范式切换当轮抑制误加）；
- 对比表：行 = ontology 顺序（stages.yaml 阶段序 → 阶段内字母序）的决策类型
  并集，缺失列"无此决策"（DEG 无 doublet_detection 即错位信息）；
  摘要行 = 分数 + verdict 色点 + L 分布 + 问题数（悬停看详情）；
- 窄屏（<1100px）：thead 隐藏、行转卡片纵向堆叠（CSS media query）。

### 5.4 Split Button（components.py）
- 主按钮"运行审计"（primary 琥珀）+ ▾ popover 下拉：导出 JSON 报告
  （st.download_button，含快照三元组 + exported_at）/ 复制证据链（JS
  clipboard + toast）/ 查看规则匹配明细（`bioaudit.api.match_details`
  外围 API，expander 逐决策逐规则 ✓/✗ 明细）；
- 无选择时主按钮禁用；菜单动作经 `{key}_menu_action` session 回传消费。

### 5.5 expected_types 现象演示（黄金 B · 63.7）
- 黄金对照组选中 windowL_10X_B_expected → 卡 + "演示 63.7 链路（实时重算）"：
  ① M1 声明重建（11 条，含 skip_doublet）→ ② M3 解析 executed.py 副本
  （79 候选、双联体零执行证据）→ ③ 交叉验证（consistent 10 / 虚报 1 /
  expected_added 1）→ ④ **"预期决策点缺失，已补入"**（琥珀高亮）→
  ⑤ 补入后 run_audit = **63.7 · blocked**；
- **断言基准核对**：与 demo/data/windowL_10X_B_expected.json
  （63.7 · blocked · 11 决策）实时比对，一致 ✓ 徽章；
- 机制层（勾选清单实时重算 / declared 注入）明确标注归采集页（N-c），
  本页只做现象层。

### 5.6 演示恢复
- 全部交互状态存 st.session_state（级联三级 + 对比 + 结果 + 现象开关），
  刷新不丢；"恢复演示默认态"按钮 **2 次点击**（第一次 toast 确认、第二次
  执行）回讲稿起点 = scrna / 经典轨迹 / [scrna_correct, scrna_error]
  并排结果就绪（缓存命中秒级）。

## 6. 关键决策与推导说明

### 6.1 时间轴推导（design §12 留实现窗口处理）
- **推导规则**：v2 轨迹无 workflow 字段 → 时间轴由 `step_scores`（decisions）
  + ontology `stages.yaml` 推导：按阶段顺序（data-acquisition → qc →
  preprocessing → inference → interpretation → conclusion）分组，组内保持
  轨迹内决策顺序；阶段含决策 → 该阶段标记「已审计」；无决策阶段显示
  "无决策"（不伪造节点）。
- **节点着色**：level 语义四色——L≥2 正常（绿点）/ L1 风险（黄点）/
  L0 危险（红点）/ L-1、L-2 未验证（灰点）；图例常驻。
- **「未验证」节点色去留决策：保留**。理由：① 五档徽章配色（设计 §3.2
  钉死 L-1 灰）与时间轴共用同一 level→color 映射，移除会破坏映射完整性；
  ② L-1/L-2 语义"无法评估/未验证"在当前 20 条经典轨迹中确实不可达
  （全量实测 L 分布 = L0×24/L1×23/L2×4/L3×86，无 L-1/L-2），但 G 评测
  旧版 note（L-1×12）与采集页（N-c）verdict 流转演示需要灰色语义；
  ③ 保留灰 = "未知/不可评估"与 verdict 红"危险"严格区分，防误读。
  本决策已留档，台账 §5 由 demo 设计中枢更新。

### 6.2 黄金对照 / 真实评测的呈现方式（实现说明）
- 黄金对照 ×5 与真实评测 ×2 的**决策明细不在 demo/data**（自包含性硬约束，
  demo 只读提炼摘要）→ 呈现为**产物读取卡**（摘要分数 + provenance +
  快照徽章 + 口径注 + critical_issues/L 分布），与经典轨迹的**实时审计**
  口径严格分列；黄金 B（10X）因 demo/data 含完整重建输入（verdicts +
  executed.py + 断言基准）而具备实时链路演示。此分工防"实时/产物"口径
  混写，与设计 §1.3 表格分列纪律一致。

### 6.3 口径注示例（29/30 双口径页内注释，版本号按当前快照）
- scrna_melanoma_cellvoyager 结果卡（`_kaliber_note()`，版本号运行时取
  `current_snapshot()`，当前 ruleset 1.7.0）：
  > 口径注：29.0 = D5 修复后实测（当前快照 ruleset **1.7.0**）；评测页
  > 30.0 = K1 后重评（ruleset 1.5.0 口径）——同一 Agent 运行，两套口径不混写
- 黄金 B（10X）卡 note（读 demo/data 提炼副本，非硬编码）：
  > 黄金对照 B（10X，expected_types 后，L/M 窗口）· 63.7 仅限 10X-B
  > expected 口径（静默跳过双联体被补入），禁止与 66.7 混写
- 黄金 C（Smart-seq2）note：66.7 仅限 Smart-seq2-C 口径（QC 硬阈值），
  禁止与 63.7 混写（条目级 provenance 保留）。

## 7. 双轴代码审查（code-review skill，两轴独立子代理并行）

> 审查员 A（Standards 轴，构建质量）与审查员 B（Spec 轴，是否做了该做的）
> 独立运行、分开展示、不合并裁决；意见闭环如下（采纳/驳回逐条记录）。

### 7.1 Standards 轴 findings 与闭环

> 审查员 A 结论：结构与纪律整体高质量（seam 干净、渲染层转义彻底、API 用法
> 实证全对——逐一核对 audit.py/ontology/capture 签名），1 阻塞 + 10 建议 +
> 9 吹毛求疵。

| # | 严重度 | finding | 闭环决议 |
|---|---|---|---|
| S1 | **阻塞** | `st.popover` 首发于 Streamlit 1.33.0（1.31/1.29 wheel 源码实证无此 API），违反 pyproject `>=1.31,<2` 地板；本机 1.60.0 掩盖 | **采纳**：pyproject ui + demo 双 extra 下限 1.31 → **1.33**（注释注明原因；上限 <2 不变） |
| S2 | 建议 | `_warm_registry` cache_resource 空转：registry 被丢弃、run_audit 内部每次重建（audit.py 自建），注释"加载只做一次"不实 | **部分采纳**：保留实现（验收 §8.1-4 字面要求 cache_resource 规则库），修正 docstring 如实说明语义（OS 页缓存预热 + 验收合规；真正节流靠 (trajectory, act) 结果缓存） |
| S3 | 建议 | 页面层 8 处插值进 unsafe_allow_html 未 esc()（黄金/评测卡 note、issue、口径注、结果标题等）+ 剪贴板 `</script>` 注入面 | **全部采纳**：页面层插值统一 `html.escape`（与 result_view 纪律一致）；剪贴板 JS 负载 `json.dumps(...).replace("</", "<\\/")` 防 HTML 注入 |
| S4 | 建议 | run_audit error 态裸解引用 trajectory_score → KeyError；st.warning 在 cache 函数内只在 miss 时弹一次 | **采纳**：`_fill_error_state` 兜底缺失键；页面渲染 error 卡（每次可见）；st.warning 移出缓存函数 |
| S5 | 建议 | stage_of 回退 "inference" 把未知类型错标真实阶段；对比表本体顺序外类型静默丢行 | **采纳**：未知阶段归「未分类」桶（不伪造阶段）；对比表顺序外类型按出现顺序追加末尾 |
| S6 | 建议 | 63.7 链路文案硬编码 doublet_detection，断言不校验补入类型 | **采纳**：补入类型从链路结果动态取；类型与预期不符 → st.error 警示并计入断言 |
| S7 | 建议 | 默认值双份真相（components.py 内部默认 vs 页面常量） | **采纳**：Cascader.defaults 改为必填（None → ValueError），默认路径单一事实源 = 页面常量 |
| S8 | 建议 | 黄金/评测两卡近重复 | **采纳**：合并为 `_render_case_card`（critical_issues/level_counts/note/score_original 统一处理） |
| S9 | 建议 | cache key 不含轨迹文件内容哈希；快照徽章用渲染时 current_snapshot 而非 run 自带 snapshot | **部分采纳**：轨迹为包内静态资产（发布即冻结、进程重启缓存清空），无陈旧风险（报告说明）；**快照徽章改用 run 自带 `state.report.snapshot`**（运行时刻版本，语义正确） |
| S10 | 建议 | 匹配明细 act 用 id 前缀启发式而非 state["act"] | **采纳**：改用 `state["act"]` |
| S11 | 建议 | cache_data 内调 st.warning | **采纳**：并入 S4（页面 error 卡） |
| S12 | 吹毛求疵 | "M1声明" 魔法串 | **采纳**：改用 `capture.models.PROVENANCE_SOURCE_M1` 常量 |
| S13 | 吹毛求疵 | `_kaliber_note` 硬编码 "ruleset 1.5.0" 自相矛盾（纪律禁止照抄示例） | **采纳**：K1 重评版本从 demo/data eval_summary note 正则提取（单一事实源），当前快照版本运行时取 |
| S14 | 吹毛求疵 | 魔法 id windowL_10X_B_expected | **采纳**：常量 `GOLDEN_B_EXPECTED_ID` |
| S15 | 吹毛求疵 | Optional 与 `\| None` 混用 | **采纳**：统一 `\| None` |
| S16 | 吹毛求疵 | 嵌套三元（level_badge_html / 时间轴 tone） | **采纳**：改 if/elif 链 |
| S17 | 吹毛求疵 | 死 CSS / int(None) / 引导文案重复 / 剪贴板 toast 虚报 | **核对**：死 CSS 复查无命中（placeholder 仍被空壳页使用）；int(None) 无实际路径（level 恒 int）；引导文案去重（deg/pan 专属 + 空组通用兜底）；toast 文案已含"如浏览器拦截"条件说明 |

### 7.2 Spec 轴 findings 与闭环

> 审查员 B 结论：10 项验收 9 ✅ / 1 部分 / 0 ❌；关键数字经独立运行时验证
> （scrna_correct=85.0·pass、scrna_error=40.0·blocked；63.7 链路
> n_m1=11/candidates=79/stats{consistent10,fp1,expected_added1}/final 11
> → 63.7·blocked == windowL_10X_B_expected.json，doublet_detection L0）。

| # | 严重度 | finding | 闭环决议 |
|---|---|---|---|
| F1 | 中 | 「DEG 无 doublet_detection」类跨范式错位对比在 UI 不可达：多选选项集按范式过滤（01_workshop.py 对比区），同一范式内决策集差异（如 deg_correct 5 vs deg_edge_nofilter 3）虽可见"无此决策"，但 doublet_detection 行在 deg 范式内永不生成 | **部分采纳**：对比区补口径说明 caption（"对比限同范式——跨范式混表对比分数违反口径分列纪律（site-design §6.2）；决策集跨范式差异见评测页平台对照（N-d）"）；同范式内决策数不同的轨迹对比仍呈现"无此决策"错位信息；**不采纳"不限范式"档**——跨范式分数对比混口径，与设计 §1.3 分列纪律冲突 |
| F2 | 低 | 复制证据链用 components.html + clipboard.writeText（01_workshop.py 动作消费处），rerun 后执行无用户手势，浏览器可能拒绝（NotAllowedError） | **采纳**：JS 加 try/catch（clipboard API → 失败降级 execCommand + 提示）；同时渲染证据链 code 展开区作为手动复制兜底，提示文案说明浏览器策略 |
| F3 | 低 | _warm_registry 直取 bioaudit.storage.RuleRegistry，超出"api + capture 公共类"字面清单 | **驳回（附理由）**：RuleRegistry 属存储外围类（run_audit 内部同样使用），只读加载规则文件、不触碰任何评分路径；且验收 §8.1-4 明确要求 "st.cache_resource 缓存 RuleRegistry"（设计 §5 缓存纪律），保留为合规实现；纪律口径以"不碰评分路径 + 零引擎/规则/本体改动"为准（§8 golden 0 差异实证） |
| F4 | 吹毛求疵 | 黄金/评测卡 generated 时间兜底链 generated_at → exported_at → "?" 语义混用 | **说明**：产物读取卡时间戳优先 provenance.generated_at（源产物生成时间），缺失时用 exported_at（导出时间）并已标注来源 chip 区分，语义可追溯 |
| F5 | 吹毛求疵 | 现象演示按钮文案含字面 "63.7" | **采纳**：按钮文案改为「演示补入链路（实时重算）」——63.7 只出现在实时结果与断言徽章中，界面文案零硬编码数字 |

### 7.3 闭环后最终验证

- ruff check demo/ → 0 错误
- AppTest 全量回归 12 项全过（启动默认态/范式切换清空/运行 85.0+40.0/
  复制/明细动作/29.0 口径注/黄金 B 链路动态补入+断言/2 次点击恢复）
- pytest 269 passed；`bio-audit golden --json` diffs=[]（见 §8）
- Playwright 闭环后截图 4 状态复核（结果页/决策点/时间轴/黄金 B 链路）：
  无视觉回归、无乱码、无溢出

## 8. 工程纪律核对

- [x] **golden 0 差异**：`bio-audit golden --json` → `"diffs": []`（137 决策）
- [x] **pytest 全绿**：269 passed（104.1s）
- [x] **ruff**：demo/ 源码 0 错误（data/ 生成产物 exclude，N-a 既定）
- [x] **实时出分与 golden 一致**：20/20 轨迹全量核对（分数 + verdict 双字段
      0 差异）；黄金 B 链路 63.7 与断言基准一致
- [x] **推送纪律**：commit 仅 demo/ 工作文件（components.py / result_view.py /
      01_workshop.py / theme.css）+ 本报告 + index.md 登记；push 前三查——
      ① git status 无预期外文件 ② git log origin/main..HEAD 仅 1 commit
      ③ git ls-files demo/ 无大文件
- [x] **CI 云上绿**：见 §8.1
- [x] **零改动**：src/、tests/、ui/、demo/data/ 未触碰（git diff 确认）

### 8.1 CI 云上结果

（push 后填）

## 9. 遗留与说明（给后续子窗口）

1. **goldenb 弹层交互**：Streamlit 1.60 selectbox 弹层在 headless Chrome 下
   点击不提交（视觉验证改用状态播种临时 App 完成）；AppTest（真实 widget
   状态机）与真实浏览器主按钮/多选交互均正常——真实演示环境不受影响，
   记录备查。
2. **多选自动加入**：级联选经典轨迹自动加入对比区（≤3）；范式切换当轮
   抑制误加；若演示中需"纯浏览不加入"，可直接在对比区移除。
3. **恢复默认态语义**：恢复 = 级联/对比回默认 + 默认两条结果就绪（缓存秒级）；
   N-e 讲稿如定义不同起点，以此处语义为准微调。
4. **黄金/评测组实时重算**：若后续要求黄金对照也实时 run_audit，需 export
   脚本增补各窗口 final 轨迹决策（当前 demo/data 仅 10X-B 有重建输入）。
5. **execution-plan 打勾**：§六.十八 N-b 4-7 已勾（仓库外文档，不随仓库 push）。
6. **台账状态表**（demo-n-window-ledger.md §1）：N-b ⏳ → ✅ 由 demo 设计
   中枢验收后更新。
