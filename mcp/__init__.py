"""MCP server 骨架（阶段 2 落地；refactor-plan-v1.1 B1/B3：MCP 工具契约）。

B1 现状：仅占位。阶段 2 将在此暴露工具：
- run_audit（轨迹 → 审计报告，含 verdict 状态位 provisional/final，B4）
- audit_decision（单决策，必填 paradigm 参数，B2）
- reward（阶段 4）

协议实现（FastMCP / mcp python SDK）在阶段 2 选定并落地。
"""

MCP_VERSION = "0.0.0"

__all__ = ["MCP_VERSION"]
