from argparse import ArgumentParser
import  argparse
from typing import * 
from collections import OrderedDict
try:
    unicode = unicode
except:
    unicode = str
#TODO: should wrap the result in the NamedTuples as appropriate
#TODO: create subcommands by function name
#TODO: inspect local module and produce subcommands for all functions matching a given pattern
#TODO: finish tests

is_namedtuple = lambda t: hasattr(t, '_fields')

def type_to_argparse(t: type, p: ArgumentParser) -> Dict[str,Any]:
   to_argparse = lambda x: type_to_argparse(x, p)
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
       p.add_argument(flag, required=False, **rest)

   elif issubclass(t, list):
       element_type = to_argparse(t.__parameters__[0]) 
       return dict(nargs='+', **(element_type))
   elif issubclass(t, object):
       return dict(type=t)
   else:
       raise ValueError("Type %s not supported" % t)

def dict2argparser(args): 
   if 'return' in args: 
       del args['return']
   a = argparse.ArgumentParser()
   for name, t in args.items():
      d =  type_to_argparse(t, a)
      if d:
          if is_namedtuple(t):
              name = '--%s' % name
              if 'required' not in d and d.get('action') != 'store_true':
                  d['required'] = True
          a.add_argument(name, **d)
   return a
