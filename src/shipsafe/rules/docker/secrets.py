import re

from shipsafe.parsers.docker import DockerfileInfo
from shipsafe.rules.base import Rule
from shipsafe.scanner.result import Finding


SECRET_PATTERN = re.compile(
    r"\b(password|passwd|secret|api[_-]?key|token|"
    r"access[_-]?key|private[_-]?key)\b\s*=",
    re.IGNORECASE,
)


class DockerSecretRule(Rule):
    """Detect likely hardcoded secrets in Dockerfile instructions."""

    rule_id = "DOCKER005"
    name = "Possible secret in Dockerfile"
    description = (
        "Checks Dockerfile instructions for likely hardcoded secrets."
    )

    def check(
        self,
        context: DockerfileInfo,
    ) -> list[Finding]:
        findings = []

        for instruction in context.instructions:
            if instruction.keyword not in {"ENV", "ARG", "RUN"}:
                continue

            if SECRET_PATTERN.search(instruction.arguments):
                findings.append(
                    Finding(
                        rule_id=self.rule_id,
                        severity="CRITICAL",
                        title=self.name,
                        message=(
                            f"Possible hardcoded secret found in "
                            f"Dockerfile on line "
                            f"{instruction.line_number}."
                        ),
                    )
                )

        return findings
