'''
Classes for NBT tags that fully contain data from a file.
'''

import struct
from typing import BinaryIO, override, Any, Iterable, Mapping
from gzip import GzipFile # just import for the type
from abc import ABC, abstractmethod

from .constants import *

def tag_kind_to_str(tag_type: int) -> str:
    '''Get the string name for a tag type'''
    try:
        return TAG_NAMES[tag_type]
    except IndexError:
        raise ValueError("value does not represent a type of tag")

class TagDataABC(ABC):
    '''Abstract base class for all the NBT payload classes.'''

    # Default tag type value
    kind = TAG_END

    def name(self) -> str:
        return TAG_NAMES[self.kind]

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
    def kind_tag(self) -> 'TagByte':
        return TagByte(self.kind)
    
    @property
    def element_count(self) -> int:
        type_name = tag_kind_to_str(self.kind)
        raise TypeError(f"this kind of tag, {type_name}, has no element count aka length")
    
    @property
    def element_kind_tag(self) -> 'TagByte':
        type_name = tag_kind_to_str(self.kind)
        raise TypeError(f"this kind of tag, {type_name} has no element kind")
    
    @property
    def kind_name(self) -> str:
        return TAG_NAMES[self.kind]
    
    def __str__(self) -> str:
        type_name = type(self).__name__
        return f"{type_name}()"
    
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
        self._val = int(val)

    def __bytes__(self) -> bytes:
        return self.int_to_bytes(self._val, self.size)
    
    @property
    def value(self) -> int:
        return self._val
    
class TagShort(TagDataABC): 

    kind = TAG_SHORT
    size = 2

    @classmethod
    def read_from_file(cls, file: BinaryIO | GzipFile) -> 'TagShort':
        return TagShort(cls.int_from_bytes(file.read(cls.size), cls.size))
    
    def __init__(self, val: int):
        self._val = int(val)

    def __bytes__(self) -> bytes:
        return self.int_to_bytes(self._val, self.size)
    
    @property
    def value(self) -> int:
        return self._val
    
class TagInt(TagDataABC): 

    kind = TAG_INT
    size = 4

    @classmethod
    def read_from_file(cls, file: BinaryIO | GzipFile) -> 'TagInt':
        return TagInt(cls.int_from_bytes(file.read(cls.size), cls.size))
    
    def __init__(self, val: int):
        self._val = int(val)

    def __bytes__(self) -> bytes:
        return self.int_to_bytes(self._val, self.size)
    
    @property
    def value(self) -> int:
        return self._val
    
class TagLong(TagDataABC): 

    kind = TAG_LONG
    size = 8

    @classmethod
    def read_from_file(cls, file: BinaryIO | GzipFile) -> 'TagLong':
        return TagLong(cls.int_from_bytes(file.read(cls.size), cls.size))
    
    def __init__(self, val: int):
        self._val = int(val)

    def __bytes__(self) -> bytes:
        return self.int_to_bytes(self._val, self.size)
    
    @property
    def value(self) -> int:
        return self._val
    
class TagFloat(TagDataABC):

    kind = TAG_FLOAT
    size = 4

    @classmethod
    def read_from_file(cls, file: BinaryIO | GzipFile) -> 'TagFloat':
        x: float = struct.unpack('>f', file.read(cls.size))[0]
        return TagFloat(x)
    
    def __init__(self, val: float):
        self._val = float(val)

    def __bytes__(self) -> bytes:
        result = struct.pack('>f', self._val)
        assert(len(result) == self.size)
        return result
    
    @property
    def value(self) -> float:
        return self._val
    
class TagDouble(TagDataABC): 

    kind = TAG_DOUBLE
    size = 8

    @classmethod
    def read_from_file(cls, file: BinaryIO | GzipFile) -> 'TagDouble':
        x: float = struct.unpack('>d', file.read(cls.size))[0]
        return TagDouble(x)
    
    def __init__(self, val: float):
        self._val = float(val)

    def __bytes__(self) -> bytes:
        result = struct.pack('>d', self._val)
        assert(len(result) == self.size)
        return result
    
    @property
    def value(self) -> float:
        return self._val
    
class TagByteArray(TagDataABC): 

    kind = TAG_BYTE_ARRAY

    @classmethod
    def read_from_file(cls, file: BinaryIO | GzipFile) -> 'TagByteArray':
        byte_count = TagInt.read_from_file(file)._val
        return TagByteArray(file.read(byte_count))
    
    def write_to_file_stepped(self, file: BinaryIO | GzipFile):
        '''Override the parent method so that this can be broken down into 2 write calls.'''
        TagInt(self.element_count).write_to_file_stepped(file)
        file.write(self._val)
    
    def __init__(self, val: bytes | Iterable[int]):
        self._val = bytearray(val)

    def __bytes__(self) -> bytes:
        result = bytearray()
        result.extend(bytes(TagInt(self.element_count)))
        result.extend(self._val)
        return bytes(result)
    
    @property
    def element_count(self) -> int:
        return len(self._val)
    
    @property
    def value(self) -> bytearray:
        return self._val
    
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
        file.write(self._val.encode())
    
    def __init__(self, val: str):
        self._val = str(val)

    def __bytes__(self) -> bytes:
        result = bytearray()
        result.extend(bytes(TagShort(self.element_count)))
        result.extend(self._val.encode('utf-8'))
        return bytes(result)
    
    @property
    def element_count(self) -> int:
        return len(self._val)
    
    @property
    def value(self) -> str:
        return self._val
    
class TagList(TagDataABC): 

    kind = TAG_LIST

    @classmethod
    def read_from_file(cls, file: BinaryIO | GzipFile) -> 'TagList':
        item_kind = TagByte.read_from_file(file)._val
        item_count = TagInt.read_from_file(file)._val
        the_class = TagDataABC.kind_to_class_type(item_kind)
        return TagList(item_kind, [the_class.read_from_file(file) for _ in range(item_count)])
    
    @override
    def write_to_file_stepped(self, file: BinaryIO | GzipFile):
        '''Override the parent method so that this can be broken down into 2 write calls.'''
        self.element_kind_tag.write_to_file_stepped(file)
        TagShort(self.element_count).write_to_file_stepped(file)
        for tag in self._val:
            tag.write_to_file_stepped(file)
    
    def __init__(self, item_kind: int|TagByte, val: Iterable[TagDataABC]):
        self._val = list()

        # Set item_kind (element type)
        if isinstance(item_kind, int):
            self._item_kind = item_kind
        elif isinstance(item_kind, TagByte):
            # Extract value from integer tag
            self._item_kind = item_kind.value
        else:
            raise TypeError("`item_kind` must be an int or a int-like kind of TagDataABC")
        
        # Set and check the elements
        for i, tag_i in enumerate(val):
            if not isinstance(tag_i, TagDataABC):
                raise TypeError(f"item \"{tag_i}\", is not an instance of `TagDataABC`")
            if tag_i.kind != self._item_kind:
                expected_type = tag_kind_to_str(self._item_kind)
                raise TypeError(f"NBT item {tag_i}, does not have the same NBT type as the TagList's expected item type: {expected_type}")
            self._val.append(tag_i)
        
    def __bytes__(self) -> bytes:
        result = bytearray()
        result.extend(bytes(TagByte(self._item_kind)))
        result.extend(bytes(TagInt(self.element_count)))
        for tag in self._val:
            result.extend(bytes(tag))
        return bytes(result)
    
    @property
    def element_count(self) -> int:
        return len(self._val)
    
    @property
    def element_kind_tag(self) -> TagByte:
        return TagByte(self._item_kind)
    
    @property
    def value(self) -> list[TagDataABC]:
        return self._val
    
class TagCompound(TagDataABC):
    '''
    A `TagCompound` is an non-homogeneous container for NBT tags.
    NOTE: TagCompound instances are not meant to be mutated.
    NOTE: this class will automatically ensure that the value ends with a `TagEnd` tag.
    NOTE: if this tag's value has any tags after a TagEnd, those tags will not be included when written to a file or converted to bytes.
    '''

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
    
    def __init__(self, val: Iterable['NamedTag'] | Mapping[str, TagDataABC]):
        '''
        Create a new `TagCompound` with either a sequence of `NamedTag`s or a dict that maps
        `str`s to instances that inherit from `TagDataABC`.
        '''
        temp_val: list[NamedTag] = list()
        if isinstance(val, dict):
            ## Initialize from a dictionary that maps names to tag data
            for name, tag in val.items():
                if not isinstance(name, str):
                    raise TypeError("name is not a `str`")
                if not isinstance(tag, TagDataABC):
                    raise TypeError(f"item \"{tag}\" is not a `TagDataABC` instance")
                temp_val.append(NamedTag(name, tag))
        elif isinstance(val, list):
            ## Initialize from a list of named tags
            for named_tag in val:
                if not isinstance(named_tag, NamedTag):
                    raise TypeError("named_tag is not a `NamedTag` instance")
                temp_val.append(named_tag)
        else:
            raise TypeError("must initialize a TagCompound from a list of `NamedTag`s or from a `dict` that maps `str`s to `TagDataABC`s")
        self._ensure_end(temp_val)
        self._val: tuple[NamedTag, ...] = tuple(temp_val)

    def __bytes__(self) -> bytes:
        assert(len(self._val) > 0 and isinstance(self._val[-1], TagEnd))
        result = bytearray()
        for named_tag in self._val:
            result.extend(bytes(named_tag))
            # Don't write any tags after the first TagEnd is encountered
            if named_tag.kind == TAG_END:
                break
        return bytes(result)
    
    def _ensure_end(self, tag_list: list['NamedTag']):
        '''Make sure this TagCompound's values array ends with a TAG_END tag.'''
        if (not len(tag_list)) or (not isinstance(tag_list[-1], TagEnd)):
            tag_list.append(NamedTag('', TagEnd()))
        assert(len(tag_list) >= 1)
    
    @override
    @property
    def element_count(self) -> int:
        # Subtract 1 because the end tag at the end doesn't count
        return len(self._val) - 1
    
    @property
    def value(self) -> list['NamedTag']:
        return list(self._val)
    
    def get_many(self, name: str) -> set[TagDataABC]:
        '''
        Get the set of tags that have the given name.
        This method is supported just because a non-standard NBT file may have multiple tags with the same name.
        '''
        result: set[TagDataABC] = set()
        for named_tag in self._val:
            if named_tag.name == name:
                result.add(named_tag.payload)
        return result
    
    def __getitem__(self, key: str) -> TagDataABC:
        '''Get the first tag found that has the given name. See also: the `get_tags_named` method.'''
        if not isinstance(key, str):
            raise TypeError("index `key` must be a `str`")
        for named_tag in self._val:
            if named_tag.name == key:
                return named_tag.payload
        raise KeyError(f"this TagCompound has no tag item named \"{key}\"")
    
    def with_update(self, named_tag: 'NamedTag') -> 'TagCompound':
        '''Return a new TagCompound that has the given tag added to it'''
        return self.with_updates([named_tag])
    
    def with_updates(self, named_tags: Iterable['NamedTag']) -> 'TagCompound':
        '''Return a new TagCompound that has the given tags added to it'''
        new_val: list[NamedTag] = []
        for named in self._val:
            new_val.append(named)
        for named in named_tags:
            new_val.append(named)
        return TagCompound(new_val)
    
    def to_dict(self) -> dict[str, TagDataABC]:
        '''Get a dict that maps tag names to tag data payloads within this TagCompound's values.'''
        return { named_tag.name: named_tag.payload for named_tag in self._val }
    
class TagIntArray(TagDataABC):

    kind = TAG_INT_ARRAY

    @classmethod
    def read_from_file(cls, file: BinaryIO | GzipFile) -> 'TagIntArray':
        count = TagInt.read_from_file(file)._val
        return TagIntArray([TagInt.read_from_file(file)._val for _ in range(count)])
    
    def __init__(self, val: Iterable[int]):
        self._val = list(int(x) for x in val)

    def __bytes__(self) -> bytes:
        result = bytearray()
        result.extend(bytes(TagInt(self.element_count)))
        for x in self._val:
            result.extend(bytes(TagInt(x)))
        return bytes(result)
    
    @property
    def element_count(self) -> int:
        return len(self._val)
    
    @property
    def value(self) -> list[int]:
        return self._val
    
class TagLongArray(TagDataABC):

    kind = TAG_LONG_ARRAY

    @classmethod
    def read_from_file(cls, file: BinaryIO | GzipFile) -> 'TagLongArray':
        count = TagInt.read_from_file(file)._val
        return TagLongArray([TagLong.read_from_file(file)._val for _ in range(count)])
    
    def __init__(self, val: Iterable[int]):
        self._val = list(int(x) for x in val)

    def __bytes__(self) -> bytes:
        result = bytearray()
        result.extend(bytes(TagInt(self.element_count)))
        for x in self._val:
            result.extend(bytes(TagLong(x)))
        return bytes(result)
    
    @property
    def element_count(self) -> int:
        return len(self._val)
    
    @property
    def value(self) -> list[int]:
        return self._val
    
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
        '''Create a `NamedTag` with a `name` string and a NBT tag `payload`.'''
        if not isinstance(payload, TagDataABC):
            raise TypeError("a `NamedTag` must be initialized with a payload that is an instance of `TagDataABC`")
        self.name: str = ''
        self.payload: TagDataABC = payload
        if isinstance(name, TagString):
            self.name = str(name._val)
        else:
            self.name = str(name)

    def __str__(self) -> str:
        type_name = type(self).__name__
        return f"{type_name}(name=\"{self.name}\", payload={self.payload})"
        
    @property
    def kind(self) -> int:
        '''Get this named tag's tag kind.'''
        return self.payload.kind
    
    @property
    def kind_tag(self) -> TagByte:
        '''Get the TabByte that indicates the NBT payload tag type'''
        return self.payload.kind_tag
    
    @property
    def kind_int(self) -> int:
        '''Get the int that indicates the NBT payload tag type'''
        return self.payload.kind
    
    @property
    def kind_name(self) -> str:
        '''Get the name str that indicates the NBT payload tag type'''
        return self.payload.kind_name
    
    @property
    def payload_bytes(self) -> bytes:
        '''Get the bytes for this tag's payload.'''
        return bytes(self.payload)
    
    @property
    def name_tag(self) -> TagString:
        '''Get a string name tag that represents this tag's name.'''
        return TagString(self.name)
    
    def __bytes__(self) -> bytes:
        '''Convert this entire named tag to bytes, including type, name, and tag payload.'''
        arr = bytearray()
        arr.append(self.kind)
        if not isinstance(self.payload, TagEnd): # TAG_END cannot be named and has no data payload
            arr.extend(bytes(self.name_tag))
            arr.extend(self.payload_bytes)
        return bytes(arr)
    
    def write_to_file(self, file: BinaryIO | GzipFile) -> int:
        '''
        Write all of this named tag's data to a file by creating the byte buffer first and then writing it all at once.
        '''
        return file.write(bytes(self))
    
    def write_to_file_stepped(self, file: BinaryIO | GzipFile):
        '''
        Write all of this named tag's data to a file by calling the `write_to_file_stepped` method on all sub-tags.
        This can prevent converting the whole structure to bytes before writing to a file, so it might be more performant.
        '''
        self.kind_tag.write_to_file_stepped(file)
        if not isinstance(self.payload, TagEnd): # TAG_END cannot be named and has no data payload
            self.name_tag.write_to_file_stepped(file)
            self.payload.write_to_file_stepped(file)
    