from abc import ABC, abstractmethod

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
