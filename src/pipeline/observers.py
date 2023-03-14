""" Module that contains queue observers"""
import asyncio
import multiprocessing as mp

from abc import ABC, abstractmethod
from typing import Union, Optional


class QueueProtocol(ABC):

    @abstractmethod
    def __init__(
            self, input_queue: Union[asyncio.Queue, mp.Queue],
            output_queue: Optional[Union[asyncio.Queue, mp.Queue]]) -> None:
        ...

    @abstractmethod
    def __len__(self) -> int:
        ...


class AsyncQueueObserver(QueueProtocol):

    def __init__(self,
                 input_queue: asyncio.Queue,
                 output_queue: Optional[asyncio.Queue] = None) -> None:
        self.__input_queue = input_queue
        self.__output_queue = output_queue

    def __len__(self) -> int:
        return self.__input_queue.qsize()
