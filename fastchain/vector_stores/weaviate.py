from docarray.index.backends.weaviate import (
    WeaviateDocumentIndex,
    EmbeddedOptions,
)
from typing import List

from docarray import DocList
import os
from dotenv import load_dotenv

from fastchain.indexers.base import VectorStore
from fastchain.document.chunk.base import Chunk


class WeaviateStore(VectorStore):
    def __init__(self, host: str, auth_method: str = "none"):
        self.host = host
        self.auth_method = auth_method
        connection = self._connect_to_store(host, auth_method)

        return connection

    def _connect_to_store(host: str, auth_method: str = "none"):
        if auth_method == "none":
            dbconfig = WeaviateDocumentIndex.DBConfig(
                embedded_options=EmbeddedOptions()
            )
        elif auth_method == "password":
            dbconfig = WeaviateDocumentIndex.DBConfig(
                username=os.environ.get("WEAVIATE_USERNAME"),
                PASSWORD=os.environ.get("WEAVIATE_PASSWORD"),
                host=host,
            )
        elif auth_method == "api":
            dbconfig = WeaviateDocumentIndex.DBConfig(
                auth_api_key=os.environ.get(
                    "WEAVIATE_API_KEY"
                ),  # Replace with your own API key
                host="http://localhost:8080",  # Replace with your endpoint
            )

        doc_index = WeaviateDocumentIndex[Chunk](db_config=dbconfig)

    def _create_index(self):
        batch_config = {
            "batch_size": 20,
            "dynamic": False,
            "timeout_retries": 3,
            "num_workers": 1,
        }

        runtimeconfig = WeaviateDocumentIndex.RuntimeConfig(
            batch_config=batch_config
        )

        self.store = WeaviateDocumentIndex[Chunk]()
        self.store.configure(runtimeconfig)  # Batch settings being passed on

    def index(self, chunks: DocList[Chunk]):
        self.store.index(chunks)

    def query(self, query: Document, top_k: int = 5):

    # find similar documents
    matches, scores = self.doc_index.find(query, limit=top_k)
    
    return matches, scores

    


    def update(self):
        ...

    def delete(self, doc_ids: List[int]):
        del self.doc_index[doc_ids]
