import asyncio
from typing import Any
from random import randint

import pytest

from async_pipeline.pipeline.observers import AsyncQueueObserver


@pytest.fixture(name="input_queue")
def input_asyncio_queue() -> asyncio.Queue:
    return asyncio.Queue()


@pytest.fixture(name="output_queue")
def output_asyncio_queue() -> asyncio.Queue:
    return asyncio.Queue()


async def nope(element: Any) -> Any:
    return element


@pytest.mark.asyncio
async def test_multiple_observers_must_do_different_job(
        input_queue: asyncio.Queue, output_queue: asyncio.Queue) -> None:

    async def increase_a_number(number: int) -> int:
        await asyncio.sleep(randint(1, 3))
        number = number + 1
        return number

    async_queue_observer_01: AsyncQueueObserver = AsyncQueueObserver(
        input_queue, on_item=increase_a_number, output_queue=output_queue)

    async_queue_observer_02: AsyncQueueObserver = AsyncQueueObserver(
        input_queue, on_item=increase_a_number, output_queue=output_queue)

    async_queue_observer_01.start()
    async_queue_observer_02.start()

    input_queue.put_nowait(1)
    input_queue.put_nowait(2)

    await asyncio.sleep(5)

    assert output_queue.qsize() == 2

    item_one: Any = output_queue.get_nowait()
    item_two: Any = output_queue.get_nowait()

    assert item_one != item_two
