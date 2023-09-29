from __future__ import annotations

from typing import List, Dict, Union, Optional, Type, Any
import uuid
from pydantic import BaseModel, Field, validator, ValidationError
from docarray import BaseDoc
from docarray.typing import NdArray, NdArrayEmbedding
from uuid import UUID as UUID4

EMBEDDING_SIZE = 512


class Chunk(BaseDoc):
    _id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique ID of the chunk.",
        alias="chunk_id",
    )
    document_id: Optional[UUID4]
    page_id: Optional[UUID4]
    EMBEDDING_SIZE: Optional[int] = Field(const=True)
    embedding: Optional[NdArrayEmbedding[EMBEDDING_SIZE]] = Field(
        is_embedding=True
    )
    content: str
    coordinates: Optional[tuple]
    _previous: Union[Type[Chunk], None] = None
    _next: Union[Type[Chunk], None] = None
