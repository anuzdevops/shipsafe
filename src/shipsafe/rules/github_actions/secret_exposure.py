from shipsafe.rules.base import Rule
from shipsafe.scanner.github_actions_context import GitHubActionsContext
from shipsafe.scanner.result import Finding


class SecretExposureRule(Rule):
    """Detect obvious hard-coded secrets in workflow configuration."""

    rule_id = "GHA003"
    name = "Potential hard-coded secret"
    description = (
        "Checks workflow configuration for obvious hard-coded "
        "credential values."
    )

    sensitive_keys = (
        "password",
        "passwd",
        "token",
        "secret",
        "api_key",
        "apikey",
        "access_key",
        "private_key",
    )

    def check(
        self,
        context: GitHubActionsContext,
    ) -> list[Finding]:
        findings = []

        for workflow in context.workflows:
            try:
                content = workflow.path.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )
            except OSError:
                continue

            for line_number, line in enumerate(
                content.splitlines(),
                start=1,
            ):
                stripped = line.strip().lower()

                if stripped.startswith("#"):
                    continue

                if "${{ secrets." in stripped:
                    continue

                if ":" not in stripped:
                    continue

                key, value = stripped.split(":", 1)

                key = key.strip()
                value = value.strip().strip("'\"")

                if not any(
                    sensitive in key
                    for sensitive in self.sensitive_keys
                ):
                    continue

                if not value:
                    continue

                if value.startswith("${{"):
                    continue

                findings.append(
                    Finding(
                        rule_id=self.rule_id,
                        severity="CRITICAL",
                        title=self.name,
                        message=(
                            f"Workflow appears to contain a hard-coded "
                            f"secret value near line {line_number}."
                        ),
                        file=str(workflow.path),
                    )
                )

        return findings
