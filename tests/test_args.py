from argparse import Namespace
from collections import OrderedDict
from mypyextras.ioutils import Platform, Fastq, MiSeq
from mypyextras.args import dict2argparser, func2parsed, get_ordered_annotations
import unittest
from typing import *
FilterOpts = NamedTuple("FilterOpts",
                        [('indexQualMin', int),
                         ('drop_ns', bool),
                         ('platforms', List[Platform])])
PairedEnd = NamedTuple('PairedEnd', [('fwd', Fastq), ('rev', Fastq)])
def filter_fastq(fwdPos: Fastq, revPos: Fastq, opts: FilterOpts) -> Fastq:
    pass
def filter_paired_end(fqs: PairedEnd, opts: FilterOpts) -> Fastq:
    pass
class TestArgs(unittest.TestCase):

    def test_with_positional_arguments(self):
        p = dict2argparser(get_ordered_annotations(filter_fastq), {})
        res = (p.parse_args(['R1', 'R2', '--platforms', 'MiSeq',   '--indexQualMin', '10']))
        expected = Namespace(drop_ns=False, fwdPos=Fastq('R1'),
                             indexQualMin=10, platforms=[MiSeq()],
                             revPos=Fastq('R2'))
        self.assertEqual(expected, res)

    def test_func2parsed(self):
        p, extract_args = func2parsed(filter_fastq, {})
        ns = (p.parse_args(['R1', 'R2', '--platforms', 'MiSeq',   '--indexQualMin', '10']))
        d = extract_args(ns)
        expected = dict(fwdPos=Fastq('R1'), revPos=Fastq('R2'), \
                        opts=FilterOpts(drop_ns=False, \
                        indexQualMin=10, platforms=[MiSeq()]))
        self.assertEqual(expected, d)
   #def test_optional_is_not_required
   #def test_non_optional_is_required
   #def test_rejects_empty_lists
