# 窗口 H 完成报告：文档站化（Site Documentation）

> **日期**：2026-08-16
> **执行依据**：execution-plan-v1 §六.十一（H1-H3 验收清单，7 项冻结）+ handoff-design-hub §四/§五/§六/§七.H
> **执行顺序**：H1（site-design 规范）→ H2（导航升级 + 目录组织 + 双语 + Release 衔接）→ H3（可访问性 + CI 回归）
> **验收状态**：7 项执行侧逐项打勾 ✅（自检通过；**审计中枢独立验收待执行**——不轻信自检是审计中枢纪律）

## 一、验收清单逐项打勾（§六.十一 H1-H3，7 项）

### H1.1 站点规范 docs/site-design.md（导航结构/目录组织/双语策略/与 Release 衔接）✅
- [x] `docs/site-design.md` v1.0 落盘：§2 站点机制（实测事实）、§3 导航结构（9 项）、§4 目录组织（分类法 +
  根级保留理由）、§5 双语策略 + Release 衔接、§6 链接规范 + 数字口径纪律（教训 #2）、§7 可访问性与构建纪律、
  §8 维护流程（教训 #4 git 纪律）。**先定规范再动手**：本文件先于一切站点改动编写。

### H2.2 Pages 导航升级（README / 快速开始 / API 契约 / 规则贡献 / 设计文档 / 窗口报告）✅
- [x] 自定义 `_layouts/default.html`（仓库根，**Pages 相关文件**）：覆盖 cayman 主题默认 layout，
  `jekyll-default-layout` 使全站页面（含无 front matter 旧文档）自动套用 → 导航 9 项全覆盖：
  首页 / README / 快速开始 / API 契约 / 规则贡献 / 设计文档 / 窗口报告 / Release / English；
  `aria-label` + 内联样式（对比度达标），不新增 CSS 资产
- [x] `_config.yml`：`lang: zh-CN`、`github_repo`、`exclude`（src/tests/scripts/mcp/ui 代码目录不进 Pages）
- [x] 实测事实驱动设计：README.md / CONTRIBUTING.md 被 GitHub Pages 跳过不转 `.html`（实测 404，
  社区讨论 #30162 同题）→ 导航中这两项指向 GitHub 仓库渲染视图（避免裸 `.md` 目标）

### H2.3 docs/ 目录组织（散报告归入 docs/{specs,migration,environment,protocols}）✅
- [x] `docs/migration/`：agent-eval-report.md / agent-eval-report-g2.md 迁入（窗口报告），现有 11 份报告不动；
  新增 `index.md`（13 份报告索引）
- [x] `docs/protocols/`（新建）：agent-eval-protocol.md + benchmark-protocol.md 迁入（宪法协议）
- [x] `docs/environment/`（新建）：github-pages.md（Pages 部署与维护说明）
- [x] `docs/specs/`（新建）：index.md（仓库内规范索引 + 与外部审计内存的区别声明）
- [x] `docs/index.md`（新建）：文档中心首页
- [x] **根级保留决策**（site-design §4 记录）：api-contract / mcp-contract / reward-mapping / reward-protocol
  为一级文档固定根级——`tests/test_mcp.py:216` 断言 docs/mcp-contract.md 存在 + src 各包 docstring 锚定
  这些路径，移动会造成失效引用且窗口纪律禁止改 src
- [x] **全库引用更新**（注意事项 #3）：repo 内 CHANGELOG（3 处）/ CONTRIBUTING（2 处）/ D3、F1 完成报告（3 处）/
  agent-eval 报告内部互引（8 处）全部更新；仓库外审计内存 execution-plan-v1（9 处）+ handoff-design-hub（文档树）
  同步更新；本地链接预检 27 个文件全 OK（相对 .html 目标存在）

### H2.4 核心文档中英双语（README + 快速开始，H11 裁决）✅
- [x] README：`README.md`（中文主版，v0.2.x 现状重写）+ `README.en.md`（完整英文版），互相提供切换入口
- [x] 快速开始：`docs/quickstart.md`（中文）+ `docs/quickstart.en.md`（English）
- [x] 双语范围克制（注意事项 #5）：其余文档不翻译，策略写进 site-design §5.1 决策记录

### H2.5 与 Release 页面衔接（release notes 引用文档链接）✅
- [x] `CHANGELOG.md`：新增 0.2.1 条目（G-2 漏记，补齐）+ 文档站化条目，均引用文档路径；
  既有条目 benchmark-protocol 路径更新
- [x] GitHub Release v0.2.0 body 更新：文档区改为文档站链接（quickstart zh/en / G-2 报告 / API·MCP 契约 /
  窗口报告索引 / CHANGELOG），并加 G-2/H 状态更新块
- [x] 站点导航含 Release 项（→ github.com/Tubo2333/bio-audit/releases）

### H3.6 站点可访问（构建成功 + HTTP 200 + 导航可达、链接无 404）✅（见 §二 云上验证）
- [x] Pages 构建成功（pages-build-deployment，legacy build，source main/root）
- [x] 首页 + 导航 9 项 + 文档索引页 HTTP 200；站点内链接爬取无 404
- [x] 数字口径分离实测：首页"当前状态"卡区分 demo 轨迹 29 分 5 L0 与 G-2 真实运行 30.0（L1×7/L3×1/L-1×12），
  全文无混写（教训 #2 单一事实源）

### H3.7 仓库 CI 仍绿（golden 0 差异硬验收 + 双矩阵全绿）✅（见 §二 云上验证）
- [x] 本地复现：pytest **234/234** · golden **20 轨迹 137 决策 0 差异** · ruff **41→40 零新增**
  （仅 G-2 遗留 minor 消除）
- [x] 云上：CI 双矩阵（3.10/3.12）全绿（见 §二）

## 二、验证证据

### 本地（2026-08-16 执行侧）
| 检查 | 结果 |
|---|---|
| `python -m pytest -q` | **234 passed** |
| `bio-audit golden --json` | **diffs: []（0 差异）**，基线 golden_expected_output_after.json |
| `python -m ruff check src tests scripts` | **40 errors（基线 41，仅 __init__.py:8 消除，零新增）** |
| 相对链接预检 | 27 个 md 文件全部 OK |
| Liquid 风险字符扫描 | docs/ 全量 0 命中（唯一命中为我方 github-pages.md 排障表示例，已改写规避） |

### 云上（2026-08-16，push 572cfb6）
| 检查 | 结果 |
|---|---|
| CI run 31893468210（双矩阵） | **pytest+golden (Python 3.10): success** · **(Python 3.12): success**（含 golden 步骤） |
| pages-build-deployment run 31893467583 | **success**（headSha 572cfb6；deployment id 5921994696 / environment github-pages） |
| 首页 + 导航实测 | 首页 200；导航 9 项渲染确认（首页 / README / 快速开始 / API 契约 / 规则贡献 / 设计文档 / 窗口报告 / Release / English） |
| 文档索引页 | /docs/ · /docs/specs/ · /docs/migration/ · quickstart zh/en · site-design · api/mcp-contract · reward-mapping/protocol · protocols ×2 · environment/github-pages · CHANGELOG · README.en.html **全部 HTTP 200** |
| 全站链接爬取 | **23 个唯一 URL，0 死链**（排除 HTML 注释后；favicon.ico 为 cayman head-custom 注释占位符，非真实链接） |
| README.en.md 转换 | 实测 `/README.en.html` → **200 text/html**（GitHub Pages 仅跳过精确文件名 README.md，README.en 正常转换） |
| 旧 URL | /docs/agent-eval-report*.html 等旧路径 404（预期；引用已全库更新，含仓库外审计内存） |

## 三、改动清单

| 类别 | 文件 |
|---|---|
| 新增（站点机制） | `_layouts/default.html` |
| 修改（配置） | `_config.yml`（lang / github_repo / exclude） |
| 新增（规范与入门） | `docs/site-design.md`、`docs/quickstart.md`、`docs/quickstart.en.md`、`docs/index.md` |
| 新增（目录组织） | `docs/specs/index.md`、`docs/migration/index.md`、`docs/environment/github-pages.md` |
| 移动（git mv 保历史） | `docs/agent-eval-report.md`→`docs/migration/`、`docs/agent-eval-report-g2.md`→`docs/migration/`、`docs/agent-eval-protocol.md`→`docs/protocols/`、`docs/benchmark-protocol.md`→`docs/protocols/` |
| 修改（双语与首页） | `README.md`（重写）、`README.en.md`（新增）、`index.md`（重写，口径分离） |
| 修改（引用更新） | `CHANGELOG.md`（0.2.1 条目 + 路径）、`CONTRIBUTING.md`（路径）、`docs/migration/{D3,F1,agent-eval-report,agent-eval-report-g2}.md`（路径） |
| 唯一代码改动（G-2 minor） | `src/bioaudit/__init__.py:8` ruff E501（注释独立成行，`__version__` 值不变） |
| 外部（不进仓库） | execution-plan-v1 §五/§六.十一 完成标记 + 路径引用；handoff-design-hub §二/§三/§七；v0.2.0 Release body |

## 四、未触碰项（注意事项逐条）

- 评分路径零改动：engine/rules/ruleset/ontology/tasks 全未动；golden 0 差异
- 冻结资产（tests/golden、src/bioaudit/data）未动；asset_manifest 未重算
- 外部 docs/specs 只改文本引用，不动路径结构
- index.md 图片路径 assets/01_landing.png 等保持有效，无仓库外资源
- 首页/README 中 CellVoyager 分数全部标注口径（demo 29 分 5 L0 ≠ G-2 真实 30.0，禁止混写）

## 五、遗留与声明

- 审计中枢独立验收待执行（H3.6/H3.7 云上实测证据见 §二，全部通过）
- 可选后续（不阻塞）：v0.2.1 GitHub Release 未创建（CHANGELOG 已记录；发不发由审计中枢裁决）
- favicon.ico：cayman head-custom 模板内为**注释占位符**（非真实链接），站点无 favicon 文件，浏览器按惯例忽略——未新增资产（遵守改动范围纪律）
