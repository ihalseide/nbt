'''
Classes for NBT tags that fully contain the data payload from a file.
'''

import struct
from typing import BinaryIO, override, Any, Iterable, Mapping, ItemsView
from gzip import GzipFile # imported for the type annotation
from abc import ABC, abstractmethod

from .constants import *

def file_expect_read(file: GzipFile | BinaryIO, size: int) -> bytes:
    '''Read exactly 'size' bytes from the 'file' or raise an 'EOFError' if end of file is reached.'''
    result = file.read(size)
    if (actual_length := len(result)) < size:
        raise EOFError(f"expected to read {size} bytes but only got {actual_length} bytes")
    return result

def nbt_int_from_bytes(b: bytes, length: int) -> int:
    '''
    Convenience function for converting integer from bytes consistently for all of the int-like tag classes
    NOTE: should be synchronized with the 'nbt_int_to_bytes' function
    '''
    if len(b) != length:
        raise ValueError(f"not enough bytes for data type of length {length} (only found {len(b)} bytes)")
    return int.from_bytes(b, byteorder='big', signed=True)

def nbt_int_to_bytes(x: int, length: int) -> bytes:
    '''NOTE: should be synchronized with the 'nbt_int_from_bytes' function'''
    return x.to_bytes(length, byteorder='big', signed=True)

def expect_read_int(file: GzipFile | BinaryIO, size: int) -> int:
    return nbt_int_from_bytes(file_expect_read(file, size), size)

def int_sized(x: Any, size_bytes: int) -> int:
    '''Convert a value to int and make sure it can be represented by at most 'size_bytes' bytes.
    Raises a 'ValueError' otherwise.'''
    result = int(x)
    if (result.bit_length() / 8.0) > size_bytes:
        raise ValueError(f"magnitude of integer value '{result}' is too large to fir within a {size_bytes}-byte representation")
    return result

def tag_kind_to_str(tag_type: int) -> str:
    '''Get the string name for a tag type'''
    try:
        return TAG_NAMES[tag_type]
    except IndexError:
        raise ValueError("int value does not represent a type of NBT tag")

class TagDataABC(ABC):
    '''Abstract base class for all the NBT payload classes.'''

    # Default tag type value
    kind = TAG_END

    def name(self) -> str:
        return TAG_NAMES[self.kind]

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
        tag_class = TagDataABC.kind_to_class_type(tag_kind)
        return tag_class.read_from_file(file)
    
    @classmethod
    @abstractmethod
    def read_from_file(cls, file: BinaryIO | GzipFile) -> 'TagDataABC':
        '''Read the tag payload of this classes type from a binary file.'''
        raise NotImplementedError()
    
    def write_to_file_stepped(self, file: BinaryIO | GzipFile):
        '''
        Meant to be overridden (but not required to be).
        Write a tag to a file (special version which may be overrided if the tag type has a way to split up writes into steps).
        If a subclass doesn't override this method, this default implementation is always correct!
        '''
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
    
    def __len__(self) -> int:
        raise NotImplementedError("this NBT tag type does not implement `len`")
    
    def get(self, key):
        raise NotImplementedError("this NBT tag type does not implement `get`")
    
    def __getitem__(self, key) -> 'TagDataABC':
        raise NotImplementedError("this NBT tag type is not subscriptable")
    
    def __setitem__(self, key, value):
        raise NotImplementedError("this NBT tag type is not subscriptable")
    
    def __str__(self) -> str:
        type_name = type(self).__name__
        return f"{type_name}()"
    
class TagArrayABC(TagDataABC):
    '''Convenient abstract base class to reduce repetition within the implementation of TagList, TagByteArray, TagIntArray, and TagLongArray.'''

    @override
    def __len__(self) -> int:
        return len(self.value)
    
    @override
    def __getitem__(self, index: int) -> TagDataABC:
        return self.value[index]
    
    @override
    def __setitem__(self, index: int, value: TagDataABC):
        if not isinstance(value, TagDataABC):
            raise TypeError("value must be an instance of 'TagDataABC'")
        self.value[index] = value

    @override
    def get(self, index: int) -> TagDataABC | None:
        try:
            return self[index]
        except (IndexError, KeyError):
            return None
        
    @abstractmethod
    def append(self, item: TagDataABC):
        raise NotImplementedError()
        
class TagEnd(TagDataABC):

    kind = TAG_END

    @classmethod
    def read_from_file(cls, file: BinaryIO | GzipFile) -> 'TagEnd':
        return TagEnd()

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
        return TagByte(nbt_int_from_bytes(file.read(cls.size), cls.size))
    
    def __init__(self, val: int):
        self._val = int_sized(val, self.size)

    def __bytes__(self) -> bytes:
        return nbt_int_to_bytes(self._val, self.size)
    
    @property
    def value(self) -> int:
        return self._val
    
class TagShort(TagDataABC): 

    kind = TAG_SHORT
    size = 2

    @classmethod
    def read_from_file(cls, file: BinaryIO | GzipFile) -> 'TagShort':
        return TagShort(expect_read_int(file, cls.size))
    
    def __init__(self, val: int):
        self._val = int_sized(val, self.size)

    def __bytes__(self) -> bytes:
        return nbt_int_to_bytes(self._val, self.size)
    
    @property
    def value(self) -> int:
        return self._val
    
class TagInt(TagDataABC): 

    kind = TAG_INT
    size = 4

    @classmethod
    def read_from_file(cls, file: BinaryIO | GzipFile) -> 'TagInt':
        return TagInt(expect_read_int(file, cls.size))
    
    def __init__(self, val: int):
        self._val: int = int_sized(val, self.size)

    def __bytes__(self) -> bytes:
        return nbt_int_to_bytes(self._val, self.size)
    
    @property
    def value(self) -> int:
        return self._val
    
class TagLong(TagDataABC): 

    kind = TAG_LONG
    size = 8

    @classmethod
    def read_from_file(cls, file: BinaryIO | GzipFile) -> 'TagLong':
        return TagLong(expect_read_int(file, cls.size))
    
    def __init__(self, val: int):
        self._val = int_sized(val, self.size)

    def __bytes__(self) -> bytes:
        return nbt_int_to_bytes(self._val, self.size)
    
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
    
class TagList(TagArrayABC):

    kind = TAG_LIST

    @classmethod
    def read_from_file(cls, file: BinaryIO | GzipFile) -> 'TagList':
        ## Read [item-type, a byte] then [item-count, an int] 
        item_kind = TagByte.read_from_file(file).value
        item_class = cls.kind_to_class_type(item_kind) # TODO: if this raises a ValueError, raise some file format exception
        item_count = TagInt.read_from_file(file).value
        ## And then read item-count tags of item-type.
        return TagList(item_kind, [ item_class.read_from_file(file) for _ in range(item_count) ])
    
    @override
    def write_to_file_stepped(self, file: BinaryIO | GzipFile):
        '''Override the parent method so that this can be broken down into 2 write calls.'''
        self.element_kind_tag.write_to_file_stepped(file)
        TagShort(self.element_count).write_to_file_stepped(file)
        for tag in self._val:
            tag.write_to_file_stepped(file)
    
    def __init__(self, item_kind: int|TagByte, val: Iterable[TagDataABC] = ()):
        self._val = list()

        # Set item_kind (element type)
        if isinstance(item_kind, int):
            self._item_kind = item_kind
        elif isinstance(item_kind, TagByte):
            # Extract value from integer tag
            self._item_kind = item_kind.value
        else:
            raise TypeError("'item_kind' must be an int or a int-like kind of TagDataABC")
        
        # Set and check the elements
        for i, tag_i in enumerate(val):
            if not isinstance(tag_i, TagDataABC):
                raise TypeError(f"item \"{tag_i}\", is not an instance of 'TagDataABC'")
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
    def value(self) -> list[TagDataABC]:
        return self._val
    
    @property
    def element_count(self) -> int:
        return len(self)
    
    @property
    def element_kind_tag(self) -> TagByte:
        return TagByte(self._item_kind)
    
    def append(self, item: TagDataABC):
        if not isinstance(item, TagDataABC):
            raise TypeError()
        self._val.append(item)
    
class TagCompound(TagDataABC):
    '''
    A 'TagCompound' is an non-homogeneous container for NBT tags.
    NOTE: this class will automatically ensure that the value ends with a 'TagEnd' tag (so don't manually add one).
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
    
    @override
    def write_to_file_stepped(self, file: BinaryIO | GzipFile):
        # Add all data values (but don't allow TagEnd values before the end!)
        for name, tag in self._val.items():
            if isinstance(tag, TagEnd):
                #raise TypeError("an extraneous TagEnd value was found within a TagCompound")
                continue
            NamedTag(name, tag).write_to_file_stepped(file)
        # Add the terminating TagEnd value
        NamedTag('', TagEnd()).write_to_file_stepped(file)
    
    def __init__(self, val: Iterable['NamedTag'] | Mapping[str, TagDataABC]):
        '''
        Create a new 'TagCompound' with either a sequence of 'NamedTag's or a dict that maps
        'str's to instances that inherit from 'TagDataABC'.
        '''
        self._val: dict[str, TagDataABC] = {}
        if isinstance(val, dict):
            ## Initialize from a dictionary that maps names to tag data
            for name, tag in val.items():
                if not isinstance(name, str):
                    raise TypeError("name is not a 'str'")
                if not isinstance(tag, TagDataABC):
                    raise TypeError(f"item \"{tag}\" is not a 'TagDataABC' instance")
                if isinstance(tag, TagEnd):
                    # Ignore TagEnd values
                    continue
                self._val[name] = tag
        elif isinstance(val, list):
            ## Initialize from a list of named tags
            for named_tag in val:
                if not isinstance(named_tag, NamedTag):
                    raise TypeError("named_tag is not a 'NamedTag' instance")
                if isinstance(named_tag.payload, TagEnd):
                    # Ignore TagEnd values
                    continue
                self._val[named_tag.name] = named_tag.payload
        else:
            raise TypeError("must initialize a 'TagCompound' from a list of 'NamedTag's or from a dict that maps 'str's to 'TagDataABC's")

    def __bytes__(self) -> bytes:
        result = bytearray()
        # Add all data values (but don't allow TagEnd values before the end!)
        for name, tag in self._val.items():
            if isinstance(tag, TagEnd):
                #raise TypeError("an extraneous TagEnd value was found within a TagCompound")
                continue
            named_tag = NamedTag(name, tag)
            result.extend(bytes(named_tag))
        # Add the terminating TagEnd value
        result.extend(bytes(NamedTag('', TagEnd())))
        return bytes(result)
    
    @override
    @property
    def element_count(self) -> int:
        # Subtract 1 because the end tag at the end doesn't count
        return len(self._val)
    
    @property
    def value(self) -> list['NamedTag']:
        '''NOTE: value list of tags does not have the 'TagEnd' at the end'''
        #return [ NamedTag(name, tag) for name, tag in self._val.items() ] + [ NamedTag('', TagEnd()) ]
        return [ NamedTag(name, tag) for name, tag in self._val.items() ]
    
    def items(self) -> ItemsView[str, TagDataABC]:
        return self._val.items()
    
    def get(self, key: str) -> TagDataABC | None:
        '''Get the first tag found that has the given name.'''
        try:
            return self[key]
        except KeyError:
            return None
    
    @override
    def __getitem__(self, key: str) -> TagDataABC:
        '''Get the first tag found that has the given name.'''
        if not isinstance(key, str):
            raise TypeError("index 'key' must be a 'str'")
        return self._val[key]
    
    @override
    def __setitem__(self, key: str, value: TagDataABC):
        if not isinstance(key, str):
            raise TypeError("index 'key' must be a 'str'")
        if not isinstance(value, TagDataABC):
            raise TypeError("'value' must be an instance of 'TagDataABC'")
        if isinstance(value, TagEnd):
            raise TypeError("cannot put a literal TagEnd value into a TagCompound (the terminating TagEnd is handled automatically)")
        self._val[key] = value
    
class TagIntArray(TagArrayABC):

    kind = TAG_INT_ARRAY

    @classmethod
    def read_from_file(cls, file: BinaryIO | GzipFile) -> 'TagIntArray':
        count = TagInt.read_from_file(file)._val
        return TagIntArray([ TagInt.read_from_file(file)._val for _ in range(count) ])
    
    def __init__(self, val: Iterable[int]):
        self._val = list( int_sized(x, TagInt.size) for x in val )

    def __bytes__(self) -> bytes:
        result = bytearray()
        result.extend(bytes(TagInt(self.element_count)))
        for x in self._val:
            result.extend(bytes(TagInt(x)))
        return bytes(result)
    
    @property
    def value(self) -> list[int]:
        return self._val
    
    @property
    def element_count(self) -> int:
        return len(self._val)
    
    def append(self, item: TagDataABC):
        if not isinstance(item, TagInt):
            raise TypeError()
        self._val.append(item.value)
    
class TagLongArray(TagArrayABC):

    kind = TAG_LONG_ARRAY

    @classmethod
    def read_from_file(cls, file: BinaryIO | GzipFile) -> 'TagLongArray':
        count = TagInt.read_from_file(file)._val
        return TagLongArray([ TagLong.read_from_file(file)._val for _ in range(count) ])
    
    def __init__(self, val: Iterable[int]):
        self._val = list( int_sized(x, TagLong.size) for x in val )

    def __bytes__(self) -> bytes:
        result = bytearray()
        result.extend(bytes(TagInt(self.element_count)))
        for x in self._val:
            result.extend(bytes(TagLong(x)))
        return bytes(result)
    
    @property
    def value(self) -> list[int]:
        return self._val
    
    @property
    def element_count(self) -> int:
        return len(self._val)
    
    def append(self, item: TagDataABC):
        if not isinstance(item, TagLong):
            raise TypeError()
        self._val.append(item.value)
    
class NamedTag:

    @staticmethod
    def read_from_file(file: BinaryIO | GzipFile) -> 'NamedTag':
        '''
        Read a named tag from a file. If EOF is reached, return a 'TagEnd' tag.
        NOTE: because of this behavior, a file may omit the trail of ending TagEnd tag(s) to close the top-level TagCompound(s).
        '''
        ## Read the tag type byte
        try:
            kind = TagByte.read_from_file(file)
        except (IndexError, EOFError):
            return NamedTag("", TagEnd())
        if kind.value not in ALL_TAG_TYPES:
            raise ValueError(f"encountered invalid tag type: {kind.value}")
        if kind.value == TAG_END:
            ## Special case: don't read a name or payload for TagEnd
            return NamedTag('', TagEnd())
        else:
            ## Read the tag name (string tag)
            name_tag = TagString.read_from_file(file)
            ## Read the tag payload pay
            data_tag = TagDataABC.dispatch_read_from_file(kind.value, file)
            return NamedTag(name_tag, data_tag)

    def __init__(self, name: str | TagString = '', payload: TagDataABC | None = None):
        '''Create a 'NamedTag' with a 'name' string and a NBT tag 'payload'.'''
        if not isinstance(payload, TagDataABC):
            raise TypeError("a 'NamedTag' must be initialized with a payload that is an instance of 'TagDataABC'")
        self.name: str = name.value if isinstance(name, TagString) else str(name)
        self.payload: TagDataABC = TagEnd() if (payload is None) else payload
        if not isinstance(payload, TagDataABC):
            raise TypeError(f"payload for a 'NamedTag' must be an instance of 'TagDataABC' but is of type {type(payload)}")
    
    def get(self, key: str | int) -> TagDataABC | None:
        '''Calls 'get' on the 'payload' data tag.'''
        return self.payload.get(key)
        
    def __getitem__(self, key: str | int) -> TagDataABC:
        '''Calls '__getitem__' on the 'payload' data tag.'''
        return self.payload[key]
    
    def __setitem__(self, key: str | int, value: TagDataABC):
        '''Calls '__setitem__' on the 'payload' data tag.'''
        self.payload[key] = value

    def __str__(self) -> str:
        return f"NamedTag(name=\"{self.name}\", payload={self.payload})"
        
    @property
    def kind(self) -> int:
        '''Get this named tag's tag type a.k.a. kind.'''
        return self.payload.kind
    
    @property
    def kind_tag(self) -> TagByte:
        '''Get the TabByte that indicates the NBT payload tag type a.k.a kind.'''
        return self.payload.kind_tag
    
    @property
    def kind_int(self) -> int:
        '''Get the int that indicates the NBT payload tag type a.k.a kind.'''
        return self.payload.kind
    
    @property
    def kind_name(self) -> str:
        '''Get the name string that indicates the NBT payload tag type a.k.a kind.'''
        return self.payload.kind_name
    
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
            arr.extend(bytes(self.payload))
        return bytes(arr)
    
    def write_to_file(self, file: BinaryIO | GzipFile) -> int:
        '''
        Write all of this named tag's data to a file by first creating the entire data byte buffer and then writing it all at once.
        
        See also: 'write_to_file_stepped'.
        '''
        return file.write(bytes(self))
    
    def write_to_file_stepped(self, file: BinaryIO | GzipFile):
        '''
        Write all of this named tag's data to a file by calling the 'write_to_file_stepped' method on all sub-tags.
        This can prevent converting the whole structure to bytes before writing to a file, so it might be more performant.

        See also: 'write_to_file'
        '''
        self.kind_tag.write_to_file_stepped(file)
        if not isinstance(self.payload, TagEnd): # TAG_END cannot be named and has no data payload
            self.name_tag.write_to_file_stepped(file)
            self.payload.write_to_file_stepped(file)
    