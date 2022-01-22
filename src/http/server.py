import asyncio
import logging

from typing import List, Optional
from aiohttp import web
from http.endpoint import Endpoint


logger = logging.get_logger(__name__)


class Server:
    def __init__(self, endpoints: List[Endpoint], port: Optional[int]=None):
        self._app = web.Application()
        self._port = port
        self._endpoints = endpoints
        self._validate_endpoints()
        self._register_endpoints()

    def _validate_endpoints(self):
        endpoint_keys = set()
        duplicated_keys = set()
        for endpoint in self.endpoints:
            key = (endpoint.formatted_path, endpoint.method)
            if key not in endpoint_keys:
                endpoint_keys.add(key)
            else:
                duplicated_keys.add(key)
        if duplicated_keys:
            raise RuntimeError(f"duplicated endpoints: {list(duplicated_keys)}")

    def _register_endpoints(self):
        routes = []
        for endpoint in self.endpoints:
            routes.append(web.route(endpoint.method,
                                    endpoint.formatted_path,
                                    endpoint.handle_request))
        if routes:
            self._app.add_routes(routes)

    def start(self):
        web.run_app(self._app, port=self._port)

    async def teardown(self):
        tasks = []
        for endpoint in self._endpoints:
            tasks.append(asyncio.create_task(endpoint.teardown()))

        for task in tasks:
            try:
                await task
            except asyncio.CancelledError:
                continue
            except Exception as e:
                logger.error(f"failed to tearndown: {e.__repr__()}")
