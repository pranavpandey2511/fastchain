from abc import ABC, abstractmethod

class BaseConnector(ABC):
    def __init__(self):
        ...
    def connect(self):
        ...

    def __exit__(self, exc_type, exc_val, exc_tb):
        ...