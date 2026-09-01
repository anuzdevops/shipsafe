from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class ContainerPort:
    name: str | None
    port: int


@dataclass
class ContainerInfo:
    name: str
    ports: list[ContainerPort] = field(default_factory=list)
    has_readiness_probe: bool = False
    has_resources: bool = False


@dataclass
class DeploymentInfo:
    name: str
    labels: dict[str, str]
    containers: list[ContainerInfo]


@dataclass
class ServicePort:
    port: int
    target_port: int | str | None
    name: str | None = None


@dataclass
class ServiceInfo:
    name: str
    selector: dict[str, str]
    ports: list[ServicePort] = field(default_factory=list)
    target_ports: list[int | str] = field(default_factory=list)


def parse_kubernetes_file(path: Path) -> list[dict]:
    """Parse a YAML file and return Kubernetes resources."""
    resources = []

    try:
        with path.open("r", encoding="utf-8") as file:
            documents = yaml.safe_load_all(file)

            for document in documents:
                if not isinstance(document, dict):
                    continue

                if "apiVersion" not in document:
                    continue

                if "kind" not in document:
                    continue

                if "metadata" not in document:
                    continue

                resources.append(document)

    except (OSError, yaml.YAMLError):
        return []

    return resources


def extract_deployment(resource: dict) -> DeploymentInfo | None:
    """Extract useful information from a Kubernetes Deployment."""
    if resource.get("kind") != "Deployment":
        return None

    metadata = resource.get("metadata", {})
    spec = resource.get("spec", {})
    template = spec.get("template", {})
    template_metadata = template.get("metadata", {})
    pod_spec = template.get("spec", {})

    containers = []

    for container in pod_spec.get("containers", []):
        ports = []

        for port in container.get("ports", []):
            container_port = port.get("containerPort")

            if isinstance(container_port, int):
                ports.append(
                    ContainerPort(
                        name=port.get("name"),
                        port=container_port,
                    )
                )

        containers.append(
            ContainerInfo(
                name=container.get("name", "unknown"),
                ports=ports,
                has_readiness_probe=bool(
                    container.get("readinessProbe")
                ),
                has_resources=bool(
                    container.get("resources")
                ),
            )
        )

    return DeploymentInfo(
        name=metadata.get("name", "unknown"),
        labels=template_metadata.get("labels", {}),
        containers=containers,
    )


def extract_service(resource: dict) -> ServiceInfo | None:
    """Extract useful information from a Kubernetes Service."""
    if resource.get("kind") != "Service":
        return None

    metadata = resource.get("metadata", {})
    spec = resource.get("spec", {})

    service_ports = []
    target_ports = []

    for port in spec.get("ports", []):
        service_port = port.get("port")
        target_port = port.get("targetPort")

        if isinstance(service_port, int):
            service_ports.append(
                ServicePort(
                    name=port.get("name"),
                    port=service_port,
                    target_port=target_port,
                )
            )

        if isinstance(target_port, (int, str)):
            target_ports.append(target_port)

    return ServiceInfo(
        name=metadata.get("name", "unknown"),
        selector=spec.get("selector", {}),
        ports=service_ports,
        target_ports=target_ports,
    )
