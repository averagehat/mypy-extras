from argparse import ArgumentParser, Namespace
from fn.iters import partition
import  argparse
from typing import *
from collections import OrderedDict
from operator import itemgetter as get
try:
    unicode = unicode
except:
    unicode = str
#TODO: should wrap the result in the NamedTuples as appropriate
#TODO: create subcommands by function name
#TODO: inspect local module and produce subcommands for all functions matching a given pattern
#TODO: finish tests
compose = lambda f,g: lambda *x: f(g(*x))

is_namedtuple = lambda t: hasattr(t, '_fields')

def type_to_argparse(t: type, p: ArgumentParser, default: Optional[Any]) -> Dict[str,Any]:
   to_argparse = lambda x: type_to_argparse(x, p, None)
   primitives  = [int, str, float, unicode, bytes]


   def is_enum(t: type) -> bool:
      return is_namedtuple(t) and not t._fields

   if t == bool:
        return dict(action='store_true')

   elif t in primitives:
       return dict(type=t)

   elif is_enum(t):
       raise ValueError("Enum types not allowed outside of Union.")

   elif is_namedtuple(t):
       for name, typ in t._field_types.items():
           d = to_argparse(typ)
           if 'required' not in d and d.get('action') != 'store_true':
               d['required'] = True
           p.add_argument('--'+name, **d)


   elif issubclass(t, Tuple):
       if t.__tuple_use_ellipsis__: # variable lenth tuple
           element_type = t.__tuple_params__[0]
           return to_argparse(List[element_type])
       raise NotImplemented("Well-defined tuples not supported")

   elif issubclass(t, Union):
       params = t.__union_params__
       assert all(map(is_enum, params))
       choices = list(map(lambda x: x(), params))
       def choice(s: str) -> NamedTuple:
           try:
               #TODO: This is . . . questionable.
               return next(filter(lambda x: str(x) == s + '()', choices) )
           except:
               raise ValueError
           #("Needed one of %s" % ' '.join(map(lambda x: x.__name__, params)))
       return dict(type=choice, choices=choices)

   elif issubclass(t, Optional):
       rest = to_argparse(t.__union_params__[0]) or {}
       # Only optional options can have defaults
       if default is not None:
           rest.update(default=default)
       p.add_argument(flag, required=False, **rest)

   elif issubclass(t, list):
       element_type = to_argparse(t.__parameters__[0])
       return dict(nargs='+', **(element_type))
   elif issubclass(t, object):
       return dict(type=t)
   else:
       raise ValueError("Type %s not supported" % t)

def get_ordered_annotations(func):
    ann = func.__annotations__
    argnames = func.__code__.co_varnames
    od = OrderedDict()
    for a in argnames:
        od[a] = ann[a]
    return od
def dict2argparser(args, defaults):
   if 'return' in args:
       del args['return']
   a = argparse.ArgumentParser()
   for name, t in args.items():
      d =  type_to_argparse(t, a, defaults.get(name))
      if d:
          a.add_argument(name, **d)
   return a

# this problem is because argparse needs them in the right orderh
# for fwd to be added as a positional argument before rev
#def func2parsed(func: Callable[[...],Any], defaults: Dict[str,Any]) -> Tuple[ArgumentParser, Callble[[Namespace],Namespace]]:
def func2parsed(func,  defaults: Dict[str,Any]) -> Tuple[ArgumentParser, Callable[[Namespace],Namespace]]:
    types = get_ordered_annotations(func)
    p = dict2argparser(types, defaults)

    def extract_args(name_space):
        def extract(nt, args):
            vals = (getattr(name_space, arg) for arg in args)
            args_dict = dict(zip(args, vals))
            return nt(**args_dict)

        non_nt_types, nts = partition(compose(is_namedtuple, get(1)), types.items())
        nt_names, nt_types = zip(*nts)
        nt_args = map(lambda x: x._fields, nt_types)
        args_dict = dict(zip(nt_names, map(extract, nt_types, nt_args)))
        non_nt_types = list(non_nt_types)
        non_nts = dict((attr, getattr(name_space, attr)) for (attr,_) in non_nt_types)
        args_dict.update(non_nts)
        return args_dict

    # intended usage: func(**extract_nts(p.parse_args()))
    return p, extract_args

def run_args(func):
    p, extract_args = func2parsed(func)
    return func(**extract_args(p.parse_args()))

