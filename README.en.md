# Bio-Audit

[![CI](https://github.com/Tubo2333/bio-audit/actions/workflows/ci.yml/badge.svg)](https://github.com/Tubo2333/bio-audit/actions)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-Apache--2.0-green)

**A methodological "exam proctor" for bioinformatics AI agents: it audits every analytical
decision an agent makes — scoring it against literature-anchored rules, citing the evidence,
and keeping the receipts — turning black-box analyses into auditable, reproducible, comparable ones.**

> **中文版**: [README.md](README.md) · **Site**: https://tubo2333.github.io/bio-audit/

---

## Why

AI agents are now fluent at running bioinformatics analyses: the code runs, the output looks
plausible, and the summary sounds convincing. But they will **not volunteer whether their
methodological choices are sound**:

- Why normalize with TPM instead of running DESeq2 on raw counts?
- With 12 patients and no batch correction, can you separate patient effects from biology?
- Treating each single cell as an independent sample for differential expression
  (pseudoreplication) — how much does the p-value inflate?
- Without multiple-testing correction, how many "significant" genes are false positives?

These are not bugs — nothing crashes and the output looks normal. They are **wrong method
choices and skipped critical steps**, invisible to conventional code review. Catching them
requires auditing each step against scientific-method consensus.

We let CellVoyager (a single-cell analysis agent) run a complete analysis on real melanoma
data (GSE115978), then opened its decision scratchpad step by step: **5 of 12 decisions were
dangerous (L0)** — skipping doublet detection, skipping batch correction, cell-level
pseudoreplication for DE, arbitrary PCA dimensionality, skipping trajectory inference.
Under conventional review, all of it "looked completely normal."

**Bio-Audit encodes scientific-method consensus into executable rules and checks, scores,
and traces every methodological decision an agent makes.**

## What it does

| Layer | Plain English | How |
|---|---|---|
| **lint** (runtime verification) | The agent is audited as it runs; "said vs. did" mismatches surface immediately | M1 self-report + M3 artifact parsing + cross-validation (false-positive/negative detection) + verdict lifecycle (provisional → final / revoked) |
| **benchmark** (evaluation) | "Is this agent actually good?" becomes a reproducible number | 60 gold-labeled tasks (double annotation IRR κ=0.83, pre-registration, contamination screening, power analysis) |
| **reward** (training signal) | Audit scores become signals you can feed to RL | level→reward mapping constitution (-1 masked, L0 hard penalty γ=0.30), three-recipe ablation, spike-in anchors |

Every decision's score is **anchored to a specific citation (PMID)**, not "trust me."
Agents can call the audit inline during analysis through the **MCP server** (`audit_decision`)
and get immediate feedback.

## Real results

CellVoyager ran for real on GSE115978 (2026-08, total cost ¥2.55); after the G-2 fixes the run
was re-scored:

| Caliber | Result |
|---|---|
| Demo trajectory (re-run after D5 fix, 2026-08-13, 12-step analysis) | **29 / Blocked / 5 × L0** |
| **G-2 real-run re-score** (GSE115978 · declared injection + platform-key relaxation) | **30.0 / needs_correction / L0=0 · L1×7 · L3×1 · L-1×12** |

The two calibers are different objects and must **never be mixed** (see
[site-design §6.2](https://tubo2333.github.io/bio-audit/docs/site-design.html#62-数字口径纪律教训-2-单一事实源)).
Reports: [G-2 report](https://tubo2333.github.io/bio-audit/docs/migration/agent-eval-report-g2.html) ·
[G main report (archived)](https://tubo2333.github.io/bio-audit/docs/migration/agent-eval-report.html).

The engine's own reliability is independently validated (R0–R3): on simulated ground-truth
data, audit scores rank method combinations consistently with actual F1 (Spearman ρ=0.9747,
recomputed after the D5 fix, conclusion unchanged); 4/4 canonical error cases correctly graded.

## Quick start

```bash
pip install -e ".[dev,ui]"          # Python >= 3.10

bio-audit run src/bioaudit/data/trajectories/v2/deg_correct.json   # audit one trajectory
bio-audit golden                    # golden regression (20 trajectories / 137 decisions, must be 0 diff)
bio-audit ruleset-validate          # ruleset three gates (manifest / conflict / golden)
```

Full walkthrough (install / commands / API & MCP integration / regression):
**[Quick Start](https://tubo2333.github.io/bio-audit/docs/quickstart.en.html)**
([中文](https://tubo2333.github.io/bio-audit/docs/quickstart.html))

## Status & roadmap

**Current (v0.2.x, 2026-08)**: core system closed loop — stable engine + 34-type decision
ontology + governed ruleset; real capture pipeline (M1/M3 cross-validation); 60-task benchmark;
reward layer; real-agent evaluation pipeline live with first fix round (G-2). Engineering:
pytest 235/235 · CI dual matrix (Python 3.10/3.12) green · golden regression 0 diff · reports
carry a snapshot triple (engine/ruleset/ontology versions) so any score is reproducible.

**Next**: L3/L4 conclusion- and consistency-level audits (general implementation), PRM
(process reward model), task-set expansion (batch 3, cross-model annotation), more real-agent
evaluations (multiple datasets/agents).

## Docs

- [Documentation hub](https://tubo2333.github.io/bio-audit/docs/) · [Quick Start](https://tubo2333.github.io/bio-audit/docs/quickstart.en.html)
- [API contract](https://tubo2333.github.io/bio-audit/docs/api-contract.html) · [MCP contract](https://tubo2333.github.io/bio-audit/docs/mcp-contract.html)
- [Contributing guide](CONTRIBUTING.md) · [Window reports](https://tubo2333.github.io/bio-audit/docs/migration/) · [Releases](https://github.com/Tubo2333/bio-audit/releases)

## Repository layout

```
src/bioaudit/
├── engine/       # matching / scoring / aggregation (rule engine core)
├── ontology/     # 34 decision-type ontology + validator
├── rules/        # 44 rule YAMLs (39 unique) + ruleset version snapshot
├── capture/      # capture: M1 hook / M3 parsing / cross-validation / verdict
├── benchmark/    # tasks / difficulty / IRR / runner / contamination scan
├── reward/       # level→reward mapping / recipes / calibration
├── api/          # three-entry contract (pydantic + error codes)
└── data/         # 20 trajectories / validation / mappings
```

## Contributing

Rules, task sets, and code are all welcome — the three-gate ruleset governance
(manifest / conflict / golden) keeps changes safe. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[Apache-2.0](LICENSE). Design acknowledges findings and methodology from BiomniBench,
GeneBench, FlowBench, and CoE Audit.
