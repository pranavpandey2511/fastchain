"""Vector store index types."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import (
    Any,
    List,
    Optional,
    Protocol,
    Sequence,
    Union,
    runtime_checkable,
)

import fsspec

from pydantic import (
    BaseModel,
    StrictFloat,
    StrictInt,
    StrictStr,
    ValidationError,
    root_validator,
    validator,
)
from schema import BaseNode, BaseComponent

DEFAULT_PERSIST_DIR = "./storage"
DEFAULT_PERSIST_FNAME = "vector_store.json"


@dataclass
class NodeWithEmbedding:
    """Node with embedding.

    Args:
        node (Node): Node
        embedding (List[float]): Embedding

    """

    node: BaseNode
    embedding: List[float]

    @property
    def id(self) -> str:
        return self.node.node_id

    @property
    def ref_doc_id(self) -> str:
        return self.node.ref_doc_id or "None"


@dataclass
class VectorStoreQueryResult:
    """Vector store query result."""

    nodes: Optional[Sequence[BaseNode]] = None
    similarities: Optional[List[float]] = None
    ids: Optional[List[str]] = None


class VectorStoreQueryMode(str, Enum):
    """Vector store query mode."""

    DEFAULT = "default"
    SPARSE = "sparse"
    HYBRID = "hybrid"
    TEXT_SEARCH = "text_search"

    # fit learners
    SVM = "svm"
    LOGISTIC_REGRESSION = "logistic_regression"
    LINEAR_REGRESSION = "linear_regression"

    # maximum marginal relevance
    MMR = "mmr"


class ExactMatchFilter(BaseModel):
    """Exact match metadata filter for vector stores.

    Value uses Strict* types, as int, float and str are compatible types and were all
    converted to string before.

    See: https://docs.pydantic.dev/latest/usage/types/#strict-types"""

    key: str
    value: Union[StrictInt, StrictFloat, StrictStr]


class MetadataFilters(BaseModel):
    """Metadata filters for vector stores.

    Currently only supports exact match filters.
    TODO: support more advanced expressions.
    """

    filters: List[ExactMatchFilter]


class VectorStoreQuerySpec(BaseModel):
    """Schema for a structured request for vector store
    (i.e. to be converted to a VectorStoreQuery).

    Currently only used by VectorIndexAutoRetriever.
    """

    query: str
    filters: List[ExactMatchFilter]
    top_k: Optional[int] = None


class MetadataInfo(BaseModel):
    """Information about a metadata filter supported by a vector store.

    Currently only used by VectorIndexAutoRetriever.
    """

    name: str
    type: str
    description: str


class VectorStoreInfo(BaseModel):
    """Information about a vector store (content and supported metadata filters).

    Currently only used by VectorIndexAutoRetriever.
    """

    metadata_info: List[MetadataInfo]
    content_info: str


@dataclass
class VectorStoreQuery:
    """Vector store query."""

    query_embedding: Optional[List[float]] = None
    similarity_top_k: int = 1
    doc_ids: Optional[List[str]] = None
    node_ids: Optional[List[str]] = None
    query_str: Optional[str] = None
    output_fields: Optional[List[str]] = None
    embedding_field: Optional[str] = None

    mode: VectorStoreQueryMode = VectorStoreQueryMode.DEFAULT

    # NOTE: only for hybrid search (0 for bm25, 1 for vector search)
    alpha: Optional[float] = None

    # metadata filters
    filters: Optional[MetadataFilters] = None

    # only for mmr
    mmr_threshold: Optional[float] = None

    # NOTE: currently only used by postgres hybrid search
    sparse_top_k: Optional[int] = None


@runtime_checkable
class VectorStore(Protocol):
    """Abstract vector store protocol."""

    stores_text: bool
    is_embedding_query: bool = True

    @property
    def client(self) -> Any:
        """Get client."""
        ...

    def add(
        self,
        embedding_results: List[NodeWithEmbedding],
    ) -> List[str]:
        """Add embedding results to vector store."""
        ...

    async def async_add(
        self,
        embedding_results: List[NodeWithEmbedding],
    ) -> List[str]:
        """
        Asynchronously add embedding results to vector store.
        NOTE: this is not implemented for all vector stores. If not implemented,
        it will just call add synchronously.
        """
        return self.add(embedding_results)

    def delete(self, ref_doc_id: str, **delete_kwargs: Any) -> None:
        """
        Delete nodes using with ref_doc_id."""
        ...

    async def adelete(self, ref_doc_id: str, **delete_kwargs: Any) -> None:
        """
        Delete nodes using with ref_doc_id.
        NOTE: this is not implemented for all vector stores. If not implemented,
        it will just call delete synchronously.
        """
        self.delete(ref_doc_id, **delete_kwargs)

    def query(
        self, query: VectorStoreQuery, **kwargs: Any
    ) -> VectorStoreQueryResult:
        """Query vector store."""
        ...

    async def aquery(
        self, query: VectorStoreQuery, **kwargs: Any
    ) -> VectorStoreQueryResult:
        """
        Asynchronously query vector store.
        NOTE: this is not implemented for all vector stores. If not implemented,
        it will just call query synchronously.
        """
        return self.query(query, **kwargs)

    def persist(
        self, persist_path: str, fs: Optional[fsspec.AbstractFileSystem] = None
    ) -> None:
        return None


# TODO: Temp copy of VectorStore for pydantic, can't mix with runtime_checkable
class BasePydanticVectorStore(BaseComponent, ABC):
    """Abstract vector store protocol."""

    stores_text: bool
    is_embedding_query: bool = True

    @property
    @abstractmethod
    def client(self) -> Any:
        """Get client."""

    @abstractmethod
    def add(
        self,
        embedding_results: List[NodeWithEmbedding],
    ) -> List[str]:
        """Add embedding results to vector store."""

    async def async_add(
        self,
        embedding_results: List[NodeWithEmbedding],
    ) -> List[str]:
        """
        Asynchronously add embedding results to vector store.
        NOTE: this is not implemented for all vector stores. If not implemented,
        it will just call add synchronously.
        """
        return self.add(embedding_results)

    @abstractmethod
    def delete(self, ref_doc_id: str, **delete_kwargs: Any) -> None:
        """
        Delete nodes using with ref_doc_id."""

    async def adelete(self, ref_doc_id: str, **delete_kwargs: Any) -> None:
        """
        Delete nodes using with ref_doc_id.
        NOTE: this is not implemented for all vector stores. If not implemented,
        it will just call delete synchronously.
        """
        self.delete(ref_doc_id, **delete_kwargs)

    @abstractmethod
    def query(
        self, query: VectorStoreQuery, **kwargs: Any
    ) -> VectorStoreQueryResult:
        """Query vector store."""

    async def aquery(
        self, query: VectorStoreQuery, **kwargs: Any
    ) -> VectorStoreQueryResult:
        """
        Asynchronously query vector store.
        NOTE: this is not implemented for all vector stores. If not implemented,
        it will just call query synchronously.
        """
        return self.query(query, **kwargs)

    def persist(
        self, persist_path: str, fs: Optional[fsspec.AbstractFileSystem] = None
    ) -> None:
        return None
