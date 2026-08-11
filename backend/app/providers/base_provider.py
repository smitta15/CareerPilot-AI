from abc import ABC, abstractmethod


class JobProvider(ABC):

    @abstractmethod
    def search_jobs(self, query: str) -> list:
        pass