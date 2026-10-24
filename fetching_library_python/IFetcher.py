from abc import ABC, abstractmethod


class IFetcher(ABC):

    @abstractmethod
    def fetch(self, url: str):
        pass
