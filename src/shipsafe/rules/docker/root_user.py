from shipsafe.parsers.docker import DockerfileInfo
from shipsafe.rules.base import Rule
from shipsafe.scanner.result import Finding


class RootUserRule(Rule):
    """Detect Dockerfiles that explicitly run as root."""

    rule_id = "DOCKER002"
    name = "Docker container runs as root"
    description = (
        "Checks whether the final Docker image explicitly runs as root."
    )

    def check(
        self,
        context: DockerfileInfo,
    ) -> list[Finding]:
        findings = []

        user_instructions = [
            instruction
            for instruction in context.instructions
            if instruction.keyword == "USER"
        ]

        if not user_instructions:
            findings.append(
                Finding(
                    rule_id=self.rule_id,
                    severity="HIGH",
                    title=self.name,
                    message=(
                        "Dockerfile does not define a non-root USER. "
                        "The container may run as root."
                    ),
                )
            )

            return findings

        final_user = user_instructions[-1]

        if final_user.arguments.strip().lower() in {
            "root",
            "0",
            "root:root",
            "0:0",
        }:
            findings.append(
                Finding(
                    rule_id=self.rule_id,
                    severity="HIGH",
                    title=self.name,
                    message=(
                        f"Dockerfile explicitly switches to root on line "
                        f"{final_user.line_number}."
                    ),
                )
            )

        return findings
