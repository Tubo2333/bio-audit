"""API 单一入口包（v1 蓝图：run_audit / audit_decision / reward；B3 契约完成）。

B3（2026-08-14）：输入 pydantic 校验 + 错误码体系 + audit_decision 必填 paradigm +
human_overrides -1..4 校验；契约文档 docs/api-contract.md。
"""

from bioaudit.api.audit import audit_decision, match_details, run_audit
from bioaudit.errors import BioAuditError, ErrorCode

__all__ = ["run_audit", "audit_decision", "match_details", "BioAuditError", "ErrorCode"]
