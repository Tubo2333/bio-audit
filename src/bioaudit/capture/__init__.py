"""采集包（阶段 2 落地，当前为骨架占位）。

设计依据：docs/specs/2026-08-13-trajectory-capture-design-v1.md + refactor-plan-v1.1
（B3/B4/B5：M1 主动上报 + M3 产物解析交叉验证；verdict 状态位 provisional/final/revoked；
session_id 白名单 + 幂等键 + WAL；G3 unit / G4 confound / G5 适用性谓词）。

阶段 2 待落地：
- M1 CellVoyager hook（注入 agent 工作流）
- M3 解析器（signatures + provenance，修复 F6 伪造注入）
- 交叉验证器（一致/虚报/漏报/未验证 四类判定，F4 进报告不进 reward）
- MCP server（mcp/ 目录）
"""

CAPTURE_VERSION = "0.0.0"
