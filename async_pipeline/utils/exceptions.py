class AsyncObserverException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ObserverStatusException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
