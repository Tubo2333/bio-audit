"""Decision 与 ParsedStep 数据模型（自 fullflow-demo 迁移，未改动）。"""

from pydantic import BaseModel, Field
from typing import Optional


class Decision(BaseModel):
    """A single decision made by an AI Agent during bioinformatics analysis."""
    step_id: str
    decision_type: str  # e.g. "deg_method", "normalization"
    choice: str         # e.g. "DESeq2", "TMM"
    rationale: str = ""  # Agent's stated reason
    context: dict = Field(default_factory=dict)
    tool_call: Optional[str] = None
    code_snippet: Optional[str] = None


class ParsedStep(BaseModel):
    """Normalized step after parsing."""
    step_id: str
    original: Decision
    decision_type: str
    normalized_context: dict
