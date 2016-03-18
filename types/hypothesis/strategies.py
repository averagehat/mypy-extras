from typing import * 
A = TypeVar("A")
B = TypeVar("B")

class SearchStrategy(Generic[A]): 
    def __ror__(self, other): # type: (SearchStrategy[B]) -> Union[SearchStrategy[A],SearchStrategy[B]]
        pass
    def map(self, f): # type: (Callable[[A],B]) -> SearchStrategy[B]
        pass
    def flatmap(self, f): # type: (Callable[[A],SearchStrategy[B]]) -> SearchStrategy[B]
        pass
    def filter(self, f): # type: (Callable[[A],bool]) -> SearchStrategy[A]
        pass
def text(): # type: () -> SearchStrategy[str]
    pass
def integers(): # type: () -> SearchStrategy[int]
  pass 
def booleans(): # type: () -> SearchStrategy[bool]
    pass
def floats(): # type: () -> SearchStrategy[float]
    pass
def none(): # type: () -> SearchStrategy[None]
    pass
def characters(): # type: () -> SearchStrategy[bytes]
    pass
def binary(): # type: () -> SearchStrategy[bytes]
    pass
#class SearchStrategy(object): 
#    def __ror__(self, other): # type: (SearchStrategy) -> SearchStrategy
#        pass
#def text(): # type: () -> SearchStrategy
#    pass
#def integers(): # type: () -> SearchStrategy
#  pass 
#def booleans(): # type: () -> SearchStrategy
#    pass
#def floats(): # type: () -> SearchStrategy
#    pass
#def : st.none(): # type: () -> SearchStrategy
#    pass
#def characters(): # type: () -> SearchStrategy
#    pass
#def binary(): # this is weird because str == bytes in py2 # type: () -> SearchStrategy
#    pass
