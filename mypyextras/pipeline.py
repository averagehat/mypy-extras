from ioutils import *
from toolz import compose
from gadt import partition
from operator import itemgetter as get
from toolz.dicttoolz import keyfilter
from functools import partial, reduce

Node = Tuple[Callable[...,Any], Dict[str,type], Dict[str,type]]

def get_pos_opt_args(func: Callable[...,Any]) -> Node:
    annotations = func.__annotations__
    is_opt = lambda x: x[0] == 'opts' # type: Callable[[Tuple[str,type]], bool]
    pos_args, opt_args = partition(is_opt, annotations.items()) 
    return func, dict(pos_args), dict(opt_args)

def order_funcs(funcs: List[Callable[...,Any]], input: Union[File, Tuple[File,File]]) -> List[Node]:
    nodes = map(get_pos_opt_args, funcs)
    def fill_opts(node: Node) -> Callable[...,Any]:
        f, _, optargs = node
        if not optargs: return node
        assert len(optargs) == 1
        #TODO: fill in options by their type. for now fill with None.
        return partial(f, **{next(iter(optargs.keys())) :  None}) , _, optargs
    filled_nodes = list(map(fill_opts, nodes))
    def top_sort(acc: List[Node], to_go: List[Node]) -> List[Node]:
        if to_go == []: return acc
        def is_satisfied(node: Node) -> bool:
            f, args, _ = node
            required = keyfilter(lambda x: x != 'return', args) #rettype = args['return']
            get_ret = lambda x: x[1]['return'] # type: Callable[[Node],type]
            acc_rets = map(get_ret, acc)
            acc_rets = list(acc_rets)
            satisfied = all([(t in acc_rets) for t in required.values()])
            return satisfied
        nextnode = next(filter(is_satisfied, to_go))
        next_to_go = list(filter(is_satisfied, to_go))[1:]
        return top_sort([nextnode] + acc, next_to_go)
    sorted = top_sort([input], filled_nodes)
    return sorted

def build_pipeline(funcs: List[Callable[...,Any]], input) -> Callable[...,Any]:
    nodes = order_funcs(funcs, input)
    ordered_funcs = map(get(0), nodes)
    return reduce(compose, ordered_funcs)

#funcs = [consensus, freebayes, tagbam, align_paired, filter_fastq, trim_fastq, gunzip]
#res = build_pipeline(funcs, (id, {'return' : Tuple[Fastq, Fastq]}, []))
#nodes = (order_funcs(funcs, (id, {'return' : Tuple[Fastq, Fastq]}, [])))
#print(res)
#print(nodes)
# file_funcs = dir(__file__)

# most, if not all the difficulty of writing this could've been mitigated by pinning down the types . . . 
# worth biting the bullet, especially for higher-order functions right now
