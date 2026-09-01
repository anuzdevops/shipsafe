from shipsafe.parsers.docker import DockerfileInfo
from shipsafe.rules.base import Rule
from shipsafe.scanner.result import Finding


class HealthcheckRule(Rule):
    """Detect Dockerfiles without a HEALTHCHECK instruction."""

    rule_id = "DOCKER003"
    name = "Docker image missing healthcheck"
    description = (
        "Checks whether the Dockerfile defines a HEALTHCHECK."
    )

    def check(
        self,
        context: DockerfileInfo,
    ) -> list[Finding]:
        if context.has_healthcheck:
            return []

        return [
            Finding(
                rule_id=self.rule_id,
                severity="MEDIUM",
                title=self.name,
                message=(
                    f"Dockerfile '{context.path.name}' does not define "
                    "a HEALTHCHECK instruction."
                ),
            )
        ]
