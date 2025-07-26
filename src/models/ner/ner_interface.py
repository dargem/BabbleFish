from abc import ABC, abstractmethod

class NER_Model_Interface(ABC):

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def get_names(self, paragraph):
        pass

    @abstractmethod
    def get_entities(self, paragraph):
        pass
