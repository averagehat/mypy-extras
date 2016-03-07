from ioutils import *
from typing import * 
from toolz import compose
from gadt import partition
from toolz.dicttoolz import keyfilter
from functools import partial, reduce

FilterOpts = AlignOpts = NamedTuple("Warning", [])
def gunzip(gz: GZip) -> Fastq:
    sh.gunzip(gz.name)
    return Fastq(gz.drop("gz"))

def trim_fastq(fqs: PairedEnd, opts: TrimOpts) -> PairedEnd:
    cmd = sh.cutadapt.bake(removebases=opts.removebases, qualcutoff=opts.qualcutoff, trim_n=opts.trim_n)
    cmd(fwd, rev)
    return fwd.trim, rev.trim

def filter_fastq(fqs: PairedEnd, opts: FilterOpts) -> PairedEnd:
    pass # run filter

def align_paired(fqs: PairedEnd, opts: AlignOpts) -> Bam:
    sh.bwa.mem(*fqs)
    return Bam("paired.bam")

def tagbam(bam: Bam) -> Bam:
    pass

def freebayes(bam: Bam, ref: Fasta) -> VCF:
    vcf = VCF("freebayes.vcf")
    sh.freebayes(bam, f=ref, _out=vcf.name)
    return vcf

def consensus(bam: Bam, ref: Fasta, vcf: VCF) -> Fasta:
    pass # run consensus
Func = Callable[...,Any]
Node = Tuple[Func, Tuple[str,type], Tuple[str,type]]

def get_pos_opt_args(func: Func) -> Node:
    annotations = func.__annotations__
    pos_args, opt_args = partition(lambda x: x[0] == 'opts', annotations.items()) 
    return func, dict(pos_args), dict(opt_args)

def order_funcs(funcs: List[Func], input: Tuple[File,File]) -> List[Node]:
    nodes = map(get_pos_opt_args, funcs)
    def fill_opts(node: Node) -> Func:
        f, _, optargs = node
        if not optargs: return node
        assert len(optargs) == 1
        #TODO: fill in options by their type.
        return partial(f, **{next(iter(optargs.keys())) :  None}) , _, optargs

    filled_nodes = list(map(fill_opts, nodes))
    def top_sort(acc: List[Node], to_go: List[Node]) -> List[Node]:
        if to_go == []: return acc
        def is_satisfied(node: Node) -> bool:
            f, args, _ = node
            required = keyfilter(lambda x: x != 'return', args) #rettype = args['return']
            acc_rets = map(lambda x: x[1]['return'], acc)
            acc_rets = list(acc_rets)
            satisfied = all([(t in acc_rets) for t in required.values()])
            return satisfied
        nextnode = next(filter(is_satisfied, to_go))
        next_to_go = list(filter(is_satisfied, to_go))[1:]
        return top_sort([nextnode] + acc, next_to_go)
    sorted = top_sort([input], filled_nodes)
    return sorted

def build_pipeline(funcs: List[Func], input) -> Func:
    nodes = order_funcs(funcs, input)
    ordered_funcs = map(lambda x: x[0], nodes)
    return reduce(compose, ordered_funcs)

funcs = [consensus, freebayes, tagbam, align_paired, filter_fastq, trim_fastq, gunzip]
res = build_pipeline(funcs, (id, {'return' : Tuple[Fastq, Fastq]}, []))
print(res)
nodes = (order_funcs(funcs, (id, {'return' : Tuple[Fastq, Fastq]}, [])))
print(nodes)
# file_funcs = dir(__file__)

# most, if not all the difficulty of writing this could've been mitigated by pinning down the types . . . 
# worth biting the bullet, especially for higher-order functions right now
