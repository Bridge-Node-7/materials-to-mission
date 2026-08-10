from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import sys
from pathlib import Path

from . import __version__
from .boundary import scan_public_boundary
from .errors import MaterialsToMissionError
from .io import read_json, write_text
from .release import build_deterministic_zip, sha256
from .report import render_decision_passport
from .resources import schema_dir
from .validator import validate_case
from .validation_profiles import (
    DEFAULT_VALIDATION_PROFILE,
    VALIDATION_PROFILE_IDS,
)


EXAMPLES = """examples:
  m2m validate examples/synthetic-critical-material-pathway/case.json --public
  m2m validate examples/invalid/missing-human-owner.json --public --json
  m2m render examples/synthetic-critical-material-pathway/case.json
  m2m scan examples/synthetic-critical-material-pathway/case.json --json
  m2m package --root . --output-dir dist

exit codes:
  0  successful result
  2  validation or public-boundary finding
  3  input, filesystem, or controlled operational error
"""


class _ArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        self.print_usage(sys.stderr)
        self.exit(3, f"{self.prog}: error: {message}\n")


def _subparser(sub, name: str, *, help_text: str, example: str) -> argparse.ArgumentParser:
    return sub.add_parser(
        name,
        help=help_text,
        description=help_text,
        epilog=f"example:\n  {example}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )


def _parser() -> argparse.ArgumentParser:
    parser = _ArgumentParser(
        prog="m2m",
        description="Materials-to-Mission public reference toolkit",
        epilog=EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--version", action="version", version="%(prog)s " + __version__
    )
    sub = parser.add_subparsers(
        dest="command", required=True, parser_class=_ArgumentParser
    )

    validate = _subparser(
        sub,
        "validate",
        help_text="validate a Materials-to-Mission case",
        example="m2m validate examples/synthetic-critical-material-pathway/case.json --public",
    )
    validate.add_argument("case", help="path to a Materials-to-Mission case JSON file")
    validate.add_argument("--public", action="store_true", help="enforce the public synthetic boundary")
    validate.add_argument("--json", action="store_true", help="emit machine-readable findings")
    validate.add_argument(
        "--profile",
        choices=VALIDATION_PROFILE_IDS,
        default=DEFAULT_VALIDATION_PROFILE,
        help=f"semantic validation profile; default: {DEFAULT_VALIDATION_PROFILE}",
    )

    render = _subparser(
        sub,
        "render",
        help_text="render the Decision Passport as Markdown",
        example="m2m render examples/synthetic-critical-material-pathway/case.json --output build/passport.md",
    )
    render.add_argument("case", help="path to a Materials-to-Mission case JSON file")
    render.add_argument("--output", "-o", help="write Markdown to this path instead of standard output")
    render.add_argument(
        "--profile",
        choices=VALIDATION_PROFILE_IDS,
        default=DEFAULT_VALIDATION_PROFILE,
        help=f"semantic validation profile; default: {DEFAULT_VALIDATION_PROFILE}",
    )

    scan = _subparser(
        sub,
        "scan",
        help_text="scan a JSON record for public-boundary tokens",
        example="m2m scan examples/synthetic-critical-material-pathway/case.json --json",
    )
    scan.add_argument("case", help="path to a JSON record")
    scan.add_argument("--json", action="store_true", help="emit machine-readable findings")

    package = _subparser(
        sub,
        "package",
        help_text="build a deterministic repository archive",
        example="m2m package --root . --output-dir dist",
    )
    package.add_argument("--root", default=".", help="repository root; default: current directory")
    package.add_argument(
        "--output-dir",
        default="dist",
        help="output directory; use dist, build, or a directory outside the release root; default: dist",
    )

    _subparser(
        sub,
        "schema-dir",
        help_text="print the installed schema directory",
        example="m2m schema-dir",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "validate":
            case = read_json(args.case)
            result = validate_case(
                case,
                public=args.public,
                profile=args.profile,
            )
            if args.json:
                print(
                    json.dumps(
                        {
                            "valid": result.valid,
                            "schema_version": case.get("schema_version"),
                            "validation_profile": result.validation_profile,
                            "toolkit_version": __version__,
                            "findings": [asdict(f) for f in result.findings],
                        },
                        indent=2,
                    )
                )
            elif result.valid:
                print("PASS - case is structurally and semantically valid")
            else:
                for finding in result.findings:
                    print(f"{finding.severity} {finding.code} {finding.path} - {finding.message}")
                print("STOP - correct the reported findings and run validation again.")
            return 0 if result.valid else 2

        if args.command == "render":
            case = read_json(args.case)
            result = validate_case(
                case,
                public=bool(case.get("public_safe")),
                profile=args.profile,
            )
            if not result.valid:
                for finding in result.findings:
                    print(f"ERROR {finding.code} {finding.path} - {finding.message}", file=sys.stderr)
                print("STOP - correct the reported findings before rendering.", file=sys.stderr)
                return 2
            content = render_decision_passport(case)
            if args.output:
                write_text(args.output, content)
                print(f"PASS - wrote {args.output}")
            else:
                print(content, end="")
            return 0

        if args.command == "scan":
            case = read_json(args.case)
            findings = scan_public_boundary(case)
            if args.json:
                print(json.dumps({"clean": not findings, "findings": findings}, indent=2))
            else:
                if not findings:
                    print("PASS - no prohibited public-boundary tokens detected")
                else:
                    print("\n".join(f"ERROR - {item}" for item in findings))
                    print("STOP - remove protected content and scan again.")
            return 0 if not findings else 2

        if args.command == "package":
            root = Path(args.root).resolve()
            version = (root / "VERSION").read_text(encoding="utf-8").strip()
            output_dir = Path(args.output_dir)
            archive = output_dir / f"materials-to-mission-v{version}.zip"
            build_deterministic_zip(root, archive)
            digest = sha256(archive)
            sidecar = archive.with_suffix(archive.suffix + ".sha256")
            sidecar.write_text(f"{digest}  {archive.name}\n", encoding="utf-8")
            print(f"PASS - {archive}")
            print(f"SHA-256 {digest}")
            return 0

        if args.command == "schema-dir":
            print(schema_dir())
            return 0
    except MaterialsToMissionError as exc:
        print(f"STOP - {exc}", file=sys.stderr)
        return 3
    except OSError as exc:
        print(f"STOP - {exc}", file=sys.stderr)
        return 3
    return 1
