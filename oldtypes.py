from hypothesis import strategies as st
from typing import Dict, Tuple, List, Iterator, Set, Union, Optional, TypingMeta, NamedTuple
import re
import operator
from functools import partial
import string
from collections import namedtuple, OrderedDict
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
       try:
           #Only way I know how to extract the name so it's pretty...
           name = re.compile("([^\.]+)'>$").search(str(x)).groups()[0]
       except:
           name = str(x) 
       fts = OrderedDict(x._field_types)
       nt = namedtuple(name, fts.keys())
       vals = map(resolve, fts.values())
       strat = st.tuples(*vals).map(lambda x: nt(*x))
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
          } #TODO: missing: Iterable , etc.
       # For some reason List[T] not a subclass of List: issubclass(x, List) == False. So do these hijinks
       params = x.__parameters__
       assert len(params) == 1, "Wrong type %s, not a list-like" % x
       matches = filter(lambda k: k == x.__origin__, collections.keys())
       assert len(matches) == 1, "Should have exactly one match. %s matched with %s" % (x, matches)
       collection_strat = collections[matches[0]]
       strat = collection_strat(resolve(params[0]))
   return strat
# see https://docs.python.org/3/library/typing.html
# not Generics
# not Callables
def ADT(name: str, **fields: Type) -> NamedTuple:
   return NamedTuple(name, fields.items())

T = NamedTuple("TRUE", [])
F = NamedTuple("FALSE", [])
Or = NamedTuple("Or", [])
And = NamedTuple("And", [])
Xor = NamedTuple("Xor", [])
Neg = ADT("Neg")
Bool = Union[TRUE,FALSE]
UnaryOp = Union[Negate]
BinaryOp = Union[Or,Xor,And]
Op = Union[UnaryOp,BinaryOp]
arbitrary = resolve
given_binary = partial(given, Bool, Bool, BinaryOp)
way to do it like this?:
   And(Or(x, Neg(y)), y)
def beval(op: BinaryOp, x: Bool, y: Bool) -> Bool:
   if issubclass(op, Or):
      return T if T in [x, y] else F
   if issubclass(op, And):
      return T if T == x and T == y else F
   if issubclass(op, Xor):
      return beval(And, beval(Or, x, y), ueval(Neg, beval(And, x, y)))

@given(Bool, BinaryOp)
def test_idempotent_law(self, b, op):
   assert op(b, b) == op(b, b)

@given_binary
def test_commutative_law(self, b1, b2, op):
   assert beval(op, b1, b2)  == beval(op, b2, b1)

@given(Bool, Bool, Bool, BinaryOp)
def test_associative_law(self, b1, b2, b3, op):
   assert beval(op, b1, beval(op, b2, b3)) == beval(op, b1, beval(op, b2, b3))

@given(Bool, Bool, Bool, BinaryOp)
def test_demorgans_law(self, x, y, op1, op2):
   assume(op1 != op2)
   assert ueval(Neg, beval(op1, x, y)) == beval(op2, ueval(Neg, x), ueval(Neg, y))
   #assert ueval(Neg, beval(op2, x, y)) == beval(op1, ueval(Neg, x), ueval(Neg, y))

MakeFileType = lambda n,**kv: GADT(n, [('name', str)] + kv.items())
Fastq = MakeFT('Fastq', ext='fastq')
Bam   = MakeFT('Bam', ext='bam') 
Fasta = MakeFT('Fasta', ext='fasta') 
VCF   = MakeFT('VCF', ext='vcf') 
PairedEnd = Tuple[Fastq, Fastq]
SeqFile = Union[Fasta, Fastq]
BioFile = Union[SeqFile, Bam, VCF]
Qual = int
TrimOpts = GADT('TrimOpts', 
        paired=Optional[bool], trim_n=Optional[bool], 
        q=Optional[Qual], removebases=Optional[int])

id = lambda x: x
case = issubclass

def prep_fastq(f: SeqFile) -> Fastq:
    if case(f, Fastq): return f
    if case(f, Fasta): return add_qual(f) # return a Task instead?

def trim_reads(fs: PairedEnd, opts: TrimOpts) -> PairedEnd:

Just = lambda s: Literal(s).suppress()
#NOTE: could genralize the `resolve` function above to 
# yield a sequence of the type tree (while applying the approprate functions?
if case(f, Optional):
    return Just('[') + make(f.__union_params__[0]) + Just(']')
long = Literal('--').suppress()
short = Literal('-').suppress()
flag = long + (Literal(name)) | short + Literal(name[0]))
if case(f, bool):
    return flag.setParseAction(lambda: bool)
if case(f, int):
    return flag.setParseAction(lambda: int)

# def match(f: T, d: #fancy typevar stuff
#def prep_fastq(f: SeqFile) -> Fastq:
#    match(f, {
#        Fasta : lambda x: add_qual(f),
#        Fastq : id
#        })
#



