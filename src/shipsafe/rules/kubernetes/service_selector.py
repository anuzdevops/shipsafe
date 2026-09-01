from shipsafe.rules.base import Rule
from shipsafe.scanner.context import KubernetesContext
from shipsafe.scanner.result import Finding


class ServiceSelectorRule(Rule):
    """Detect Services that do not select any Deployment."""

    rule_id = "K8S002"
    name = "Kubernetes Service has no matching Deployment"
    description = (
        "Checks whether a Service selector matches at least "
        "one Deployment."
    )

    def check(
        self,
        context: KubernetesContext,
    ) -> list[Finding]:
        findings = []

        for service in context.services:
            matching_deployment = any(
                self._selector_matches(
                    deployment.labels,
                    service.selector,
                )
                for deployment in context.deployments
            )

            if not matching_deployment:
                selector = ", ".join(
                    f"{key}={value}"
                    for key, value in service.selector.items()
                )

                findings.append(
                    Finding(
                        rule_id=self.rule_id,
                        severity="HIGH",
                        title=self.name,
                        message=(
                            f"Service '{service.name}' selects "
                            f"{selector}, but no Deployment "
                            "matches that selector."
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
