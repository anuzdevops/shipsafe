from pathlib import Path

from shipsafe.parsers.kubernetes import (
    extract_deployment,
    extract_service,
    parse_kubernetes_file,
)
from shipsafe.rules.kubernetes.port_mismatch import check_port_mismatch
from shipsafe.scanner.result import Finding


def run_kubernetes_rules(root: Path) -> list[Finding]:
    resources = []

    for pattern in ("*.yaml", "*.yml"):
        for file in root.rglob(pattern):
            resources.extend(parse_kubernetes_file(file))

    deployments = []
    services = []

    for resource in resources:
        deployment = extract_deployment(resource)

        if deployment:
            deployments.append(deployment)

        service = extract_service(resource)

        if service:
            services.append(service)

    findings = []

    for service in services:
        for deployment in deployments:
            findings.extend(
                check_port_mismatch(
                    deployment,
                    service,
                )
            )

    return findings
