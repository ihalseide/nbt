'''
Classes for NBT tags that fully contain the data payload from a file (in-memory).'

NOTE: TAG_END is often used as a default or error value in this file
'''


import struct
from typing import BinaryIO, Any, Iterable, Mapping
from gzip import GzipFile # imported for the type annotation

from .constants import *


def nbt_int_from_bytes(b: bytes, length: int) -> int:
    '''
    Converts integer from bytes consistently for all of the int-like tag classes.
    NOTE: should be synchronized with the 'nbt_int_to_bytes' function
    '''
    if len(b) != length:
        raise ValueError(f"not enough bytes for data type of length {length} (only found {len(b)} bytes)")
    return int.from_bytes(b, byteorder='big', signed=True)


def nbt_int_to_bytes(x: int, length: int) -> bytes:
    '''
    Converts integer to bytes consistently for all of the int-like tag classes.
    NOTE: should be synchronized with the 'nbt_int_from_bytes' function
    '''
    return x.to_bytes(length, byteorder='big', signed=True)


def numeric_tag_size(tag_type: int) -> int:
    '''Size in bytes for an integer-like and float-like tag type'''
    result = TAG_NUMERIC_BYTE_COUNT.get(tag_type)
    if not result: raise ValueError(f'tag_type {tag_type} is not a integer or float tag type')
    return result


def int_sized(x: Any, size_bytes: int) -> int:
    '''Convert a value to int and make sure it can be represented by at most 'size_bytes' bytes.
    Raises a 'ValueError' otherwise.'''
    result = int(x)
    if (result.bit_length() / 8.0) > size_bytes:
        raise ValueError(f"magnitude of integer value '{result}' is too large to fit within a {size_bytes}-byte representation")
    return result


def tag_kind_to_str(tag_type: int) -> str:
    '''Get the string name for a tag type'''
    try:
        return TAG_NAMES[tag_type]
    except IndexError:
        raise ValueError(f"int value of {tag_type} does not represent a type of NBT tag")


def tag_array_type_to_item_type(tag_type: int) -> int:
    '''
    Get what the sub-item tag type for the given array-like tag type is.
    The default/error value returned is TAG_END.
    '''
    return TAG_ARRAY_SUBTYPES.get(tag_type, TAG_END)


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
            size = numeric_tag_size(k)
            return TagPayload(k, nbt_int_from_bytes(file.read(size), size))
        elif k == TAG_FLOAT: 
            return TagPayload(k, struct.unpack('>f', file.read(numeric_tag_size(TAG_FLOAT)))[0])
        elif k == TAG_DOUBLE:
            return TagPayload(k, struct.unpack('>d', file.read(numeric_tag_size(TAG_DOUBLE)))[0])
        elif k == TAG_STRING:
            ## Read length-prefixed string (length prefix is a tag_short)
            str_len = TagPayload.read_from_file(TAG_SHORT, file).val_int
            return TagPayload(k, file.read(str_len).decode())
        elif k == TAG_LIST:
            ## Read type-prefixed, length-prefixed list
            item_type = TagPayload.read_from_file(TAG_BYTE, file).val_int
            item_count = TagPayload.read_from_file(TAG_INT, file).val_int
            return TagPayload(k, [ TagPayload.read_from_file(item_type, file) for _ in range(item_count) ], list_item_kind=item_type)
        elif k in (TAG_BYTE_ARRAY, TAG_INT_ARRAY, TAG_LONG_ARRAY):
            ## Read length-prefixed array
            item_type = tag_array_type_to_item_type(k)
            item_count = TagPayload.read_from_file(TAG_INT, file).val_int
            return TagPayload(k, [ TagPayload.read_from_file(item_type, file) for _ in range(item_count) ])
        elif k == TAG_COMPOUND:
            ## Read tags for a tag compound until a tag_end tag is encountered (or EOF)
            compound: dict[str, TagPayload] = dict()
            while (named_tag := NamedTag.read_from_file(file)).payload.tag_kind != TAG_END:
                compound[named_tag.name] = named_tag.payload
            return TagPayload(k, compound)
        else:
            raise ValueError(f"cannot read a tag with invalid tag kind: {tag_kind}")


    def __init__(self, 
                 tag_kind: int = TAG_END, 
                 tag_value: int | float | str | Iterable['TagPayload'] | Mapping[str, 'TagPayload'] | None = None,
                 list_item_kind: int = TAG_END) -> None:
        if not tag_kind in ALL_TAG_TYPES:
            raise ValueError(f"Attempted to initialize 'TagPayload' with invalid 'tag_kind': {tag_kind}")
        
        self._tag_kind: int = tag_kind
        self._list_item_kind: int = list_item_kind
        if (self.tag_kind == TAG_LIST) and list_item_kind == TAG_END:
            raise ValueError(f"must provide a tag 'list_item_kind' argument for a {self.kind_name}")
        
        ## Potential value types. It is only expected that one of these is valid at a time:
        self.val_int: int = 0
        self.val_float: float = 0.0
        self.val_str: str = ''
        self.val_list: list[TagPayload] = []
        self.val_comp: dict[str, TagPayload] = {}

        ## Assign the correct value (if given None, the default value will be kept, which also covers the case with a tag_end tag).
        if tag_value is not None:
            if self.tag_kind in (TAG_BYTE, TAG_SHORT, TAG_INT, TAG_LONG) and isinstance(tag_value, int):
                self.val_int = int_sized(tag_value, numeric_tag_size(self._tag_kind))
            elif self.tag_kind in (TAG_FLOAT, TAG_DOUBLE) and isinstance(tag_value, float):
                self.val_float = tag_value
            elif self.tag_kind == TAG_STRING and isinstance(tag_value, str):
                self.val_str = str(tag_value)
            elif self.tag_kind in (TAG_LIST, TAG_BYTE_ARRAY, TAG_INT_ARRAY, TAG_LONG_ARRAY) and isinstance(tag_value, list):
                for i, item in enumerate(tag_value):
                    if item.tag_kind != self.item_kind:
                        item_kind_name = tag_kind_to_str(self.item_kind)
                        raise ValueError(f"item at index {i} is a {item.kind_name} instead of the expected {item_kind_name}")
                    self.val_list.append(item)
            elif self.tag_kind == TAG_COMPOUND and isinstance(tag_value, dict) and isinstance(tag_value, dict):
                for k, v in tag_value.items():
                    ## Do extra type-checking
                    if not isinstance(k, str): 
                        raise TypeError(f"dictionary key is of type {type(v)} instead of 'str'")
                    if not isinstance(v, TagPayload): 
                        raise TypeError(f"dictionary value is of type {type(v)} instead of 'TagPayload'")
                self.val_comp = tag_value
            elif self.tag_kind not in ALL_TAG_TYPES:
                raise ValueError(f'TagPayload has invalid tag_kind: {self.tag_kind}')
            else:
                raise TypeError(f"Cannot assign value of type {type(tag_value)} to TagPayload of type {self.kind_name}")
    

    def __str__(self) -> str:
        if self.tag_kind in (TAG_BYTE, TAG_SHORT, TAG_INT, TAG_LONG):
            info = str(self.val_int)
        elif self.tag_kind == TAG_STRING:
            info = f"\"{self.val_str}\""
        else:
            info = '...'

        return f"{self.kind_name}({info})"


    def __len__(self) -> int:
        '''For list-like tags only, get the length of this tag's value (sub-element count)'''
        if self.tag_kind in (TAG_LIST, TAG_BYTE_ARRAY, TAG_INT, TAG_LONG_ARRAY):
            return len(self.val_list)
        elif self.tag_kind == TAG_STRING:
            return len(self.val_str)
        elif self.tag_kind == TAG_COMPOUND:
            return len(self.val_comp)
        else:
            raise AttributeError(f"TagPayload of kind {self.kind_name} does not have a 'len'")
    

    def __getitem__(self, index: int | str) -> 'TagPayload':
        if self.tag_kind in (TAG_LIST, TAG_BYTE_ARRAY, TAG_INT, TAG_LONG_ARRAY):
            if not isinstance(index, int):
                raise TypeError(f"TagPayload of kind {self.kind_name} may only be indexed by {type(int)}, not {type(index)}")
            return self.val_list[index]
        elif (self.tag_kind == TAG_COMPOUND):
            if not isinstance(index, str):
                raise TypeError(f"TagPayload of kind {self.kind_name} may only be indexed by {type(str)}, not {type(index)}")
            return self.val_comp[index]
        else:
            raise AttributeError(f"TagPayload of kind {self.kind_name} is not indexable")
    

    def __setitem__(self, index: int | str, value: 'TagPayload'):
        if self.tag_kind == TAG_LIST:
            if not isinstance(index, int):
                raise TypeError(f"TagPayload of kind {self.kind_name} may only be indexed by {type(int)}, not {type(index)}")
            if self._list_item_kind != value.tag_kind:
                raise ValueError(f"Cannot assign an element within a {value.kind_name} tag to a value of kind {value.kind_name}")
            self.val_list[index] = value
        elif self.tag_kind in (TAG_BYTE_ARRAY, TAG_INT, TAG_LONG_ARRAY):
            if not isinstance(index, int):
                raise TypeError(f"TagPayload of kind {self.kind_name} may only be indexed by {type(int)}, not {type(index)}")
            if tag_array_type_to_item_type(self.tag_kind) != value.tag_kind:
                raise ValueError(f"Cannot assign an element within a {value.kind_name} tag to a value of kind {value.kind_name}")
            self.val_list[index] = value
        elif (self.tag_kind == TAG_COMPOUND):
            if not isinstance(index, str):
                raise ValueError(f"Cannot assign an element within a {value.kind_name} tag to a value of kind {value.kind_name}")
            self.val_comp[index] = value
        else:
            raise AttributeError(f"TagPayload of kind {self.kind_name} is not indexable")
    

    def write_to_file(self, file: BinaryIO | GzipFile) -> None:
        '''Write the binary tag payload data to a binary file.'''
        k = self._tag_kind
        if k == TAG_END:
            # No payload
            return
        elif k in (TAG_BYTE, TAG_SHORT, TAG_INT, TAG_LONG):
            # Integer kind
            file.write(nbt_int_to_bytes(self.val_int, numeric_tag_size(self.tag_kind)))
        elif k == TAG_FLOAT: 
            # Float as standard float
            n = file.write(struct.pack('>f', self.val_float))
            assert(n == numeric_tag_size(k))
        elif k == TAG_DOUBLE:
            # Double as standard double
            n = file.write(struct.pack('>d', self.val_float))
            assert(n == numeric_tag_size(k))
        elif k == TAG_STRING:
            # String is length-encoded with an (unnamed) short value
            TagShort(len(self.val_str)).write_to_file(file)
            file.write(self.val_str.encode('utf-8'))
        elif k in (TAG_LIST, TAG_BYTE_ARRAY, TAG_INT_ARRAY, TAG_LONG_ARRAY):
            # Lists/arrays have an element count and then the elements
            if k == TAG_LIST:
                ## List additionally has an element type byte
                TagByte(self._list_item_kind).write_to_file(file)
            ## Element count
            TagInt(len(self.val_list)).write_to_file(file)
            ## Elements
            for tag in self.val_list:
                tag.write_to_file(file)
        elif k == TAG_COMPOUND:
            # Compound tag has named sub-tags up until a tag_end at this level
            for name, tag in self.val_comp.items():
                if tag.tag_kind == TAG_END:
                    ## Stop if a tag_end is encountered early
                    break
                NamedTag(name, tag).write_to_file(file)
            ## Write the tag_end tag
            NamedTag().write_to_file(file)
        else:
            # Invalid tag_kind
            raise ValueError(f"cannot save this TagPayload because it has an unhandled/invalid 'tag_kind': {k}")
    

    @property
    def tag_kind(self) -> int:
        return self._tag_kind
    

    @property
    def kind_name(self) -> str: 
        return tag_kind_to_str(self._tag_kind)
    

    @property
    def item_kind(self) -> int:
        '''For list-like TagPayloads only, get the tag type of the inner element.'''
        if self.tag_kind == TAG_LIST:
            return self._list_item_kind
        return tag_array_type_to_item_type(self.tag_kind)
         

class NamedTag:
    '''
    Represents a Named Binary Tag.
    The binary format for this is [tag-type, a TagByte], and then [name, a TagString], and finally [payload, a Tag].
    '''

    @classmethod
    def read_from_file(cls, file: BinaryIO | GzipFile | str) -> 'NamedTag':
        '''
        Read a named tag from a file or file path. If EOF is reached, return a 'TagEnd' tag.
        NOTE: because of this behavior, a file may omit the trail of ending TagEnd tag(s) to close the top-level TagCompound(s).
        '''
        if isinstance(file, str):
            with open(file, "rb") as arg:
                return cls._read_from_file(arg)
        else:
            return cls._read_from_file(file)
    

    @classmethod
    def _read_from_file(cls, file: BinaryIO | GzipFile) -> 'NamedTag':
        '''
        Read a named tag from a file. If EOF is reached, return a 'TagEnd' tag.
        NOTE: because of this behavior, a file may omit the trail of ending TagEnd tag(s) to close the top-level TagCompound(s).
        '''
        ## Read the tag type byte
        try:
            kind = TagPayload.read_from_file(TAG_BYTE, file)
        except (IndexError, EOFError):
            return NamedTag()
        if kind.val_int not in ALL_TAG_TYPES:
            raise ValueError(f"encountered invalid tag type byte value: {kind.val_int} while reading file")
        
        if kind.val_int == TAG_END:
            ## Special case: don't read a name or payload for a tag_end (it doesn't have a name or payload)
            return NamedTag()
        
        ## Read the tag name (string tag)
        name_tag = TagPayload.read_from_file(TAG_STRING, file)
        ## Read the tag payload
        data_tag = TagPayload.read_from_file(kind.val_int, file)
        return NamedTag(name_tag.val_str, data_tag)


    def __init__(self, name: str = '', payload: TagPayload | None = None):
        '''Create a 'NamedTag' with a 'name' string and a 'payload' NBT tag . If given no arguments, creates an unnamed tag_end tag.'''
        self.name: str = str(name)
        self.payload: TagPayload = TagEnd() if (payload is None) else payload
    

    def write_to_file(self, file: BinaryIO | GzipFile) -> None:
        '''Write this named tag's binary representation to the given file'''
        ## Write the tag type byte
        TagPayload(TAG_BYTE, self.payload.tag_kind).write_to_file(file)
        if self.payload.tag_kind == TAG_END:
            ## tag_end tags don't have a name or payload
            return
        ## Write the name and payload
        TagString(self.name).write_to_file(file)
        self.payload.write_to_file(file)
    

    def __getitem__(self, key: str | int) -> TagPayload:
        return self.payload[key]
    

    def __setitem__(self, key: str | int, value: TagPayload):
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
    def __init__(self, item_type: int, values: list[TagPayload] | None = None):
        super().__init__(TAG_LIST, values, list_item_kind=item_type)


class TagCompound(TagPayload):
    def __init__(self, values: Mapping[str, TagPayload] | None = None):
        super().__init__(TAG_COMPOUND, values)


class TagIntArray(TagPayload):
    def __init__(self, values: list[TagPayload] | None = None):
        super().__init__(TAG_INT_ARRAY, values)


class TagLongArray(TagPayload):
    def __init__(self, values: list[TagPayload] | None = None):
        super().__init__(TAG_LONG_ARRAY, values)
