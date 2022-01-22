import os
import json

from aiohttp import web
from abc import ABC, abstractmethod
from src.service.message import ServiceRequest
from src.service.service import ModelService


class Endpoint(ABC):
    """Endpoint is an abstract base class. It serves an interface for subclasses.
    """
    def __init__(self, path: str, method: str):
        super().__init__()
        self._original_path = path
        self._formatted_path = self._format_path(path)
        self._method = method.upper()

    def _format_path(path):
        if path[0] != '/':
            path = '/' + path
        return os.path.normpath(path)

    @property
    def formatted_path(self):
        return self._formatted_path

    @property
    def original_path(self):
        return self._original_path

    @property
    def method(self):
        return self._method

    @abstractmethod
    async def teardown(self):
        raise NotImplementedError()

    @abstractmethod
    async def handle_request(self, request: ServiceRequest):
        raise NotImplementedError()


class ServiceEndpoint(Endpoint):
    def __init__(self, path: str, method: str, model_service: ModelService):
        super().__init__(path, method)
        self.model_service = model_service

    async def handle_request(self, request: ServiceRequest):
        ret_data = await self.model_service.handle_request(request)
        text = json.dumps(ret_data)
        return web.json_response(text=text)

    async def teardown(self):
        return await super().teardown()


if __name__ == '__main__':
    try:
        print(Endpoint())
    except TypeError as e:
        print(f"it should not instantiate {e}")
