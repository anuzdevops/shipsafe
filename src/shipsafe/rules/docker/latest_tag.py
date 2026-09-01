from shipsafe.parsers.docker import DockerfileInfo
from shipsafe.rules.base import Rule
from shipsafe.scanner.result import Finding


class LatestTagRule(Rule):
    """Detect Docker base images explicitly using the latest tag."""

    rule_id = "DOCKER004"
    name = "Docker image uses latest tag"
    description = (
        "Checks whether Docker base images explicitly use the latest tag."
    )

    def check(
        self,
        context: DockerfileInfo,
    ) -> list[Finding]:
        findings = []

        for instruction in context.instructions:
            if instruction.keyword != "FROM":
                continue

            image = instruction.arguments.split(" AS ", 1)[0].strip()

            if image.endswith(":latest"):
                findings.append(
                    Finding(
                        rule_id=self.rule_id,
                        severity="MEDIUM",
                        title=self.name,
                        message=(
                            f"Base image '{image}' on line "
                            f"{instruction.line_number} explicitly uses "
                            "the 'latest' tag."
                        ),
                    )
                )

        return findings
