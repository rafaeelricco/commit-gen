from abc import ABC
from pydantic import BaseModel


class BaseCommand(BaseModel, ABC):
    """
    Immutable base class for all commands in the CQRS system.
    
    Provides automatic validation and serialization through Pydantic.
    Commands represent write operations and must be frozen to ensure immutability.
    """
    
    class Config:
        frozen = True