from docarray.index.backends.weaviate import (
    WeaviateDocumentIndex,
    EmbeddedOptions,
)
import os
from dotenv import load_dotenv

from fastchain.document.chunk.base import Section
from fastchain.indexers.base import VectorStore


class WeaviateStore(VectorStore):
    def __init__(self):
        connection = self._connect_to_weaviate()

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

        doc_index = WeaviateDocumentIndex[Section](db_config=dbconfig)

    def insert(self):
        ...

    def query(self):
        ...
