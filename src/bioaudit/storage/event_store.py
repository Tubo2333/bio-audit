"""AuditEvent 与 EventStore（自 fullflow-demo 迁移），默认日志目录改为 cwd 无关。

迁移变更：默认 log_dir 由相对 cwd 的旧默认 logs/events 改为
``$BIOAUDIT_LOG_DIR``（环境变量覆盖）→ ``~/.bioaudit/logs/events``（F7 修复）。
显式传入 log_dir 时保持兼容。
"""

import json
import os
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

DEFAULT_LOG_DIR = Path(
    os.environ.get("BIOAUDIT_LOG_DIR", str(Path.home() / ".bioaudit" / "logs" / "events"))
)


class AuditEvent(BaseModel):
    """Immutable audit event for event sourcing."""
    schema_version: str = "1.0"  # For future migration
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    event_type: str  # "rule_matched" | "decision_scored" | "conflict_detected" |
                     # "human_overrode" | "aggregation_complete" |
                     # "propagation_traced" | "report_generated" |
                     # "parse_complete" | "error_occurred"
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    node: str
    payload: dict = Field(default_factory=dict)


class EventStore:
    """Append-only JSONL event store. One file per audit session."""

    def __init__(self, log_dir: Optional[str | Path] = None):
        self.log_dir = Path(log_dir) if log_dir else DEFAULT_LOG_DIR
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._session_id: str | None = None
        self._file_path: Path | None = None

    def start_session(self, session_id: str):
        self._session_id = session_id
        self._file_path = self.log_dir / f"{session_id}.jsonl"

    def append(self, event: AuditEvent):
        if self._file_path is None:
            raise RuntimeError("No active session. Call start_session() first.")
        try:
            with open(self._file_path, "a", encoding="utf-8") as f:
                f.write(event.model_dump_json() + "\n")
        except (OSError, IOError) as e:
            # Log but don't crash the pipeline
            import logging
            logging.error(f"EventStore write failed: {e}")

    def replay(self, session_id: str) -> list[AuditEvent]:
        file_path = self.log_dir / f"{session_id}.jsonl"
        if not file_path.exists():
            return []
        events = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        events.append(AuditEvent(**json.loads(line)))
                    except Exception:
                        continue  # Skip corrupt lines
        return events

    def list_sessions(self) -> list[str]:
        return sorted([
            f.stem for f in self.log_dir.glob("*.jsonl")
        ], reverse=True)
