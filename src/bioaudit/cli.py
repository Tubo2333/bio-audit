"""bio-audit 命令行入口（v1 蓝图：引擎 + CLI）。

子命令：
  run <trajectory.json> [--act deg|pan|scrna]  审计一条轨迹，输出 JSON
  golden [--baseline path]                      golden 回归（20 轨迹 137 决策）
  audit-decision <json> --act deg|pan|scrna    单决策审计（B3：paradigm 必填）
  validate-ontology                            P1 校验器三职责（B2：覆盖/语义边界/冲突）
  ruleset-validate                             B5：规则治理三闸（清单+冲突+golden 一条命令）
  migrate-trajectories [--dry-run]             B4：v1 → v2 轨迹迁移（只读迁移器）
  trajectory-validate <path|dir>               B4：v2 轨迹 schema 校验（缺必填字段报错）
"""

import argparse
import json
import sys
from pathlib import Path


def _load_trajectory(path: Path) -> list[dict] | dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "decisions" in data:
        return data
    raise ValueError("轨迹文件必须是决策数组或含 decisions 键的对象")


def _print_bioaudit_error(exc) -> None:
    """契约错误输出：{"error": {"code", "message", "details"}}（B3 错误码）。"""
    print(json.dumps(exc.to_dict(), ensure_ascii=False, indent=1))
    print(f"\n❌ {exc.code}: {exc.message}", file=sys.stderr)


def cmd_run(args: argparse.Namespace) -> int:
    from bioaudit.api import run_audit
    from bioaudit.errors import BioAuditError

    try:
        trajectory = _load_trajectory(Path(args.trajectory))
        result = run_audit(trajectory, act=args.act)
    except BioAuditError as exc:
        _print_bioaudit_error(exc)
        return 1
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": {"code": "bad-request", "message": str(exc)}},
                         ensure_ascii=False, indent=1))
        return 1
    if result.get("error"):
        print(json.dumps({"error": {
            "code": result.get("error_code") or "internal-error",
            "message": result["error"],
        }}, ensure_ascii=False, indent=1))
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
    from bioaudit.errors import BioAuditError

    try:
        decision = json.loads(Path(args.decision).read_text(encoding="utf-8"))
        result = audit_decision(decision, paradigm=args.act)
    except BioAuditError as exc:
        _print_bioaudit_error(exc)
        return 1
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": {"code": "bad-request", "message": str(exc)}},
                         ensure_ascii=False, indent=1))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=1))
    return 0


def cmd_validate_ontology(args: argparse.Namespace) -> int:
    from bioaudit.ontology.validator import main as validator_main

    return validator_main([
        *(["--rules-dir", args.rules_dir] if args.rules_dir else []),
        *(["--ontology-dir", args.ontology_dir] if args.ontology_dir else []),
        *(["--json"] if args.json else []),
    ])


def cmd_ruleset_validate(args: argparse.Namespace) -> int:
    """B5：规则治理三闸（清单校验 + D2 冲突检查 + golden 重放）一条命令。"""
    from bioaudit.rules.validator import main as ruleset_main

    return ruleset_main([
        *(["--rules-dir", args.rules_dir] if args.rules_dir else []),
        *(["--baseline", args.baseline] if args.baseline else []),
        *(["--json"] if args.json else []),
    ])


def cmd_migrate_trajectories(args: argparse.Namespace) -> int:
    """B4：只读迁移器（v1 → v2）；--dry-run 不写盘。"""
    from bioaudit.capture.trajectory_migrator import TrajectoryMigrator
    from bioaudit.errors import BioAuditError

    try:
        migrator = TrajectoryMigrator(
            src_dir=Path(args.src_dir) if args.src_dir else None,
            dst_dir=Path(args.dst_dir) if args.dst_dir else None,
        )
        rows = migrator.migrate_all(dry_run=args.dry_run)
    except (BioAuditError, OSError, ValueError) as exc:
        print(f"❌ 迁移失败: {exc}", file=sys.stderr)
        return 1

    print(json.dumps({
        "dry_run": args.dry_run,
        "n_migrated": len(rows),
        "trajectories": rows,
    }, ensure_ascii=False, indent=1))
    if args.dry_run:
        print("\n（dry-run：未写任何文件）")
    return 0


def cmd_trajectory_validate(args: argparse.Namespace) -> int:
    """B4：v2 轨迹 schema 校验；缺必填字段 → 显式报错（A15）。"""
    from bioaudit.errors import BioAuditError
    from bioaudit.models.trajectory import validate_trajectory

    path = Path(args.path)
    files = sorted(path.glob("*.json")) if path.is_dir() else [path]
    if not files:
        print(f"❌ 未找到轨迹文件: {path}", file=sys.stderr)
        return 1

    ok_all = True
    results = []
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            traj = validate_trajectory(data)
            results.append({
                "file": str(f),
                "ok": True,
                "version": traj.version,
                "trajectory_id": traj.trajectory_id,
                "act": traj.act,
                "provenance_source": traj.provenance.source,
                "n_decisions": len(traj.decisions),
            })
        except (BioAuditError, ValueError, OSError, json.JSONDecodeError) as exc:
            ok_all = False
            results.append({"file": str(f), "ok": False, "error": str(exc)})

    print(json.dumps(results, ensure_ascii=False, indent=1))
    return 0 if ok_all else 1


def main(argv: list[str] | None = None) -> int:
    # JSON 输出含中文 → 强制 UTF-8（Windows 控制台 GBK 会破坏管道捕获）
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
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
    p_ad.add_argument("--act", required=True, choices=["deg", "pan", "scrna"],
                      help="范式（B3 契约：必填，deg_method 同名异构消歧）")
    p_ad.set_defaults(func=cmd_audit_decision)

    p_vo = sub.add_parser(
        "validate-ontology",
        help="P1 校验器三职责（覆盖报告 / 语义边界 / 冲突完整性）",
    )
    p_vo.add_argument("--rules-dir", default=None, help="规则目录（默认包内）")
    p_vo.add_argument("--ontology-dir", default=None, help="本体目录（默认包内）")
    p_vo.add_argument("--json", action="store_true", help="输出原始 JSON 报告")
    p_vo.set_defaults(func=cmd_validate_ontology)

    p_rs = sub.add_parser(
        "ruleset-validate",
        help="B5 规则治理三闸：清单校验 + D2 冲突检查 + golden 重放（D1 变更流程）",
    )
    p_rs.add_argument("--rules-dir", default=None, help="规则目录（默认包内）")
    p_rs.add_argument("--baseline", default=None, help="golden 基线路径（默认包内副本）")
    p_rs.add_argument("--json", action="store_true", help="输出原始 JSON 报告")
    p_rs.set_defaults(func=cmd_ruleset_validate)

    p_mig = sub.add_parser("migrate-trajectories", help="B4：v1 → v2 轨迹迁移（只读）")
    p_mig.add_argument("--src-dir", default=None, help="v1 旧轨迹目录（默认 data/trajectories）")
    p_mig.add_argument("--dst-dir", default=None, help="v2 输出目录（默认 data/trajectories/v2）")
    p_mig.add_argument("--dry-run", action="store_true", help="只生成清单，不写盘")
    p_mig.set_defaults(func=cmd_migrate_trajectories)

    p_tv = sub.add_parser("trajectory-validate", help="B4：v2 轨迹 schema 校验")
    p_tv.add_argument("path", help="v2 轨迹 JSON 文件或目录")
    p_tv.set_defaults(func=cmd_trajectory_validate)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
