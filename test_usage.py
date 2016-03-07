
from path import Path
from typing import Tuple, Dict, Union, Optional, NamedTuple, List, Callable
from gadt import gen_usage_for_function
#Fastq = NamedTuple('Fastq', [('name', str)])
class Fastq(Path): pass
MiSeq = NamedTuple("MiSeq", [])
Roche454 = NamedTuple("Roche454", [])
IonTorrent = NamedTuple("IonTorrent", [])
Platform = Union[MiSeq,Roche454,IonTorrent]
PairedEnd = Tuple[Fastq, Fastq]

TrimOpts = NamedTuple('TrimOpts', 
        [('paired',bool), 
         ('trim_n', bool),
         ('q', Optional[int]),
         ('removebases', Optional[int]),
         ('platforms', List[Platform])])
def func(f1: Fastq, f2: Fastq, opts: TrimOpts) -> PairedEnd:
    print(f1, f2, opts)

string = gen_usage_for_function(func)
expected = """<Fastq> <Fastq> --platforms ( <MiSeq> | <Roche454> | <IonTorrent> )... [ --removebases <int> ] --paired  --trim_n  [ --q <int> ]"""
print(string)
print("\nShould look like,\n")
print(expected)
print("Warning, Nothing was tested . . . ")
# assert(string == expected) # dictionary order problems

# Ugh, want to use GADTs as positional arguments (e.g., `Fastq`),
# But also for options arguments, can't simply pattern match off
# of namedtuple in that case
# pos_args, opt_args = dict(partition(lambda x: x[0] == 'opts', annotations.items()))
# str needs to be generalized to T


