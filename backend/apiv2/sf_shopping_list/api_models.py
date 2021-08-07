# generated by datamodel-codegen:
#   filename:  openapi.yaml
#   timestamp: 2021-08-05T22:29:31+00:00

from __future__ import annotations

from datetime import datetime
from typing import List
from uuid import UUID

from aws_lambda_powertools.utilities.parser import BaseModel
from pydantic import Field


class ListModel(BaseModel):
    id: UUID = Field(..., description='ID of a list in a shortened UUID format')
    userId: str = Field(..., description='User identifier of an owner of a list')
    listName: str = Field(..., description='Title of a list given by the owner')
    createdAt: datetime = Field(..., description='Timestamp of list creation')
    items: List[str] = Field(..., description='List of list items')
    guests: List[str] = Field(
        ..., description='List of other user who can access the list'
    )


class NewList(BaseModel):
    name: str = Field(..., description='Name of the new list')
    items: List[str] = Field(..., description='List of list items')
    guests: List[str] = Field(
        ..., description='List of IDs of users having access to the list'
    )


class Invitation(BaseModel):
    id: UUID = Field(..., description='ID of an invintation in shortened UUID format')
    listId: UUID = Field(..., description='ID of a list the invintation is about')
    validUntil: datetime = Field(..., description='Invitation expiration time')