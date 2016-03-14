from argparse import NameSpace
from ioutils import Platform, Fastq
FilterOpts = NamedTuple("FilterOpts",
                        [('indexQualMin', int),
                         ('drop_ns', bool),
                         ('platforms', List[Platform])])
PairedEnd = NamedTuple('PairedEnd', [('fwd', Fastq), ('rev', Fastq)])
#p = (dict2argparser(dict(opts=FilterOpts)))
class TestArgs(unittest.TestCase):

    def filter_fastq(fwdPos: Fastq, revPos: Fastq, opts: FilterOpts) -> Fastq:
        pass # run filter
    def filter_paired_end(fqs: PairedEnd, opts: FilterOpts) -> Fastq:
        pass
    def test_with_positional_arguments(self):
        p = (dict2argparser(filter_fastq.__annotations__))
        res = (p.parse_args(['R1', 'R2', '--platforms', 'MiSeq',   '--indexQualMin', '10'])) 
        expected = Namespace(drop_ns=False, fwdPos=Fastq('R1'), indexQualMin=10, platforms=[MiSeq()], revPos=Fastq('R2'))
        self.assertEqual(expected, res)


        def test_with_positional_arguments(self):
            p = (dict2argparser(filter_fastq.__annotations__))
            res = (p.parse_args(['R1', 'R2', '--platforms', 'MiSeq',   '--indexQualMin', '10'])) 
            Namespace(drop_ns=False, fwd=Fastq('R2'), indexQualMin=10, platforms=[MiSeq()], rev=Fastq('R1'))
            self.assertEqual(expected, res)
    
    #def test_optional_is_not_required
    #def test_non_optional_is_required
    #def test_rejects_empty_lists
