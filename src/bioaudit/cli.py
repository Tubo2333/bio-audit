"""bio-audit 命令行入口（v1 蓝图：引擎 + CLI）。

子命令：
  run <trajectory.json> [--act deg|pan|scrna]  审计一条轨迹，输出 JSON
  golden [--baseline path]                      golden 回归（20 轨迹 137 决策）
  audit-decision <json> [--act ...]            单决策审计
"""

import argparse
import json
import sys
from pathlib import Path


def _load_trajectory(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "decisions" in data:
        return data["decisions"]
    raise ValueError("轨迹文件必须是决策数组或含 decisions 键的对象")


def cmd_run(args: argparse.Namespace) -> int:
    from bioaudit.api import run_audit

    trajectory = _load_trajectory(Path(args.trajectory))
    result = run_audit(trajectory, act=args.act)
    if result.get("error"):
        print(json.dumps({"error": result["error"]}, ensure_ascii=False, indent=1))
        return 1
    print(json.dumps({
        "trajectory_score": result["trajectory_score"],
        "verdict": result["eval_verdict"],
        "dimension_scores": result["dimension_scores"],
        "n_decisions": len(result["step_scores"]),
        "critical_issues": result["critical_issues"],
        "report": result["report"],
    }, ensure_ascii=False, indent=1))
    return 0


def cmd_golden(args: argparse.Namespace) -> int:
    from bioaudit.regression import replay_golden

    ok, summary = replay_golden(baseline=Path(args.baseline))
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return 0 if ok else 1


def cmd_audit_decision(args: argparse.Namespace) -> int:
    from bioaudit.api import audit_decision

    decision = json.loads(Path(args.decision).read_text(encoding="utf-8"))
    print(json.dumps(audit_decision(decision, act=args.act), ensure_ascii=False, indent=1))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="bio-audit", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="审计一条轨迹（JSON）")
    p_run.add_argument("trajectory", help="轨迹 JSON 文件路径")
    p_run.add_argument("--act", choices=["deg", "pan", "scrna"], default=None)
    p_run.set_defaults(func=cmd_run)

    p_golden = sub.add_parser("golden", help="golden 回归（0 差异验收）")
    p_golden.add_argument(
        "--baseline",
        default=str(Path(__file__).resolve().parent.parent.parent / "tests" / "golden" / "golden_expected_output_after.json"),
    )
    p_golden.set_defaults(func=cmd_golden)

    p_ad = sub.add_parser("audit-decision", help="单决策审计")
    p_ad.add_argument("decision", help="决策 JSON 文件路径")
    p_ad.add_argument("--act", choices=["deg", "pan", "scrna"], default=None)
    p_ad.set_defaults(func=cmd_audit_decision)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
