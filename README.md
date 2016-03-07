
Define file inputs. Alternatively subclass typing.io.TextIO to be okay with sdin/stdout

```python 
from path import Path
class Fastq(Path): pass
class Fasta(Path): pass 
PairedEnd = Tuple[Fastq, Fastq]
```
Define options
```python
from typing import *
#sort of like an Enums in other langauges
MiSeq = NamedTuple("MiSeq", [])
Roche454 = NamedTuple("Roche454", [])
IonTorrent = NamedTuple("IonTorrent", []) 

Platform = Union[MiSeq,Roche454,IonTorrent]

TrimOpts = NamedTuple('TrimOpts', 
        [('paired',bool), 
         ('trim_n', bool),
         ('q', Optional[int]),
         ('removebases', Optional[int]),
         ('platforms', List[Platform])])
```
Define some functions to process the files based on the options.
```python
def trim_reads(f1: Fastq, f2: Fastq, opts: TrimOpts) -> PairedEnd:
    pass # do stuff with input

def fasta_to_fastq(fs: Fasta) -> Fastq:
    pass # do stuff with input
```
Run 
```
if __name__ == '__main__':
    command = basic_command(trim_reads)
    command.run()
    command = command.sub_commands(trim_reads, prep_fastq)
    command.run()
```
Usage statement
```bash
<Fastq> <Fastq> --platforms ( <MiSeq> | <Roche454> | <IonTorrent> )... --trim_n  [ --removebases <int> ] --paired  --adapters <str>... [ --q <int> ]
```
Commandline Parsing
```
#TODO
```
