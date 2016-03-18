from ioutils import File, sh, StatsFile, FastaIndex, Fastq, Fasta, Bam, VCF, GZip, PairedEnd, Platform
from typing import Callable, Tuple, List, TypeVar, Iterator, Set, Any, NamedTuple, Iterable, Optional, Union
from collections import Counter
from itertools import starmap
A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")

TrimOpts = NamedTuple('TrimOpts', 
        [('paired',bool), 
         ('trim_n', bool),
         ('q', Optional[int]),
         ('removebases', Optional[int]),
         ('platforms', List[Platform])])

TagBamOptions = NamedTuple("TagBamOptions",
                          [('CN', Optional[str]),
                           ('SM', Optional[str])])

FilterOpts = NamedTuple("FilterOpts",
                        [('indexQualMin', int),
                         ('drop_ns', bool),
                         ('platforms', List[Platform])])

def gunzip(gz: GZip) -> Fastq:
    sh.gunzip(gz.name)
    return Fastq(gz.drop("gz"))

def samtools_flagstats(bam: Bam) -> StatsFile:
    stats = sh.samtools("flagstats", bam, _iter=True)
    statsFile = StatsFile("flagstats.txt") 
    fields = ['in total', 'duplicates', ' mapped (', 'paired in sequencing', 'read1', 'read2', 'properly paired', 'with itself and mate mapped', 'singletons']
    with statsFile.open('w') as out:
        fieldsInLine = lambda s: filter(s.__contains__, fields) # type: Callable[[str], Iterable[str]]
        counts = Counter(map(fieldsInLine, stats))
        lines = starmap("{}{}".format, counts.items())
        out.writelines(lines)
    return statsFile

def trim_fastq(fqs: PairedEnd, opts: TrimOpts) -> PairedEnd:
    fwd, rev = fqs
    cmd = sh.cutadapt(fwd, rev, removebases=opts.removebases, trim_n=opts.trim_n)
    return Fastq(fwd.trim), Fastq(rev.trim)

def filter_fastq(fqs: PairedEnd, opts: FilterOpts) -> PairedEnd:
    pass # run filter

def align_paired(fqs: PairedEnd, ref: FastaIndex) -> Bam:
    sh.bwa("mem", fqs[0], fqs[1])
    return Bam("paired.bam") 

def tagbam(bam: Bam, opts: TagBamOptions) -> Bam:
    sh.tagreads(bam, CN=opts.CN, SM=opts.SM)
    return bam

def freebayes(bam: Bam, ref: Fasta) -> VCF:
    vcf = VCF("freebayes.vcf")
    sh.freebayes(bam, f=ref, _out=vcf.name)
    return vcf 

def index_fasta(f: Fasta) -> List[FastaIndex]:
    index_extensions = ['amb', 'ann', 'bwt', 'pac', 'sa']
    outputs = [FastaIndex(getattr(f, ext)) for ext in index_extensions]
    sh.bowtie("index", f)
    return outputs

def consensus(bam: Bam, ref: Fasta, vcf: VCF) -> Fasta:
    pass # run consensus


#required_order = [tagbam, freebayes]

id = lambda x: x
funcs = [consensus, freebayes, tagbam, align_paired, filter_fastq, trim_fastq, gunzip]
nodes = (order_funcs(funcs, (id, {'return' : Tuple[Fastq, Fastq]}, [])))

runner = build_pipeline(funcs, (id, {'return' : Tuple[Fastq, Fastq]}, []))

# file_funcs = dir(__file__)
