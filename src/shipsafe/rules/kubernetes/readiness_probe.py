from shipsafe.rules.base import Rule
from shipsafe.scanner.context import KubernetesContext
from shipsafe.scanner.result import Finding


class ReadinessProbeRule(Rule):
    """Detect Deployments without readiness probes."""

    rule_id = "K8S004"
    name = "Kubernetes missing readiness probe"
    description = (
        "Checks whether containers define a readiness probe."
    )

    def check(
        self,
        context: KubernetesContext,
    ) -> list[Finding]:
        findings = []

        for deployment in context.deployments:
            for container in deployment.containers:
                if not container.has_readiness_probe:
                    findings.append(
                        Finding(
                            rule_id=self.rule_id,
                            severity="MEDIUM",
                            title=self.name,
                            message=(
                                f"Deployment '{deployment.name}' "
                                f"container '{container.name}' "
                                "does not define a readiness probe."
                            ),
                        )
                    )

        return findings
