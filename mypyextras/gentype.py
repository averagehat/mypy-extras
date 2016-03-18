from itertools import starmap
def lineToNT(line: str) -> str:
    name, rawFields = line.split('=')
    name = name.strip()
    rawFields = rawFields.strip(' \s}{')
    rawPairs = map(str.strip, rawFields.split(","))
    pairs = map(lambda x:  x.split(":"), rawPairs)
    field_types = ', '.join(starmap("({0}, {1})".format, pairs))
    template = """{name} = NamedTuple({name}, [{field_types}])"""
    return template.format(name=name, field_types=field_types)


example = """SeqID = {id : str}
OneBasedIndex = {index : int}
PileUpRow = {refId : SeqID, position : OneBasedIndex, reference : str, depth: int, readBases : str, baseQuals : str }
IdxStatRow = {refId: SeqID, sequenceLength: int, mappedReadCount: int, unmappedReadCount: int}"""

print('\n'.join(map(lineToNT, example.split('\n'))))
