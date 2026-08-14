# B3 完成报告（阶段 1 · API 契约）— 2026-08-14

> 执行窗口 ⑥（窗口 B 内）· B3：三入口 pydantic 校验 + 错误码体系 + audit_decision
> 必填 paradigm + human_overrides 范围校验 + 契约文档 + 契约测试。
> 依据：refactor-plan-v1.1 B1/B2、audit-report A5/A7/A15、execution-plan-v1 §六.五（B3 清单，已冻结）。
> 验收：**B3 验收清单 7 项全部通过**（见下逐项打勾）；golden 回归 0 差异。

## 一、产出清单

```
src/bioaudit/errors.py                 # ★ 错误码体系（5 码 + BioAuditError + pydantic 归一化）
src/bioaudit/api/contract.py           # ★ 请求 schema 与校验（TrajectoryPayload /
                                       #   AuditDecisionRequest / validate_human_overrides /
                                       #   validate_paradigm）
src/bioaudit/api/audit.py              # ★ 三入口改造（校验前置 + error_code + rule-not-found）
src/bioaudit/api/__init__.py           # 再导出 BioAuditError / ErrorCode
src/bioaudit/models/decision.py        # Decision extra="forbid"（A15：未知字段显式报错）
src/bioaudit/models/trajectory.py      # v2 schema + validate_trajectory（B4 共用，见 B4 报告）
src/bioaudit/report/schema.py          # schema 常量再导出（B4 验收项 1）
src/bioaudit/storage/event_store.py    # log_dir 初始化时读 BIOAUDIT_LOG_DIR（事件可测/可重定向）
src/bioaudit/cli.py                    # audit-decision --act 必填；错误码 JSON 输出；stdout UTF-8
ui/pages/02_audit.py                   # BioAuditError 显式展示（错误码）
docs/api-contract.md                   # ★ 契约文档（三入口 schema + 错误码 + 示例）
tests/test_api_contract.py             # ★ 契约测试（非法输入/错误码/paradigm 消歧/事件/守卫）
tests/test_engine.py                   # audit_decision 调用改为 paradigm= 关键字
```

## 二、B3 验收清单逐项打勾（execution-plan-v1 §六.五）

- [x] **1. run_audit / audit_decision 输入全部 pydantic schema 校验，非法输入显式报错（错误码），不静默降级**（v1.1 B1；audit-report A5/A15）
      → `TrajectoryPayload`/`AuditDecisionRequest`/`Decision(extra="forbid")`；测试：
      `test_run_audit_missing_required_field_validation_error`、
      `test_run_audit_typo_field_not_silently_ignored`（decisionType 拼错 → validation-error）、
      `test_run_audit_bad_request_payload`、`test_audit_decision_invalid_decision`。
- [x] **2. audit_decision 契约必填 paradigm（act）参数——deg_method 同名异构消歧**（v1.1 B2）
      → 签名 `audit_decision(decision, paradigm: str, ...)`（无默认，缺参 TypeError）；
      非法值 → `paradigm-not-found`；消歧测试 `test_paradigm_disambiguation_same_choice_different_scores`
      （deg_method/DESeq2：deg → L3（M1.1-DEG-001）；scrna → L0（要求 pseudobulk 形式））。
- [x] **3. human_overrides 校验：int 且 -1..4 范围，非法拒绝并记录事件**（v1.1 A7）
      → `validate_human_overrides`：非 int（含 bool/float/str）或越界（-2/5）→ validation-error；
      EventStore 记录 `invalid_override_rejected` 事件（测试
      `test_human_overrides_invalid_records_event` 用重定向 log_dir 验证事件落盘）；
      合法 override 照常应用（`test_human_overrides_valid_range_applies`）。
- [x] **4. 错误码体系：定义并文档化，异常不裸抛**
      → `bioaudit.errors`：`bad-request` / `validation-error` / `paradigm-not-found` /
      `rule-not-found` / `internal-error`（+HTTP 映射）；`test_error_code_set_documented` 守卫
      文档集合 == 代码集合；run_audit 管道内部失败写 `state["error_code"]`，
      match 规则缺失 → `rule-not-found`（不再静默丢弃）。
- [x] **5. 契约文档写入 docs/api-contract.md：三入口请求/响应 schema + 错误码 + 示例**
      → `bio-audit-v2/docs/api-contract.md`（§二错误码表 / §三-五三入口 schema 与示例 /
      §六 human_overrides / §七轨迹 v2 摘要 / §八行为变更清单）。
- [x] **6. 契约测试（pytest）：非法输入、错误码、paradigm 消歧（同 choice 不同范式不同评分）各 ≥1 例**
      → `tests/test_api_contract.py` 24 项：非法输入 6 例、错误码 2 例（含守卫）、
      paradigm 消歧 1 例（assert 两范式 level 不同）、human_overrides 5 例（含事件落盘）、
      match_details 3 例、v2 兼容 1 例。
- [x] **7. 回归：golden_replay 仍 0 差异**
      → `python scripts/golden_replay.py`：✅ 0 差异（20 轨迹 137 决策）；
      pytest 全量 75/75 通过（38 基线 + 37 新增）。

## 三、验证记录

| 验证 | 结果 |
|------|------|
| `python scripts/golden_replay.py` | ✅ 0 差异（20 轨迹 137 决策） |
| `python -m pytest -q` | ✅ 75 passed（含新增 37 项） |
| `python scripts/check_no_cwd_paths.py` | ✅ 未发现相对 cwd 路径 |
| CLI `bio-audit audit-decision --act` 必填 | ✅ 缺参 argparse 报错；错误 JSON 含 code |
| CLI `bio-audit run` 非法输入 | ✅ 输出 `{"error": {"code": ...}}`，退出码 1 |

## 四、遗留项

- `rule-not-found` 为防御性路径（当前 matched_rules 恒来自同一 registry，无法自然触发）；
  契约测试未覆盖该码的实际触发，保留在错误码体系中供未来 registry 场景使用。
- reward 入口（refactor-plan-v1.1 B1 提到三 API 含 reward）按蓝图属阶段 4，本窗口未实现。
