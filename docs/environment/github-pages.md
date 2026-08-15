# GitHub Pages 部署与站点维护说明

> 本文件记录文档站的**构建机制 / 导航实现 / 发布流程 / 排障**（2026-08-16 窗口 H 实测）。

## 1. 构建机制（实测事实）

- 站点：https://tubo2333.github.io/bio-audit/（项目站，subpath `/bio-audit/`，https 强制）。
- 部署形态：**legacy build type**，Pages source = `main` 分支 / 根目录（`gh api repos/Tubo2333/bio-audit/pages`
  可见 `build_type: legacy, source: {branch: main, path: /}`）。
- 触发：push 到 main 后 GitHub Actions **自动**出现 `pages-build-deployment`，构建 + 发布一体；
  **无需**提交 `_site/` 或手动 workflow。
- Jekyll 插件（GitHub Pages 默认启用，实测行为）：
  - `jekyll-optional-front-matter`：无 front matter 的 `.md` 也转 `.html`；
  - `jekyll-default-layout`：所有页面自动套用 `_layouts/default.html`（仓库内存在时覆盖主题 layout）；
  - 主题：`jekyll-theme-cayman`（_config.yml 声明）。
- **特例**：`README.md` 与 `CONTRIBUTING.md` 不转 `.html`（GitHub Pages 行为）——
  导航中这两项指向 GitHub 仓库渲染视图（site-design.md §2）。

## 2. 导航实现

- 自定义 `_layouts/default.html`（仓库根）：在 cayman page-header 内注入 `nav.site-nav`（9 项导航，
  `aria-label="主导航"`），样式内联；`jekyll-default-layout` 使其覆盖全站页面，无需逐文件加 front matter。
- `_config.yml` 关键项：`lang`（zh-CN）、`github_repo`（导航外部链接基址）、`exclude`（src/tests/scripts/mcp/ui
  代码目录不进站点——冻结资产不进 Pages）。

## 3. 发布流程（改文档 → 上线）

1. 本地改文档（遵守 site-design.md：链接规范 + 数字口径纪律）；
2. `git commit` + `git push`（教训 #4：不 push 等于没做；GitHub 通道见仓库外 environment/github-channel.md）；
3. 等 `pages-build-deployment` 完成：
   `gh api repos/Tubo2333/bio-audit/pages/builds/latest` 看 status（`built` / `errored`）；
4. 实测（教训 #5：本地绿不算数，部署后必须实测）：
   - 首页 + 导航 9 项 HTTP 200；
   - 文档索引页（/docs/、/docs/specs/、/docs/migration/）可达；
   - 站点内链接爬取无 404（有自动化检查脚本则用，无则逐链接 HEAD）。

## 4. 排障速查

| 症状 | 排查 |
|---|---|
| 构建 errored | GitHub Actions → pages-build-deployment 日志（Jekyll 构建错误，常见：Liquid 模板语法错误（双花括号/百分号花括号）、无效 YAML） |
| 页面 404 | 文件名大小写（站点 URL 大小写敏感）；README/CONTRIBUTING 不转 HTML（走 GitHub 链接）；移动文件后旧链接未更新 |
| 导航未出现 | _layouts/default.html 是否在仓库根；构建缓存（重推一次触发） |

## 5. 冻结资产声明

`tests/golden/`、`src/bioaudit/data/` 等冻结资产**不参与站点**（_config.yml exclude），
不在站点构建/发布路径上；asset_manifest 不因站点改动重算。
