from __future__ import annotations

from typing import List, Dict, Union, Optional, Type, Any
import uuid
from pydantic import BaseModel, Field, validator, ValidationError
from docarray import BaseDoc


class Section(BaseDoc):
    _id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique ID of the node.",
        alias="doc_id",
    )
    document_id: uuid.UUID
    content: str
    previous: Type[Section] = None
    next: Type[Section] = None
