"""OpenAI embeddings file."""
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
import openai
from tenacity import (
    retry,
    stop_all,
    stop_after_delay,
    stop_after_attempt,
    wait_random_exponential,
)
from fastchain.embedding.base import DEFAULT_EMBED_BATCH_SIZE, BaseEmbedding
from fastchain.llms.openai_utils import validate_openai_api_key
from fastchain.document.base import Document
import numpy as np

EMB_TYPE = np.ndarray
DEFAULT_EMBED_BATCH_SIZE = 10
class OpenAIEmbeddingMode(str, Enum):
    """OpenAI embedding mode."""
    SIMILARITY_MODE = "similarity"
    TEXT_SEARCH_MODE = "text_search"


class OpenAIEmbeddingModelType(str, Enum):
    """OpenAI embedding model type."""
    DAVINCI = "davinci"
    CURIE = "curie"
    BABBAGE = "babbage"
    ADA = "ada"
    TEXT_EMBED_ADA_002 = "text-embedding-ada-002"


class OpenAIEmbeddingModeModel(str, Enum):
    """OpenAI embedding mode model."""

    # davinci
    TEXT_SIMILARITY_DAVINCI = "text-similarity-davinci-001"
    TEXT_SEARCH_DAVINCI_QUERY = "text-search-davinci-query-001"
    TEXT_SEARCH_DAVINCI_DOC = "text-search-davinci-doc-001"

    # curie
    TEXT_SIMILARITY_CURIE = "text-similarity-curie-001"
    TEXT_SEARCH_CURIE_QUERY = "text-search-curie-query-001"
    TEXT_SEARCH_CURIE_DOC = "text-search-curie-doc-001"

    # babbage
    TEXT_SIMILARITY_BABBAGE = "text-similarity-babbage-001"
    TEXT_SEARCH_BABBAGE_QUERY = "text-search-babbage-query-001"
    TEXT_SEARCH_BABBAGE_DOC = "text-search-babbage-doc-001"

    # ada
    TEXT_SIMILARITY_ADA = "text-similarity-ada-001"
    TEXT_SEARCH_ADA_QUERY = "text-search-ada-query-001"
    TEXT_SEARCH_ADA_DOC = "text-search-ada-doc-001"

    # text-embedding-ada-002
    TEXT_EMBED_ADA_002 = "text-embedding-ada-002"


# convenient shorthand
OAEM = OpenAIEmbeddingMode
OAEMT = OpenAIEmbeddingModelType
OAEMM = OpenAIEmbeddingModeModel

EMBED_MAX_TOKEN_LIMIT = 2048


_QUERY_MODE_MODEL_DICT = {
    (OAEM.SIMILARITY_MODE, "davinci"): OAEMM.TEXT_SIMILARITY_DAVINCI,
    (OAEM.SIMILARITY_MODE, "curie"): OAEMM.TEXT_SIMILARITY_CURIE,
    (OAEM.SIMILARITY_MODE, "babbage"): OAEMM.TEXT_SIMILARITY_BABBAGE,
    (OAEM.SIMILARITY_MODE, "ada"): OAEMM.TEXT_SIMILARITY_ADA,
    (OAEM.SIMILARITY_MODE, "text-embedding-ada-002"): OAEMM.TEXT_EMBED_ADA_002,
    (OAEM.TEXT_SEARCH_MODE, "davinci"): OAEMM.TEXT_SEARCH_DAVINCI_QUERY,
    (OAEM.TEXT_SEARCH_MODE, "curie"): OAEMM.TEXT_SEARCH_CURIE_QUERY,
    (OAEM.TEXT_SEARCH_MODE, "babbage"): OAEMM.TEXT_SEARCH_BABBAGE_QUERY,
    (OAEM.TEXT_SEARCH_MODE, "ada"): OAEMM.TEXT_SEARCH_ADA_QUERY,
    (OAEM.TEXT_SEARCH_MODE, "text-embedding-ada-002"): OAEMM.TEXT_EMBED_ADA_002,
}

_TEXT_MODE_MODEL_DICT = {
    (OAEM.SIMILARITY_MODE, "davinci"): OAEMM.TEXT_SIMILARITY_DAVINCI,
    (OAEM.SIMILARITY_MODE, "curie"): OAEMM.TEXT_SIMILARITY_CURIE,
    (OAEM.SIMILARITY_MODE, "babbage"): OAEMM.TEXT_SIMILARITY_BABBAGE,
    (OAEM.SIMILARITY_MODE, "ada"): OAEMM.TEXT_SIMILARITY_ADA,
    (OAEM.SIMILARITY_MODE, "text-embedding-ada-002"): OAEMM.TEXT_EMBED_ADA_002,
    (OAEM.TEXT_SEARCH_MODE, "davinci"): OAEMM.TEXT_SEARCH_DAVINCI_DOC,
    (OAEM.TEXT_SEARCH_MODE, "curie"): OAEMM.TEXT_SEARCH_CURIE_DOC,
    (OAEM.TEXT_SEARCH_MODE, "babbage"): OAEMM.TEXT_SEARCH_BABBAGE_DOC,
    (OAEM.TEXT_SEARCH_MODE, "ada"): OAEMM.TEXT_SEARCH_ADA_DOC,
    (OAEM.TEXT_SEARCH_MODE, "text-embedding-ada-002"): OAEMM.TEXT_EMBED_ADA_002,
}


@retry(
    wait=wait_random_exponential(min=1, max=20),
    stop=stop_all(stop_after_attempt(6), stop_after_delay(60)),
)
def get_embedding(
    text: str, engine: Optional[str] = None, **kwargs: Any
) -> List[float]:
    """Get embedding.

    NOTE: Copied from OpenAI's embedding utils:
    https://github.com/openai/openai-python/blob/main/openai/embeddings_utils.py

    Copied here to avoid importing unnecessary dependencies
    like matplotlib, plotly, scipy, sklearn.

    """
    text = text.replace("\n", " ")
    return openai.Embedding.create(input=[text], model=engine, **kwargs)["data"][0][
        "embedding"
    ]


@retry(
    wait=wait_random_exponential(min=1, max=20),
    stop=stop_all(stop_after_attempt(6), stop_after_delay(60)),
)
async def aget_embedding(
    text: str, engine: Optional[str] = None, **kwargs: Any
) -> List[float]:
    """Asynchronously get embedding.

    NOTE: Copied from OpenAI's embedding utils:
    https://github.com/openai/openai-python/blob/main/openai/embeddings_utils.py

    Copied here to avoid importing unnecessary dependencies
    like matplotlib, plotly, scipy, sklearn.

    """
    # replace newlines, which can negatively affect performance.
    text = text.replace("\n", " ")

    return (await openai.Embedding.acreate(input=[text], model=engine, **kwargs))[
        "data"
    ][0]["embedding"]


@retry(
    wait=wait_random_exponential(min=1, max=20),
    stop=stop_all(stop_after_attempt(6), stop_after_delay(60)),
)
def get_embeddings(
    list_of_text: List[str], engine: Optional[str] = None, **kwargs: Any
) -> List[List[float]]:
    """Get embeddings.

    NOTE: Copied from OpenAI's embedding utils:
    https://github.com/openai/openai-python/blob/main/openai/embeddings_utils.py

    Copied here to avoid importing unnecessary dependencies
    like matplotlib, plotly, scipy, sklearn.

    """
    assert len(list_of_text) <= 2048, "The batch size should not be larger than 2048."

    # replace newlines, which can negatively affect performance.
    list_of_text = [text.replace("\n", " ") for text in list_of_text]

    data = openai.Embedding.create(input=list_of_text, model=engine, **kwargs).data
    return [d["embedding"] for d in data]


@retry(
    wait=wait_random_exponential(min=1, max=20),
    stop=stop_all(stop_after_attempt(6), stop_after_delay(60)),
)
async def aget_embeddings(
    list_of_text: List[str], engine: Optional[str] = None, **kwargs: Any
) -> List[List[float]]:
    """Asynchronously get embeddings.

    NOTE: Copied from OpenAI's embedding utils:
    https://github.com/openai/openai-python/blob/main/openai/embeddings_utils.py

    Copied here to avoid importing unnecessary dependencies
    like matplotlib, plotly, scipy, sklearn.

    """
    assert len(list_of_text) <= 2048, "The batch size should not be larger than 2048."

    # replace newlines, which can negatively affect performance.
    list_of_text = [text.replace("\n", " ") for text in list_of_text]

    data = (
        await openai.Embedding.acreate(input=list_of_text, model=engine, **kwargs)
    ).data
    return [d["embedding"] for d in data]


def get_engine(
    mode: str,
    model: str,
    mode_model_dict: Dict[Tuple[OpenAIEmbeddingMode, str], OpenAIEmbeddingModeModel],
) -> OpenAIEmbeddingModeModel:
    """Get engine."""
    key = (OpenAIEmbeddingMode(mode), OpenAIEmbeddingModelType(model))
    if key not in mode_model_dict:
        raise ValueError(f"Invalid mode, model combination: {key}")
    return mode_model_dict[key]


class OpenAIEmbedding(BaseEmbedding):
    """OpenAI class for embeddings.

    Args:
        mode (str): Mode for embedding.
            Defaults to OpenAIEmbeddingMode.TEXT_SEARCH_MODE.
            Options are:

            - OpenAIEmbeddingMode.SIMILARITY_MODE
            - OpenAIEmbeddingMode.TEXT_SEARCH_MODE

        model (str): Model for embedding.
            Defaults to OpenAIEmbeddingModelType.TEXT_EMBED_ADA_002.
            Options are:

            - OpenAIEmbeddingModelType.DAVINCI
            - OpenAIEmbeddingModelType.CURIE
            - OpenAIEmbeddingModelType.BABBAGE
            - OpenAIEmbeddingModelType.ADA
            - OpenAIEmbeddingModelType.TEXT_EMBED_ADA_002

        deployment_name (Optional[str]): Optional deployment of model. Defaults to None.
            If this value is not None, mode and model will be ignored.
            Only available for using AzureOpenAI.
    """
    def __init__(self,
                 mode: str = OpenAIEmbeddingMode.TEXT_SEARCH_MODE,
                 model: str = OpenAIEmbeddingModelType.TEXT_EMBED_ADA_002,
                 deployment_name: Optional[str] = None,
                 embed_batch_size: int = DEFAULT_EMBED_BATCH_SIZE,
                 tokenizer: Optional[Callable] = None,
                 **kwargs: Any
                 ) -> None:
        super().__init__(tokenizer)
        validate_openai_api_key(kwargs.get("api_key", None), kwargs.get("api_type", None))
        
        self.deployment_name = deployment_name
        self.query_engine = get_engine(mode, model, _QUERY_MODE_MODEL_DICT)
        self.text_engine = get_engine(mode, model, _TEXT_MODE_MODEL_DICT)
        self.openai_kwargs = kwargs

    def _get_embedding(self, content: str) -> List[float]:
        return self._get_text_embedding(content)

    async def _aget_embedding(self, content: str) -> List[float]:
        return await self._aget_text_embedding(content)

    def queue_document_for_embedding(self, document: Document) -> None:
        self._document_queue.append(document)

    def _process_documents(self, async_mode: bool = False) -> Dict[str, Dict[str, EMB_TYPE]]:
        result = {}
        for document in self._document_queue:
            doc_embeddings = {}
            for page in document.pages or []:
                for chunk in page.chunks or []:
                    emb_func = self.aget_chunk_embedding if async_mode else self.get_chunk_embedding
                    doc_embeddings[chunk._id] = emb_func(chunk)
            for chunk in document.chunks or []:
                emb_func = self.aget_chunk_embedding if async_mode else self.get_chunk_embedding
                doc_embeddings[chunk._id] = emb_func(chunk)
            result[document._id] = doc_embeddings
        self._document_queue.clear()
        return result

    def get_queued_document_embeddings(self) -> Dict[str, Dict[str, EMB_TYPE]]:
        return self._process_documents()

    async def aget_queued_document_embeddings(self) -> Dict[str, Dict[str, EMB_TYPE]]:
        return await self._process_documents(async_mode=True)

    def _get_text_embedding(self, text: str) -> List[float]:
        """Get text embedding."""
        return get_embedding(
            text,
            engine=self.text_engine,
            deployment_id=self.deployment_name,
            **self.openai_kwargs
        )

    async def _aget_text_embedding(self, text: str) -> List[float]:
        """Asynchronously get text embedding."""
        return await aget_embedding(
            text,
            engine=self.text_engine,
            deployment_id=self.deployment_name,
            **self.openai_kwargs
        )

    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get text embeddings."""
        return get_embeddings(
            texts,
            engine=self.text_engine,
            deployment_id=self.deployment_name,
            **self.openai_kwargs
        )

    async def _aget_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Asynchronously get text embeddings."""
        return await aget_embeddings(
            texts,
            engine=self.text_engine,
            deployment_id=self.deployment_name,
            **self.openai_kwargs
        )