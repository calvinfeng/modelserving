from abc import ABC, abstractmethod
from aiohttp import web
from typing import Optional


class Adapter(ABC):
    @abstractmethod
    async def convert(self, request: web.Request,
                      request_id: Optional[str]):
        """
        Raises:
            HttpDataException
        """
        raise NotImplementedError()
