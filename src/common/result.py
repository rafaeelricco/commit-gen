from typing import TypeVar, Generic, Callable, Union, List, Any
from dataclasses import dataclass

F = TypeVar('F')  # Failure type
S = TypeVar('S')  # Success type
T = TypeVar('T')


@dataclass(frozen=True)
class Err(Generic[F]):
    """Error variant containing failure value."""
    error: F


@dataclass(frozen=True)
class Ok(Generic[S]):
    """Success variant containing success value."""
    value: S


Unwrapped = Union[Err[F], Ok[S]]


@dataclass(frozen=True)
class Result(Generic[F, S]):
    """
    Result type representing either failure (Err) or success (Ok).
    Eliminates the need for try-catch blocks through functional composition.
    """
    inner: Unwrapped[F, S]
    
    def map(self, func: Callable[[S], T]) -> 'Result[F, T]':
        """Transform the success value if present."""
        match self.inner:
            case Ok(value=value):
                return Result(Ok(func(value)))
            case Err(error=error):
                return Result(Err(error))
    
    def map_err(self, func: Callable[[F], T]) -> 'Result[T, S]':
        """Transform the error value if present."""
        match self.inner:
            case Ok(value=value):
                return Result(Ok(value))
            case Err(error=error):
                return Result(Err(func(error)))
    
    def then(self, func: Callable[[S], 'Result[F, T]']) -> 'Result[F, T]':
        """Chain operations that return Result (flatMap/bind)."""
        match self.inner:
            case Ok(value=value):
                return func(value)
            case Err(error=error):
                return Result(Err(error))
    
    def unwrap(self) -> S:
        """Extract the success value or raise an exception."""
        match self.inner:
            case Ok(value=value):
                return value
            case Err(error=error):
                raise RuntimeError(f"Called unwrap on an Err value: {error}")
    
    def unwrap_or(self, default: S) -> S:
        """Extract the success value or return default."""
        match self.inner:
            case Ok(value=value):
                return value
            case Err():
                return default
    
    @property
    def is_ok(self) -> bool:
        """Check if this is a success result."""
        return isinstance(self.inner, Ok)
    
    @property
    def is_err(self) -> bool:
        """Check if this is an error result."""
        return isinstance(self.inner, Err)
    
    @staticmethod
    def traverse(items: List[T], func: Callable[[T], 'Result[F, S]']) -> 'Result[F, List[S]]':
        """Apply function to each item, collecting results."""
        results = []
        for item in items:
            result = func(item)
            match result.inner:
                case Ok(value=value):
                    results.append(value)
                case Err(error=error):
                    return Result(Err(error))
        return Result(Ok(results))


def try_catch(func: Callable[[], S]) -> Result[Exception, S]:
    """
    Execute a function and wrap the result in Result type.
    Captures any exception and returns it as Err.
    """
    try:
        return Result(Ok(func()))
    except Exception as e:
        return Result(Err(e))


def safe(func: Callable[..., S]) -> Callable[..., Result[Exception, S]]:
    """
    Decorator that wraps a function to return Result instead of raising exceptions.
    """
    def wrapper(*args: Any, **kwargs: Any) -> Result[Exception, S]:
        return try_catch(lambda: func(*args, **kwargs))
    return wrapper