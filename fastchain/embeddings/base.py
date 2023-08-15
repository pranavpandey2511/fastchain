import asyncio
from abc import ABC, abstractmethod
from typing import Callable, Optional, Tuple, Dict, List
import numpy as np

EMB_TYPE = np.ndarray

class BaseEmbedding(ABC):
    def __init__(self, tokenizer: Optional[Callable] = None) -> None:
        self._total_tokens_used = 0
        self._tokenizer = tokenizer
        self._text_queue: List[Tuple[str, str]] = []

    @abstractmethod
    def _get_embedding(self, text: str) -> EMB_TYPE:
        """Retrieve the embedding for a given text."""

    async def _aget_embedding(self, text: str) -> EMB_TYPE:
        """Asynchronous version of _get_embedding."""
        return self._get_embedding(text)

    def get_embedding(self, text: str) -> EMB_TYPE:
        self._total_tokens_used += len(self._tokenizer(text))
        return self._get_embedding(text)

    async def aget_embedding(self, text: str) -> EMB_TYPE:
        self._total_tokens_used += len(self._tokenizer(text))
        return await self._aget_embedding(text)

    def queue_text_for_embedding(self, text_id: str, text: str) -> None:
        """Queue text for embedding."""
        self._text_queue.append((text_id, text))

    def get_queued_text_embeddings(self) -> Dict[str, EMB_TYPE]:
        """Retrieve embeddings for all queued texts."""
        result = {text_id: self.get_embedding(text) for text_id, text in self._text_queue}
        self._text_queue.clear() 
        return result

    async def aget_queued_text_embeddings(self) -> Dict[str, EMB_TYPE]:
        """Asynchronous version of get_queued_text_embeddings."""
        result = {text_id: await self.aget_embedding(text) for text_id, text in self._text_queue}
        self._text_queue.clear() 
        return result

    @property
    def total_tokens_used(self) -> int:
        """get total tokens"""
        return self._total_tokens_used
