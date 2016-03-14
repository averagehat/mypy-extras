from pyparsing import delimitedList, Literal, Regex, Word, alphas, White, ZeroOrMore, Or, And
from itertools import starmap
from pyparsing import Optional as ParseOpt
from toolz.dicttoolz import valfilter
from gadt import * 
from functools import reduce
import operator
from typing import * 
is_Option = lambda x: issubclass(x, Union) and x.__union_params__[1] == type(None)
listOf = lambda x: delimitedList(x, ' ') #.setAction(lambda s: s.split(',')) # not sure how works if x has a setAction already

        # NamedTuple represents args that are grouped together (by parens)
        # this is to enable grouped optional arguements, for example.
        # Union should represent |
        # Optional represents [ ] 
#make_positional_parser = traverse_type(_type, opt_parse_funcs)

#TODO: Need an outer-most function which won't add an --to the front.
def handle_NT_parser(x, _):  # ingore resolved fields because have to convert them to parsers
       name = x.__name__
       if resolved_fields == []:  # treat as Enum
           return Literal(name).setAction(lambda _: x)
       subparsers = starmap(make_option_parser, x._field_types.items())
       parser = reduce(operator.add, subparsers)
       return Just('(') + parser + Just(')')
#def make_option_parser(nt: NamedTuple) -> None: 
def make_option_parser(name: str, type: type) -> None: 
    long = Literal('--').suppress()
    short = Literal('-').suppress()
    flag = (long + (Literal(name)).leaveWhitespace() | (short + Literal(name[0]))).leaveWhitespace().setParseAction(lambda _: name)
    Number = Regex("[0-9]+")
    Float = Regex("[0-9.]+")
    wrap = lambda f:  {name : f }
    id = lambda x: x 
    opt_parse_funcs = {
            bool : lambda _: ZeroOrMore(flag).setParseAction(lambda x: [name, bool(x)]), # so it must default to False somehow
            int  : lambda _: flag + Number().setParseAction(lambda x: int(x[0])),
            float  : lambda _: flag + Float().setParseAction(float),
            str    : lambda _: (flag + Word(alphas)),
            Optional : lambda x: ParseOpt(x),
            #List : lambda x: flag + White() + listOf(next(x)),
            List : lambda x: delimitedList(next(x), White()).setParseAction(lambda xs: [name , xs[1::2]]),
            object : lambda x: flag + Word(alphas).setParseAction(x),
            NamedTuple : lambda x: Literal(x.__name__).setParseAction(lambda _: x),
            Union : lambda xs: flag + reduce(operator.ior, xs)
    }
    option = traverse_type(type, opt_parse_funcs)
    return option
ExampleOpts = NamedTuple('ExampleOpts', [('bool', bool),  ('str', str)])

pairs = lambda xs: [] if not xs else [(xs[0], xs[1])] + pairs(xs[2:]) 
Opts = NamedTuple('Opts', [('list', List[int])])
opts = list(starmap(make_option_parser, Opts._field_types.items()))
trim = starmap(make_option_parser, TrimOpts._field_types.items())
items = TrimOpts._field_types.items()
trim = list(trim)
input = "-p MiSeq -p IonTorrent -q 99"
#NOTE: may need to support optional files as input (not in options object)
PFunc = Callable[...,Any]
Parser = Any
def func_parser(func: PFunc) -> Parser:
    pos_args, opt_args = get_file_options_args(func)
    opts_parser = options_parser(opt_args[0])
    posparser = And([Word(alphas) for _ in range(len(pos_args))] + [opts_parser])
    return posparser #+ White() +  opts_parser 

def get_default_args(opt: Dict[str,type]) -> Dict[str,Optional[bool]]:
    items = opt._field_types.items()
    defaults = {k : None for k,v in items if is_Option(v)}
    bools = {k : False for k,v in items if v == bool}
    defaults.update(bools)
    return defaults

OptionNT = type
def execute_func_parser(func: PFunc, string: Parser) -> Tuple[str,OptionNT]:
    pos_args, opt_args = get_file_options_args(func)
    Opt = opt_args[0]
    defaults = get_default_args(Opt)
    parser = func_parser(func)
    raw_result = parser.parseString(string, parseAll=True)
    just_opts = raw_result[len(pos_args):]
    pos_files = raw_result[:len(pos_args)]
    d = dict(pairs(just_opts))
    defaults.update(d)
    opt_obj = Opt(**defaults)
    return pos_files, opt_obj

def just_options_parse(opts: OptionNT, string: str) -> OptionNT:
    defaults = get_default_args(opts)
    parser = options_parser(opts)
    raw_result = parser.parseString(string, parseAll=True)
    d = dict(pairs(raw_result))
    defaults.update(d)
    return opts(**defaults) 

def options_parser(opts: OptionNT) -> Parser: 
    parsers = starmap(make_option_parser, opts._field_types.items())
    return delimitedList(Or(parsers), White())
#result = TrimOpts(**defaults)

def func(f1: Fastq, f2: Fastq, opts: TrimOpts) -> PairedEnd:
    print(f1, f2, opts)

#s = """A B --platforms <MiSeq> -p <Roche454> --removebases 2 --paired  --trim_n  --q 0"""
#s = """--platforms MiSeq -p Roche454 --removebases 2 --paired  --trim_n  --q 0"""
#parser = func_parser(func)

#print(execute_func_parser(func, s))

