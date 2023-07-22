from abc import ABC, abstractmethod
from uuid import uuid4
from pydantic import BaseModel
from typing import Optional, Union, List, Tuple, Dict, Type


class Document(BaseModel):
    _id: uuid4()
    data: str
    metadata: Dict


class BaseDataloader(ABC):
    """Base dataloader class for creating dataloaders

    Args:
        ABC (abstract): Abstract class inherited
    """

    def __init__(self) -> None:
        pass

    @abstractmethod
    def load_data(self):
        pass

    @abstractmethod
    def _verify_data(self):
        pass
