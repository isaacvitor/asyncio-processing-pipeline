""" Module that contains queue observers"""
import asyncio
import multiprocessing as mp

from abc import ABC, abstractmethod
from typing import Union, Optional, Callable, Any, Coroutine


class QueueProtocol(ABC):

    @abstractmethod
    def __init__(
            self, input_queue: Union[asyncio.Queue, mp.Queue],
            on_item: Callable[..., Coroutine[Any, Any, Any]],
            output_queue: Optional[Union[asyncio.Queue, mp.Queue]]) -> None:
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


class AsyncQueueObserver(QueueProtocol):

    def __init__(
        self,
        input_queue: asyncio.Queue,
        on_item: Callable[..., Coroutine[Any, Any, Any]],
        output_queue: Optional[asyncio.Queue] = None,
    ) -> None:
        self.__input_queue: asyncio.Queue = input_queue
        self.__output_queue: Union[asyncio.Queue, None] = output_queue
        self.observer_task: asyncio.Future
        self.on_item: Callable[..., Coroutine[Any, Any, Any]] = on_item

    def start(self) -> asyncio.Future:
        self.observer_task = asyncio.create_task(self._observer())
        return self.observer_task

    def stop(self) -> None:
        self.observer_task.cancel()

    async def _observer(self) -> None:
        while True:
            if self.__input_queue.qsize():
                task: Any = await self.__input_queue.get()
                result: Any = await self.on_item(task)
                self.__input_queue.task_done()

                if self.__output_queue is not None:
                    self.__output_queue.put_nowait(result)
            else:
                await asyncio.sleep(0)

    def __len__(self) -> int:
        return self.__input_queue.qsize()
