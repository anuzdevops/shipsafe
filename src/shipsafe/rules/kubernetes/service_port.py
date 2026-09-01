from shipsafe.rules.base import Rule
from shipsafe.scanner.context import KubernetesContext
from shipsafe.scanner.result import Finding


class DuplicatePortNameRule(Rule):
    """Detect duplicate named container ports in a Deployment."""

    rule_id = "K8S003"
    name = "Kubernetes duplicate port name"
    description = (
        "Checks whether a Deployment defines the same named "
        "container port more than once."
    )

    def check(
        self,
        context: KubernetesContext,
    ) -> list[Finding]:
        findings = []

        for deployment in context.deployments:
            port_names: dict[str, list[str]] = {}

            for container in deployment.containers:
                for port in container.ports:
                    if not port.name:
                        continue

                    port_names.setdefault(port.name, []).append(
                        container.name
                    )

            for port_name, containers in port_names.items():
                if len(containers) > 1:
                    findings.append(
                        Finding(
                            rule_id=self.rule_id,
                            severity="MEDIUM",
                            title=self.name,
                            message=(
                                f"Deployment '{deployment.name}' defines "
                                f"container port name '{port_name}' more "
                                "than once."
                            ),
                        )
                    )

        return findings
