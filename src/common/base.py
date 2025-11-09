from dataclasses import dataclass

@dataclass(frozen=True)
class BaseFrozen:
    """Base class for immutable data structures."""
    pass