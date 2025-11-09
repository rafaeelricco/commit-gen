from abc import ABC, abstractmethod
from typing import TypeVar, Generic
from common.command.base_command import BaseCommand

C = TypeVar('C', bound=BaseCommand)


class BaseCommandHandler(Generic[C], ABC):
    """
    Abstract interface for command handlers in the CQRS system.
    
    Each handler processes a specific command type and returns an HTTP response tuple.
    Implementations must define the business logic for handling their command type.
    """
    
    @abstractmethod
    async def handle_command(self, command: C) -> tuple[dict, int]:
        """
        Process a command and return HTTP response data.
        
        Args:
            command: The validated command to process
            
        Returns:
            Tuple of (response_data, status_code) for HTTP response
        """
        pass