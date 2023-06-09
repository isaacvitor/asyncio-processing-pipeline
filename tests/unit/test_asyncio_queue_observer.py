import asyncio
import logging
from typing import Any
from unittest.mock import Mock

import pytest

from async_pipeline.pipeline.observers import AsyncQueueObserver, ObserverStatus
from async_pipeline.utils.exceptions import (
    AsyncObserverException,
    ObserverStatusException,
)

LOGGER = logging.getLogger(__name__)


@pytest.fixture(name="input_queue")
def input_asyncio_queue() -> asyncio.Queue:
    return asyncio.Queue()


@pytest.fixture(name="output_queue")
def output_asyncio_queue() -> asyncio.Queue:
    return asyncio.Queue()


@pytest.fixture(name="exception_queue")
def exception_asyncio_queue() -> asyncio.Queue:
    return asyncio.Queue()


async def nope(element: Any) -> Any:
    return element


@pytest.mark.asyncio
async def test_start_observer(input_queue: asyncio.Queue) -> None:
    async_queue_observer: AsyncQueueObserver = AsyncQueueObserver(
        input_queue, on_item=nope
    )

    async_queue_observer.start()
    assert async_queue_observer.status == ObserverStatus.RUNNING


@pytest.mark.asyncio
async def test_start_observer_twice(input_queue: asyncio.Queue) -> None:
    async_queue_observer: AsyncQueueObserver = AsyncQueueObserver(
        input_queue, on_item=nope
    )

    with pytest.raises(ObserverStatusException):
        async_queue_observer.start()
        async_queue_observer.start()


@pytest.mark.asyncio
async def test_stop_observer_without_start(input_queue: asyncio.Queue) -> None:
    async_queue_observer: AsyncQueueObserver = AsyncQueueObserver(
        input_queue, on_item=nope
    )

    with pytest.raises(ObserverStatusException):
        async_queue_observer.stop()


@pytest.mark.asyncio
async def test_stop_observer(input_queue: asyncio.Queue) -> None:
    async_queue_observer: AsyncQueueObserver = AsyncQueueObserver(
        input_queue, on_item=nope
    )

    async_queue_observer.start()

    async_queue_observer.stop()
    await asyncio.sleep(1)
    assert async_queue_observer.status == ObserverStatus.STOPPED


def test_no_elements_in_the_input_queue(input_queue: asyncio.Queue) -> None:
    async_queue_observer = AsyncQueueObserver(input_queue, on_item=nope)

    assert len(async_queue_observer) == 0


def test_one_element_in_the_input_queue(input_queue: asyncio.Queue) -> None:
    element: Mock = Mock()
    input_queue.put_nowait(element)
    async_queue_observer: AsyncQueueObserver = AsyncQueueObserver(
        input_queue, on_item=nope
    )

    assert len(async_queue_observer) == 1


def test_get_element_input_queue(input_queue: asyncio.Queue) -> None:
    element_one: Mock = Mock(name="Element 01")
    element_two: Mock = Mock(name="Element 02")

    input_queue.put_nowait(element_one)
    input_queue.put_nowait(element_two)

    async_queue_observer: AsyncQueueObserver = AsyncQueueObserver(
        input_queue, on_item=nope
    )

    retrieved_element: Mock = input_queue.get_nowait()

    assert len(async_queue_observer) == 1
    assert retrieved_element == element_one


@pytest.mark.asyncio
async def test_start_observer_must_return_a_future(input_queue: asyncio.Queue) -> None:
    async_queue_observer: AsyncQueueObserver = AsyncQueueObserver(
        input_queue, on_item=nope
    )

    observer_task: asyncio.Future = async_queue_observer.start()

    assert isinstance(observer_task, asyncio.Future)


@pytest.mark.asyncio
async def test_stop_observer_cancel_observer_task(input_queue: asyncio.Queue) -> None:
    async_queue_observer: AsyncQueueObserver = AsyncQueueObserver(
        input_queue, on_item=nope
    )

    observer_task: asyncio.Future = async_queue_observer.start()

    with pytest.raises(asyncio.CancelledError):
        async_queue_observer.stop()
        await observer_task


@pytest.mark.asyncio
async def test_output_queue_get_value(
    input_queue: asyncio.Queue, output_queue: asyncio.Queue
) -> None:
    async def increase_a_number(number: int) -> int:
        number = number + 1
        return number

    async_queue_observer: AsyncQueueObserver = AsyncQueueObserver(
        input_queue, on_item=increase_a_number, output_queue=output_queue
    )

    async_queue_observer.start()
    input_queue.put_nowait(1)

    await asyncio.sleep(0)

    assert output_queue.qsize() != 0
    result: Any = output_queue.get_nowait()
    assert result == 2


@pytest.mark.asyncio
async def test_raise_exception_without_exception_queue(
    input_queue: asyncio.Queue, output_queue: asyncio.Queue
) -> None:
    async def raise_exception(number: int) -> int:
        raise ValueError("Raising a ValueError just because.")

    async_queue_observer: AsyncQueueObserver = AsyncQueueObserver(
        input_queue,
        on_item=raise_exception,
        output_queue=output_queue,
        exception_queue=None,
    )

    async_queue_observer.start()
    input_queue.put_nowait(1)
    await asyncio.sleep(0)
    returned_exception = async_queue_observer.observer_task.exception()
    assert isinstance(returned_exception, AsyncObserverException)
    assert async_queue_observer.status == ObserverStatus.FAILED


@pytest.mark.asyncio
async def test_raise_exception_with_exception_queue(
    input_queue: asyncio.Queue,
    output_queue: asyncio.Queue,
    exception_queue: asyncio.Queue,
) -> None:
    async def raise_exception(number: int) -> int:
        raise ValueError("Raising a ValueError just because.")

    async_queue_observer: AsyncQueueObserver = AsyncQueueObserver(
        input_queue,
        on_item=raise_exception,
        output_queue=output_queue,
        exception_queue=exception_queue,
    )

    async_queue_observer.start()
    input_queue.put_nowait(1)
    await asyncio.sleep(0)

    assert exception_queue.qsize() == 1

    returned_exception = exception_queue.get_nowait()
    assert isinstance(returned_exception, AsyncObserverException)


@pytest.mark.asyncio
async def test_restart_observer_after_an_exception(
    input_queue: asyncio.Queue, output_queue: asyncio.Queue
) -> None:
    async def raise_exception(number: int) -> int:
        raise ValueError("Raising a ValueError just because.")

    async_queue_observer: AsyncQueueObserver = AsyncQueueObserver(
        input_queue,
        on_item=raise_exception,
        output_queue=output_queue,
        exception_queue=None,
    )

    async_queue_observer.start()
    input_queue.put_nowait(1)
    await asyncio.sleep(0)

    assert async_queue_observer.observer_task.done()
    assert async_queue_observer.status == ObserverStatus.FAILED

    async_queue_observer.start()
    await asyncio.sleep(0)
    assert not async_queue_observer.observer_task.done()
    assert async_queue_observer.status == ObserverStatus.RUNNING
