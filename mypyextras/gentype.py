from typing import *
STRIPCHARS = ' {}'
def split2(splitOn: str) -> Callable[[str],Tuple[str,str]]:
   def inner(toSplit: str) -> Tuple[str,str]:
      split = toSplit.split(splitOn)
      return split[0].strip(STRIPCHARS), split[1].strip(STRIPCHARS)
   return inner

def lineToNT(line: str) -> str:
   name, rawFields = line.split('=')
   name = name.strip()
   rawFields = rawFields.strip(STRIPCHARS)
   rawPairs = map(str.strip, rawFields.split(','))
   pairs = map(split2(':'), rawPairs)
   field_types = ',\n'.join(map(lambda x: '("%s", %s)' % x, pairs))
   template = """{name} = NamedTuple("{name}",\n[{field_types}])"""
   return template.format(name=name, field_types=field_types)

example = \
"""SeqID = {id : str}
OneBasedIndex = {index : int}
IdxStatRow = {refId : SeqID, sequenceLength: int, mappedReadCount: int, unmappedReadCount: int}
DepthRow = {refId : SeqID, index : OneBasedIndex, depth: int}"""
print('\n'.join(map(lineToNT, example.split('\n'))))
