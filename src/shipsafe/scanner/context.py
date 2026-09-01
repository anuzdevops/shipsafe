from dataclasses import dataclass, field

from shipsafe.parsers.kubernetes import (
    DeploymentInfo,
    ServiceInfo,
)


@dataclass
class KubernetesContext:
    """All parsed Kubernetes resources available to rules."""

    deployments: list[DeploymentInfo] = field(default_factory=list)
    services: list[ServiceInfo] = field(default_factory=list)
