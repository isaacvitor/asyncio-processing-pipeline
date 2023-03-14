import asyncio
from typing import Any
from unittest.mock import Mock

import pytest

from src.pipeline.observers import AsyncQueueObserver


@pytest.fixture(name="input_queue")
def input_asyncio_queue() -> asyncio.Queue:
    return asyncio.Queue()


@pytest.fixture(name="output_queue")
def output_asyncio_queue() -> asyncio.Queue:
    return asyncio.Queue()


async def nope(element: Any) -> Any:
    return element


def test_no_elements_in_the_input_queue(input_queue: asyncio.Queue) -> None:

    async_queue_observer = AsyncQueueObserver(input_queue, on_item=nope)

    assert len(async_queue_observer) == 0


def test_one_element_in_the_input_queue(input_queue: asyncio.Queue) -> None:
    element: Mock = Mock()
    input_queue.put_nowait(element)
    async_queue_observer: AsyncQueueObserver = AsyncQueueObserver(input_queue,
                                                                  on_item=nope)

    assert len(async_queue_observer) == 1


def test_get_element_input_queue(input_queue: asyncio.Queue) -> None:
    element_one: Mock = Mock(name='Element 01')
    element_two: Mock = Mock(name='Element 02')

    input_queue.put_nowait(element_one)
    input_queue.put_nowait(element_two)

    async_queue_observer: AsyncQueueObserver = AsyncQueueObserver(input_queue,
                                                                  on_item=nope)

    retrieved_element: Mock = input_queue.get_nowait()

    assert len(async_queue_observer) == 1
    assert retrieved_element == element_one


@pytest.mark.asyncio
async def test_start_observer_must_return_a_future(
        input_queue: asyncio.Queue) -> None:
    async_queue_observer: AsyncQueueObserver = AsyncQueueObserver(input_queue,
                                                                  on_item=nope)

    observer_task: asyncio.Future = async_queue_observer.start()

    assert isinstance(observer_task, asyncio.Future)


@pytest.mark.asyncio
async def test_stop_observer_cancel_observer_task(
        input_queue: asyncio.Queue) -> None:
    async_queue_observer: AsyncQueueObserver = AsyncQueueObserver(input_queue,
                                                                  on_item=nope)

    observer_task: asyncio.Future = async_queue_observer.start()

    async_queue_observer.stop()

    with pytest.raises(asyncio.CancelledError):
        await observer_task


@pytest.mark.asyncio
async def test_output_queue_get_value(input_queue: asyncio.Queue,
                                      output_queue: asyncio.Queue) -> None:

    async def increase_a_number(number: int) -> int:
        number = number + 1
        return number

    async_queue_observer: AsyncQueueObserver = AsyncQueueObserver(
        input_queue, on_item=increase_a_number, output_queue=output_queue)

    async_queue_observer.start()
    input_queue.put_nowait(1)

    await asyncio.sleep(0)

    assert output_queue.qsize() != 0
    result: Any = output_queue.get_nowait()
    assert result == 2
