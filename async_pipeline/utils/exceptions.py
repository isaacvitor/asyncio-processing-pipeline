from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(init=False)
class ExceptionInfo:
    exception: str = field(init=False)
    stack_trace: str = field(init=False)
    task: Optional[Any] = field(init=False)

    def __init__(
        self, exception: Exception, stack_trace: str, task: Optional[Any] = None
    ) -> None:
        self.exception = str(exception)
        self.stack_trace = stack_trace
        self.task = task


class AsyncObserverException(Exception):
    def __init__(self, *args: object, exception_info: ExceptionInfo) -> None:
        super().__init__(*args)
        self.exception_info: ExceptionInfo = exception_info


class ObserverStatusException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
