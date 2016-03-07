from typing import Tuple, Dict, Union, Optional, NamedTuple, List, \
        Callable, Any, TypeVar
from path import Path
from toolz.dicttoolz import merge
T = TypeVar("T")
t_params = {
        Tuple :    lambda x: x.__tuple_params__,
        Dict  :    lambda x: x.__parameters__,
        Union :    lambda x: x.__union_params__,
        Optional : lambda x: x.__union_params__[0],
        List :     lambda x: x.__parameters__
}

primitives = [str   , int   , bool  , float , type(None), bytes ]

is_NamedTuple = lambda x:  hasattr(x, '_fields') # type: Callable[[type], bool]
is_Option = lambda x: issubclass(x, Union) and x.__union_params__[1] == type(None)

def traverse_type(x: type, tfuncs:  Dict[Union[Any,type], Callable[[Any], T]]) -> T:
   # it's unclear how to type the below lambda because it's dependent on T,
   # which is a type-parameter of the function & tfuncs
   recur = lambda y: traverse_type(y, tfuncs) 
   if x in primitives:
       return tfuncs[x](x)
   elif is_NamedTuple(x):
       return tfuncs[NamedTuple](x) 
   elif is_Option(x):
       #NOTE: Optional will get swallowed by Union otherwise,
       # because Optional is an alias for Union[T, None]
       value = recur(x.__union_params__[0])
       return tfuncs[Optional](value)
   else: 
       matches = list(filter(lambda kv: issubclass(x, kv[0]), t_params.items()))
       if matches:
           _type, paramfunc = matches[0]
           params = paramfunc(x)
           vals = map(recur, params)
           return tfuncs[_type](vals)
       elif hasattr(x, '__origin__'): # list-like
           match_listish = lambda k: k == x.__origin__ # type: Callable[[Any], bool]
           matches = list(filter(match_listish, t_params.keys()))
           assert matches, "%s not in t_params" % x
           assert len(matches) == 1
           _type = matches[0]
           params = t_params[_type](x)
           vals = map(recur, params)
           return tfuncs[_type](vals)
       else:  # some other subclass
           return tfuncs[object](x) 

def make_str_func(flag: str) -> Dict[Any,Callable[[Any],str]]: # flag is empty in case of positional
    just = lambda x: lambda _: x # type: Callable[[str], Callable[[Any], str]]
    flag = '--' + flag + ' ' 
    return {
            bool : just(flag),
            str : just(flag + '<str>'),
            int  : just(flag + '<int>'),
            float  : just(flag + '<float>'),
            object : lambda x: '<{}>'.format(x.__name__),
            NamedTuple : lambda x: '<{}>'.format(x.__name__),
            Optional : '[ {} ]'.format,
            List : lambda xs: '{}...'.format(next(xs)),
            Union : lambda xs: flag + '( {} )'.format(' | '.join(xs)), # these last two will add `--` to the front . . .
            Tuple : lambda xs: '( {} )'.format(' '.join(xs)), 
            #NamedTuple : lambda xs: '( {} )'.format(' '.join(map(make_tostr, xs))), 
    }

make_tostr_positional = lambda x: traverse_type(x, make_str_func(''))
def make_tostr_option(nt: NamedTuple) -> str:
    strings = [traverse_type(_type, make_str_func(field)) for field, _type in nt._field_types.items()]
    return ' '.join(strings)

def partition(pred: Callable[[T], bool], seq: Iterator[T]) -> Tuple[Iterator[T], Iterator[T]]:
    _not = lambda f: lambda x: not f(x) # type: Callable[[Callable[[T], bool]],Callable[[T], bool]]
    return filter(_not(pred), seq), filter(pred, seq)
#Fastq = NamedTuple('Fastq', [('name', str)])
#NOTE: could sort by type (booleans first) to make clearer
from operator import itemgetter as get
def get_file_options_args(func):
    annotations = func.__annotations__.copy()
    del annotations['return']
    pos_args, opt_args = partition(lambda x: x[0] == 'opts', annotations.items()) 
    pos_args = list(map(get(1), pos_args) )
    opt_args = list(map(get(1),  opt_args))
    return pos_args, opt_args

def gen_usage_for_function(func):
    pos_args, opt_args = get_file_options_args(func)
    string =  ' '.join(map(make_tostr_positional, pos_args)) 
    string += ' ' 
    string += ' '.join(map(make_tostr_option, opt_args))
    return string
