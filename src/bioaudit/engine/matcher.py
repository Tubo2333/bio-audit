"""RuleMatcher — 自 fullflow-demo 迁移（含 B1/B8 修正），mappings 路径改为包内锚定。

迁移变更（F7 修复）：默认映射文件由相对 cwd 的旧默认 data/mappings/*.yaml 改为
bioaudit.paths.MAPPINGS_DIR；构造参数保持兼容（可显式传路径）。

保留修正：
- B1: Split into .parse() and .match_parsed() to avoid duplicate work
- B8: Alias/key mappings moved to data/mappings/
"""

import yaml
from pathlib import Path

from bioaudit.storage.rule_registry import RuleRegistry
from bioaudit.models.decision import Decision, ParsedStep
from bioaudit.models.rule import Rule
from bioaudit.paths import MAPPINGS_DIR


class RuleMatcher:
    """Matches agent decisions to applicable scientific rules.

    Two-phase design (B1 fix):
    1. parse(Decision) → ParsedStep (normalization only)
    2. match_parsed(ParsedStep) → list[Rule] (rule matching only)
    """

    def __init__(self, registry: RuleRegistry, mappings_dir: Path | str | None = None):
        self.registry = registry
        self._mappings_dir = Path(mappings_dir) if mappings_dir else MAPPINGS_DIR
        self._aliases = self._load_mapping(self._mappings_dir / "type_aliases.yaml")
        self._key_map = self._load_mapping(self._mappings_dir / "context_keys.yaml")

    def _load_mapping(self, path: Path) -> dict:
        """B8: Load mapping from YAML, fallback to defaults."""
        try:
            with open(path, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return {}

    def parse(self, decision: Decision) -> ParsedStep:
        """B1: Parse only — normalize decision type and context."""
        return ParsedStep(
            step_id=decision.step_id,
            original=decision,
            decision_type=self._normalize_type(decision.decision_type),
            normalized_context=self._normalize_context(decision.context),
        )

    def match_parsed(self, parsed: ParsedStep) -> list[Rule]:
        """B1: Match only — find rules for an already-parsed step."""
        return self.registry.match(
            parsed.decision_type, parsed.normalized_context
        )

    def match(self, decision: Decision) -> tuple[ParsedStep, list[Rule]]:
        """Convenience: parse + match in one call (for non-pipeline use)."""
        parsed = self.parse(decision)
        rules = self.match_parsed(parsed)
        return parsed, rules

    def _normalize_type(self, raw_type: str) -> str:
        """Normalize decision type using configurable alias map."""
        return self._aliases.get(raw_type, raw_type)

    def _normalize_context(self, context: dict) -> dict:
        """Normalize context keys using configurable key map."""
        normalized = {}
        for k, v in context.items():
            normalized[self._key_map.get(k, k)] = v
        return normalized
