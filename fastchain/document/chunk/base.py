from __future__ import annotations

from typing import List, Dict, Union, Optional, Type, Any
import uuid
from pydantic import BaseModel, Field, validator, ValidationError
from docarray import BaseDoc
from docarray.typing import NdArray, NdArrayEmbedding


class Chunk(BaseDoc):
    _id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique ID of the chunk.",
        alias="chunk_id",
    )
    doc_id: Optional[UUID4]
    seq_id: Optional[UUID4]
    EMBEDDING_SIZE: Optional[int] = Field(default=512, const=True)
    embedding: Optional[NdArrayEmbedding[EMBEDDING_SIZE]] = Field(
        is_embedding=True
    )
    content: str
    previous: Union[Type[Chunk], None] = None
    next: Union[Type[Chunk], None] = None
