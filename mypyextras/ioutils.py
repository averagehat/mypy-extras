from path import Path
from typing import * 

class File(Path):
  def __getattr__(self, ext: str): # how type this?
    try:
      return super(self.__class__, self).__getattr__(ext)
    except:
      return self.__init__('{0}.{1}'.format(self.name, ext))

  def drop(self, ext: str) -> None:
      xs = self.name.split('.')
      assert xs[-1] == ext
      return '.'.join(xs[:-1])

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

TrimOpts = NamedTuple('TrimOpts', 
        [('paired',bool), 
         ('trim_n', bool),
         ('q', Optional[int]),
         ('removebases', Optional[int]),
         ('platforms', List[Platform])])
