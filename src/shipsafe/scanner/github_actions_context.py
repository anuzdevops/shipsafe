from dataclasses import dataclass, field

from shipsafe.parsers.github_actions import WorkflowInfo


@dataclass
class GitHubActionsContext:
    """All parsed GitHub Actions workflows."""

    workflows: list[WorkflowInfo] = field(default_factory=list)
