# Bio-Audit

**A deterministic audit layer for bioinformatics AI-agent methodological decisions
(Scientific Decision CI).**

We encode scientific-method consensus into literature-anchored, executable rules and check,
score, and trace every methodological decision an agent makes — plugging into agent workflows
(MCP/SDK) to deliver three layers of value:
**lint** (runtime verification) / **benchmark** (evaluation) / **reward** (training signal).

> **中文版**: [README.md](README.md) · **Site**: https://tubo2333.github.io/bio-audit/

## Current status (v0.2.x, 2026-08-16)

All five refactoring phases (stabilize → foundation → capture lint → benchmark → reward) are
complete, and the real-agent evaluation pipeline is live:

- **Real evaluation (G-2 re-scored)**: CellVoyager ran for real on GSE115978; after G-2 fixes the
  effective score is **30.0 needs_correction (L0=0 / L1×7 / L3×1 / L-1×12)**, total cost ¥2.55;
  report: [docs/migration/agent-eval-report-g2.md](https://tubo2333.github.io/bio-audit/docs/migration/agent-eval-report-g2.html)
- **Caliber discipline (lesson #2)**: the demo-trajectory score (29 / 5×L0) is *not* the real-run
  score (30.0); the two calibers are strictly separated
  ([site-design §6.2](https://tubo2333.github.io/bio-audit/docs/site-design.html#62-数字口径纪律教训-2-单一事实源))
- **Engineering**: pytest 234/234 · CI dual matrix (3.10/3.12) green · golden 20 trajectories /
  137 decisions 0 diff · ruleset 1.2.0 / engine 0.2.1 / taskset 60 items (IRR κ=0.8336)

## Quick start

```bash
pip install -e ".[dev,ui]"          # Python >= 3.10

bio-audit run src/bioaudit/data/trajectories/v2/deg_correct.json   # audit one trajectory
bio-audit golden                    # golden regression (20/137, must be 0 diff)
bio-audit ruleset-validate          # ruleset three gates (manifest/conflict/golden)
```

Full walkthrough (install / commands / API & MCP integration / regression):
**[Quick Start (EN)](https://tubo2333.github.io/bio-audit/docs/quickstart.en.html)**
([中文](https://tubo2333.github.io/bio-audit/docs/quickstart.html))

## The three value layers

| Layer | Capability | Key artifacts |
|---|---|---|
| **lint** | Runtime verification: M1 active reporting + M3 artifact parsing + cross-validation (false claims / omissions) + verdict state machine (provisional/final/revoked) | `capture/` + MCP server |
| **benchmark** | Evaluation: 60-task set (3 paradigms × difficulty tiers), double annotation IRR, pre-registered gap, contamination defense, power analysis | `benchmark/` + protocol |
| **reward** | Training signal: level→reward mapping constitution (-1 masked, γ=0.30 hard penalty), three-recipe ablation, spike-in anchors | `reward/` |

## Repository layout

```
bio-audit-v2/
├── pyproject.toml            # Apache-2.0; Python>=3.10
├── src/bioaudit/
│   ├── paths.py              # packaged path anchoring (zero cwd dependency, F7)
│   ├── engine/               # matching/scoring/aggregation/conflict/propagation (post-D5 baseline)
│   ├── ontology/             # 34 decision types + P1 validator (three duties)
│   ├── rules/                # 43 rule YAMLs (38 unique) + ruleset snapshot (semver)
│   ├── capture/              # M1 hook / M3 parser / cross-validation / verdict
│   ├── benchmark/            # tasks + difficulty + IRR + runner + contamination scan
│   ├── reward/               # mapping/recipes/calibration (peripheral layer; scoring path untouched)
│   ├── api/ + errors.py      # three-entry contract (pydantic + error codes + required paradigm)
│   ├── report/               # report schema (engine/ruleset/ontology snapshot triple)
│   └── data/                 # packaged assets: 20 trajectories / validation / mappings
├── mcp/                      # MCP server (stdio JSON-RPC)
├── ui/                       # Streamlit shell (calls api only)
├── tests/                    # 234 tests (tests/golden/ frozen baseline copy)
├── docs/                     # documentation site (see docs/site-design.md)
└── .github/workflows/ci.yml  # dual matrix + golden + three/four/five gates
```

## Documentation

- [Docs index](https://tubo2333.github.io/bio-audit/docs/) · [Quick Start](https://tubo2333.github.io/bio-audit/docs/quickstart.en.html)
- [API Contract](https://tubo2333.github.io/bio-audit/docs/api-contract.html) · [MCP Contract](https://tubo2333.github.io/bio-audit/docs/mcp-contract.html)
- [Contributing](CONTRIBUTING.md) · [Window reports](https://tubo2333.github.io/bio-audit/docs/migration/) · [Releases](https://github.com/Tubo2333/bio-audit/releases)
- Site design: docs/site-design.md (nav / layout / bilingual policy / release linkage)

## Path anchoring & data governance

- All resources resolve through `bioaudit.paths` (derived from `Path(__file__)`), runnable from any cwd (F7);
- Large data never enters git (h5ad/csv.gz etc.); secrets are environment-variable-only, `.env` fully
  gitignored, zero secret logic in the engine.

## License

Apache-2.0.
