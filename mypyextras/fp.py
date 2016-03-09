class Stream(fn.Stream, Generic[A]):

    #def __getitem__(self, index: int) -> Maybe[A]: 

    def map(f: Callable[[A], B]) -> Stream[B]:
        return Stream() << map(f, self)

    def filter(f: Callable[[A], bool]) -> Stream[A]:
        return Stream() << filter(f, self)
