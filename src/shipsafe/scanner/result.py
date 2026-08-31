from dataclasses import dataclass


@dataclass
class Finding:
    rule_id: str
    severity: str
    title: str
    message: str
    file: str | None = None
