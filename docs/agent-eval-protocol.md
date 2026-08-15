# Agent 真实评测协议（宪法）v1.0

> **状态**：2026-08-16 冻结（窗口 G 开工前）；冒烟结果（模型映射实测）以「修订记录」追加，不改变协议条款。
> **对应**：execution-plan-v1 §六.十（G0 执行设计 + G0.5 数据与流程优化）；benchmark-protocol.md（运行器/功效）。
> **性质**：本评测**花钱**（DeepSeek API）、**不可完全复现**（LLM 随机）、**环境风险**（hook 首次真实运行、CellVoyager 依赖首次安装）。

## 1. 评测目标与问题

1. **主问题**：真实 CellVoyager Agent（LLM 驱动）在 GSE115978 黑色素瘤 scRNA 数据上的完整分析中，会产生哪些**方法学决策**（34 类型本体视角），其质量如何（audit 分数/verdict 分布）？
2. **采集链路验证**：M1 hook（真实 NotebookSession 上）→ M3 解析（notebook 产物）→ 交叉验证（四类判定）→ verdict 状态位，是否端到端可用——闭环 C 窗口遗留（hook 从未真实运行）。
3. **对比问题**：真实 Agent 轨迹 vs benchmark 任务集（60 条）的检出/分数对比（benchmark-run 口径），如实呈现差异，**不做排名**（n=1 不具统计意义，见 §9 局限）。
4. **成本-效率问题**：一次真实 Agent 评测的 API 成本与耗时（报告必含指标）。

## 2. 对象选择与运行次数

| 项 | 值 | 依据 |
|---|---|---|
| 评测对象 | CellVoyager（`D:\C-file\scRNA-audit\CellVoyager`，只读参考，**不 fork 不改码**） | C 窗口遗留闭环 |
| 运行次数 | **1 次**（注明随机性：LLM 采样 + 时序差异，结果不可逐字节复现） | G0.1 |
| 数据集 | `D:\C-file\fullflow-demo\data\scRNA_datasets\GSE115978_raw.h5ad`（485.5MB，7186 cells，Melanoma） | G0.3；与 C 窗口样例同源 |
| 数据策略 | 全量载入；**h5ad 只读**（预检发现问题转副本到临时目录处理，绝不修改原文件） | G0.5-A1/A2 |
| 运行参数 | `num-analyses=1`、`max-iterations=5`、`--no-deepresearch`、execution-mode=claude | G0.4/G0.5-B2/C3 |
| max-iterations 依据 | 标准 scRNA 主流程 ≈ QC→归一化→HVG→PCA/UMAP→聚类→注释→DEG ≈ 5-6 步；5 次迭代覆盖主流程。**这是预算决策（成本控制），不是质量妥协**——宪法明示，报告如实声明 | G0.5-B2 |
| 模型 | DeepSeek（anthropic 兼容端点）；具体模型名**冒烟实测后回填**（§8 修订记录） | G0.4 |
| 端点 | `https://api.deepseek.com/anthropic`（ANTHROPIC_BASE_URL 环境变量注入） | 密钥纪律 |
| 执行日期 | 2026-08-16 | G0.1 |

## 3. 环境声明

- **venv 隔离**：`D:\C-file\cellvoyager-env`（独立 venv，Python 3.12）。CellVoyager 依赖栈（scanpy/anndata/h5py/pandas/litellm/claude-agent-sdk 等）只装在该 venv，**不进仓库、不污染 bio-audit 环境**（G0.2）。
- **bio-audit 接入**：`pip install -e D:\C-file\bio-audit-v2`（editable 装入 cellvoyager-env）。
- **密钥纪律（最高优先）**：`ANTHROPIC_API_KEY` / `ANTHROPIC_BASE_URL` **只通过进程环境变量注入**（运行入口脚本从父进程环境读取，脚本自身不包含、不写入任何密钥）；`DEEPSEEK_API_KEY` 同样只经环境变量注入。绝不写入任何文件（.env.cellvoyager 是占位符，不填）。
- **代理纪律**：运行前检查 `http_proxy/https_proxy/HTTP_PROXY/HTTPS_PROXY`，如有则 `unset`（DeepSeek 国内直连；旧脚本 run_cellvoyager_audit.sh 有 unset 先例）。
- **旧仓纪律**：`D:\C-file\scRNA-audit\CellVoyager\` 只读；wrapper 方案（hook attach）不 fork、不改旧仓代码。
- **采集存储**：`BIOAUDIT_WAL_DIR` / `BIOAUDIT_VERDICT_DIR` 指向 `D:\C-file\cellvoyager-outputs\data\{wal,verdicts}`（产物统一收口，默认 ~/.bioaudit 不落评测数据）。

## 4. 采集接入方式（hook 部署）

1. 运行入口脚本（`cellvoyager-outputs/scripts/run_cellvoyager_with_hook.py`）：
   - `from cellvoyager.execution.claude import NotebookSession`；
   - 包装 `NotebookSession.__init__`（monkey-patch，不动 CellVoyager 源码）：实例化后立即 `hook.attach(session)`（包装 `execute_cell` / `insert_execute_code_cell`）；
   - hook = `make_cellvoyager_hook(paradigm="scrna", session_id="cv_gse115978_...")`（session 白名单注册 + M1Reporter + WAL 崩溃恢复 + M3Parser 预解析）。
2. 方法签名若与 `_CODE_EXTRACTORS` 不匹配 → 仅需扩展 `_CODE_EXTRACTORS`（C 遗留闭环），仍不改 CellVoyager。
3. **异常隔离验证**：hook 任何异常只记日志（`n_errors` 计数），绝不影响分析继续（C1.2，F6 教训）；真实运行前在真实 NotebookSession 上再验一次。
4. 采集三通道：M1（hook 上报，WAL+verdict 落盘）→ M3（`bio-audit parse-notebook` 解析产物 notebook）→ 交叉验证（`bio-audit cross-validate`，四类判定 + verdict 联动，final-only）。

### 4.1 declared 注入（G-2 修订，2026-08-16）

- **四级可信源**：`call_arg > data_metadata > declared > unverified`（G-2a.1）；
- **declared 来源定义**：只允许来自**评测者/数据事实**——运行宪法/评测配置注入的键值
  （如数据集平台 `sequencing=smartseq2`，须附来源注记与评测者署名）；
- **与 Agent claim（M1 声明）严格区分**：Agent 上报的键**永远不进 declared**
  （那是 M1/M3 交叉验证的职责）；declared 提供键 → 该键不再 unverified；
- 注入通道：`make_cellvoyager_hook(declared=...)`（实时运行）/ `bio-audit parse-notebook --declared`、
  `bio-audit cross-validate --declared`（事后重评）；重评声明文件示例：
  `cellvoyager-outputs/reports/gse115978_declared.json`。

## 5. 报告必含指标

1. 运行环境（数据/模型/端点/日期/venv/依赖版本）；
2. **API 成本与耗时**（成本按 DeepSeek 实际定价核算，输入/输出分开；token 从 CellVoyager 日志 usage 提取；耗时按阶段记录）；
3. 分数（trajectory_score 口径、avg_score 辅助口径）与 verdict（L0-L4/-1 计数）；
4. M1/M3/交叉验证统计（n 决策、四类判定计数、verdict 状态分布）；
5. 检出 vs 任务集表现（benchmark-run 对比口径 + 局限）；
6. **诚实局限**（n=1 无统计功效、LLM 随机性、hook 首次实测、工具默认行为 vs Agent 决策的区分等）。

## 6. 诚实声明要求

- 任何失败**如实呈现**（含部分完成/失败分析），**不硬凑结果**；
- 若 CellVoyager 完全不可用（依赖装不上/端点不通）→ 退化为「用已有 notebook 产物做 M3+交叉验证演练」并在报告声明（G0.7）；
- 区分「Agent 决策」与「工具默认行为」（如 CellVoyager 内部降采样策略——若有，记录其策略）；
- 成本/耗时数字可复核（原始日志 + 换算表随报告存档）。

## 7. 停止条件（硬约束）

| 条件 | 阈值 | 动作 |
|---|---|---|
| **成本上限** | **¥5**（DeepSeek 账户扣费口径；预/后余额差 + 用量换算双核算） | 立即停止，如实报告已发生成本 |
| **超时上限** | **60 分钟**（Phase1 正式运行启动起算） | 停止进程，报告部分完成产物 |
| API 重试 | 错误重试 **1 次**（指数退避 5s/15s）；连续失败 **3 次** | 停止并如实报告（G0.5-C2） |
| hook/采集失败 | hook 挂掉 | 分析继续（隔离），报告注明采集缺口 |
| 数据异常 | h5ad 预检发现问题 | 副本修复策略（G0.5-A1），不改原文件 |

## 8. 冒烟前置（Phase 0，30 分钟内三件事全通才允许正式运行）

1. DeepSeek anthropic 端点连通 + **model 名映射实测**（1 次最小调用，候选：`deepseek-chat` / `claude-sonnet-4-6` / `deepseek-reasoner`——记录实测结果，决定 --model-name 与 --execution-model 取值）；
2. hook attach 在**真实 NotebookSession** 上验证（方法签名匹配 + n_reports>0 + n_errors==0 + 异常隔离）；
3. M3 解析器对已有 notebook（C 窗口 fixture / 旧产物）预跑。

**修订记录（冒烟后追加）**：
- 模型映射实测（2026-08-16，Phase0 冒烟①，报告 `cellvoyager-outputs/reports/phase0_smoke_endpoint.json`）：
  - anthropic 端点（`https://api.deepseek.com/anthropic`）**接受** `deepseek-chat`（纯文本回复）、`claude-sonnet-4-6`（→ 思考模式，仅 thinking block）、`deepseek-reasoner`（thinking+text）；`deepseek-chat` 为无思考开销的首选；
  - litellm（hypothesis 路径）需 provider 前缀：`deepseek/deepseek-chat`（原生 API，DEEPSEEK_API_KEY）实测 OK；
  - claude_agent_sdk（执行路径）`ClaudeAgentOptions(model="deepseek-chat")` 实测 OK（2.98s 返回 OK；Claude Code CLI 打 `unrecognized_model` 警告但正常使用该模型——如实记录）；
- 最终运行参数：`--model-name deepseek/deepseek-chat`（hypothesis，litellm 原生路径）+ `--execution-model deepseek-chat`（agent，anthropic 端点）+ 环境 `ANTHROPIC_MODEL=deepseek-chat` 兜底；冒烟总成本 < ¥0.001。
- **部署发现（真实运行 1-4 次尝试，如实记录，均计入窗口成本）**：
  1. stdout GBK 编码 → 需 `PYTHONIOENCODING=utf-8`（Windows 重定向）——运行第 1 次失败（零 token 损失）；
  2. hook 主进程 patch 无效：NotebookSession 由 **MCP server 子进程**创建执行（`python claude.py mcp-server`，Claude Code CLI 通过 `--mcp-config` 拉起）；C 窗口部署脚本 attach `agent.executor` 亦无效（claude 执行器无可包装方法）——运行第 2-3 次 M1 通道空跑（~¥1.7 损失）；
  3. 子进程环境继承不可靠 → 改为**运行时 patch `ClaudeJupyterExecutor._server_command`**，以 `python -c <引导代码>` 启动 MCP server（引导代码自带 sys.path 注入 + hook attach + `run_mcp_server()`；同一模块命名空间，避免 runpy 重复类）；验证脚本（stdio JSON-RPC + 剥离环境）证明 attach + WAL 上报全通；
  4. **hook kwargs 缺陷（C 窗口测试盲区）**：FastMCP 工具以 `session.execute_cell(index=...)` **关键字**调用，`_CODE_EXTRACTORS` 只处理位置参数 → `args[0]` IndexError 被隔离吞掉（n_errors++ 不可见）→ 运行第 4 次 M1 仍空（~¥1.7 损失）。**修复**：`cellvoyager_hook.py` 提取器支持 args+kwargs（`_extract_execute_cell`/`_extract_insert_execute`/`_extract_run_last_cell`），新增 2 项 kwargs 回归测试（test_m1_hook.py 15/15 绿）；
  5. agent 完成分析后会出现与评测无关的 "session-close 协议" 尾流（Claude Code 行为）——监控完成信号（final summary cell）即停止，不烧尾巴 token。

## 9. 局限与解读纪律（预注册）

- n=1 运行：**不做**与任务集的统计检验（功效分析对 benchmark 任务集有效，对单次真实运行无效）；
- LLM 随机性：单次结果不可复现，报告注明；
- benchmark 对比仅呈现「检出面/分数分布」的**描述性对比**，不做优劣结论；
- 若 hook 上报与 M3 解析存在差异（四类判定非一致），以事实为准逐条记录，不圆场。
