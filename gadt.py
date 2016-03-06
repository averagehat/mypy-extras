from typing import Tuple, Dict, Union, Optional, NamedTuple, List, \
        Callable, Any, TypeVar

from toolz.dicttoolz import merge
T = TypeVar("T")
t_params = {
        Tuple :    lambda x: x.__tuple_params__,
        Dict  :    lambda x: x.__parameters__,
        Union :    lambda x: x.__union_params__,
        Optional : lambda x: x.__union_params__[0],
        List :     lambda x: x.__parameters__
}
TypeFilter = Callable[[type], bool]
is_GADT = lambda x:  hasattr(x, '_fields') # type: TypeFilter
is_NamedTuple = lambda x:  hasattr(x, '_fields') # type: TypeFilter
is_Settings = lambda x: False if not hasattr(x, '_field_types') else 'Settings' in str(x) # type: TypeFilter
primitives = [str   , int   , bool  , float , type(None), bytes ]
# Ugh, want to use GADTs as positional arguments (e.g., `Fastq`),
# But also for options arguments, can't simply pattern match off
# of namedtuple in that case
# pos_args, opt_args = dict(partition(lambda x: x[0] == 'opts', annotations.items()))
# str needs to be generalized to T
def traverse_type(x: type, tfuncs:  Dict[Union[Any,type], Callable[[Any], T]]) -> T:
   # it's unclear how to type the below lambda because it's dependent on T,
   # which is a type-parameter of the function & tfuncs
   recur = lambda y: traverse_type(y, tfuncs) 
   if x in primitives:
       return tfuncs[x](x)
   elif is_NamedTuple(x):
       return tfuncs[GADT](x) 
   elif issubclass(x, Union) and x.__union_params__[1] == type(None):
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
       else: # list-like
           match_listish = lambda k: k == x.__origin__ # type: Callable[[Any], bool]
           matches = list(filter(match_listish, t_params.keys()))
           assert matches, "%s not in t_params" % x
           assert len(matches) == 1
           _type = matches[0]
           params = t_params[_type](x)
           vals = map(recur, params)
           return tfuncs[_type](vals)

just = lambda x: lambda: x
def get_NamedTuple_name(x: type) -> str:
    import re
    try:
        return re.compile("([^\.]+)[']>$").search(str(x)).groups()[0]
    except IndexError:
        return str(x) 

def GADT(_name: str, **fields: type) -> NamedTuple:
    return NamedTuple(_name, fields.items())#fields.items())

def Settings(_name: str, **fields: type) -> NamedTuple:
    return GADT(name+'Settings', **fields)

def make_str_func(flag: str) -> Dict[Any,Callable[[Any],str]]: # flag is empty in case of positional
    just = lambda x: lambda _: x # type: Callable[[str], Callable[[Any], str]]
    flag = '--' + flag + ' ' 
    return {
            bool : just(flag),
            str : just(flag + '<str>'),
            int  : just(flag + '<int>'),
            float  : just(flag + '<float>'),
            Optional : '[ {} ]'.format,
            List : lambda xs: '{}...'.format(next(xs)),
            GADT : lambda x: '<{}>'.format(get_NamedTuple_name(x)),
            Union : lambda xs: flag + '( {} )'.format(' | '.join(xs)), # these last two will add `--` to the front . . .
            Tuple : lambda xs: '( {} )'.format(' '.join(xs)), 
            #NamedTuple : lambda xs: '( {} )'.format(' '.join(map(make_tostr, xs))), 
            #NamedTuple : lambda n,xs: '( {} )'.format(' '.join(xs)),
    }

make_tostr_positional = lambda x: traverse_type(x, make_str_func(''))
def make_tostr_option(nt: NamedTuple) -> str:
    strings = [traverse_type(_type, make_str_func(field)) for field, _type in nt._field_types.items()]
    return ' '.join(strings)

#@@@@@@@@@@@#
# Interface #
#@@@@@@@@@@@#
# TODO: GADT function doesn't work, because MyPy can't handle dynamically generated types. It can handle NamedTuples, though.

MiSeq = GADT("MiSeq")
Roche454 = GADT("Roche454")
IonTorrent = GADT("IonTorrent")
Platform = Union[MiSeq,Roche454,IonTorrent]
MakeFileType = lambda n,**kv: GADT(n, **merge(kv, {'name': str}))
Fastq = MakeFileType('Fastq', ext='fastq')
PairedEnd = Tuple[Fastq, Fastq]
Fasta = MakeFileType('Fasta', ext='fasta') 
SeqFile = Union[Fasta, Fastq]
TrimOpts = GADT('TrimOpts', 
        paired=bool, trim_n=bool,  # not sure Optional[bool] makes sense
        q=Optional[int], removebases=Optional[int],
        adapters=List[str], platforms=List[Platform])

def trim_reads(fs: PairedEnd, opts: TrimOpts) -> PairedEnd:
    pass # do stuff with input
def prep_fastq(f: SeqFile) -> Fastq:
    pass # do stuff with input
'''
if __name__ == '__main__':
    command = basic_command(trim_reads)
    command.run()
    command = command.sub_commands(trim_reads, prep_fastq)
    command.run()
    # this.py trim_reads foo 
    # this.py prep_fastq foo
    # Where command.run() handles --help, printing usage statemetns, etc., and calling the function with the positional + optional arguments.

'''
def partition(pred: Callable[[T], bool], seq: List[T]) -> Tuple[List[T], List[T]]:
    _not = lambda f: lambda x: not f(x) # type: Callable[[Callable[[T], bool]],Callable[[T], bool]]
    return filter(_not(pred), seq), filter(pred, seq)

def func(f1: Fastq, f2: Fastq, opts: TrimOpts) -> PairedEnd:
    print(f1, f2, opts)
annotations = func.__annotations__
del annotations['return']
pos_args, opt_args = partition(lambda x: x[0] == 'opts', annotations.items())
pos_args, opt_args = dict(pos_args), dict(opt_args) #exclude return type from pos_args
string =  ' '.join(map(make_tostr_positional, pos_args.values()))
string += ' ' + ' '.join(map(make_tostr_option, opt_args.values()))
print(string)
#NOTE: could sort by type (booleans first) to make clearer
