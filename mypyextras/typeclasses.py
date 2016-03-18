from typing import Generic, Callable, TypeVar
from abc import abstractmethod
import operator
'''
Mypy doesn't actually support type classes. But you can generate the code for instances if you want to.
Here are some examples of what that would look like.'''

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar("C")
class Applicative(Generic[A]):
    @abstractmethod
    def map(self, f: Callable[[A], B])-> 'Applicative[B]': pass
    @abstractmethod
    def apply(self, fa: 'Applicative[Callable[[A],B]]') -> 'Applicative[B]': pass

class Maybe(Applicative, Generic[A]):
    # have to override here to avoid upcasting
    @abstractmethod
    def apply(self, fa: 'Maybe[Callable[[A],B]]') -> 'Maybe[B]': pass
    @abstractmethod
    def map(self, f: Callable[[A], B])-> 'Maybe[B]': pass
    @abstractmethod
    def getOrElse(self, a: A) -> A: pass

class Nothing(Generic[A], Maybe):
    # define nothing first because it doesn't require a reference to Just
    def map(self, f: Callable[[A], B])-> Maybe[B]:
        return Nothing()

    def getOrElse(self, a: A) -> A:
        return a

    def apply(self, fa: Maybe[Callable[[A],B]]) -> Maybe[B]: return Nothing()

    __str__ = lambda _: "Nothing"


class Just(Generic[A], Maybe[A]):

    def __init__(self, v: A) -> None:
        self._value = v

    def map(self, f: Callable[[A],B]) -> Maybe[B]: # Can define map
        return Just(f(self._value))

    def __str__(self) -> str: "Just({0})".format(self._value)

    def getOrElse(self, a: A) -> A:
        return self._value

    def apply(self, fa: Maybe[Callable[[A],B]]) -> Maybe[B]:
        if isinstance(fa, Just):
            return self.map(fa._value)
        else: return Nothing()

def partial(f: Callable[[A,B],C], a: A) -> Callable[[B],C]:
    return lambda b: f(a, b) # type: Callable[[B],C]:

add1 = partial(operator.add, 1) # type: Callable[[int],int]
j = Just(12).map(add1).map(add1).getOrElse(0)
print(j) # why `map` work but apply doesnt?
j2 = Just(12).map(add1).map(add1).getOrElse("asdf") # fails
j = Just("SDF").map(add1) # fails
#Func1 = Callable[[A],B]
#Func2 = Callable[[A,B],C]
# see https://github.com/python/mypy/issues/1037

def curry(f: Callable[[A,B],C]) -> Callable[[A],Callable[[B],C]]:
    return lambda x: lambda y: f(x, y) # type: Callable[[A],Callable[[B],C]]
def compose(f: Callable[[A],B], g: Callable[[B],C]) -> Callable[[A],C]:
    return lambda x: f(g(x)) # type: Callable[[A],C]

def lift2(f: Callable[[A,B],C], ma: Applicative[A], mb: Applicative[B]) -> Applicative[C]:
    cf = curry(f) # type: Callable[[A],Callable[[B],C]]
    return mb.apply(ma.map(cf))

j3 = lift2(operator.add, Just(1), Just(10))
F = TypeVar("F")
class Monad(Generic[F,A,B]):

    def flatMap(self, f: Callable[[A],F[B]]) -> F[B]: pass

    def unit(self, a: A) -> F[A]: pass

    def map(self, f: Callable[[A],B]) -> F[B]: # Can define map
        fm = compose(f, self.unit) # type Callable[[A],F[B]]
        return self.flatMap(fm)

    def apply(self, fa: F[Callable[[A],B]]) -> F[B]:
        return self.unit(fa)

    def map2(self, f: Callable[[A,B],C], fb: F[B]) -> F[C]:
        self.flatMap(lambda a: fb.map(lambda b: f(a, b)))
# stuff like `sequence` would have to be in a different function
# the problem is that even if you can generate type signatures for every
# monadic type you make, functions cannot be generalized to these type classes
# without  monadic types. i.e. you're stuck with the "upcasting" that comes with
# a sigature like
# Applicative[A] -> Applicative[B]
# if you pass in a List, you get back only an Applicative.

def lift2Maybe(f: Callable[[A,B],C], ma: Maybe[A], mb: Maybe[B]) -> Maybe[C]:
    cf = curry(f) # type: Callable[[A],Callable[[B],C]]
    return mb.apply(ma.map(cf))

j = Just(12).map(add1).map(add1)
print(j) # why does this work but apply doesnt? parameters are not covariant, but return types are.

