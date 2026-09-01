from shipsafe.rules.base import Rule
from shipsafe.scanner.result import Finding
from shipsafe.parsers.docker import DockerfileInfo


class UnpinnedBaseImageRule(Rule):
    """Detect FROM instructions without an explicit image tag."""

    rule_id = "DOCKER001"
    name = "Unpinned Docker base image"
    description = (
        "Checks whether Docker base images specify an explicit tag."
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

            if ":" not in image:
                findings.append(
                    Finding(
                        rule_id=self.rule_id,
                        severity="HIGH",
                        title=self.name,
                        message=(
                            f"Base image '{image}' on line "
                            f"{instruction.line_number} has no explicit tag."
                        ),
                    )
                )

        return findings
