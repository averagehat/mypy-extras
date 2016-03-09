from typing import *
from gadt import traverse_type, TrimOpts
import yaml
from toolz.dicttoolz import merge
from toolz import compose

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar("C")

#class Applicative(Generic[A]):
#    def map(self, f: Callable[[A], B])-> 'Applicative[B]': pass
#    def apply(self, fa: 'Applicative[Callable[[A],B]]') -> 'Applicative[B]': pass
#
#class Maybe(Applicative, Generic[A]):
#
#    def apply(self, fa: 'Maybe[Callable[[A],B]]') -> 'Maybe[B]': pass
#    def map(self, f: Callable[[A], B])-> 'Maybe[B]': pass
yaml.dump({'a' : [1, 2], 'foo' : 9999, 'opt' : {'foo' : 'bar'}}, default_flow_style=False)
examples = {
        int : 0,
        bool : False,
        str : None,
        object : None,
        Union : lambda xs: xs[0],
        List : lambda x : [examples[x]]*3, 
        } 
simple = lambda t: dict(name=dict(type=t,value=None,example=examples.get(t)))
primitives = [int, bool, str, float]
primdict = dict(zip(primitives, [simple]*len(primitives)))
enum = compose(simple, lambda x: x.__name__)
def handle_union(xs):
    xs = list(map(lambda x: x['name']['type'], xs))
    return dict(name=dict(choices=xs, example=xs[0],value=None))
def handle_list(t):
    t = next(t)
    return dict(name=dict(type=t,value=None,example=examples[List](t))),
tfuncs= merge(primdict, {
        object : enum,
        NamedTuple : enum,
        Optional :  lambda x: merge(simple(x), {'optional' : True}),
        List : handle_list,
        #Union : lambda xs: dict(name=dict(choices=xs, example=xs[0],value=None), 
        Union : handle_union
        })
#{n : t for n,t in res =  traverse_type(TrimOpts, tfuncs)
from functools import reduce 
from itertools import starmap
#res = reduce(merge, map(lambda x: traverse_type(x, tfuncs), TrimOpts._field_types), {})
print(TrimOpts.__dict__)
res =  {k : traverse_type(t, tfuncs) for k,t in TrimOpts._field_types.items()}
print(res)
