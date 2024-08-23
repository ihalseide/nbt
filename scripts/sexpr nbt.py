'''
Convert S-expressions to NBT data structure.
'''

import nbtformat
import nbtformat.constants
import nbtformat.printing

TYPE_NAMES = ("compound", "string", "int", "list", "short", "byte", "long", "float", "double")

def type_name_to_id(type_name) -> int:
    if type_name == "compound": return nbtformat.TAG_COMPOUND
    if type_name == "string": return nbtformat.TAG_STRING
    if type_name == "int": return nbtformat.TAG_INT
    if type_name == "list": return nbtformat.TAG_LIST
    if type_name == "short": return nbtformat.TAG_SHORT
    if type_name == "byte": return nbtformat.TAG_BYTE
    if type_name == "float": return nbtformat.TAG_FLOAT
    if type_name == "double": return nbtformat.TAG_DOUBLE
    if type_name == "long": return nbtformat.TAG_LONG
    raise ValueError(type_name)

'''
(compound "root1" ())

(compound "root2" (string "a" "A string")
                  (int "b" 3))
'''
def sexpr_to_nbt(sexpr: str) -> tuple[nbtformat.NamedTag, str]:
    if not sexpr:
        raise ValueError()
    sexpr = skip_space(sexpr)
    _, sexpr = expect_string('(', sexpr)
    sexpr = skip_space(sexpr)
    type_name, sexpr = expect_type_name('', sexpr)
    sexpr = skip_space(sexpr)
    name, sexpr = expect_quoted_string(sexpr)
    sexpr = skip_space(sexpr)
    tag, sexpr = sexpr_to_bt(type_name, sexpr)
    _, sexpr = expect_string(')', sexpr)
    return nbtformat.NamedTag(name, tag), sexpr

def sexpr_to_bt(type_name: str, sexpr: str) -> tuple[nbtformat.TagPayload, str]:
    if type_name in ('byte', 'short', 'int', 'long'):
        val1, sexpr = expect_int(sexpr)
        return make_tag(type_name, val1), sexpr
    elif type_name in ('float', 'double'):
        val4, sexpr = expect_float(sexpr)
        return make_tag(type_name, val4), sexpr
    elif type_name == 'string':
        val2, sexpr = expect_quoted_string(sexpr)
        return make_tag(type_name, val2), sexpr
    elif type_name == 'compound':
        values: list[nbtformat.NamedTag] = []
        _, sexpr = expect_string('(', sexpr)
        sexpr = skip_space(sexpr)
        while sexpr and not sexpr.startswith(')'):
            val3, sexpr = sexpr_to_nbt(sexpr)
            values.append(val3)
            sexpr = skip_space(sexpr)
        _, sexpr = expect_string(')', sexpr)
        values_dict = { nt.name: nt.payload for nt in values }
        return make_tag(type_name, values_dict), sexpr
    elif type_name == 'list':
        values2: list[nbtformat.TagPayload] = []
        list_type_name, sexpr = expect_type_name('', sexpr)
        sexpr = skip_space(sexpr)
        _, sexpr = expect_string('(', sexpr)
        sexpr = skip_space(sexpr)
        while sexpr and not sexpr.startswith(')'):
            val5, sexpr = sexpr_to_bt(list_type_name, sexpr)
            values2.append(val5)
            sexpr = skip_space(sexpr)
        _, sexpr = expect_string(')', sexpr)
        return make_tag(type_name, values2, list_type=type_name_to_id(list_type_name)), sexpr
    else:
        raise NotImplementedError(type_name)
    
def make_tag(type_name: str, data, list_type = None) -> nbtformat.TagPayload:
    if type_name == 'byte': return nbtformat.TagByte(data)
    if type_name == 'short': return nbtformat.TagShort(data)
    if type_name == 'int': return nbtformat.TagInt(data)
    if type_name == 'long': return nbtformat.TagLong(data)
    if type_name == 'float': return nbtformat.TagFloat(data)
    if type_name == 'double': return nbtformat.TagDouble(data)
    if type_name == 'string': return nbtformat.TagString(data)
    if type_name == 'compound': return nbtformat.TagCompound(data)
    if type_name == 'list': return nbtformat.TagList(list_type, data)
    raise NotImplementedError(type_name)

def expect_int(sexpr: str) -> tuple[int, str]:
    last_i = 0
    for i, char in enumerate(sexpr):
        if char not in '+-0123456789':
            last_i = i
            break
    integer = int(sexpr[:last_i])
    remaining = sexpr[last_i:]
    return integer, remaining

def expect_float(sexpr: str) -> tuple[float, str]:
    last_i = 0
    for i, char in enumerate(sexpr):
        if char not in '.+-0123456789':
            last_i = i
            break
    fp = float(sexpr[:last_i])
    remaining = sexpr[last_i:]
    return fp, remaining

def expect_quoted_string(sexpr: str) -> tuple[str, str]:
    _, sexpr = expect_string('"', sexpr)
    last_i = 0
    for i, c in enumerate(sexpr):
        if c == '"':
            last_i = i
            break
    name = sexpr[:last_i]
    _, sexpr = expect_string('"', sexpr[last_i:])
    return name, sexpr

def skip_space(sexpr: str) -> str:
    return sexpr.lstrip()

def expect_string(expected_pre: str, given: str) -> tuple[str, str]:
    if not given.startswith(expected_pre):
        raise ValueError(f"expected input to start with '{expected_pre}'")
    l = len(expected_pre)
    return expected_pre, given[l:]

def expect_type_name(type_name: str, given: str) -> tuple[str, str]:
    if type_name:
        return expect_string(type_name, given)
    else:
        for tn in TYPE_NAMES:
            if given.startswith(tn):
                l = len(tn)
                return tn, given[l:]
        raise ValueError(f"expected string to start with any type name")
        
sexpr = '''
(compound "root" (
    (list "l1" int ())
))
'''
nt, remaining = sexpr_to_nbt(sexpr)
nbtformat.printing.print_tag(nt)