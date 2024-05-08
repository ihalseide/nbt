TAG_NAMES = [
    'TAG_End',
    'TAG_Byte',
    'TAG_Short',
    'TAG_Int',
    'TAG_Long',
    'TAG_Float',
    'TAG_Double',
    'TAG_Byte_array',
    'TAG_String',
    'TAG_List',
    'TAG_Compound',
    'TAG_Int_array',
    'TAG_Long_array',
]

## Tag kinds
TAG_END = 0
TAG_BYTE = 1
TAG_SHORT = 2
TAG_INT = 3
TAG_LONG = 4
TAG_FLOAT = 5
TAG_DOUBLE = 6
TAG_BYTE_ARRAY = 7
TAG_STRING = 8
TAG_LIST = 9
TAG_COMPOUND = 10
TAG_INT_ARRAY = 11 # a new type added in an extension of NBT
TAG_LONG_ARRAY = 12 # a new type added in an extension of NBT

ALL_TAG_TYPES = (
    TAG_END, TAG_BYTE, 
    TAG_SHORT, TAG_INT, 
    TAG_LONG, TAG_FLOAT, 
    TAG_DOUBLE, TAG_BYTE_ARRAY, 
    TAG_STRING, TAG_LIST, 
    TAG_COMPOUND, TAG_INT_ARRAY, 
    TAG_LONG_ARRAY)

assert(len(ALL_TAG_TYPES) == len(TAG_NAMES) == 13)