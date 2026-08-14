"""ErrorPropagationTracer — 自 fullflow-demo 迁移（含 B8 修正），依赖图路径改为包内锚定。

迁移变更（F7 修复）：默认依赖图由相对 cwd 的旧默认 data/mappings/dependency_graph.yaml
改为 bioaudit.paths.MAPPINGS_DIR / "dependency_graph.yaml"；构造参数保持兼容。
"""

import yaml
from pathlib import Path

from bioaudit.models.score import DecisionScore, ErrorChain
from bioaudit.paths import MAPPINGS_DIR


class ErrorPropagationTracer:
    """Traces how errors propagate through a decision pipeline.

    B8 FIX: Dependency graph loaded from YAML, not hardcoded.
    """

    def __init__(self, dep_graph_path: Path | str | None = None):
        self.dep_graph = self._load_graph(
            Path(dep_graph_path) if dep_graph_path
            else MAPPINGS_DIR / "dependency_graph.yaml"
        )

    def _load_graph(self, path: Path) -> dict:
        try:
            with open(path, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return {}

    def trace(self, step_scores: list[DecisionScore]) -> list[ErrorChain]:
        """Find low-score steps and trace their downstream impact."""
        error_chains = []

        low_score_steps = {
            s.step_id: s for s in step_scores if 0 <= s.level <= 1
        }

        for step_id, score in low_score_steps.items():
            affected = []
            for other in step_scores:
                if other.step_id == step_id:
                    continue
                deps = self.dep_graph.get(other.decision_type, [])
                if score.decision_type in deps:
                    affected.append(other.step_id)

            if affected:
                error_chains.append(ErrorChain(
                    source_step=step_id,
                    source_error=f"{score.agent_choice} — {score.explanation}",
                    affected_steps=affected,
                    propagation_path=(
                        f"步骤 {step_id} 的 {score.decision_type} 选择错误 "
                        f"→ 影响步骤 {', '.join(affected)} 的有效性"
                    ),
                    severity="critical" if score.level == 0 else "major",
                ))

        return error_chains
