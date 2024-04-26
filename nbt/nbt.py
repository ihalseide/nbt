'''
NBT tag classes and types.
'''

import struct
from gzip import GzipFile
from typing import BinaryIO, override, Any, Iterable
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

ALL_TAG_TYPES = (
    TAG_END, TAG_BYTE, 
    TAG_SHORT, TAG_INT, 
    TAG_LONG, TAG_FLOAT, 
    TAG_DOUBLE, TAG_BYTE_ARRAY, 
    TAG_STRING, TAG_LIST, 
    TAG_COMPOUND, TAG_INT_ARRAY, 
    TAG_LONG_ARRAY)

class TagDataABC(ABC):
    '''Abstract base class for the tag payload classes.'''

    kind = TAG_END

    @staticmethod
    def int_from_bytes(b: bytes, length: int) -> int:
        '''
        Convenience function for converting integer to bytes consistently for all of the int-like tag classes
        NOTE: should be synchronized with the `int_to_bytes` method
        '''
        if len(b) != length:
            raise ValueError(f"not enough bytes for data type of length {length}")
        return int.from_bytes(b, byteorder='big', signed=True)

    @staticmethod
    def int_to_bytes(x: int, length: int) -> bytes:
        '''NOTE: should be synchronized with the `int_from_bytes` method'''
        return x.to_bytes(length, byteorder='big', signed=True)

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
    def read_from_file(cls, file: BinaryIO | GzipFile) -> 'TagDataABC':
        '''Read the tag payload of this classes type from a binary file.'''
        raise NotImplementedError()
    
    def write_to_file_stepped(self, file: BinaryIO | GzipFile):
        file.write(bytes(self))
    
    @abstractmethod
    def __bytes__ (self) -> bytes:
        raise NotImplementedError()
    
    @property
    def value(self) -> Any:
        raise NotImplementedError()
    
    @property
    def element_count(self) -> int:
        type_name = tag_kind_to_str(self.kind)
        raise TypeError(f"this kind of tag, {type_name}, has no element count aka length")
    
    @property
    def element_kind(self) -> int:
        type_name = tag_kind_to_str(self.kind)
        raise TypeError(f"this kind of tag, {type_name} has no element kind")
    
class TagEnd(TagDataABC):

    kind = TAG_END

    @classmethod
    def read_from_file(cls, file: BinaryIO | GzipFile) -> 'TagEnd':
        return TagEnd()
    
    def write_to_file_stepped(self, file: BinaryIO | GzipFile):
        pass

    def __bytes__(self) -> bytes:
        # Empty data
        return bytes()
    
    @override
    def value(self) -> None:
        return
    
class TagByte(TagDataABC): 

    kind = TAG_BYTE
    size = 1

    @classmethod
    def read_from_file(cls, file: BinaryIO | GzipFile) -> 'TagByte':
        return TagByte(cls.int_from_bytes(file.read(cls.size), cls.size))
    
    def __init__(self, val: int):
        self.val = int(val)

    def __bytes__(self) -> bytes:
        return self.int_to_bytes(self.val, self.size)
    
    @property
    def value(self) -> int:
        return self.val
    
class TagShort(TagDataABC): 

    kind = TAG_SHORT
    size = 2

    @classmethod
    def read_from_file(cls, file: BinaryIO | GzipFile) -> 'TagShort':
        return TagShort(cls.int_from_bytes(file.read(cls.size), cls.size))
    
    def __init__(self, val: int):
        self.val = int(val)

    def __bytes__(self) -> bytes:
        return self.int_to_bytes(self.val, self.size)
    
    @property
    def value(self) -> int:
        return self.val
    
class TagInt(TagDataABC): 

    kind = TAG_INT
    size = 4

    @classmethod
    def read_from_file(cls, file: BinaryIO | GzipFile) -> 'TagInt':
        return TagInt(cls.int_from_bytes(file.read(cls.size), cls.size))
    
    def __init__(self, val: int):
        self.val = int(val)

    def __bytes__(self) -> bytes:
        return self.int_to_bytes(self.val, self.size)
    
    @property
    def value(self) -> int:
        return self.val
    
class TagLong(TagDataABC): 

    kind = TAG_LONG
    size = 8

    @classmethod
    def read_from_file(cls, file: BinaryIO | GzipFile) -> 'TagLong':
        return TagLong(cls.int_from_bytes(file.read(cls.size), cls.size))
    
    def __init__(self, val: int):
        self.val = int(val)

    def __bytes__(self) -> bytes:
        return self.int_to_bytes(self.val, self.size)
    
    @property
    def value(self) -> int:
        return self.val
    
class TagFloat(TagDataABC):

    kind = TAG_FLOAT
    size = 4

    @classmethod
    def read_from_file(cls, file: BinaryIO | GzipFile) -> 'TagFloat':
        x: float = struct.unpack('>f', file.read(cls.size))[0]
        return TagFloat(x)
    
    def __init__(self, val: float):
        self.val = float(val)

    def __bytes__(self) -> bytes:
        result = struct.pack('>f', self.val)
        assert(len(result) == self.size)
        return result
    
    @property
    def value(self) -> float:
        return self.val
    
class TagDouble(TagDataABC): 

    kind = TAG_DOUBLE
    size = 8

    @classmethod
    def read_from_file(cls, file: BinaryIO | GzipFile) -> 'TagDouble':
        x: float = struct.unpack('>d', file.read(cls.size))[0]
        return TagDouble(x)
    
    def __init__(self, val: float):
        self.val = float(val)

    def __bytes__(self) -> bytes:
        result = struct.pack('>d', self.val)
        assert(len(result) == self.size)
        return result
    
    @property
    def value(self) -> float:
        return self.val
    
class TagByteArray(TagDataABC): 

    kind = TAG_BYTE_ARRAY

    @classmethod
    def read_from_file(cls, file: BinaryIO | GzipFile) -> 'TagByteArray':
        byte_count = TagInt.read_from_file(file).val
        return TagByteArray(file.read(byte_count))
    
    def write_to_file_stepped(self, file: BinaryIO | GzipFile):
        '''Override the parent method so that this can be broken down into 2 write calls.'''
        TagInt(self.element_count).write_to_file_stepped(file)
        file.write(self.val)
    
    def __init__(self, val: bytes | Iterable[int]):
        self.val = bytearray(val)

    def __bytes__(self) -> bytes:
        result = bytearray()
        result.extend(bytes(TagInt(self.element_count)))
        result.extend(self.val)
        return bytes(result)
    
    @property
    def element_count(self) -> int:
        return len(self.val)
    
    @property
    def value(self) -> bytearray:
        return self.val
    
class TagString(TagDataABC): 

    kind = TAG_STRING

    @classmethod
    def read_from_file(cls, file: BinaryIO | GzipFile) -> 'TagString':
        count = TagShort.read_from_file(file).value
        if count == 0:
            return TagString('')
        else:
            return TagString(file.read(count).decode('utf-8'))
        
    @override
    def write_to_file_stepped(self, file: BinaryIO | GzipFile):
        '''Override the parent method so that this can be broken down into 2 write calls.'''
        TagShort(self.element_count).write_to_file_stepped(file)
        file.write(self.val.encode())
    
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
    
    @property
    def value(self) -> str:
        return self.val
    
class TagList(TagDataABC): 

    kind = TAG_LIST

    @classmethod
    def read_from_file(cls, file: BinaryIO | GzipFile) -> 'TagList':
        item_kind = TagByte.read_from_file(file).val
        item_count = TagInt.read_from_file(file).val
        the_class = TagDataABC.kind_to_class_type(item_kind)
        return TagList(item_kind, [the_class.read_from_file(file) for _ in range(item_count)])
    
    @override
    def write_to_file_stepped(self, file: BinaryIO | GzipFile):
        '''Override the parent method so that this can be broken down into 2 write calls.'''
        TagByte(self.element_kind).write_to_file_stepped(file)
        TagShort(self.element_count).write_to_file_stepped(file)
        for tag in self.val:
            tag.write_to_file_stepped(file)
    
    def __init__(self, item_kind: int|TagDataABC, val: list[TagDataABC]):
        self.val = list(val)
        if isinstance(item_kind, int):
            self._item_kind = item_kind
        elif isinstance(item_kind, (TagByte, TagShort, TagInt, TagLong)):
            # Extract value from integer tag
            self._item_kind = item_kind.val
        else:
            raise TypeError("`item_kind` must be an int or a int-like kind of TagDataABC")
        for i, tag_i in enumerate(self.val):
            if tag_i.kind != self._item_kind:
                raise TypeError(f"NBT item at index {i} is not the same type as the TagList's expected item type")
        
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
    
    @property
    def value(self) -> list[TagDataABC]:
        return self.val
    
class TagCompound(TagDataABC):

    kind = TAG_COMPOUND

    @classmethod
    def read_from_file(cls, file: BinaryIO | GzipFile) -> 'TagCompound':
        '''Read the compound tag's payload: a sequence of tags until a TagEnd.'''
        tags: list[NamedTag] = []
        tag = NamedTag.read_from_file(file)
        tags.append(tag)
        while tag.kind != TAG_END:
            tag = NamedTag.read_from_file(file)
            tags.append(tag)
        return TagCompound(tags)
    
    def __init__(self, val: list['NamedTag']):
        self.val = list(val)
        self.ensure_end()

    def __bytes__(self) -> bytes:
        self.ensure_end()
        result = bytearray()
        for named_tag in self.val:
            result.extend(bytes(named_tag))
            # Don't write any tags after the first TagEnd is encountered
            if named_tag.kind == TAG_END:
                break
        return bytes(result)
    
    def append_before_end(self, tag: 'NamedTag'):
        '''Append a named tag to this compound list, making sure it comes before the TAG_END tag.'''
        self.ensure_end()
        self.val.insert(-1, tag)
    
    def ensure_end(self) -> None:
        '''Make sure this TagCompound's values array ends with a TAG_END tag.'''
        if (not len(self.val)) or (self.val[-1].kind != TAG_END):
            self.val.append(NamedTag('', TagEnd()))
    
    @override
    @property
    def element_count(self) -> int:
        # Subtract 1 because the end tag at the end doesn't count
        return len(self.val) - 1
    
    @property
    def value(self) -> list['NamedTag']:
        return self.val
    
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
    
    @property
    def value(self) -> list[int]:
        return self.val
    
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
    
    @property
    def value(self) -> list[int]:
        return self.val
    
class NamedTag:

    @staticmethod
    def read_from_file(file: BinaryIO | GzipFile) -> 'NamedTag':
        '''
        Read a named tag from a file. If EOF is reached, return a `TagEnd` tag.
        NOTE: because of this behavior, a file may omit the trail of ending TagEnd tag(s) to close the top-level TagCompound(s).
        '''
        ## Read the tag type byte
        try:
            kind = TagByte.read_from_file(file)
        except (IndexError, EOFError):
            return NamedTag("", TagEnd())
        if kind.value not in ALL_TAG_TYPES:
            raise ValueError(f"invalid tag type: {kind.value}")
        if kind.value == TAG_END:
            ## No name or payload for TagEnd
            return NamedTag("", TagEnd())
        else:
            ## Read the tag name (string tag)
            name_tag = TagString.read_from_file(file)
            ## Read the tag payload pay
            payload = TagDataABC.dispatch_read_from_file(kind.value, file)
            return NamedTag(name_tag, payload)

    def __init__(self, name: str | TagString, payload: TagDataABC):
        '''Create a NamedTag with a name and a tag payload.'''
        self.name: str = ''
        self.payload: TagDataABC = payload
        if isinstance(name, TagString):
            self.name = str(name.val)
        else:
            self.name = str(name)

    def write_to_file(self, file: BinaryIO | GzipFile) -> int:
        '''
        Write all of this named tag's data to a file by constructing
        the byte buffer first and then writing it all at once.
        '''
        return file.write(bytes(self))
    
    def write_to_file_stepped(self, file: BinaryIO | GzipFile):
        file.write(bytes(self.name_tag))
        self.payload.write_to_file_stepped(file)
        
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