from __future__ import annotations

from typing import List, Dict, Union, Optional, Type, Any
import uuid
from pydantic import BaseModel, Field, validator, ValidationError
from docarray import BaseDoc
from docarray.typing import NdArray, NdArrayEmbedding


class Section(BaseDoc):
    _id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique ID of the node.",
        alias="doc_id",
    )
    EMBEDDING_SIZE: int
    embedding: Optional[NdArrayEmbedding[EMBEDDING_SIZE]] = Field(
        is_embedding=True
    )
    content: str
    previous: Union[Type[Section], None] = None
    next: Union[Type[Section], None] = None
