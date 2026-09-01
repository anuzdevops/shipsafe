from pathlib import Path

from shipsafe.parsers.github_actions import parse_workflow
from shipsafe.rules.github_actions import (
    ExcessivePermissionsRule,
    MissingTimeoutRule,
    PullRequestTargetRule,
    SecretExposureRule,
    UnpinnedActionRule,
)
from shipsafe.scanner.github_actions_context import GitHubActionsContext


def create_workflow(tmp_path: Path, content: str) -> GitHubActionsContext:
    workflow = tmp_path / "test.yml"
    workflow.write_text(content, encoding="utf-8")

    parsed = parse_workflow(workflow)

    assert parsed is not None

    return GitHubActionsContext(workflows=[parsed])


def test_unpinned_third_party_action(tmp_path: Path):
    context = create_workflow(
        tmp_path,
        """
name: Test
on: push

jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: evil-org/action@main
""",
    )

    findings = UnpinnedActionRule().check(context)

    assert len(findings) == 1
    assert findings[0].rule_id == "GHA001"


def test_pinned_third_party_action_has_no_finding(tmp_path: Path):
    context = create_workflow(
        tmp_path,
        """
name: Test
on: push

jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: evil-org/action@v1.2.3
""",
    )

    findings = UnpinnedActionRule().check(context)

    assert findings == []


def test_write_all_permissions_detected(tmp_path: Path):
    context = create_workflow(
        tmp_path,
        """
name: Test
on: push

permissions: write-all

jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - run: echo hello
""",
    )

    findings = ExcessivePermissionsRule().check(context)

    assert len(findings) == 1
    assert findings[0].rule_id == "GHA002"


def test_hard_coded_secret_detected(tmp_path: Path):
    context = create_workflow(
        tmp_path,
        """
name: Test
on: push

jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - run: echo hello
        env:
          API_KEY: super-secret-value
""",
    )

    findings = SecretExposureRule().check(context)

    assert len(findings) == 1
    assert findings[0].rule_id == "GHA003"


def test_missing_timeout_detected(tmp_path: Path):
    context = create_workflow(
        tmp_path,
        """
name: Test
on: push

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: echo hello
""",
    )

    findings = MissingTimeoutRule().check(context)

    assert len(findings) == 1
    assert findings[0].rule_id == "GHA004"


def test_timeout_has_no_finding(tmp_path: Path):
    context = create_workflow(
        tmp_path,
        """
name: Test
on: push

jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - run: echo hello
""",
    )

    findings = MissingTimeoutRule().check(context)

    assert findings == []


def test_pull_request_target_detected(tmp_path: Path):
    context = create_workflow(
        tmp_path,
        """
name: Test
on:
  pull_request_target:

jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - run: echo hello
""",
    )

    findings = PullRequestTargetRule().check(context)

    assert len(findings) == 1
    assert findings[0].rule_id == "GHA005"


def test_normal_pull_request_has_no_finding(tmp_path: Path):
    context = create_workflow(
        tmp_path,
        """
name: Test
on:
  pull_request:

jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - run: echo hello
""",
    )

    findings = PullRequestTargetRule().check(context)

    assert findings == []
