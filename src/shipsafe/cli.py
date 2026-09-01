import argparse
from pathlib import Path

from shipsafe.scanner.detector import detect_repository
from shipsafe.scanner.engine import ScannerEngine


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Pre-deployment sanity checks for Docker, "
            "Kubernetes, and CI/CD."
        )
    )

    subparsers = parser.add_subparsers(dest="command")

    scan_parser = subparsers.add_parser(
        "scan",
        help="Scan a repository for deployment issues.",
    )

    scan_parser.add_argument(
        "path",
        help="Path to the repository to scan.",
    )

    args = parser.parse_args()

    if args.command == "scan":
        scan(Path(args.path))
    else:
        parser.print_help()


def scan(path: Path):
    print()
    print("ShipSafe v0.1.0")
    print("===============")
    print()
    print(f"Scanning: {path}")
    print()

    detection = detect_repository(path)

    print("Detected:")
    print(
        f"  {'✓' if detection['docker'] else '✗'} Docker"
    )
    print(
        f"  {'✓' if detection['kubernetes'] else '✗'} Kubernetes"
    )
    print(
        f"  {'✓' if detection['github_actions'] else '✗'} "
        "GitHub Actions"
    )
    print()

    engine = ScannerEngine()
    findings = engine.scan(path)

    if findings:
        print("Findings:")
        print()

        for finding in findings:
            print(
                f"  🔴 {finding.severity}  {finding.rule_id}"
            )
            print(f"     {finding.title}")
            print(f"     {finding.message}")
            print()

        print(f"{len(findings)} issue(s) found.")
    else:
        print("No issues found.")

    print()
    print("Scan complete.")


if __name__ == "__main__":
    main()
