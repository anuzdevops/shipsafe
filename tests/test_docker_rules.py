from pathlib import Path

from shipsafe.parsers.docker import parse_dockerfile
from shipsafe.rules.docker.healthcheck import HealthcheckRule
from shipsafe.rules.docker.latest_tag import LatestTagRule
from shipsafe.rules.docker.root_user import RootUserRule
from shipsafe.rules.docker.secrets import DockerSecretRule
from shipsafe.rules.docker.unpinned_base_image import (
    UnpinnedBaseImageRule,
)


def make_dockerfile(tmp_path: Path, content: str):
    path = tmp_path / "Dockerfile"
    path.write_text(content, encoding="utf-8")
    return parse_dockerfile(path)


def test_unpinned_base_image_is_detected(tmp_path):
    context = make_dockerfile(
        tmp_path,
        "FROM python\n",
    )

    findings = UnpinnedBaseImageRule().check(context)

    assert len(findings) == 1
    assert findings[0].rule_id == "DOCKER001"


def test_pinned_base_image_has_no_finding(tmp_path):
    context = make_dockerfile(
        tmp_path,
        "FROM python:3.12\n",
    )

    findings = UnpinnedBaseImageRule().check(context)

    assert findings == []


def test_missing_user_is_detected(tmp_path):
    context = make_dockerfile(
        tmp_path,
        "FROM python:3.12\n",
    )

    findings = RootUserRule().check(context)

    assert len(findings) == 1
    assert findings[0].rule_id == "DOCKER002"


def test_non_root_user_has_no_finding(tmp_path):
    context = make_dockerfile(
        tmp_path,
        """
FROM python:3.12
USER 1000
""",
    )

    findings = RootUserRule().check(context)

    assert findings == []


def test_missing_healthcheck_is_detected(tmp_path):
    context = make_dockerfile(
        tmp_path,
        "FROM python:3.12\n",
    )

    findings = HealthcheckRule().check(context)

    assert len(findings) == 1
    assert findings[0].rule_id == "DOCKER003"


def test_healthcheck_has_no_finding(tmp_path):
    context = make_dockerfile(
        tmp_path,
        """
FROM python:3.12
HEALTHCHECK CMD echo healthy
""",
    )

    findings = HealthcheckRule().check(context)

    assert findings == []


def test_latest_tag_is_detected(tmp_path):
    context = make_dockerfile(
        tmp_path,
        "FROM python:latest\n",
    )

    findings = LatestTagRule().check(context)

    assert len(findings) == 1
    assert findings[0].rule_id == "DOCKER004"


def test_specific_latest_safe_tag_has_no_finding(tmp_path):
    context = make_dockerfile(
        tmp_path,
        "FROM python:3.12\n",
    )

    findings = LatestTagRule().check(context)

    assert findings == []


def test_secret_in_env_is_detected(tmp_path):
    context = make_dockerfile(
        tmp_path,
        """
FROM python:3.12
ENV API_KEY=supersecret
""",
    )

    findings = DockerSecretRule().check(context)

    assert len(findings) == 1
    assert findings[0].rule_id == "DOCKER005"


def test_normal_env_has_no_finding(tmp_path):
    context = make_dockerfile(
        tmp_path,
        """
FROM python:3.12
ENV PORT=8000
""",
    )

    findings = DockerSecretRule().check(context)

    assert findings == []
