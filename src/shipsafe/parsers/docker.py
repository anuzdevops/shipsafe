from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class DockerInstruction:
    """A single Dockerfile instruction."""

    keyword: str
    arguments: str
    line_number: int


@dataclass
class DockerfileInfo:
    """Parsed information about a Dockerfile."""

    path: Path
    instructions: list[DockerInstruction] = field(default_factory=list)

    @property
    def has_user_instruction(self) -> bool:
        """Return whether the Dockerfile defines a USER instruction."""
        return any(
            instruction.keyword == "USER"
            for instruction in self.instructions
        )

    @property
    def has_healthcheck(self) -> bool:
        """Return whether the Dockerfile defines a HEALTHCHECK."""
        return any(
            instruction.keyword == "HEALTHCHECK"
            for instruction in self.instructions
        )

    @property
    def base_images(self) -> list[str]:
        """Return all images referenced by FROM instructions."""
        return [
            instruction.arguments
            for instruction in self.instructions
            if instruction.keyword == "FROM"
        ]


def parse_dockerfile(path: Path) -> DockerfileInfo:
    """Parse a Dockerfile into structured instructions."""

    instructions: list[DockerInstruction] = []

    try:
        lines = path.read_text(
            encoding="utf-8",
            errors="ignore",
        ).splitlines()
    except OSError:
        return DockerfileInfo(path=path)

    for line_number, line in enumerate(lines, start=1):
        stripped = line.strip()

        if not stripped or stripped.startswith("#"):
            continue

        parts = stripped.split(maxsplit=1)

        keyword = parts[0].upper()
        arguments = parts[1] if len(parts) > 1 else ""

        instructions.append(
            DockerInstruction(
                keyword=keyword,
                arguments=arguments,
                line_number=line_number,
            )
        )

    return DockerfileInfo(
        path=path,
        instructions=instructions,
    )
