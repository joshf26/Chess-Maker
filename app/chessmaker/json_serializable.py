from abc import ABC, abstractmethod
from typing import Union


class JsonSerializable(ABC):

    @abstractmethod
    def to_json(self) -> Union[dict, list]:
        pass
