from shipsafe.parsers.kubernetes import (
    ContainerInfo,
    ContainerPort,
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
                ports=[
                    ContainerPort(
                        name=None,
                        port=3000,
                    )
                ],
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
                ports=[
                    ContainerPort(
                        name=None,
                        port=3000,
                    )
                ],
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


def test_named_port_matches():
    deployment = DeploymentInfo(
        name="backend",
        labels={"app": "backend"},
        containers=[
            ContainerInfo(
                name="backend",
                ports=[
                    ContainerPort(
                        name="http",
                        port=3000,
                    )
                ],
            )
        ],
    )

    service = ServiceInfo(
        name="backend-service",
        selector={"app": "backend"},
        target_ports=["http"],
    )

    findings = check_port_mismatch(deployment, service)

    assert findings == []


def test_unknown_named_port_is_detected():
    deployment = DeploymentInfo(
        name="backend",
        labels={"app": "backend"},
        containers=[
            ContainerInfo(
                name="backend",
                ports=[
                    ContainerPort(
                        name="http",
                        port=3000,
                    )
                ],
            )
        ],
    )

    service = ServiceInfo(
        name="backend-service",
        selector={"app": "backend"},
        target_ports=["grpc"],
    )

    findings = check_port_mismatch(deployment, service)

    assert len(findings) == 1
    assert findings[0].rule_id == "K8S001"
    assert findings[0].severity == "HIGH"
    assert "grpc" in findings[0].message
