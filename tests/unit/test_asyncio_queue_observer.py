import asyncio
from unittest.mock import Mock

import pytest

from src.pipeline.observers import AsyncQueueObserver


@pytest.fixture(name="input_queue")
def input_asyncio_queue() -> asyncio.Queue:
    return asyncio.Queue()


@pytest.fixture(name="output_queue")
def output_asyncio_queue() -> asyncio.Queue:
    return asyncio.Queue()


def test_no_elements_in_the_input_queue(input_queue: asyncio.Queue) -> None:

    async_queue_observer = AsyncQueueObserver(input_queue)

    assert len(async_queue_observer) == 0


def test_one_element_in_the_input_queue(input_queue: asyncio.Queue) -> None:
    element: Mock = Mock()
    input_queue.put_nowait(element)
    async_queue_observer = AsyncQueueObserver(input_queue)

    assert len(async_queue_observer) == 1


def test_get_element_input_queue(input_queue: asyncio.Queue) -> None:
    element_one: Mock = Mock(name='Element 01')
    element_two: Mock = Mock(name='Element 02')

    input_queue.put_nowait(element_one)
    input_queue.put_nowait(element_two)

    async_queue_observer = AsyncQueueObserver(input_queue)

    retrieved_element: Mock = input_queue.get_nowait()

    assert len(async_queue_observer) == 1
    assert retrieved_element == element_one
