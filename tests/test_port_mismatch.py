from shipsafe.parsers.kubernetes import (
    ContainerInfo,
    DeploymentInfo,
    ServiceInfo,
)
from shipsafe.rules.kubernetes.port_mismatch import check_port_mismatch


def test_detects_port_mismatch():
    deployment = DeploymentInfo(
        name="backend",
        labels={"app": "backend"},
        containers=[
            ContainerInfo(
                name="backend",
                ports=[3000],
            )
        ],
    )

    service = ServiceInfo(
        name="backend-service",
        selector={"app": "backend"},
        target_ports=[8080],
    )

    findings = check_port_mismatch(deployment, service)

    assert len(findings) == 1
    assert findings[0].rule_id == "K8S001"
    assert findings[0].severity == "HIGH"


def test_matching_port_has_no_finding():
    deployment = DeploymentInfo(
        name="backend",
        labels={"app": "backend"},
        containers=[
            ContainerInfo(
                name="backend",
                ports=[3000],
            )
        ],
    )

    service = ServiceInfo(
        name="backend-service",
        selector={"app": "backend"},
        target_ports=[3000],
    )

    findings = check_port_mismatch(deployment, service)

    assert findings == []
