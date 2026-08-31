from shipsafe.parsers.kubernetes import DeploymentInfo, ServiceInfo
from shipsafe.scanner.result import Finding


RULE_ID = "K8S001"


def check_port_mismatch(
    deployment: DeploymentInfo,
    service: ServiceInfo,
) -> list[Finding]:
    """Check whether a Service targets ports exposed by its Deployment."""

    if not _selector_matches(deployment.labels, service.selector):
        return []

    container_ports = {
        port
        for container in deployment.containers
        for port in container.ports
    }

    findings = []

    for target_port in service.target_ports:
        if target_port not in container_ports:
            findings.append(
                Finding(
                    rule_id=RULE_ID,
                    severity="HIGH",
                    title="Kubernetes port mismatch",
                    message=(
                        f"Service '{service.name}' targets port "
                        f"{target_port}, but Deployment "
                        f"'{deployment.name}' does not expose it."
                    ),
                )
            )

    return findings


def _selector_matches(
    labels: dict[str, str],
    selector: dict[str, str],
) -> bool:
    return all(labels.get(key) == value for key, value in selector.items())
