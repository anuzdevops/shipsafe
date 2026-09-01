from shipsafe.rules.base import Rule
from shipsafe.scanner.github_actions_context import GitHubActionsContext
from shipsafe.scanner.result import Finding


class ExcessivePermissionsRule(Rule):
    """Detect workflows granting write-all permissions."""

    rule_id = "GHA002"
    name = "Excessive GitHub Actions permissions"
    description = (
        "Checks whether a workflow or job grants unrestricted "
        "write permissions."
    )

    def check(
        self,
        context: GitHubActionsContext,
    ) -> list[Finding]:
        findings = []

        for workflow in context.workflows:
            if workflow.permissions == "write-all":
                findings.append(
                    Finding(
                        rule_id=self.rule_id,
                        severity="HIGH",
                        title=self.name,
                        message=(
                            f"Workflow '{workflow.name}' grants "
                            "write-all permissions."
                        ),
                        file=str(workflow.path),
                    )
                )

            for job in workflow.jobs:
                if job.permissions == "write-all":
                    findings.append(
                        Finding(
                            rule_id=self.rule_id,
                            severity="HIGH",
                            title=self.name,
                            message=(
                                f"Job '{job.name}' grants "
                                "write-all permissions."
                            ),
                            file=str(workflow.path),
                        )
                    )

        return findings
