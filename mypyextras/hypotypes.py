from hypothesis import strategies as st
from typing import Dict, Tuple, List, Iterator, Set, Union, Optional, TypingMeta, NamedTuple
import re
import operator
from functools import partial
import string
from collections import OrderedDict
compose = lambda f,g: lambda *x: f(g(*x))
'''
support:
- [x] NamedTuple
- [ ] Automatic function arguments 
could also say, "given a function, generate random return values that it might give" because functions are also annotated with return values
'''

# Just an exmaple of a named tuple
VCFRow = NamedTuple("VCFRow",
                    [('ref', str),
                     ('AO', List[int]),
                     ('DP', int),
                     ('chrom',str),
                     ('pos', int),
                     ('alt', List[str])])

primitives = {
    str   : st.text(),
    int   : st.integers(),
    bool  : st.booleans(),
    float : st.floats(),
    type(None) : st.none(),
    unicode : st.characters(),
    bytes : st.binary() # this is weird because str == bytes in py2
} # missing: fractions, decimal

#TODO: add Iterable, handle Sequence, etc.
def resolve(x): # type: (TypingMeta) -> hypothesis.strategies.SearchStrategy
   if x in primitives:
       strat = primitives[x]
   elif hasattr(x, '_fields'):
       # NamedTuple isn't a type, so this can't be a subclass check
       name = x.__name__
       fts = OrderedDict(x._field_types)
       vals = map(resolve, fts.values()) 
       # `NamedTuple` is actually a ... `namedtuple` itself
       strat = st.tuples(*vals).map(lambda ys: x(*ys))
   elif issubclass(x, Dict):
       strat = st.dictionaries(*map(resolve, x.__parameters__))
   elif issubclass(x, Tuple):
       strat = st.tuples(*map(resolve, x.__tuple_params__))
   elif issubclass(x, Union):
       strat = operator.ior(*map(resolve, x.__union_params__))
   elif issubclass(x, Optional):
       # Optional[X] is equivalent to Union[X, type(None)]. second param is always Nonetype.
       value = x.__union_params__[0] 
       strat = (resolve(value) | st.none())
   else:  # a list-type-ish
       collections = {
           Iterator : lambda x: st.lists(x).map(iter),
           List : st.lists,
           Set : st.sets
          }
       #TODO: missing: Iterable , etc.
       # For some reason List[T] not a subclass of List: issubclass(x, List) == False.
       # So do these hijinks
       params = x.__parameters__
       assert(len(params) == 1, "Wrong type %s, not a list-like" % x)
       matches = filter(lambda k: k == x.__origin__, collections.keys())
       assert(len(matches) == 1, "Should have exactly one match. %s matched with %s" % (x, matches))
       collection_strat = collections[matches[0]]
       strat = collection_strat(resolve(params[0]))
   return strat
# see https://docs.python.org/3/library/typing.html
# not Generics
# not Callables
