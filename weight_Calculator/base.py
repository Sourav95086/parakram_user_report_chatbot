from abc import ABC, abstractmethod
from typing import List, Dict


class SocialSource(ABC):

    @abstractmethod
    def search_topic(self, topic: str) -> List[Dict]:
        """
        Search for posts related to a topic.
        """
        pass