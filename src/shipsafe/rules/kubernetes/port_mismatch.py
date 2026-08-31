from shipsafe.parsers.kubernetes import DeploymentInfo, ServiceInfo
from shipsafe.rules.base import Rule
from shipsafe.scanner.result import Finding


class PortMismatchRule(Rule):
    """Detect Kubernetes Services targeting unavailable container ports."""

    rule_id = "K8S001"
    name = "Kubernetes port mismatch"
    description = (
        "Checks whether a Service targets a port exposed by "
        "the selected Deployment."
    )

    def check(
        self,
        context: tuple[DeploymentInfo, ServiceInfo],
    ) -> list[Finding]:
        deployment, service = context

        if not self._selector_matches(
            deployment.labels,
            service.selector,
        ):
            return []

        container_ports = {
            port.port
            for container in deployment.containers
            for port in container.ports
        }

        named_ports = {
            port.name
            for container in deployment.containers
            for port in container.ports
            if port.name
        }

        findings = []

        for target_port in service.target_ports:
            if isinstance(target_port, int):
                if target_port not in container_ports:
                    findings.append(
                        Finding(
                            rule_id=self.rule_id,
                            severity="HIGH",
                            title=self.name,
                            message=(
                                f"Service '{service.name}' targets port "
                                f"{target_port}, but Deployment "
                                f"'{deployment.name}' does not expose it."
                            ),
                        )
                    )

            elif isinstance(target_port, str):
                if target_port not in named_ports:
                    findings.append(
                        Finding(
                            rule_id=self.rule_id,
                            severity="HIGH",
                            title="Kubernetes named port mismatch",
                            message=(
                                f"Service '{service.name}' targets named port "
                                f"'{target_port}', but Deployment "
                                f"'{deployment.name}' does not define it."
                            ),
                        )
                    )

        return findings

    @staticmethod
    def _selector_matches(
        labels: dict[str, str],
        selector: dict[str, str],
    ) -> bool:
        return all(
            labels.get(key) == value
            for key, value in selector.items()
        )
