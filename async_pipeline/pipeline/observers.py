""" Module that contains queue observers"""
from abc import ABC, abstractmethod
import asyncio
import multiprocessing as mp
from typing import Union, Optional, Callable, Any, Coroutine, TypeVar

from async_pipeline.exceptions.internals import AsyncObserverException

Q = TypeVar('Q', asyncio.Queue, mp.Queue)


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

    def start(self) -> asyncio.Future:
        self.observer_task = asyncio.create_task(self._observer())
        return self.observer_task

    def stop(self) -> None:
        self.observer_task.cancel()

    async def _observer(self) -> None:
        while True:
            if self.__input_queue.qsize():
                try:
                    task: Any = await self.__input_queue.get()
                    result: Any = await self.on_item(task)
                    self.__input_queue.task_done()

                    if self.__output_queue is not None:
                        self.__output_queue.put_nowait(result)
                except Exception as exc:
                    if self.__exception_queue is not None:
                        self.__exception_queue.put_nowait(
                            AsyncObserverException(exc))

            await asyncio.sleep(0)

    def __len__(self) -> int:
        return self.__input_queue.qsize()
