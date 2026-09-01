from shipsafe.rules.base import Rule
from shipsafe.scanner.github_actions_context import GitHubActionsContext
from shipsafe.scanner.result import Finding


class UnpinnedActionRule(Rule):
    """Detect third-party actions using mutable references."""

    rule_id = "GHA001"
    name = "Unpinned third-party GitHub Action"
    description = (
        "Checks whether third-party GitHub Actions use immutable "
        "or versioned references."
    )

    trusted_actions = {
        "actions/checkout",
        "actions/setup-python",
        "actions/setup-node",
        "actions/setup-java",
        "actions/upload-artifact",
        "actions/download-artifact",
        "actions/cache",
    }

    def check(
        self,
        context: GitHubActionsContext,
    ) -> list[Finding]:
        findings = []

        for workflow in context.workflows:
            for job in workflow.jobs:
                for action in job.uses:
                    if action.name in self.trusted_actions:
                        continue

                    if action.version in {"", "main", "master", "latest"}:
                        findings.append(
                            Finding(
                                rule_id=self.rule_id,
                                severity="HIGH",
                                title=self.name,
                                message=(
                                    f"GitHub Action '{action.name}' "
                                    f"uses mutable reference "
                                    f"'{action.version or 'none'}'."
                                ),
                                file=str(workflow.path),
                            )
                        )

        return findings
