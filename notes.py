
# could have automatic extension matching
#class Bam(Path): pass
#class VCF(Path): pass
#class GZip(Path): pass
# within framework
    # Where command.run() handles --help, printing usage statemetns, etc., and calling the function with the positional + optional arguments.
#from fn import _ as X
#def read_fasta(f: TextIO) -> str:
#    _ = next(takewhile(X != '\n', f))
#    seq = takewhile(X != '>', f)
#    yield seq
#reduce(lambda (i,acc)
import sys
from typing.io import TextIO
import itertools
from  itertools import takewhile
def get_sequences(p: SeqFile) -> Iterator[str]:
    with p.open('r') as f:
        if isinstance(p, Fastq):
            for x in  itertools.islice(f, 0, sys.maxsize, 4):
                yield x
        else:
            return read_fasta(p)
class SeqFile(Path): pass
class Fastq(SeqFile): pass
class Fasta(SeqFile): pass
class Bam(Path): pass
class VCF(Path): pass
class GZip(Path): pass
#alternatively could use NamedTuples: 
# Fastq = NamedTuple('Fastq', [('name', str)])
extensions =  { GZip    : ['gz'],
    Fastq : ['fq', 'fastq'], 
    Fasta : ['fa', 'fasta'], 
    Bam :   ['bam'],
    VCF : ['vcf']
    }
