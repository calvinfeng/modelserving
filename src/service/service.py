from concurrent.futures import ThreadPoolExecutor
import shortuuid
import asyncio
import functools

from abc import ABC, abstractmethod
from typing import Optional, Union
from .message import ServiceRequest, ServiceResponse, ServiceError


class Service(ABC):
    def __init__(self, id: Optional[str]):
        if id is None:
            self._id = f"service-{shortuuid.uuid()}"

    @property
    def service_id(self) -> str:
        return self._id

    @abstractmethod
    async def handle_request(self, request: ServiceRequest) -> Union[ServiceResponse, ServiceError]:
        raise NotImplementedError()


class Model(ABC):
    @abstractmethod
    def load(self):
        raise NotImplementedError()

    @abstractmethod
    def preprocess(self, request: ServiceRequest):
        raise NotImplementedError()

    @abstractmethod
    def inference(self, inference_input):
        raise NotImplementedError()

    @abstractmethod
    def postprocess(self, request: ServiceRequest, inference_input, inference_output):
        raise NotImplementedError()


class ModelService(Service):
    def __init__(self, model: Model, preprocess_thread_num=1,
                                     inference_thread_num=1,
                                     postprocess_thread_num=1):
        self._model = model
        self._event_loop = asyncio.get_event_loop()
        self._preprocess_thread_pool = ThreadPoolExecutor(preprocess_thread_num)
        self._inference_thread_pool = ThreadPoolExecutor(inference_thread_num)
        self._postprocess_thread_pool = ThreadPoolExecutor(postprocess_thread_num)
        self._started = False
        self._terminated = False

    def start(self):
        if self._started:
            return
        self._model.load()

    def teardown(self):
        if self._terminated:
            return
        self._preprocess_thread_pool.shutdown(wait=True)
        self._inference_thread_pool.shutdown(wait=True)
        self._postprocess_thread_pool.shutdown(wait=True)
        self._terminated = True

    async def handle_request(self, request: ServiceRequest) -> Union[ServiceResponse, ServiceError]:
        inference_input = await self._preprocess(request)
        inference_output = await self._inference(inference_input)
        ret_data = await self._postprocess(request, inference_input, inference_output)
        return ServiceResponse(id=None, ret_data=ret_data)

    async def _preprocess(self, request: ServiceRequest):
        try:
            routine = functools.partial(self._model.preprocess, request=request)
            inference_input = await self._event_loop.run_in_executor(self._preprocess_thread_pool,
                                                                     routine)
        except Exception as e:
            raise RuntimeError(e)

        return inference_input

    async def _inference(self, inference_input):
        try:
            routine = functools.partial(self._model.inference, inference_input=inference_input)
            inference_output = await self._event_loop.run_in_executor(self._inference_thread_pool,
                                                                     routine)
        except Exception as e:
            raise RuntimeError(e)

        return inference_output

    async def _postprocess(self, request: ServiceRequest, inference_input, inference_output):
        try:
            routine = functools.partial(self._model.postprocess, request=request,
                                                                 inference_input=inference_input,
                                                                 inference_output=inference_output)
            ret_data = await self._event_loop.run_in_executor(self._postprocess_thread_pool,
                                                              routine)
        except Exception as e:
            raise RuntimeError(e)

        return ret_data
