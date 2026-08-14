"""ScoreAggregator — 自 fullflow-demo 迁移（含 C1/C2 修正），未改动逻辑。

保留修正：
- C1: Lowest-score-dominant aggregation. Fatal errors cannot be diluted.
- C2: MVP uses 3 dimensions (not 6). 3 empty dimensions removed.
- B8: scRNA 聚合器已含 annotation_validation / trajectory_validation 两类
"""

from bioaudit.models.score import DecisionScore, AggregatedScore
from bioaudit.models.profile import ScenarioProfile


class ScoreAggregator:
    """Aggregates individual decision scores into trajectory-level report.

    C1 FIX: Uses "lowest-dimension-dominant" strategy.
    A single Level 0 in any dimension should dominate the final score.
    Weighted average is kept as a supplementary metric.
    """

    # Decision type → evaluation dimension (expanded for pancancer + scRNA)
    TYPE_TO_DIMENSION = {
        # DEG (Act 1)
        "filtering": "data_handling",
        "normalization": "data_handling",
        "deg_method": "method_selection",
        "multiple_testing_correction": "statistical_rigor",
        "significance_threshold": "statistical_rigor",
        # PanCancer survival (Act 2)
        "cox_ph_assumption": "statistical_rigor",
        "independent_prognostic_claim": "statistical_rigor",
        "events_per_variable": "statistical_rigor",
        # PanCancer genetics/immune/drug (Act 2)
        "cbioportal_projection": "data_handling",
        "immune_correlation_method": "method_selection",
        "purity_confounding": "data_handling",
        "gsea_background": "data_handling",
        "enrichment_correction": "statistical_rigor",
        "ic50_sample_size": "statistical_rigor",
        # PanCancer consistency (Act 2 L4)
        "expression_survival_consistency": "statistical_rigor",
        "immune_expression_consistency": "statistical_rigor",
        # scRNA (Act 3)
        "api_data_integrity": "data_handling",
        "qc_filtering": "data_handling",
        "qc_mito_threshold": "data_handling",
        "doublet_detection": "data_handling",
        "scRNA_normalization": "data_handling",
        "hv_gene_selection": "method_selection",
        "batch_correction": "data_handling",
        "dim_reduction": "method_selection",
        "pca_dimension": "method_selection",
        "clustering_method": "method_selection",
        "clustering_resolution": "method_selection",
        "annotation_method": "method_selection",
        "annotation_validation": "method_selection",
        "trajectory_inference": "method_selection",
        "trajectory_validation": "method_selection",
        "cluster_annotation_consistency": "method_selection",
        "annotation_deg_consistency": "method_selection",
        "trajectory_annotation_consistency": "method_selection",
    }

    # C2 FIX: 3 dimensions with rebalanced weights
    DEFAULT_DIMENSION_WEIGHTS = {
        "data_handling": 0.33,
        "method_selection": 0.34,
        "statistical_rigor": 0.33,
    }

    def aggregate(
        self, step_scores: list[DecisionScore],
        profile: ScenarioProfile | None = None
    ) -> AggregatedScore:
        # 1. Group scores by dimension (C2: 3 dims only)
        dim_scores: dict[str, list[float]] = {}
        for score in step_scores:
            if score.level == -1:
                continue
            dim = self.TYPE_TO_DIMENSION.get(score.decision_type)
            if dim is None:
                continue  # C2: skip unmapped types
            dim_scores.setdefault(dim, []).append(score.numeric_score)

        # 2. Per-dimension average
        dim_averages = {}
        for dim, scores in dim_scores.items():
            dim_averages[dim] = sum(scores) / len(scores)

        # 3. C1 FIX: Lowest-dimension-dominant score
        if dim_averages:
            lowest_dim_score = min(dim_averages.values())
        else:
            lowest_dim_score = 0.0  # No recognized dimensions → worst (all unmapped)

        # 4. Weighted average (supplementary)
        weights = (
            profile.dimension_weights if profile
            else self.DEFAULT_DIMENSION_WEIGHTS
        )
        weighted_sum = 0.0
        total_weight = 0.0
        for dim, avg in dim_averages.items():
            w = weights.get(dim, 0.0)
            weighted_sum += avg * w
            total_weight += w
        weighted_avg = (
            (weighted_sum / total_weight * 100) if total_weight > 0 else 100.0
        )

        # C1: Trajectory score = lowest-dimension score (primary)
        trajectory_score = round(lowest_dim_score * 100, 1)

        # 5. Critical issues
        critical = [
            s for s in step_scores if 0 <= s.level <= 1
        ]

        # 6. Verdict
        verdict = "pass"
        if any(s.level == 0 for s in step_scores):
            verdict = "blocked"
        elif any(s.level == 1 for s in step_scores):
            verdict = "needs_correction"
        elif trajectory_score < 60:
            verdict = "needs_correction"

        return AggregatedScore(
            step_scores=step_scores,
            dimension_scores=dim_averages,
            trajectory_score=trajectory_score,
            critical_issues=[
                f"[Level {s.level}] Step {s.step_id}: {s.agent_choice} — {s.explanation}"
                for s in critical
            ],
            verdict=verdict,
        )
