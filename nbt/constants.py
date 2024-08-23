# These are all of the constants for the NBT tag kinds/types
 
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

# Note: TAG_END is often used as a default or error value in `fully.py`
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
# The following types are new types added in a (Mojang) extension of NBT
TAG_INT_ARRAY = 11 
TAG_LONG_ARRAY = 12

ALL_TAG_TYPES = (
    TAG_END,
    TAG_BYTE, 
    TAG_SHORT,
    TAG_INT, 
    TAG_LONG,
    TAG_FLOAT, 
    TAG_DOUBLE,
    TAG_BYTE_ARRAY, 
    TAG_STRING,
    TAG_LIST, 
    TAG_COMPOUND,
    TAG_INT_ARRAY, 
    TAG_LONG_ARRAY
)

# Static check to make sure no tag types were missed
assert(len(ALL_TAG_TYPES) == len(TAG_NAMES) == 13)

# Map a "numeric" tag type to the number of bytes used for its representation
TAG_NUMERIC_BYTE_COUNT = { 
    TAG_BYTE: 1, 
    TAG_SHORT: 2, 
    TAG_INT: 4, 
    TAG_LONG: 8, 
    TAG_FLOAT: 4, 
    TAG_DOUBLE: 8,
}

# Map "array" tag types to the element's tag type
TAG_ARRAY_SUBTYPES = { 
    TAG_BYTE_ARRAY: TAG_BYTE, 
    TAG_INT_ARRAY: TAG_INT, 
    TAG_LONG_ARRAY: TAG_LONG,
}