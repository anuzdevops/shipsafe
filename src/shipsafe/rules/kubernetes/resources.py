from shipsafe.rules.base import Rule
from shipsafe.scanner.context import KubernetesContext
from shipsafe.scanner.result import Finding


class ResourceConfigurationRule(Rule):
    """Detect Deployments without container resource configuration."""

    rule_id = "K8S005"
    name = "Kubernetes missing resource configuration"
    description = (
        "Checks whether containers define CPU and memory resources."
    )

    def check(
        self,
        context: KubernetesContext,
    ) -> list[Finding]:
        findings = []

        for deployment in context.deployments:
            for container in deployment.containers:
                if not container.has_resources:
                    findings.append(
                        Finding(
                            rule_id=self.rule_id,
                            severity="MEDIUM",
                            title=self.name,
                            message=(
                                f"Deployment '{deployment.name}' "
                                f"container '{container.name}' "
                                "does not define resource requests "
                                "or limits."
                            ),
                        )
                    )

        return findings
