# 窗口 C 完成报告：阶段 2 采集 lint（M1/M3 交叉验证 + verdict 状态位 + MCP）

> **日期**：2026-08-15
> **执行依据**：docs/specs/2026-08-13-execution-plan-v1.md §六.六（C1-C6 验收清单，19 项冻结）
> + trajectory-capture-design-v1（定稿）+ refactor-plan-v1.1（B3-B5）
> **验收结果**：**C1-C6 全部 19 项 ✅**；golden **20 轨迹 137 决策 0 差异**；pytest **148/148**（原 86 + 新增 62）

---

## 一、执行顺序与范围

按方案建议顺序执行：**C2（M3 解析器）→ C3（交叉验证）→ C1（M1 hook）→ C4（MCP）→ C5（可观测）→ C6（回归）**。
采集层全部为**外围层**：未改动任何评分路径（evaluator/matcher/aggregator/error_tracer/rule_registry/评分模型均未动），golden 0 差异为硬验收。

## 二、产出清单

### C2 M3 产物解析器
| 文件 | 说明 |
|------|------|
| `src/bioaudit/capture/models.py` | CapturedDecision / DecisionProvenance / UncertainCandidate / ParseResult；三级可信源常量 + 禁猜规则注释 |
| `src/bioaudit/capture/signatures.yaml` | **34 类型签名表**（23 个有确定性签名；11 个纯上下文/一致性类型如实声明待补） |
| `src/bioaudit/capture/signatures.py` | SignatureTable 加载/校验（类型∈本体、模式编译、choice 方式互斥） |
| `src/bioaudit/capture/m3_parser.py` | M3Parser（signatures 驱动 + 三级可信源 + unverified + provenance + LLM 提名校验） |

### C3 交叉验证器 + verdict 状态位
| 文件 | 说明 |
|------|------|
| `src/bioaudit/capture/verdict.py` | VerdictStatus（provisional/final/revoked）+ 转换表 + VerdictStore（JSONL 持久化） |
| `src/bioaudit/capture/cross_validator.py` | 四类判定 + 对齐键 + 多实例建模 + 漏报自动补入 + `final_trajectory`（final-only） |

### C1 M1 主动上报（CellVoyager hook）
| 文件 | 说明 |
|------|------|
| `src/bioaudit/capture/session.py` | SessionWhitelist（env 白名单 + 程序化注册） |
| `src/bioaudit/capture/wal.py` | WAL 追加持久化 + 崩溃恢复（intent/result + interrupted 检测） |
| `src/bioaudit/capture/m1_reporter.py` | M1Reporter（幂等键 + WAL + audit_decision 契约 + verdict provisional + 异常隔离） |
| `src/bioaudit/capture/cellvoyager_hook.py` | CellVoyagerM1Hook（wrapper 优先，不 fork；run_last_cell/execute_cell/insert_execute_code_cell 前后钩子；NullM1Hook） |
| `scripts/run_cellvoyager_capture.py` | 部署入口（缺 CellVoyager 优雅降级，明确报错不半吊子运行） |

### C4 MCP server
| 文件 | 说明 |
|------|------|
| `mcp/server.py` | 最小 stdio JSON-RPC 2.0 MCP server（协议 2024-11-05；零额外依赖）；tools = audit_decision / audit_trajectory / report |
| `docs/mcp-contract.md` | MCP 契约文档（工具说明 + 请求/响应示例 + 错误码映射 + 握手） |

### C5 可观测性
| 文件 | 说明 |
|------|------|
| `src/bioaudit/storage/event_store.py` | **append 失败 → EventWriteError（不再静默丢写，F11）** + write_failures/health() + H12 日志轮转（容量上限 + 分片 + 重放不丢） |
| `src/bioaudit/capture/engine_trace.py` | trace_session / session_summary / render_trace（审计者也可审计） |
| `src/bioaudit/api/audit.py` | `_append_event` 显式告警进 state/report；audit_decision 可选 session_id 事件记录 |

### C6 回归
- 测试：`tests/test_m3_parser.py`（14）/ `test_cross_validator.py`（12）/ `test_m1_hook.py`（13）/ `test_mcp.py`（13）/ `test_event_store.py`（9）+ `tests/fixtures/sample_scrna_notebook.ipynb`
- CLI 子命令：`parse-notebook` / `cross-validate` / `trace` / `capture-validate` / `verdict`
- CI：`.github/workflows/ci.yml` 双矩阵新增「采集层自检」「MCP server 自检」步骤（pytest 已含全部采集测试）

## 三、验收对照（§六.六 C1-C6，19 项逐项）

### C1 M1 主动上报（CellVoyager hook）
- [x] **1. hook 注入方式明确 + 工具调用前后 + payload 全要素**：wrapper 优先**不 fork**（cellvoyager_hook.py 只做方法包装，零 import CellVoyager；wrapper 方法即 `attach()`）；hook 点覆盖 `run_last_cell`（legacy）/`execute_cell`/`insert_execute_code_cell`（claude executor）**调用前**（signatures 预解析上报）与**调用后**（step_completed/step_failed）；payload 含 decision_type/choice/context/provenance（测试 `test_hook_wraps_executor_before_after` 逐字段断言）
- [x] **2. 异常隔离**：hook/reporter 任何异常只记日志（`n_errors` 隔离计数），**绝不影响 CellVoyager 分析继续**；测试 `test_hook_exception_does_not_break_analysis`（audit_fn 抛异常 → 分析照常完成）+ `test_hook_before_raising_extractor_isolated` + attach 失败不抛
- [x] **3. 会话与幂等**：SessionWhitelist（env `BIOAUDIT_SESSION_WHITELIST` + register() 程序化注册），不在白名单显式拒绝；幂等键 = sha256(session+step+type+choice+context)，同一步重复上报去重返回既有 verdict；WAL 追加持久化 + `start()` 崩溃恢复预载去重（测试 5 项覆盖）
- [x] **4. M1 决策走通 audit_decision 契约**：M1Reporter 调 `audit_decision(decision, paradigm=必填)`（B2 消歧）→ 即时 verdict（provisional + DecisionScore 快照）；测试断言真实引擎评分（bulk DESeq2 → L3）

### C2 M3 产物解析器
- [x] **5. signatures 驱动**：`capture/signatures.yaml` 34 类型映射表（23 个含确定性签名，覆盖 scRNA 主线 + bulk/pan 主要调用）；`capture-validate` 校验类型 ∈ 本体 34 类型 + 模式编译 + choice 方式互斥；fixture notebook 解析产出 8 候选 + 3 未定
- [x] **6. 上下文三级可信源**：调用参数（call_arg）> 数据元数据（data_metadata）> 环境声明（declared）；任一级缺失 → 键标 **unverified**（`unverified_keys`），**绝不正则猜数字**——测试 `test_missing_context_marked_unverified_not_fabricated` / `test_no_fabricated_patient_cell_counts`（"11 patients" 注释不产生 11）
- [x] **7. provenance 逐决策记录**：{来源: M3解析, 时间戳, 证据: notebook cell #N + 工具 + pattern}，detail 含 cell_index/pos/signature_tool
- [x] **8. 旧缺陷不复现**（测试逐条守卫）：① UMAP≠PCA（`sc.tl.umap` 不再映射 choice="PCA"，进 uncertain 并注明"UMAP 投影≠聚类降维"）；② 分辨率数值不当方法名（resolution 数值进 context、choice 走规则词表 `default_0_8`，词表外 → uncertain）；③ 不伪造 n_patients/n_cells（旧默认 11/50000 已绝迹）

### C3 交叉验证器
- [x] **9. 四类判定**：一致 / 虚报（声明未执行：无证据 / 仅未定证据 / choice 不符）/ 漏报（执行未声明 → **自动补入** added_decisions + final verdict）/ 未验证（预期决策点双方都无，不伪造）；stats 四类计数
- [x] **10. verdict 状态位**：provisional → final / revoked 生命周期（转换表单一事实源，非法转换抛 VerdictTransitionError）；**报告与 reward 只消费 final**（`final_trajectory` 过滤 + MCP report 工具 final-only 视图；虚报后分数被推翻——测试 `test_report_reward_consume_final_only`）
- [x] **11. M1/M3 对齐**：按 decision_type 对齐（step_id 辅助）+ **同类型多实例建模**（instance_index 按执行位置编号；operative=最后实例；声明命中被取代实例 → 一致+标注；未命中 → 虚报）+ 参数级粒度对照（min_genes 200 vs 500 差异可见）

### C4 MCP server
- [x] **12. MCP server 实现**：tools = `audit_decision`（paradigm **必填** + 错误码复用 errors.py，含 `paradigm-not-found` 映射 JSON-RPC -32602）/ `audit_trajectory` / `report`（session 必填）
- [x] **13. 部署形态**：`mcp/` 目录独立启动（`python -m mcp.server`，测试验证子进程）+ `--selfcheck` CI 冒烟；契约文档 `docs/mcp-contract.md`（工具说明 + 示例 + 握手 + 错误码）
- [x] **14. 端到端**：MCP 调 audit_decision → 引擎 → 返回 DecisionScore（level 3 + matched_rules + evidence_citations + alternatives）；带 session_id 走 M1 通道（白名单拒绝 → validation-error 显式）

### C5 可观测性
- [x] **15. 事件写入失败显式告警**：append 失败 → **EventWriteError**（不再静默丢写）+ write_failures/last_write_error/health()；run_audit 捕获后写入 `state["event_store_warnings"]` + report（测试断言管道不崩、评分照常、告警可见）；audit_decision 失败在 explanation 标注
- [x] **16. 引擎 trace**：run_audit 全程 7 步管道事件（parse→match→evaluate→conflict→aggregate→trace→report）+ audit_decision(session_id=...) 单决策事件；`bio-audit trace <session>` 输出审计过程日志（审计者也可审计）；H12 日志轮转（容量上限 + 分片重放不丢 + 保留窗口裁剪）

### C6 回归
- [x] **17. golden 0 差异**：`bio-audit golden` → **20 轨迹 137 决策 0 差异**（采集为外围层，评分路径零改动；基线未更新）
- [x] **18. 测试全量绿 + 新增测试**：pytest **148/148**（86 → 148，新增 62 项：M3 解析 14 / 交叉验证 12 / M1 hook 13 / MCP 13 / 可观测 9 + fixture）；含幂等去重、崩溃恢复、异常隔离、轮转等
- [x] **19. CI 步骤更新**：双矩阵新增「采集层自检」（`bio-audit capture-validate --notebook tests/fixtures/sample_scrna_notebook.ipynb`）+「MCP server 自检」（`python -m mcp.server --selfcheck`）；采集测试经 pytest 全量纳入双矩阵

## 四、回归证据

```
golden:   ok=True | n_diffs=0 | trajectories=20 | decisions=137
pytest:   148 passed
ruff:     新代码零错误（src/bioaudit/capture、mcp/、新测试）
MCP:      python -m mcp.server --selfcheck → PASS
CLI:      parse-notebook（8 候选/3 未定）/ cross-validate（1 一致/1 虚报/7 漏报/1 未验证）
          / trace（14 事件 7 节点）/ verdict（provisional/final/revoked 计数）端到端验证通过
```

## 五、遗留项（如实声明）

1. **CellVoyager 真实运行未实测**：本机未安装 CellVoyager 依赖（openai/h5py/anndata），
   `scripts/run_cellvoyager_capture.py` 已验证**优雅降级路径**（缺包明确报错，exit 1）；
   hook 逻辑经 FakeExecutor 等价测试覆盖（方法签名与 IdeaExecutor/ClaudeJupyterExecutor 对齐）。
   接入真实 CellVoyager 时若执行器方法签名有出入，仅需扩展 `_CODE_EXTRACTORS`。
2. **M2 调用旁路**未实现（设计定稿：可选增强，不阻塞）。
3. **34 类型中 11 个纯上下文/一致性类型无确定性签名**（events_per_variable、ic50_sample_size、
   independent_prognostic_claim、purity_confounding、一致性族等）——签名表已逐类注明"待声明回填"，
   capture-validate 统计 23/34 有签名；这些类型的决策由 M1 声明 + LLM 提名（过本体校验）承担，
   符合"宁可 unverified 不伪造"。
4. **H12 归档周期**（冷备/归档到外部存储）未做——轮转与保留上限已落地，归档留给运维窗口。
5. **verdict revoked 为终态**（无 re-finalize）：重新定案需人工重建记录（设计如此，文档已注明）。
6. docs/specs/2026-08-14-fix-tracking.md 未新增条目（窗口 C 不在 78 条 audit-report 基线内）。

## 六、关键设计决策记录

| 决策 | 依据 |
|------|------|
| signatures 放 capture 映射表而非本体 decision_types | C2.5 允许"capture 映射表"；零触碰本体文件 → golden 风险最低 |
| verdict/score_snapshot 冻结在采集层，不改 DecisionScore 模型 | golden 逐字段 diff 守卫（模型新增字段会进 model_dump） |
| MCP 用最小 stdio JSON-RPC 实现（零额外依赖） | pyproject 核心依赖只有 pydantic+pyyaml；H8 依赖锁定不扩 |
| EventStore.append 改为抛出 EventWriteError + 管道捕获告警 | C5.15"不再静默丢写"且不拖垮审计（F6 精神） |
| 对齐键 = decision_type 主键 + step_id 辅助 + instance_index 多实例 | B5 定义；文档在 cross_validator docstring |
| 漏报补入 verdict 直接 final（M3 事实证据链） | 与"provisional→final/revoked"生命周期共存：事实驱动终态 |
