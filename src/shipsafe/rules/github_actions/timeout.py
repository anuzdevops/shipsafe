from shipsafe.rules.base import Rule
from shipsafe.scanner.github_actions_context import GitHubActionsContext
from shipsafe.scanner.result import Finding


class MissingTimeoutRule(Rule):
    """Detect jobs without a timeout."""

    rule_id = "GHA004"
    name = "Missing GitHub Actions job timeout"
    description = (
        "Checks whether GitHub Actions jobs define a timeout."
    )

    def check(
        self,
        context: GitHubActionsContext,
    ) -> list[Finding]:
        findings = []

        for workflow in context.workflows:
            for job in workflow.jobs:
                if job.timeout_minutes is None:
                    findings.append(
                        Finding(
                            rule_id=self.rule_id,
                            severity="MEDIUM",
                            title=self.name,
                            message=(
                                f"Job '{job.name}' in workflow "
                                f"'{workflow.name}' does not define "
                                "timeout-minutes."
                            ),
                            file=str(workflow.path),
                        )
                    )

        return findings
