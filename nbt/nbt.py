'''
NBT tag classes and types.
'''

import struct
from gzip import GzipFile
from typing import BinaryIO
from abc import ABC, abstractmethod

TAG_NAMES = [
    'tag_end',
    'tag_byte',
    'tag_short',
    'tag_int',
    'tag_long',
    'tag_float',
    'tag_double',
    'tag_byte_array',
    'tag_string',
    'tag_list',
    'tag_compound',
    'tag_int_array',
    'tag_long_array',
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

class TagDataABC(ABC):
    '''Abstract base class for the tag payload classes.'''

    kind = TAG_END

    @staticmethod
    def kind_to_class_type(tag_kind: int) -> type['TagDataABC']:
        '''Map a tag kind to a derived class type.'''
        if tag_kind == TAG_END: return TagEnd
        elif tag_kind == TAG_BYTE: return TagByte
        elif tag_kind == TAG_SHORT: return TagShort
        elif tag_kind == TAG_INT: return TagInt
        elif tag_kind == TAG_LONG: return TagLong
        elif tag_kind == TAG_FLOAT: return TagFloat
        elif tag_kind == TAG_DOUBLE: return TagDouble
        elif tag_kind == TAG_BYTE_ARRAY: return TagByteArray
        elif tag_kind == TAG_STRING: return TagString
        elif tag_kind == TAG_LIST: return TagList
        elif tag_kind == TAG_COMPOUND: return TagCompound
        elif tag_kind == TAG_INT_ARRAY: return TagIntArray
        elif tag_kind == TAG_LONG_ARRAY: return TagLongArray
        else:
            raise ValueError("invalid kind value")

    @staticmethod
    def dispatch_read_from_file(tag_kind: int, file: BinaryIO | GzipFile) -> 'TagDataABC':
        return TagDataABC.kind_to_class_type(tag_kind).read_from_file(file)
    
    @classmethod
    @abstractmethod
    def read_from_file(cls, file: BinaryIO|GzipFile) -> 'TagDataABC':
        '''Read the tag payload of this classes type from a binary file.'''
        raise NotImplementedError()
    
    @abstractmethod
    def __bytes__ (self) -> bytes:
        raise NotImplementedError()
    
    @property
    def element_count(self) -> int:
        raise TypeError("this kind of tag has no element count aka length")
    
    @property
    def element_kind(self) -> int:
        raise TypeError("this kind of tag has no element kind")
    
class TagEnd(TagDataABC):

    kind = TAG_END

    @classmethod
    def read_from_file(cls, file: BinaryIO | GzipFile) -> 'TagEnd':
        return TagEnd()

    def __bytes__(self) -> bytes:
        # Empty data
        return bytes()
    
class TagByte(TagDataABC): 

    kind = TAG_BYTE

    @classmethod
    def read_from_file(cls, file: BinaryIO | GzipFile) -> 'TagByte':
        return TagByte(struct.unpack('>c', file.read(1))[0])
    
    def __init__(self, val: int):
        self.val = int(val)

    def __bytes__(self) -> bytes:
        return struct.pack('>c', self.kind, self.val)
    
class TagShort(TagDataABC): 

    kind = TAG_SHORT

    @classmethod
    def read_from_file(cls, file: BinaryIO | GzipFile) -> 'TagShort':
        return TagShort(struct.unpack('>h', file.read(2))[0])
    
    def __init__(self, val: int):
        self.val = int(val)

    def __bytes__(self) -> bytes:
        return struct.pack('>h', self.val)
    
class TagInt(TagDataABC): 

    kind = TAG_INT

    @classmethod
    def read_from_file(cls, file: BinaryIO | GzipFile) -> 'TagInt':
        return TagInt(struct.unpack('>i', file.read(4))[0])
    
    def __init__(self, val: int):
        self.val = int(val)

    def __bytes__(self) -> bytes:
        return struct.pack('>i', self.val)
    
class TagLong(TagDataABC): 

    kind = TAG_LONG

    @classmethod
    def read_from_file(cls, file: BinaryIO | GzipFile) -> 'TagLong':
        return TagLong(struct.unpack('>q', file.read(8))[0])
    
    def __init__(self, val: int):
        self.val = int(val)

    def __bytes__(self) -> bytes:
        return struct.pack('>q', self.val)
    
class TagFloat(TagDataABC):

    kind = TAG_FLOAT

    @classmethod
    def read_from_file(cls, file: BinaryIO | GzipFile) -> 'TagFloat':
        return TagFloat(struct.unpack('>f', file.read(4))[0])
    
    def __init__(self, val: float):
        self.val = float(val)

    def __bytes__(self) -> bytes:
        return struct.pack('>f', self.val)
    
class TagDouble(TagDataABC): 

    kind = TAG_DOUBLE

    @classmethod
    def read_from_file(cls, file: BinaryIO | GzipFile) -> 'TagDouble':
        return TagDouble(struct.unpack('>d', file.read(8))[0])
    
    def __init__(self, val: float):
        self.val = float(val)

    def __bytes__(self) -> bytes:
        return struct.pack('>d', self.val)
    
class TagByteArray(TagDataABC): 

    kind = TAG_BYTE_ARRAY

    @classmethod
    def read_from_file(cls, file: BinaryIO | GzipFile) -> 'TagByteArray':
        byte_count = TagInt.read_from_file(file).val
        return TagByteArray(file.read(byte_count))
    
    def __init__(self, val: bytes):
        self.val = bytearray(val)

    def __bytes__(self) -> bytes:
        result = bytearray()
        result.extend(bytes(TagInt(self.element_count)))
        result.extend(self.val)
        return bytes(result)
    
    @property
    def element_count(self) -> int:
        return len(self.val)
    
class TagString(TagDataABC): 

    kind = TAG_STRING

    @classmethod
    def read_from_file(cls, file: BinaryIO | GzipFile) -> 'TagString':
        count = TagShort.read_from_file(file).val
        if count == 0:
            return TagString('')
        else:
            return TagString(file.read(count).decode('utf-8'))
    
    def __init__(self, val: str):
        self.val = str(val)

    def __bytes__(self) -> bytes:
        result = bytearray()
        result.extend(bytes(TagShort(self.element_count)))
        result.extend(self.val.encode('utf-8'))
        return bytes(result)
    
    @property
    def element_count(self) -> int:
        return len(self.val)
    
class TagList(TagDataABC): 

    kind = TAG_LIST

    @classmethod
    def read_from_file(cls, file: BinaryIO | GzipFile) -> 'TagList':
        item_kind = TagByte.read_from_file(file).val
        item_count = TagInt.read_from_file(file).val
        the_class = TagDataABC.kind_to_class_type(item_kind)
        return TagList([the_class.read_from_file(file) for _ in range(item_count)], item_kind)
    
    def __init__(self, val: list[TagDataABC], item_kind: int|TagDataABC):
        self.val = list(val)
        if isinstance(item_kind, int):
            self._item_kind = item_kind
        elif isinstance(item_kind, (TagByte, TagShort, TagInt, TagLong)):
            self._item_kind = item_kind.val
        else:
            raise TypeError("`item_kind` must be an int or a int-like kind of TagDataABC")
        
    def __bytes__(self) -> bytes:
        result = bytearray()
        result.extend(bytes(TagByte(self._item_kind)))
        result.extend(bytes(TagInt(self.element_count)))
        for tag in self.val:
            result.extend(bytes(tag))
        return bytes(result)
    
    @property
    def element_count(self) -> int:
        return len(self.val)
    
    @property
    def element_kind(self) -> int:
        return self._item_kind
    
class TagCompound(TagDataABC):

    kind = TAG_COMPOUND

    @classmethod
    def read_from_file(cls, file: BinaryIO | GzipFile) -> 'TagCompound':
        tags: list[NamedTag] = []
        while not (tag := NamedTag.read_from_file(file)).kind == TAG_END:
            tags.append(tag)
        tags.append(tag)
        return TagCompound(tags)
    
    def __init__(self, val: list['NamedTag']):
        self.val = list(val)

    def __bytes__(self) -> bytes:
        result = bytearray()
        for named_tag in self.val:
            result.extend(bytes(named_tag))
        return bytes(result)
    
class TagIntArray(TagDataABC):

    kind = TAG_INT_ARRAY

    @classmethod
    def read_from_file(cls, file: BinaryIO | GzipFile) -> 'TagIntArray':
        count = TagInt.read_from_file(file).val
        return TagIntArray([TagInt.read_from_file(file).val for _ in range(count)])
    
    def __init__(self, val: list[int]):
        self.val = list(int(x) for x in val)

    def __bytes__(self) -> bytes:
        result = bytearray()
        result.extend(bytes(TagInt(self.element_count)))
        for x in self.val:
            result.extend(bytes(TagInt(x)))
        return bytes(result)
    
    @property
    def element_count(self) -> int:
        return len(self.val)
    
class TagLongArray(TagDataABC):

    kind = TAG_LONG_ARRAY

    @classmethod
    def read_from_file(cls, file: BinaryIO | GzipFile) -> 'TagLongArray':
        count = TagInt.read_from_file(file).val
        return TagLongArray([TagLong.read_from_file(file).val for _ in range(count)])
    
    def __init__(self, val: list[int]):
        self.val = list(int(x) for x in val)

    def __bytes__(self) -> bytes:
        result = bytearray()
        result.extend(bytes(TagInt(self.element_count)))
        for x in self.val:
            result.extend(bytes(TagLong(x)))
        return bytes(result)
    
    @property
    def element_count(self) -> int:
        return len(self.val)
    
class NamedTag:

    @staticmethod
    def read_from_file(file: BinaryIO | GzipFile) -> 'NamedTag':
        ## Read the tag type byte
        try:
            kind = file.read(1)[0]
        except (IndexError, EOFError):
            return NamedTag("", TagEnd())
        ## Read the tag name (string tag)
        name_tag = TagString.read_from_file(file)
        ## Read the tag payload pay
        payload = TagDataABC.dispatch_read_from_file(kind, file)
        return NamedTag(name_tag, payload)
    
    def write_to_file(self, file: BinaryIO | GzipFile):
        file.write(bytes(self))

    def __init__(self, name: str | TagString, payload: TagDataABC):
        if isinstance(name, str):
            self.name = str(name)
        else:
            self.name = str(name.val)
        self.payload = payload
        
    @property
    def kind(self) -> int:
        '''Get this named tag's tag kind.'''
        return self.payload.kind
    
    @property
    def payload_bytes(self) -> bytes:
        '''Get the bytes for this tag's payload.'''
        return bytes(self.payload)
    
    @property
    def name_tag(self) -> TagString:
        '''Get a string name tag that represents this tag's name.'''
        return TagString(self.name)
    
    def __bytes__(self) -> bytes:
        arr = bytearray()
        arr.append(self.kind)
        if self.kind != TAG_END: # TAG_END cannot be named and has no data payload
            arr.extend(bytes(self.name_tag))
            arr.extend(self.payload_bytes)
        return bytes(arr)
    
def tag_kind_to_str(tag_type: int) -> str:
    '''Get the string name for a tag type'''
    try:
        return TAG_NAMES[tag_type]
    except IndexError:
        raise ValueError("value does not represent a type of tag")

def tag_is_list_kind(tag_type: int) -> bool:
    return int(tag_type) in (TAG_BYTE_ARRAY, TAG_STRING, TAG_LIST,
                        TAG_COMPOUND, TAG_INT_ARRAY, TAG_LONG_ARRAY)

def tag_is_atom_kind(tag_type: int) -> bool:
    return int(tag_type) in (TAG_BYTE, TAG_SHORT, TAG_INT,
                        TAG_LONG, TAG_FLOAT, TAG_DOUBLE)