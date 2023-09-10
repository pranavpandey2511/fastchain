from dotenv import load_dotenv
import logging
import os

load_dotenv("./.env")


class FastChain:
    def __init__(
        self, connectors_type="langchain", vector_db="qdrant", chunk_size=512
    ):
        pass

    def _get_embedding(self):
        pass

    def _handle_query():
        pass

    def store_data(self, type, **kwrags):
        pass

    def get_prompt(self, type):
        pass

    def get_agent(self, type):
        pass

    def query(self):
        pass


class LLM:
    def __init__(self):
        OPENAI_API_KEY = os.enviorn.get("OPNEAI_API_KEY")

    def chat():
        ...


class Prompt:
    def __init__(self, text) -> None:
        ...

    def format(self):
        ...
