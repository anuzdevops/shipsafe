from pathlib import Path

from shipsafe.parsers.docker import parse_dockerfile
from shipsafe.parsers.kubernetes import (
    extract_deployment,
    extract_service,
    parse_kubernetes_file,
)
from shipsafe.rules.docker import (
    DockerSecretRule,
    HealthcheckRule,
    LatestTagRule,
    RootUserRule,
    UnpinnedBaseImageRule,
)
from shipsafe.rules.kubernetes.port_mismatch import PortMismatchRule
from shipsafe.rules.kubernetes.readiness_probe import ReadinessProbeRule
from shipsafe.rules.kubernetes.resources import ResourceConfigurationRule
from shipsafe.rules.kubernetes.service_port import DuplicatePortNameRule
from shipsafe.rules.kubernetes.service_selector import ServiceSelectorRule
from shipsafe.scanner.context import KubernetesContext
from shipsafe.scanner.result import Finding


class ScannerEngine:
    """Coordinates ShipSafe scanners and rules."""

    def __init__(self):
        self.kubernetes_rules = [
            PortMismatchRule(),
            ReadinessProbeRule(),
            ResourceConfigurationRule(),
            DuplicatePortNameRule(),
            ServiceSelectorRule(),
        ]

        self.docker_rules = [
            UnpinnedBaseImageRule(),
            RootUserRule(),
            HealthcheckRule(),
            LatestTagRule(),
            DockerSecretRule(),
        ]

    def scan(self, path: Path) -> list[Finding]:
        """Run all available scanners against a repository."""

        findings: list[Finding] = []

        findings.extend(self.scan_docker(path))
        findings.extend(self.scan_kubernetes(path))

        return findings

    def scan_docker(self, path: Path) -> list[Finding]:
        """Scan Dockerfiles using all Docker rules."""

        findings: list[Finding] = []

        dockerfile = path / "Dockerfile"

        if not dockerfile.is_file():
            return findings

        context = parse_dockerfile(dockerfile)

        for rule in self.docker_rules:
            findings.extend(rule.check(context))

        return findings

    def scan_kubernetes(self, path: Path) -> list[Finding]:
        """Scan Kubernetes manifests using all Kubernetes rules."""

        context = KubernetesContext()

        for yaml_file in path.rglob("*.yaml"):
            self._collect_kubernetes_resources(yaml_file, context)

        for yaml_file in path.rglob("*.yml"):
            self._collect_kubernetes_resources(yaml_file, context)

        findings: list[Finding] = []

        for rule in self.kubernetes_rules:
            findings.extend(rule.check(context))

        return findings

    @staticmethod
    def _collect_kubernetes_resources(
        yaml_file: Path,
        context: KubernetesContext,
    ) -> None:
        resources = parse_kubernetes_file(yaml_file)

        for resource in resources:
            deployment = extract_deployment(resource)

            if deployment:
                context.deployments.append(deployment)
                continue

            service = extract_service(resource)

            if service:
                context.services.append(service)
