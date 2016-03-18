
from gadt import * 
from tparser import just_options_parse, TrimOpts, MiSeq, Roche454


expected = TrimOpts(platforms=[MiSeq,Roche454], removebases=2, paired=True, trim_n=True, q=12)
s = """--platforms MiSeq -p Roche454 --removebases 2 --paired  --trim_n  --q 12"""
result = (just_options_parse(TrimOpts, s))
print(result)
assert result == expected
