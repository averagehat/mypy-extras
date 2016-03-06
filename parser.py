
listOf = lambda x: delimitedList(x, ',') #.setAction(lambda s: s.split(',')) # not sure how works if x has a setAction already

        # NamedTuple represents args that are grouped together (by parens)
        # this is to enable grouped optional arguements, for example.
        # Union should represent |
        # Optional represents [ ] 
#make_positional_parser = traverse_type(_type, opt_parse_funcs)

#TODO: Need an outer-most function which won't add an --to the front.

def handle_NT_parser(x, _):  # ingore resolved fields because have to convert them to parsers
       name = get_NamedTuple_name(x)
       if resolved_fields == []:  # treat as Enum
           return Literal(name).setAction(lambda _: x)
       subparsers = starmap(make_option_parser, x._field_types.items())
       parser = reduce(operator.add, subparsers)
       return Just('(') + parser + Just(')')
def make_option_parser(nt: NamedTuple) -> None: 
    name = get_NamedTuple_name(nt)
    long = Literal('--').suppress()
    short = Literal('-').suppress()
    flag = (long + (Literal(name))).leaveWhitespace() | (short + Literal(name[0])).leaveWhitespace()
    opt_parse_funcs = {
            bool : flag.setAction(lambda _: True), # so it must default to False somehow
            int  : flag + Number().setAction(int),
            float  : flag + Float().setAction(float),
            str    : flag + Word(),
            Optional : lambda x: Just('[') + flag + x + Just(']'),
            List : lambda x: flag + listOf(x[0]),
            Enum : handle_NT_parser,
            Union : lambda xs: Just('(') + reduce(operator.ior, xs) + Just(')') # this works because NTs will get resolved to parsers
    }
    option = traverse_type(nt, opt_parse_funcs)
    return option