from pathlib import Path

from shipsafe.parsers.docker import parse_dockerfile


def test_parse_dockerfile(tmp_path: Path):
    dockerfile = tmp_path / "Dockerfile"

    dockerfile.write_text(
        """
FROM python:3.12

WORKDIR /app

COPY . .

USER 1000

HEALTHCHECK CMD curl --fail http://localhost:8000/health
""",
        encoding="utf-8",
    )

    result = parse_dockerfile(dockerfile)

    assert len(result.instructions) == 5

    assert result.base_images == ["python:3.12"]
    assert result.has_user_instruction is True
    assert result.has_healthcheck is True


def test_parse_empty_dockerfile(tmp_path: Path):
    dockerfile = tmp_path / "Dockerfile"

    dockerfile.write_text(
        "",
        encoding="utf-8",
    )

    result = parse_dockerfile(dockerfile)

    assert result.instructions == []
    assert result.base_images == []
    assert result.has_user_instruction is False
    assert result.has_healthcheck is False
