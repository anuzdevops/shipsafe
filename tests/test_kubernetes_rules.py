from shipsafe.parsers.kubernetes import (
    ContainerInfo,
    ContainerPort,
    DeploymentInfo,
    ServiceInfo,
)
from shipsafe.rules.kubernetes.service_selector import ServiceSelectorRule
from shipsafe.rules.kubernetes.service_port import DuplicatePortNameRule
from shipsafe.rules.kubernetes.readiness_probe import ReadinessProbeRule
from shipsafe.rules.kubernetes.resources import ResourceConfigurationRule
from shipsafe.scanner.context import KubernetesContext


def make_deployment(
    labels=None,
    ports=None,
    readiness_probe=False,
    resources=False,
):
    return DeploymentInfo(
        name="backend",
        labels=labels or {"app": "backend"},
        containers=[
            ContainerInfo(
                name="backend",
                ports=ports or [],
                has_readiness_probe=readiness_probe,
                has_resources=resources,
            )
        ],
    )


def make_service(
    selector=None,
    ports=None,
    target_ports=None,
):
    return ServiceInfo(
        name="backend-service",
        selector=selector or {"app": "backend"},
        ports=ports or [],
        target_ports=target_ports or [],
    )


# ============================================================
# K8S002 — Service selector
# ============================================================


def test_service_selector_without_matching_deployment():
    deployment = make_deployment(
        labels={"app": "frontend"},
    )

    service = make_service(
        selector={"app": "backend"},
    )

    context = KubernetesContext(
        deployments=[deployment],
        services=[service],
    )

    findings = ServiceSelectorRule().check(context)

    assert len(findings) == 1
    assert findings[0].rule_id == "K8S002"


def test_service_selector_with_matching_deployment():
    deployment = make_deployment(
        labels={"app": "backend"},
    )

    service = make_service(
        selector={"app": "backend"},
    )

    context = KubernetesContext(
        deployments=[deployment],
        services=[service],
    )

    findings = ServiceSelectorRule().check(context)

    assert findings == []


# ============================================================
# K8S003 — Duplicate port names
# ============================================================


def test_duplicate_port_name_is_detected():
    deployment = make_deployment(
        ports=[
            ContainerPort(
                name="http",
                port=3000,
            ),
            ContainerPort(
                name="http",
                port=8080,
            ),
        ],
    )

    context = KubernetesContext(
        deployments=[deployment],
        services=[],
    )

    findings = DuplicatePortNameRule().check(context)

    assert len(findings) == 1
    assert findings[0].rule_id == "K8S003"


def test_unique_port_names_have_no_finding():
    deployment = make_deployment(
        ports=[
            ContainerPort(
                name="http",
                port=3000,
            ),
            ContainerPort(
                name="grpc",
                port=5000,
            ),
        ],
    )

    context = KubernetesContext(
        deployments=[deployment],
        services=[],
    )

    findings = DuplicatePortNameRule().check(context)

    assert findings == []


# ============================================================
# K8S004 — Readiness probe
# ============================================================


def test_missing_readiness_probe_is_detected():
    deployment = make_deployment(
        readiness_probe=False,
    )

    context = KubernetesContext(
        deployments=[deployment],
        services=[],
    )

    findings = ReadinessProbeRule().check(context)

    assert len(findings) == 1
    assert findings[0].rule_id == "K8S004"


def test_readiness_probe_has_no_finding():
    deployment = make_deployment(
        readiness_probe=True,
    )

    context = KubernetesContext(
        deployments=[deployment],
        services=[],
    )

    findings = ReadinessProbeRule().check(context)

    assert findings == []


# ============================================================
# K8S005 — Resource configuration
# ============================================================


def test_missing_resources_are_detected():
    deployment = make_deployment(
        resources=False,
    )

    context = KubernetesContext(
        deployments=[deployment],
        services=[],
    )

    findings = ResourceConfigurationRule().check(context)

    assert len(findings) == 1
    assert findings[0].rule_id == "K8S005"


def test_resource_configuration_has_no_finding():
    deployment = make_deployment(
        resources=True,
    )

    context = KubernetesContext(
        deployments=[deployment],
        services=[],
    )

    findings = ResourceConfigurationRule().check(context)

    assert findings == []
