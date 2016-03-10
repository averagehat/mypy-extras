from ioutils import File, sh, StatsFile, FastaIndex, Fastq, Fasta, Bam, VCF, GZip, PairedEnd, Platform
from pipeliine import build_pipeline, order_funcs
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

def tagbam(bam: Bam, opts: TagBamOptions) -> Sam:
    outSam = Bam(bam.drop("bam").tagged.bam)
    sh.tagreads(bam, CN=opts.CN, SM=opts.SM, o=outSam)
    return outSam

just_bam = run('sam_to_bam', input=options['input'])
sort_bam = run('sort_bam', input=just_bam, output=output)
index_bam = run('index_bam', input=sort_bam)

def toBamIndexSort(sam: Sam) -> (Bam, Index):
    # sh can't do pipes properly
    from plumbum.cmd import samtools
    bam = Bam(sam.drop("sam").bam)
    chain = samtools['view', sam, '-hb'] | \
        samtools['sort', '-', bam.drop("bam")]
    # samtools view tagged.sam -hb | samtools sort - tagged.bam
    print chain
    chain()
    next = samtools['index', bam]
    print next
    next()
    return bam

def freebayes(bam: Bam, ref: Fasta) -> VCF:
    vcf = VCF("freebayes.vcf")
    sh.freebayes(bam, f=ref, _out=vcf)
    return vcf

def index_fasta(f: Fasta) -> List[FastaIndex]:
    index_extensions = ['amb', 'ann', 'bwt', 'pac', 'sa']
    outputs = [FastaIndex(getattr(f, ext)) for ext in index_extensions]
    sh.bowtie("index", f)
    return outputs

def consensus(bam: Bam, ref: Fasta, vcf: VCF) -> Fasta:
    out = Fasta("conesnsus.fasta")
    sh.consensus(**locals())
    return out


funcs = [consensus, freebayes, tagbam, align_paired, filter_fastq, trim_fastq, gunzip]
res = build_pipeline(funcs, (id, {'return' : Tuple[Fastq, Fastq]}, []))
print(res)
nodes = (order_funcs(funcs, (id, {'return' : Tuple[Fastq, Fastq]}, [])))
print(nodes)


