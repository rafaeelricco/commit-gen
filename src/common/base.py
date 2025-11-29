"""
Base classes and data structures for the application.

This module provides fundamental building blocks for immutable data structures
used throughout the application, ensuring consistency and type safety.
"""

from pydantic import BaseModel, ConfigDict
from common.json import FromJSON, ToJSON


class BaseFrozen(BaseModel):
    """
    A frozen base model class
    """

    model_config = ConfigDict(
        strict=True,  # no type coercion
        frozen=True,  # make immutable
        arbitrary_types_allowed=False,  # properties that don't inherit from BaseModel
        extra="forbid",  # disallow extra fields
    )


class BaseMutable(BaseModel):
    """
    A mutable base model class
    """

    model_config = ConfigDict(
        strict=True,  # no type coercion
        frozen=False,  # make mutable
        arbitrary_types_allowed=False,  # properties that don't inherit from BaseModel
        extra="forbid",  # disallow extra fields
    )


class BaseMutableArbitrary(BaseModel):
    """
    A mutable base model class
    """

    model_config = ConfigDict(
        strict=True,  # no type coercion
        frozen=False,  # make mutable
        arbitrary_types_allowed=True,  # properties that don't inherit from BaseModel
        extra="forbid",  # disallow extra fields
    )


class BaseFrozenArbitrary(BaseModel):
    """
    A mutable base model class
    """

    model_config = ConfigDict(
        strict=True,  # no type coercion
        frozen=True,  # make mutable
        arbitrary_types_allowed=True,  # properties that don't inherit from BaseModel
        extra="forbid",  # disallow extra fields
    )


class BaseSerializable(BaseFrozen, FromJSON, ToJSON):
    pass
