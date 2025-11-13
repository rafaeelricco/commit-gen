"""
Base command classes for the CQRS pattern implementation.

This module provides the foundation for all command objects in the application.
Commands represent write operations and are designed to be immutable through Pydantic's
frozen model configuration, ensuring data integrity throughout the command processing pipeline.
"""

from abc import ABC
from pydantic import BaseModel, ConfigDict


class BaseCommand(BaseModel, ABC):
    """
    Immutable base class for all commands in the CQRS system.
    
    Provides automatic validation and serialization through Pydantic.
    Commands represent write operations and must be frozen to ensure immutability.
    """
    
    model_config = ConfigDict(frozen=True)