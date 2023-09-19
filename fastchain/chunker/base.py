from abc import ABC, abstractmethod
from typing import List, Type, Callable
from pydantic import BaseModel, Field, ValidationError, validator
from enum import Enum

from fastchain.chunker.utils import num_tokens_from_string
from fastchain.constants import MAX_CHUNK_SIZE_TOKENS
from fastchain.document.chunk.schema import Chunk

ChunkType = Enum(
    "ChunkType",
    [
        "TEXT",
        "TOKENS",
        "CODE",
        "DOCUMENTATION",
    ],
)


class Chunker(ABC):
    @abstractmethod
    def create_chunks(self, input) -> List[Chunk]:
        ...

    def _postprocess_chunks(self, chunks: List[str]) -> List[str]:
        """Post process and validate chunks."""
        updated_chunks = []
        for entry in chunks:
            if entry.replace(" ", "") == "":
                continue
            updated_chunks.append(entry)
        return updated_chunks
