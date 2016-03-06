from typing import Tuple, Dict, List, Iterator, Iterable, Any, Callable, NamedTuple, BinaryIO, Union, Generic, TypeVar, Optional

Blue = NamedTuple("Blue", [])
Green = NamedTuple("Green", [])

Color = Union[Green,Blue]

Cat = NamedTuple("Cat", [("name", str)])
Fish = NamedTuple("Fish",   [("name", str), ("color", Color)])
Squid = NamedTuple("Squid", [("name", str), ("age", int)])

Pet = Union[Cat,Fish,Squid]

def optional_with_operators_passes(a: Union[int, None]) -> int:
    return a + 20 

def _passes_synonym(x: Optional[int]) -> None:
    a = x + 10

def other_unions_fail(x: Union[int, bool]) -> None:
     a = x * 2.0

def pet_union_passes() -> Pet:
    return Cat("neko")

def none_return_type_passes() -> Pet:
    return None

def pet_color_fails(x: Pet) -> None:
    a = x.color

def pet_color_passes(x: Pet) -> None:
    if isinstance(x, Fish):  a = x.color


def does_pass(x: Union[Fish, None]) -> None:  # passes :disappointed:
       a = x.color

    
#NOTE: couldn't get this to work
#class Tree(Generic[T]): pass
#class Leaf(Tree): pass
#class Node(Tree):
#    def __init__(self, value: T, value2: T, left: Tree[T], right: Tree[T]) -> None:
#        self.value = value
#        self.left = left # type: Tree[T]
#        self.right = right # type: Tree[T]
#
##NOTE: Below doesn't work because `Tree` not yet defined. Limit of python.
#Tree = Union[NamedTuple("Leaf", []), NamedTuple("Node", [("value", int), ("left", Tree), ("right", Tree)])]
#
