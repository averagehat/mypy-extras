from path import Path
from typing import *
import sh as __sh
from itertools import starmap, permutations

A = TypeVar("A")
class File(Path): 
  def __getattr__(self, ext: str) -> str:
    return '{0}.{1}'.format(self.name, ext)

  def open(self, mode: Optional[str] = None) -> TextIO:
    pass

  def drop(self, ext: str) -> str:
    xs = self.name.split('.')
    assert xs[-1] == ext
    return '.'.join(xs[:-1]) 
class StatsFile(File): pass
class FastaIndex(File): pass
class SeqFile(File): pass
class Fastq(File): pass
class Fasta(File): pass
class Bam(File): pass
class VCF(File): pass
class GZip(File): pass

MiSeq = NamedTuple("MiSeq", [])
Roche454 = NamedTuple("Roche454", [])
IonTorrent = NamedTuple("IonTorrent", [])

Platform = Union[MiSeq,Roche454,IonTorrent] 

PairedEnd = Tuple[Fastq, Fastq]


# switch over to Either???
class ShWrapper(object):
  def __getattr__(self, name: str) ->  Callable[...,Union[List[str],Iterator[str]]]: # note: can't represen i.e. sh.foo.bar
    return __sh.Command(name)

sh = ShWrapper()

def anyIntersection(*sets: Set[A]) -> bool:
    return any( starmap( set.intersection, permutations( sets))) 

def _not(f: Callable[...,bool]) -> Callable[...,bool]:
  def wrapped(*x: Any) -> bool: return not f(*x)
  return wrapped

def _or(f: Callable[...,bool], g: Callable[...,bool]) -> Callable[...,bool]:
  def wrapped(*x: Any) -> bool: return f(*x) or g(*x)
  return wrapped

FqFilter = Callable[[Fastq],bool]

def group_fqs(fqs: List[Fastq]) -> Tuple[List[PairedEnd], List[Fastq]]:
    isFwd = lambda x: '_R1_' in x.name  # type: FqFilter
    isRev = lambda x: '_R2_' in x.name  # type: FqFilter
    isUnpaired = _not(_or(isFwd,isRev)) # type: FqFilter
    fwd =      set(filter(isFwd, fqs))
    rev =      set(filter(isRev, fqs))
    unpaired = set(filter(isUnpaired, fqs))
    assert (fwd | rev | unpaired) == set(fqs), "Not all fqs grouped in %s" % fqs
    assert not anyIntersection(fwd, rev, unpaired), "Sets intersected! %s" % fqs
    # could check that none of them intersect
    return list(zip(fwd, rev)), list(unpaired)

#"pattern matching" example
#def get_sequences(p: SeqFile) -> Iterator[str]:
#    with p.open('r') as f:
#        if isinstance(p, Fastq):
#            for x in  itertools.islice(f, 0, sys.maxsize, 4):
#                yield x
#        else:
#            return read_fasta(p)

#alternatively could use NamedTuples: 
# Fastq = NamedTuple('Fastq', [('name', str)])
#extensions =  { GZip    : ['gz'],
#    Fastq : ['fq', 'fastq'], 
#    Fasta : ['fa', 'fasta'], 
#    Bam :   ['bam'],
#    VCF : ['vcf']
#    }
