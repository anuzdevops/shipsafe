from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class ActionUse:
    """A GitHub Action referenced by a workflow."""

    name: str
    version: str
    line_number: int


@dataclass
class WorkflowJob:
    """Information about a GitHub Actions job."""

    name: str
    permissions: object | None
    timeout_minutes: int | None
    uses: list[ActionUse] = field(default_factory=list)


@dataclass
class WorkflowInfo:
    """Parsed GitHub Actions workflow."""

    path: Path
    name: str
    trigger: object
    permissions: object | None
    jobs: list[WorkflowJob] = field(default_factory=list)


def parse_workflow(path: Path) -> WorkflowInfo | None:
    """Parse a GitHub Actions workflow."""

    try:
        content = path.read_text(
            encoding="utf-8",
            errors="ignore",
        )
        data = yaml.safe_load(content)
    except (OSError, yaml.YAMLError):
        return None

    if not isinstance(data, dict):
        return None

    jobs_data = data.get("jobs", {})

    if not isinstance(jobs_data, dict):
        jobs_data = {}

    jobs = []

    for job_name, job_data in jobs_data.items():
        if not isinstance(job_data, dict):
            continue

        actions = []

        steps = job_data.get("steps", [])

        if isinstance(steps, list):
            for index, step in enumerate(steps, start=1):
                if not isinstance(step, dict):
                    continue

                uses = step.get("uses")

                if not isinstance(uses, str):
                    continue

                action_name, version = _split_action(uses)

                actions.append(
                    ActionUse(
                        name=action_name,
                        version=version,
                        line_number=index,
                    )
                )

        timeout = job_data.get("timeout-minutes")

        if not isinstance(timeout, int):
            timeout = None

        jobs.append(
            WorkflowJob(
                name=str(job_name),
                permissions=job_data.get("permissions"),
                timeout_minutes=timeout,
                uses=actions,
            )
        )

    return WorkflowInfo(
        path=path,
        name=str(data.get("name", path.stem)),
        trigger=data.get(True, data.get("on")),
        permissions=data.get("permissions"),
        jobs=jobs,
    )


def _split_action(value: str) -> tuple[str, str]:
    """Split an action reference into name and version."""

    value = value.strip()

    if "@" not in value:
        return value, ""

    name, version = value.rsplit("@", 1)

    return name, version
