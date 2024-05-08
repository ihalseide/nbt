'''
Classes for NBT tags that fully contain the data payload from a file.
'''

import struct
from typing import BinaryIO, override, Any, Iterable, Mapping, ItemsView, Generator, Union, Literal
from gzip import GzipFile # imported for the type annotation
from abc import ABC, abstractmethod

from nbt.constants import TAG_END

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
    
def int_tag_size(tag_type: int) -> int:
    if tag_type == TAG_BYTE: return 1
    if tag_type == TAG_SHORT: return 2
    if tag_type == TAG_INT: return 4
    if tag_type == TAG_LONG: return 8
    raise ValueError()

def tag_array_type_to_item_type(tag_type: int) -> int:
    if tag_type == TAG_BYTE_ARRAY: return TAG_BYTE
    if tag_type == TAG_INT_ARRAY: return TAG_INT
    if tag_type == TAG_LONG_ARRAY: return TAG_LONG
    return TAG_END

class TagPayload:

    @classmethod
    def read_from_file(cls, tag_kind: int, file: BinaryIO | GzipFile) -> 'TagPayload':
        '''Read the tag payload of the given tag type from a binary file.'''
        k = tag_kind
        if k == TAG_END:
            ## Read no bytes
            return TagPayload(k)
        elif k in (TAG_BYTE, TAG_SHORT, TAG_INT, TAG_LONG):
            ## Integer types
            return TagPayload(k, nbt_int_from_bytes(file.read(int_tag_size(k)), int_tag_size(k)))
        elif k == TAG_FLOAT: 
            return TagPayload(k, struct.unpack('>f', file.read(4))[0])
        elif k == TAG_DOUBLE:
            return TagPayload(k, struct.unpack('>d', file.read(8))[0])
        elif k == TAG_STRING:
            ## Read length-prefixed string (length prefix is a tag_short)
            str_len = TagPayload.read_from_file(TAG_SHORT, file).val_int
            return TagPayload(k, file.read(str_len).decode())
        elif k == TAG_LIST:
            item_type = TagPayload.read_from_file(TAG_BYTE, file).val_int
            item_count = TagPayload.read_from_file(TAG_INT, file).val_int
            return TagPayload(k, [ TagPayload.read_from_file(item_type, file) for _ in range(item_count) ])
        elif k in (TAG_BYTE_ARRAY, TAG_INT_ARRAY, TAG_LONG_ARRAY):
            item_type = tag_array_type_to_item_type(k)
            item_count = TagPayload.read_from_file(TAG_INT, file).val_int
            return TagPayload(k, [ TagPayload.read_from_file(item_type, file) for _ in range(item_count) ])
        elif k == TAG_COMPOUND:
            compound: dict[str, TagPayload] = { }
            while (named_tag := NamedTag.read_from_file(file)).kind != TAG_END:
                compound[named_tag.name] = named_tag.payload
            return TagPayload(k, compound)
        else:
            raise ValueError(f"Invalid tag kind: {tag_kind}")

    def __init__(self, 
                 tag_kind: int = TAG_END, 
                 value: int | float | str | Iterable['TagPayload'] | Mapping[str, 'TagPayload'] | None = None,
                 list_item_kind: int = TAG_END) -> None:
        if not tag_kind in ALL_TAG_TYPES:
            raise ValueError(f"Attempted to initialize 'TagPayload' with invalid 'tag_kind': {tag_kind}")
        self._tag_kind: int = tag_kind
        self._list_item_kind: int = list_item_kind
        self.val_int: int = 0
        self.val_float: float = 0.0
        self.val_str: str = ''
        self.val_list: list[TagPayload] = []
        self.val_comp: dict[str, TagPayload] = {}
        if value is not None:
            if self.tag_kind in (TAG_BYTE, TAG_SHORT, TAG_INT, TAG_LONG) and isinstance(value, int):
                self.val_int = int_sized(value, int_tag_size(self._tag_kind))
            elif self.tag_kind in (TAG_FLOAT, TAG_DOUBLE) and isinstance(value, float):
                self.val_float = value
            elif self.tag_kind == TAG_STRING and isinstance(value, str):
                self.val_str = str(value)
            elif self.tag_kind in (TAG_LIST, TAG_BYTE_ARRAY, TAG_INT_ARRAY, TAG_LONG_ARRAY) and isinstance(value, list):
                self.val_list = list(value)
            elif self.tag_kind == TAG_COMPOUND and isinstance(value, dict) and isinstance(value, dict):
                self.val_comp = value
            elif self.tag_kind not in ALL_TAG_TYPES:
                raise ValueError(f'TagPayload has invalid tag_kind: {self.tag_kind}')
            else:
                raise TypeError(f"Cannot assign value of type {type(value)} to TagPayload of type {self.kind_name}")
    
    def __str__(self) -> str:
        return f"{self.kind_name}()"

    def __len__(self) -> int:
        '''Return the length of this tag's value (sub-element count)'''
        if self.tag_kind in (TAG_LIST, TAG_BYTE_ARRAY, TAG_INT, TAG_LONG_ARRAY):
            return len(self.val_list)
        elif self.tag_kind == TAG_STRING:
            return len(self.val_str)
        elif self.tag_kind == TAG_COMPOUND:
            return len(self.val_comp)
        else:
            raise ValueError(f"TagPayload of kind {self.kind_name} does not have a 'len'")
    
    def __getitem__(self, index: int | str) -> 'TagPayload':
        raise NotImplementedError('TODO')
    
    def __setitem__(self, index: int | str, value: 'TagPayload'):
        raise NotImplementedError('TODO')
    
    def write_to_file(self, file: BinaryIO | GzipFile) -> None:
        k = self._tag_kind
        if k == TAG_END: 
            return
        elif k in (TAG_BYTE, TAG_SHORT, TAG_INT, TAG_LONG):
            file.write(nbt_int_to_bytes(self.val_int, int_tag_size(self._tag_kind)))
        elif k == TAG_FLOAT: 
            file.write(struct.pack('>f', self.val_float))
        elif k == TAG_DOUBLE:
            file.write(struct.pack('>d', self.val_float))
        elif k == TAG_STRING:
            TagShort(len(self.val_str)).write_to_file(file)
            file.write(self.val_str.encode('utf-8'))
        elif k in (TAG_LIST, TAG_BYTE_ARRAY, TAG_INT_ARRAY, TAG_LONG_ARRAY):
            if k == TAG_LIST:
                ## List element type byte
                TagByte(self._list_item_kind).write_to_file(file)
            ## Element count
            TagInt(len(self.val_list)).write_to_file(file)
            ## Elements
            for tag in self.val_list:
                tag.write_to_file(file)
        elif k == TAG_COMPOUND:
            for name, tag in self.val_comp.items():
                if tag.tag_kind == TAG_END:
                    ## Stop if a tag_end is encountered early
                    break
                NamedTag(name, tag).write_to_file(file)
            ## Write the tag_end tag
            NamedTag().write_to_file(file)
        else:
            raise ValueError("this TagPayload has invalid 'tag_kind'")
    
    @property
    def tag_kind(self) -> int:
        return self._tag_kind
    
    @property
    def kind_tag(self) -> 'TagPayload':
        return TagByte(self._tag_kind)
    
    @property
    def kind_name(self) -> str: 
        return tag_kind_to_str(self._tag_kind)
         
class NamedTag:
    '''
    Represents a Named Binary Tag.
    The binary format for this is [tag-type, a TagByte], and then [name, a TagString], and finally [payload, a Tag].
    '''

    @classmethod
    def read_from_file(cls, file: BinaryIO | GzipFile) -> 'NamedTag':
        '''
        Read a named tag from a file. If EOF is reached, return a 'TagEnd' tag.
        NOTE: because of this behavior, a file may omit the trail of ending TagEnd tag(s) to close the top-level TagCompound(s).
        '''
        ## Read the tag type byte
        try:
            kind = TagPayload.read_from_file(TAG_BYTE, file)
        except (IndexError, EOFError):
            return NamedTag("", TagEnd())
        if kind.val_int not in ALL_TAG_TYPES:
            raise ValueError(f"encountered invalid tag type: {kind.val_int}")
        if kind.val_int == TAG_END:
            ## Special case: don't read a name or payload for TagEnd
            return NamedTag('', TagEnd())
        ## Read the tag name (string tag)
        name_tag = TagPayload.read_from_file(TAG_STRING, file)
        ## Read the tag payload
        data_tag = TagPayload.read_from_file(kind.val_int, file)
        return NamedTag(name_tag.val_str, data_tag)

    def __init__(self, name: str = '', payload: TagPayload | None = None):
        '''Create a 'NamedTag' with a 'name' string and a NBT tag 'payload'. If given no arguments, creates an unnamed tag_end tag.'''
        self.name: str = str(name)
        self.payload: TagPayload = TagEnd() if (payload is None) else payload
        if not isinstance(self.payload, TagPayload):
            raise TypeError(f"payload for a 'NamedTag' must be an instance of 'TagPayload' but is of type {type(payload)}")
    
    @property
    def kind(self) -> int:
        '''Get this named tag's tag type a.k.a. kind.'''
        return self.payload.tag_kind
    
    @property
    def kind_name(self) -> str:
        '''Get the name string that indicates the NBT payload tag type a.k.a kind.'''
        return self.payload.kind_name
    
    @property
    def name_tag(self) -> TagPayload:
        '''Get a string name tag that represents this tag's name.'''
        return TagString(self.name)
    
    def write_to_file(self, file: BinaryIO | GzipFile) -> None:
        '''Write this named tag's binary representation to the given file'''
        TagPayload(TAG_BYTE, self.kind).write_to_file(file)
        if self.payload.tag_kind == TAG_END:
            return
        self.name_tag.write_to_file(file)
        self.payload.write_to_file(file)
    
    def __getitem__(self, key: str | int) -> TagPayload:
        '''Calls '__getitem__' on the 'payload' data tag.'''
        return self.payload[key]
    
    def __setitem__(self, key: str | int, value: TagPayload):
        '''Calls '__setitem__' on the 'payload' data tag.'''
        self.payload[key] = value

    def __str__(self) -> str:
        return f"NamedTag(name=\"{self.name}\", payload={self.payload})"
    
class TagEnd(TagPayload):
    def __init__(self, ):
        super().__init__(TAG_END)

class TagByte(TagPayload):
    def __init__(self, val: int):
        super().__init__(TAG_BYTE, val)

class TagShort(TagPayload):
    def __init__(self, val: int):
        super().__init__(TAG_SHORT, val)

class TagInt(TagPayload):
    def __init__(self, val: int):
        super().__init__(TAG_INT, val)

class TagLong(TagPayload):
    def __init__(self, val: int):
        super().__init__(TAG_LONG, val)

class TagFloat(TagPayload):
    def __init__(self, val: float):
        super().__init__(TAG_FLOAT, val)

class TagDouble(TagPayload):
    def __init__(self, val: float):
        super().__init__(TAG_DOUBLE, val)

class TagByteArray(TagPayload):
    def __init__(self, val: int):
        super().__init__(TAG_BYTE_ARRAY, val)

class TagString(TagPayload):
    def __init__(self, val: str):
        super().__init__(TAG_STRING, val)

class TagList(TagPayload):
    def __init__(self, item_type: int, values: list[TagPayload]):
        super().__init__(TAG_LIST, values, list_item_kind=item_type)

class TagCompound(TagPayload):
    def __init__(self, values: Mapping[str, TagPayload]):
        super().__init__(TAG_COMPOUND, values)

class TagIntArray(TagPayload):
    def __init__(self, values: list[TagPayload]):
        super().__init__(TAG_INT_ARRAY, values, list_item_kind=TAG_INT)

class TagLongArray(TagPayload):
    def __init__(self, values: list[TagPayload]):
        super().__init__(TAG_LONG_ARRAY, values, list_item_kind=TAG_LONG)
