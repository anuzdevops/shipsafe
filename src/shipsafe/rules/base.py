from abc import ABC, abstractmethod
from typing import Any

from shipsafe.scanner.result import Finding


class Rule(ABC):
    """Base class for all ShipSafe rules."""

    rule_id: str
    name: str
    description: str

    @abstractmethod
    def check(self, context: Any) -> list[Finding]:
        """Run the rule against the supplied context."""
        raise NotImplementedError
