from shipsafe.rules.base import Rule
from shipsafe.scanner.github_actions_context import GitHubActionsContext
from shipsafe.scanner.result import Finding


class PullRequestTargetRule(Rule):
    """Detect workflows triggered by pull_request_target."""

    rule_id = "GHA005"
    name = "Dangerous pull_request_target trigger"
    description = (
        "Checks whether workflows use pull_request_target, which "
        "can expose repository privileges to untrusted code."
    )

    def check(
        self,
        context: GitHubActionsContext,
    ) -> list[Finding]:
        findings = []

        for workflow in context.workflows:
            trigger = workflow.trigger

            if isinstance(trigger, list):
                dangerous = "pull_request_target" in trigger
            elif isinstance(trigger, dict):
                dangerous = "pull_request_target" in trigger
            else:
                dangerous = trigger == "pull_request_target"

            if dangerous:
                findings.append(
                    Finding(
                        rule_id=self.rule_id,
                        severity="CRITICAL",
                        title=self.name,
                        message=(
                            f"Workflow '{workflow.name}' uses "
                            "pull_request_target."
                        ),
                        file=str(workflow.path),
                    )
                )

        return findings
