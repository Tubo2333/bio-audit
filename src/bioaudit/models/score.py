"""Score 与聚合分数模型（自 fullflow-demo 迁移，未改动）。"""

from pydantic import BaseModel, Field


class DecisionScore(BaseModel):
    """Score for a single decision."""
    step_id: str
    decision_type: str
    agent_choice: str
    agent_rationale: str
    matched_rules: list[str] = Field(default_factory=list)
    level: int  # -1 (unevaluable), 0 (dangerous), 1 (risky), 2 (acceptable), 3 (correct), 4 (exemplary)
    numeric_score: float  # 0.0–1.0
    explanation: str
    evidence_citations: list[str] = Field(default_factory=list)
    alternatives: list[str] = Field(default_factory=list)
    reward_signal: float  # EXPERIMENTAL — not calibrated for RLHF training


class AggregatedScore(BaseModel):
    """Aggregated trajectory-level score."""
    step_scores: list[DecisionScore] = Field(default_factory=list)
    dimension_scores: dict[str, float] = Field(default_factory=dict)
    trajectory_score: float = 0.0
    critical_issues: list[str] = Field(default_factory=list)
    verdict: str = "pass"  # "pass" | "needs_correction" | "blocked"


class ErrorChain(BaseModel):
    """Error propagation chain."""
    source_step: str
    source_error: str
    affected_steps: list[str] = Field(default_factory=list)
    propagation_path: str = ""
    severity: str = "minor"  # "critical" | "major" | "minor"
