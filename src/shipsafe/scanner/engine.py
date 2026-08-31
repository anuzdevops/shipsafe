from shipsafe.parsers.kubernetes import (
    extract_deployment,
    extract_service,
    parse_kubernetes_file,
)
from shipsafe.rules.kubernetes.port_mismatch import PortMismatchRule
from shipsafe.scanner.result import Finding


class ScannerEngine:
    """Coordinates ShipSafe scanners and rules."""

    def __init__(self):
        self.kubernetes_rules = [
            PortMismatchRule(),
        ]

    def scan_kubernetes(self, path):
        """Scan Kubernetes manifests in a directory."""
        findings: list[Finding] = []

        deployments = []
        services = []

        for yaml_file in path.rglob("*.yaml"):
            resources = parse_kubernetes_file(yaml_file)

            for resource in resources:
                deployment = extract_deployment(resource)

                if deployment:
                    deployments.append(deployment)
                    continue

                service = extract_service(resource)

                if service:
                    services.append(service)

        for service in services:
            for deployment in deployments:
                context = (deployment, service)

                for rule in self.kubernetes_rules:
                    findings.extend(rule.check(context))

        return findings
