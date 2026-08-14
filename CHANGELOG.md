# Changelog

## 0.1.0 — 2026-08-13（B1 阶段 1 骨架）

- 单仓库建立（替代 bio-audit / pancancer-audit / scRNA-audit / fullflow-demo 四项目）
- 引擎迁移（fullflow-demo D5 修复后 + DEG 双副本统一 + mappings 补齐为基准）
- 43 条规则 / 20 轨迹 / validation 数据 / mappings 迁入包内（哈希核对 asset_manifest）
- 路径锚定：所有资源经 `bioaudit.paths` 解析，零 cwd 依赖（F7）
- API 单一入口 `run_audit` / `audit_decision`（B3 契约细化待办）
- UI 薄壳化：只调 api，移除内联管道与演示 sleep（D7），导出 JSON 修正（D1）
- golden 回归：20 轨迹 137 决策 0 差异（`scripts/golden_replay.py` + `tests/test_golden.py`）
- 全新 git 历史（不携带旧仓 13GB 二进制）；Apache-2.0；README/CONTRIBUTING 就位
