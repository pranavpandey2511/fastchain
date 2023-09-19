from abc import ABC, abstractmethod


class VectorStore(ABC):
    @abstractmethod
    def _connect_to_store(self, connection_params: dict):
        ...

    @abstractmethod
    def index(self):
        ...

    @abstractmethod
    def query(self):
        ...

    @abstractmethod
    def update(self):
        ...

    @abstractmethod
    def delete(self):
        ...
