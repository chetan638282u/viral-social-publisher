from abc import ABC, abstractmethod

from viral_publisher.models import DraftPost


class Publisher(ABC):
    @abstractmethod
    def publish(self, draft: DraftPost) -> dict:
        raise NotImplementedError
