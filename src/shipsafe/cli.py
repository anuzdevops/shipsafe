import argparse

from shipsafe.scanner.detector import detect_repository


def main():
    parser = argparse.ArgumentParser(
        prog="shipsafe",
        description="Pre-deployment sanity checks for Docker, Kubernetes, and CI/CD.",
    )

    subparsers = parser.add_subparsers(dest="command")

    scan_parser = subparsers.add_parser(
        "scan",
        help="Scan a repository for deployment issues.",
    )

    scan_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to the repository to scan.",
    )

    args = parser.parse_args()

    if args.command == "scan":
        run_scan(args.path)
    else:
        parser.print_help()


def run_scan(path: str):
    print()
    print("ShipSafe v0.1.0")
    print("===============")
    print()
    print(f"Scanning: {path}")
    print()

    detected = detect_repository(path)

    print("Detected:")

    print(f"  {'✓' if detected['docker'] else '✗'} Docker")
    print(f"  {'✓' if detected['kubernetes'] else '✗'} Kubernetes")
    print(f"  {'✓' if detected['github_actions'] else '✗'} GitHub Actions")

    print()
    print("Scan complete.")


if __name__ == "__main__":
    main()
