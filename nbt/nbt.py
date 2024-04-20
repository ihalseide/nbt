import gzip, struct, enum
from gzip import GzipFile
from typing import BinaryIO, Self, Any

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

@enum.unique
class TagKind(enum.IntEnum):

    END = 0
    BYTE = 1
    SHORT = 2
    INT = 3
    LONG = 4
    FLOAT = 5
    DOUBLE = 6
    BYTE_ARRAY = 7
    STRING = 8
    LIST = 9
    COMPOUND = 10
    INT_ARRAY = 11
    LONG_ARRAY = 12

    @staticmethod
    def to_str(tag_type: int) -> str:
        '''Get the string name for a tag type'''
        return TAG_NAMES[tag_type]

    @staticmethod
    def is_list_kind(tag_type: int) -> bool:
        return int(tag_type) in (TagKind.BYTE_ARRAY, TagKind.STRING, TagKind.LIST,
                            TagKind.COMPOUND, TagKind.INT_ARRAY, TagKind.LONG_ARRAY)

    @staticmethod
    def is_atom_kind(tag_type: int) -> bool:
        return int(tag_type) in (TagKind.BYTE, TagKind.SHORT, TagKind.INT,
                            TagKind.LONG, TagKind.FLOAT, TagKind.DOUBLE)

class Tag:
    '''Main NBT data tag class.'''

    @staticmethod
    def as_name_tag(name) -> 'Tag':
        if isinstance(name, Tag):
            return name
        elif isinstance(name, str):
            result_tag = Tag(TagKind.STRING)
            result_tag.val_str = name
            result_tag.length_tag = Tag(TagKind.SHORT)
            result_tag.length_tag.val_int = len(name)
            return result_tag
        else:
            raise TypeError()
        
    @staticmethod
    def from_str(val: str, name: str|None = None) -> 'Tag':
        if not isinstance(val, str): raise TypeError()
        result = Tag(TagKind.STRING, name)
        result.val_str = val
        return result
    
    @staticmethod
    def from_int(val: int, name: str|None = None) -> 'Tag':
        if not isinstance(val, int): raise TypeError()
        if _int_can_fit(val, 1): kind = TagKind.BYTE
        elif _int_can_fit(val, 2): kind = TagKind.SHORT
        elif _int_can_fit(val, 4): kind = TagKind.INT
        elif _int_can_fit(val, 8): kind = TagKind.LONG
        else:
            raise OverflowError("cannot represent the integer value with a NBT long integer tag")
        result = Tag(kind, name)
        result.val_int = val
        return result

    @staticmethod
    def from_float(val: float, name: str|None = None) -> 'Tag':
        if not isinstance(val, float): raise TypeError()
        result = Tag(TagKind.FLOAT, name)
        result.val_float = val
        return result
    
    @staticmethod
    def from_double(val: float, name: str|None = None) -> 'Tag':
        if not isinstance(val, float): raise TypeError()
        result = Tag(TagKind.DOUBLE, name)
        result.val_float = val
        return result
    
    @staticmethod
    def from_bytes(val: bytes, name: str|None = None) -> 'Tag':
        '''Create a bytearray tag using bytes'''
        if not isinstance(val, bytes): raise TypeError()
        result = Tag(TagKind.BYTE_ARRAY, name)
        result.val_bytes = val
        return result
    
    @staticmethod
    def from_list(val: tuple['Tag'], name: str|None = None) -> 'Tag':
        '''Create a compound tag from a tuple of tags. Will add a end tag at the end if not already present.'''
        if not isinstance(val, tuple): raise TypeError()
        result = Tag(TagKind.COMPOUND, name)
        result.val_list = list(val)
        if result.val_list and result.val_list[-1].kind != TagKind.END:
            result.val_list.append(Tag(TagKind.END))
        return result

    def __init__(self, tag_type: TagKind, name: Self|str|None = None):
        self.kind: TagKind = tag_type
        ## Name is a TAG_STRING
        self.name_tag: Tag|None = name if (name is None) else Tag.as_name_tag(name)
        if self.name_tag is not None:
            assert(self.name_tag.kind == TagKind.STRING)
        ## The `self.kind` determines Which of these values to actually use:
        self.val_float: float = 0
        self.val_int: int = 0
        self.val_list: list[Tag] = []
        self.val_bytes: bytes = bytes()
        self.val_str: str = ''
        ## Only used for list, string, bytearray, int_array, and long_array tag types.
        self.length_tag: Tag|None = None
        ## Only used for the list tag type to keep track of the type of the array elements.
        self.item_type: Tag|None = None

    def get_value(self) -> Any:
        '''Get the appropriate value type that this tag holds.'''
        match self.kind:
            case TagKind.END:
                return None
            case TagKind.BYTE_ARRAY: 
                return self.val_bytes
            case TagKind.STRING: 
                return self.val_str
            case TagKind.BYTE | TagKind.SHORT | TagKind.INT | TagKind.LONG: 
                return self.val_int
            case TagKind.FLOAT | TagKind.DOUBLE: 
                return self.val_float
            case TagKind.LIST | TagKind.COMPOUND | TagKind.INT_ARRAY | TagKind.LONG_ARRAY: 
                return self.val_list
            case _:
                raise ValueError("this Tag has an unexpected TagKind")

    def get_name_str(self) -> str:
        if self.kind == TagKind.END:
            return ''
        elif self.name_tag is not None:
            return self.name_tag.val_str
        else:
            return ''
        
    def get_item_kind(self) -> TagKind:
        if self.item_type is not None:
            return TagKind(self.item_type.val_int)
        else:
            raise ValueError("NBT tag {self.kind} has no item kind")
        
    def get_length(self) -> int:
        if self.length_tag is not None:
            return self.length_tag.val_int
        else:
            raise ValueError("NBT tag {self.kind} has no array length")

    def __getitem__ (self, key: int|str):
        if TagKind.is_list_kind(self.kind):
            ## A list type index access
            if isinstance(key, int):
                return self.val_list[key]
            else:
                raise TypeError('NBT list tag must be indexed with an integer key')
        elif TagKind.COMPOUND == self.kind:
            ## Lookup item by name within a compound tag
            if not isinstance(key, str):
                raise TypeError('NBT compound tag must be indexed with a string key')
            for tag in self.val_list:
                if TagKind.END == tag.kind:
                    break
                # Find named tags
                if (tag.name_tag is not None) and (tag.name_tag.val_str == key):
                    return tag
            raise KeyError()
        else:
            ## Other types are not indexable
            kind = TagKind.to_str(self.kind)
            raise ValueError(f"NBT tag of type {kind} is not indexable")

    def __setitem__ (self, key, value):
        raise NotImplementedError()

    def __repr__ (self):
        try:
            typename = TagKind.to_str(self.kind)
        except ValueError:
            return '<Unknown Tag %s>' % str(self.kind)

        props = [typename] 
        if self.name_tag is not None:
            props.append('name="%s"' % self.name_tag.value) 
        if TagKind.is_atom_kind(self.kind):
            props.append('value=%d' % self.val_list)
        else:
            props.append('length=%d' % self.length_tag.value)
            # Item type only exists if length does too
            if self.item_type is not None:
                k = TagKind.to_str(self.item_type.value)
                props.append(f"item_type={k}") 

        return 'Tag(%s)' % ', '.join(props)

    def __bytes__ (self) -> bytes:
        '''Convert a Tag's inner data value (payload) to bytes.'''
        if TagKind.END == self.kind: 
            return bytes()
        elif TagKind.BYTE == self.kind:
            return struct.pack('>c', self.val_int)
        elif TagKind.SHORT == self.kind:
            return struct.pack('>h', self.val_int)
        elif TagKind.INT == self.kind:
            return struct.pack('>i', self.val_int)
        elif TagKind.LONG == self.kind:
            return struct.pack('>q', self.val_int)
        elif TagKind.FLOAT == self.kind:
            return struct.pack('>f', self.val_float)
        elif TagKind.DOUBLE == self.kind:
            return struct.pack('>d', self.val_float)
        elif TagKind.BYTE_ARRAY == self.kind:
            assert(self.length_tag is not None)
            return bytes(self.length_tag) + self.val_bytes
        elif TagKind.STRING == self.kind:
            assert(self.length_tag is not None)
            return bytes(self.length_tag) + self.val_str.encode('utf-8')
        elif TagKind.LIST == self.kind: 
            # Write a length encoded list of unnamed tags
            assert(self.item_type is not None)
            assert(self.length_tag is not None)
            item_type = bytes(self.item_type)
            length = bytes(self.length_tag)
            items_bytes = bytearray()
            for item in self.val_list:
                items_bytes += bytes(item)
            return bytes(item_type + length + items_bytes)
        elif TagKind.COMPOUND == self.kind:
            items_bytes = bytearray()
            for item in self.val_list:
                # These are named tags, except for TAG_END
                items_bytes += bytes(item.kind)
                if TagKind.END != item.kind:
                    assert(item.name_tag is not None)
                    items_bytes += bytes(item.name_tag)
                items_bytes += bytes(item)
            return bytes(items_bytes)
        elif self.kind in (TagKind.LONG_ARRAY, TagKind.INT_ARRAY):
            # TAG_LONG_ARRAY and TAG_INT_ARRAY both have the same high-level pattern
            assert(self.length_tag is not None)
            items_bytes = bytearray()
            items_bytes += bytes(self.length_tag)
            for t in self.val_list:
                items_bytes += bytes(t)
            return bytes(items_bytes)
        else:
            raise ValueError('unknown tag type')
        
    def add_bytes_to(self, arr: bytearray, use_name=False):
        '''Add full byte representation of the tag to the given array.'''
        if use_name:
            # Write tag type
            arr.append(int(self.kind))
            # Write name, but TAG_END cannot be named
            if TagKind.END != self.kind:
                assert(self.name_tag is not None)
                self.name_tag.add_bytes_to(arr, use_name=False)
            # Write payload
            arr.extend(bytes(self))
        else:
            # Just write raw data
            arr.extend(bytes(self))

    def to_bytes(self, use_name=False) -> bytes:
        '''Return full byte representation of the tag.'''
        return self.add_bytes_to(bytearray(), use_name)

class NBTFile:
    '''Main NBT file class'''

    def __init__(self, file_name: str):
        # Unzip the file
        self.file_name: str = file_name
        with gzip.open(self.file_name, 'rb') as file:
            # Read the root TAG_COMPOUND tag
            self.nbt: Tag = read_named_tag(file)
            if TagKind.COMPOUND != self.nbt.kind:
                expected = TagKind.to_str(TagKind.COMPOUND)
                found = TagKind.to_str(self.nbt.kind)
                raise ValueError(f"the NBT file \"{file_name}\" must start with a \"{expected}\" but begins with a \"{found}\" instead") 

    def __repr__(self):
        return f"NBTFile(file_name=\"{self.file_name}\")"

    def __getitem__(self, name: str):
        if not isinstance(name, str):
            raise TypeError('name must be a str')
        return self.nbt[name]

    def __setitem__(self, name, value):
        if type(name) != str:
            raise TypeError('name must be a instance of str')
        if type(value) != Tag:
            raise TypeError('value must be an instance of Tag')
        self.nbt[name] = value


def read_named_tag(file: BinaryIO|GzipFile): 
    kind = TagKind(file.read(1)[0])
    if TagKind.END == kind:
        # TAG_END is an exception to the rule and cannot be named
        return Tag(TagKind.END)
    name_tag = read_tag(file, TagKind.STRING) 
    tag = read_tag(file, kind) 
    tag.name_tag = name_tag
    return tag


def read_tag(file: BinaryIO|GzipFile, tag_type: TagKind) -> Tag:
    tag_result = Tag(tag_type)
    if TagKind.END == tag_type:
        # TAG_END has no payload to read
        pass
    elif TagKind.BYTE == tag_type:
        # 1 byte
        tag_result.val_int = file.read(1)[0]
    elif TagKind.SHORT == tag_type:
        # 2 byte short
        tag_result.val_int = struct.unpack('>h', file.read(2))[0]
    elif TagKind.INT == tag_type:
        # 4 byte integer
        tag_result.val_int = struct.unpack('>i', file.read(4))[0]
    elif TagKind.LONG == tag_type:
        # 8 byte long
        tag_result.val_int = struct.unpack('>q', file.read(8))[0]
    elif TagKind.FLOAT == tag_type:
        # 4 byte float
        tag_result.val_float = struct.unpack('>f', file.read(4))[0]
    elif TagKind.DOUBLE == tag_type:
        # 8 byte double
        tag_result.val_float = struct.unpack('>d', file.read(8))[0]
    elif TagKind.BYTE_ARRAY == tag_type:
        # Read a length encoded bytearray
        tag_result.length_tag = read_tag(file, TagKind.INT)
        tag_result.val_bytes = file.read(tag_result.length_tag.val_int)
    elif TagKind.STRING == tag_type:
        # Read a length-encoded string
        tag_result.length_tag = read_tag(file, TagKind.SHORT)
        tag_result.val_str = file.read(tag_result.length_tag.val_int).decode('utf-8')
    elif TagKind.LIST == tag_type: 
        # Read a length encoded list of unnamed tags
        tag_result.item_type = read_tag(file, TagKind.BYTE) # Read type for list elements
        tag_result.length_tag = read_tag(file, TagKind.INT) # Read number of elements
        item_kind = TagKind(tag_result.item_type.val_int)
        item_count = tag_result.length_tag.val_int
        tag_result.val_list = [read_tag(file, item_kind) for _ in range(item_count)]
    elif TagKind.COMPOUND == tag_type:
        # Read a bunch of named tags until TAG_END
        compound = []
        item = read_named_tag(file)
        while TagKind.END != item.kind:
            compound.append(item)
            item = read_named_tag(file)
        tag_result.val_list = compound
        # Add an extra length tag for consistency with the other list-like tags
        # TODO: should I keep this step?
        tag_result.length_tag = Tag(TagKind.INT)
        tag_result.length_tag.val_int = len(compound)
    elif TagKind.INT_ARRAY == tag_type:
        # Read int length, and then int[length]
        tag_result.length_tag = read_tag(file, TagKind.INT)
        item_count = tag_result.length_tag.val_int
        tag_result.val_list = [read_tag(file, TagKind.INT) for x in range(item_count)]
    elif TagKind.LONG_ARRAY == tag_type:
        # Read int length, and then long[length]
        tag_result.length_tag = read_tag(file, TagKind.INT)
        item_count = tag_result.length_tag.val_int
        tag_result.val_list = [read_tag(file, TagKind.LONG) for x in range(item_count)]
    else:
        raise ValueError(f"cannot read data for unknown NBT tag type: {tag_type}")
    return tag_result

def _write_tag(tag: Tag, file: BinaryIO|GzipFile, include_name=False):
    '''Private method to implement `write_tag_to_file`.'''
    if include_name:
        # Write tag type
        file.write(bytes(int(tag.kind)))
        # Write name, but TAG_END cannot be named
        if TagKind.END != tag.kind:
            assert(tag.name_tag is not None)
            _write_tag(tag.name_tag, file, include_name=False)
        # Write payload
        file.write(bytes(tag))
    else:
        # Just write raw data
        file.write(bytes(tag))

def _write_tag_to_file(tag, file: BinaryIO|GzipFile):
    _write_tag(tag, file, include_name=True)
        
def write_tag_to_file(tag: Tag, file: BinaryIO|GzipFile|str):
    '''Write a compound NBT tag to a file.'''
    if TagKind.COMPOUND != tag.kind:
        raise ValueError("only a NBT compound tag should be written to a file")
    if isinstance(file, str):
        with gzip.open(file, 'wb') as f:
            _write_tag_to_file(tag, f)
    else:
        _write_tag_to_file(tag, file)

def _int_can_fit(x: int, num_bytes: int) -> bool:
    '''Get if a signed integer can fit into and be represented by a certain number of bytes.'''
    try:
        int.to_bytes(x, num_bytes, signed=True)
        return True
    except OverflowError:
        return False