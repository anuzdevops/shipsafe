from pathlib import Path


def detect_repository(path: str) -> dict[str, bool]:
    root = Path(path)

    return {
        "docker": (root / "Dockerfile").exists(),
        "kubernetes": _contains_kubernetes_files(root),
        "github_actions": (root / ".github" / "workflows").is_dir(),
    }


def _contains_kubernetes_files(root: Path) -> bool:
    for file in root.rglob("*.yaml"):
        if _looks_like_kubernetes(file):
            return True

    for file in root.rglob("*.yml"):
        if _looks_like_kubernetes(file):
            return True

    return False


def _looks_like_kubernetes(file: Path) -> bool:
    try:
        content = file.read_text(errors="ignore")
    except OSError:
        return False

    return (
        "apiVersion:" in content
        and "kind:" in content
        and "metadata:" in content
    )
