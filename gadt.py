from fn import _ as X
from functools import partial
from typing import *
from fn.iters import partition
from toolz.dicttoolz import merge
from pyparsing import Literal, Word, delimitedList
import typing
print(typing.__file__)
class Settings(NamedTuple): pass
class ADT(NamedTuple): pass
t_params = {
        Tuple :    X.__tuple_params__,
        Dict  :    X.__parameters__,
        Union :    X.__union_params__,
        Optional : X.__union_params__[0],
        List :     X.__parameters__
}

Enum = 'Enum'
is_GADT = lambda x:  hasattr(x, '_fields')

primitives = [str   , int   , bool  , float , type(None), bytes ]

def traverse_type(x, tfuncs):
   recur = lambda y: traverse_type(y, tfuncs)
   if x in primitives:
       return tfuncs[x]
   elif is_GADT(x):
       # NamedTuple isn't a type, so this can't be a subclass check
       vals = list(map(recur, x._field_types.values()))
       if vals == []:
           return tfuncs['Enum'](x)
       #return tfuncs[NamedTuple](x, vals)
       return tfuncs[NamedTuple](x, vals)
   else: 
       matches = list(filter(lambda kv: issubclass(x, kv[0]), t_params.items()))
       if matches:
           _type, paramfunc = matches[0]
           params = paramfunc(x)
           vals = map(recur, params)
           return tfuncs[_type](params)
       else:
           matches = list(filter(lambda k: k == x.__origin__, t_params.keys()))
           assert matches, "%s not in t_params" % x
           assert len(matches) == 1
           _type = matches[0]
           params = t_params[_type](x)
           return tfuncs[_type](params)

just = lambda x: lambda: x
def get_NamedTuple_name(x):
    try:
        return re.compile("([^\.]+)'>$").search(str(x)).groups()[0]
    except:
        return str(x) 
# add case for Enum (NamedTuple?), provided as 
# Union[NamedTuple1, NamedTuple1]
       
listOf = lambda x: delimitedList(x, ',') #.setAction(lambda s: s.split(',')) # not sure how works if x has a setAction already

        # NamedTuple represents args that are grouped together (by parens)
        # this is to enable grouped optional arguements, for example.
        # Union should represent |
        # Optional represents [ ] 

#NOTE: oh, could simply use `traverse_type` because a function
# is a `Callable`?
def GADT(name: str, **fields) -> NamedTuple:
   return ADT(name, fields.items())
TrimOpts = GADT('TrimOpts', 
        paired=Optional[bool], trim_n=Optional[bool], 
        q=Optional[int], removebases=Optional[int])
#MakeFileType = lambda n,**kv: GADT(n, [('name', str)] + list(kv.items()))
MakeFileType = lambda n,**kv: GADT(n, merge(kv, {'name', str}))
Fastq = MakeFileType('Fastq', ext='fastq')
PairedEnd = Tuple[Fastq, Fastq]

#TODO: needs to be paramaterizable based on positional/optional
def make_str_func(make_tostr): 
    return {
            bool : '',
            int  : '<int>',
            float  : '<float>',
            Optional : '[ {} ]'.format,
            List : lambda xs: x[0] + '...',
            Enum : lambda x,_: get_NamedTuple_name(x),
            NamedTuple : lambda xs: '( {} )'.format(' '.join(map(make_tostr, xs))), 
            Tuple : lambda xs: '( {} )'.format(' '.join(map(make_tostr, xs))), 
            Union : lambda xs: '( {} )'.format(' | '.join(map(make_tostr, xs))) # these last two will add `--` to the front . . .
    }
make_tostr_positional = lambda x: traverse_type(x, make_str_func(make_tostr_positional))
def make_tostr_option(nt: NamedTuple) -> str:
    string = traverse_type(nt, make_str_func(make_tostr_option))
    return '--{} {}'.format(get_NamedTuple_name(nt), string)

def handle_NT_parser(x, _):  # ingore resolved fields because have to convert them to parsers
       name = get_NamedTuple_name(x)
       if resolved_fields == []:  # treat as Enum
           return Literal(name).setAction(lambda _: x)
       subparsers = starmap(make_option_parser, x._field_types.items())
       parser = reduce(operator.add, subparsers)
       return Just('(') + parser + Just(')')



#make_positional_parser = traverse_type(_type, opt_parse_funcs)

#TODO: Need an outer-most function which won't add an --to the front.
def make_option_parser(nt: NamedTuple) -> None: 
    name = get_NamedTuple_name(nt)
    long = Literal('--').suppress()
    short = Literal('-').suppress()
    flag = (long + (Literal(name))).leaveWhitespace() | (short + Literal(name[0])).leaveWhitespace()
    opt_parse_funcs = {
            bool : flag.setAction(lambda _: True), # so it must default to False somehow
            int  : flag + Number().setAction(int),
            float  : flag + Float().setAction(float),
            str    : flag + Word(),
            Optional : lambda x: Just('[') + flag + x + Just(']'),
            List : lambda x: flag + listOf(x[0]),
            Enum : handle_NT_parser,
            Union : lambda xs: Just('(') + reduce(operator.ior, xs) + Just(')') # this works because NTs will get resolved to parsers
    }
    option = traverse_type(nt, opt_parse_funcs)
    return option


#@@@@@@@@@@@#
# Interface #
#@@@@@@@@@@@#
Fasta = MakeFileType('Fasta', ext='fasta') 
SeqFile = Union[Fasta, Fastq]

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
def func(f1: Fastq, f2: Fastq, opts: TrimOpts) -> PairedEnd:
    print(f1, f2, opts)
annotations = func.__annotations__
pos_args, opt_args = partition(is_GADT, annotations.values())
string =  ' '.join(map(make_tostr_positional, pos_args))
string += ' '.join(map(make_tostr_option, opt_args))
