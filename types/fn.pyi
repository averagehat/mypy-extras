class Stream(object):

    def __init__(self, *origin: A) -> None: pass

    def __lshift__(self, rvalue: Iterator[A]) -> None: pass

    def cursor(self) -> int: pass

    def __iter__(self) -> Iterator[A]: pass

    def __getitem__(self, index: int) -> A: pass
