from pathlib import Path

from shipsafe.parsers.kubernetes import (
    extract_deployment,
    extract_service,
    parse_kubernetes_file,
)
from shipsafe.rules.kubernetes.port_mismatch import PortMismatchRule
from shipsafe.rules.kubernetes.service_selector import ServiceSelectorRule
from shipsafe.rules.kubernetes.service_port import DuplicatePortNameRule
from shipsafe.rules.kubernetes.readiness_probe import ReadinessProbeRule
from shipsafe.rules.kubernetes.resources import ResourceConfigurationRule
from shipsafe.scanner.context import KubernetesContext
from shipsafe.scanner.result import Finding


class ScannerEngine:
    """Coordinates ShipSafe scanners and rules."""

    def __init__(self):
        self.kubernetes_rules = [
            PortMismatchRule(),
            ServiceSelectorRule(),
            DuplicatePortNameRule(),
            ReadinessProbeRule(),
            ResourceConfigurationRule(),
        ]

    def scan_kubernetes(self, path: Path) -> list[Finding]:
        """Scan Kubernetes manifests in a directory."""
        context = self._build_kubernetes_context(path)

        findings: list[Finding] = []

        for rule in self.kubernetes_rules:
            findings.extend(rule.check(context))

        return findings

    def _build_kubernetes_context(
        self,
        path: Path,
    ) -> KubernetesContext:
        """Parse Kubernetes manifests into a rule context."""
        deployments = []
        services = []

        yaml_files = list(path.rglob("*.yaml"))
        yaml_files.extend(path.rglob("*.yml"))

        for yaml_file in yaml_files:
            resources = parse_kubernetes_file(yaml_file)

            for resource in resources:
                deployment = extract_deployment(resource)

                if deployment:
                    deployments.append(deployment)
                    continue

                service = extract_service(resource)

                if service:
                    services.append(service)

        return KubernetesContext(
            deployments=deployments,
            services=services,
        )
