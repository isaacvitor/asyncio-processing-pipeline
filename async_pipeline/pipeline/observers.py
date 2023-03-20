""" Module that contains queue observers"""
from abc import ABC, abstractmethod
import asyncio
from enum import Enum, auto
import multiprocessing as mp
from sys import exc_info
from typing import Union, Optional, Callable, Any, Coroutine, TypeVar

from async_pipeline.utils.exceptions import AsyncObserverException, ObserverStatusException

Q = TypeVar('Q', asyncio.Queue, mp.Queue)


class ObserverStatus(Enum):
    CREATED: int = auto()
    RUNNING: int = auto()
    FAILED: int = auto()
    STOPPED: int = auto()


class QueueObserver(ABC):

    @abstractmethod
    def __init__(
        self,
        input_queue: Q,
        on_item: Callable[..., Coroutine[Any, Any, Any]],
        output_queue: Optional[Q],
        exception_queue: Optional[Q],
    ) -> None:
        ...

    @abstractmethod
    def start(self) -> asyncio.Future:
        ...

    @abstractmethod
    def stop(self) -> None:
        ...

    @abstractmethod
    async def _observer(self) -> None:
        ...

    @abstractmethod
    def __len__(self) -> int:
        ...


class AsyncQueueObserver(QueueObserver):

    def __init__(
        self,
        input_queue: asyncio.Queue,
        on_item: Callable[..., Coroutine[Any, Any, Any]],
        output_queue: Optional[asyncio.Queue] = None,
        exception_queue: Optional[asyncio.Queue] = None,
    ) -> None:
        self.__input_queue: asyncio.Queue = input_queue
        self.on_item: Callable[..., Coroutine[Any, Any, Any]] = on_item
        self.__output_queue: Union[asyncio.Queue, None] = output_queue
        self.__exception_queue: Union[asyncio.Queue, None] = exception_queue
        self.observer_task: asyncio.Future
        self.__status: ObserverStatus = ObserverStatus.CREATED

    def start(self) -> asyncio.Future:
        if self.__status is not ObserverStatus.RUNNING:
            self.observer_task = asyncio.create_task(self._observer())
            self.__status = ObserverStatus.RUNNING
            return self.observer_task
        raise ObserverStatusException('Observer already running')


    def stop(self) -> None:
        if self.__status is not ObserverStatus.RUNNING:
            raise ObserverStatusException('Observer is not running')
        try:
            if not self.observer_task.cancelled():
                self.observer_task.cancel()
        except asyncio.CancelledError:
            ...
        finally:
            self.__status = ObserverStatus.STOPPED

    @property
    def status(self):
        return self.__status

    async def _observer(self) -> None:
        while True:
            if self.__input_queue.qsize():
                try:
                    task: Any = await self.__input_queue.get()
                    result: Any = await self.on_item(task)
                    self.__input_queue.task_done()

                    if self.__output_queue is not None:
                        self.__output_queue.put_nowait(result)
                except Exception as ex:
                    if self.__exception_queue is not None:
                        self.__exception_queue.put_nowait(
                            AsyncObserverException(ex))
                    else:
                        raise AsyncObserverException from ex

            await asyncio.sleep(0)

    def __len__(self) -> int:
        return self.__input_queue.qsize()
