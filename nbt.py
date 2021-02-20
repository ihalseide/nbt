import gzip, sys, struct

# Tag types
TAG_END, \
TAG_BYTE, \
TAG_SHORT, \
TAG_INT, \
TAG_LONG, \
TAG_FLOAT, \
TAG_DOUBLE, \
TAG_BYTEARRAY, \
TAG_STRING, \
TAG_LIST, \
TAG_COMPOUND, \
= range(11)

TAG_NAMES = [
    'TAG_END',
    'TAG_BYTE',
    'TAG_SHORT',
    'TAG_INT',
    'TAG_LONG',
    'TAG_FLOAT',
    'TAG_DOUBLE',
    'TAG_BYTEARRAY',
    'TAG_STRING',
    'TAG_LIST',
    'TAG_COMPOUND',
]

def name_tag_type (tagtype):
    try:
        return TAG_NAMES[tagtype]
    except (IndexError, TypeError):
        raise ValueError('invalid tag type')

class Tag:

    def __init__ (self, tagtype, name=None, **kwargs):
        self.tagtype = tagtype
        self.name = name
        if self.tagtype:
            for attr, val in kwargs.items():
                setattr(self, attr, val)

    def __repr__ (self):
        if self.name is None:
            return '<Tag(%s)>' % (tagname)
        else:
            tagname = name_tag_type(self.tagtype)
            return '<Tag(%s, name="%s")>' % (tagname, self.name) 

def tag_to_data (tag):
    tagtype = tag.tagtype
    if TAG_END == tagtype:
        return None
    elif TAG_BYTE == tagtype:
        return tag.byte
    elif TAG_SHORT == tagtype:
        return tag.short
    elif TAG_INT == tagtype:
        return tag.int
    elif TAG_LONG == tagtype:
        return tag.long
    elif TAG_FLOAT == tagtype:
        return tag.float
    elif TAG_DOUBLE == tagtype:
        return tag.double
    elif TAG_STRING == tagtype:
        return tag.string
    elif TAG_LIST == tagtype:
        return [tag_to_data(subtag) for subtag in tag.list]
    elif TAG_BYTEARRAY == tagtype:
        return tag.bytearray
    elif TAG_COMPOUND == tagtype:
        return {subtag.name: tag_to_data(subtag) for subtag in tag.compound if subtag.tagtype != TAG_END}

def next_bytes (stream, n):
    result = bytearray(n)
    for i in range(n):
        result[i] = next(stream)
    return result

def read_tag (stream, tagtype) -> Tag:
    if TAG_END == tagtype:
        tag = Tag(tagtype)
    elif TAG_BYTE == tagtype:
        byte = next(stream)
        tag = Tag(tagtype, byte=byte)
    elif TAG_SHORT == tagtype:
        short = struct.unpack('>h', next_bytes(stream, 2))[0]
        tag = Tag(tagtype, short=short)
    elif TAG_INT == tagtype:
        integer = struct.unpack('>i', next_bytes(stream, 4))[0]
        tag = Tag(tagtype, int=integer)
    elif TAG_LONG == tagtype:
        long_ = struct.unpack('>q', next_bytes(stream, 8))[0]
        tag = Tag(tagtype, long=long_) 
    elif TAG_FLOAT == tagtype:
        float_ = struct.unpack('>f', next_bytes(stream, 4))[0]
        tag = Tag(tagtype, float=float_)
    elif TAG_DOUBLE == tagtype:
        double = struct.unpack('>d', next_bytes(stream, 8))[0]
        tag = Tag(tagtype, double=double) 
    elif TAG_BYTEARRAY == tagtype:
        length = read_tag(stream, TAG_INT).int
        array = next_bytes(stream, length)
        tag = Tag(tagtype, bytearray=array)
    elif TAG_STRING == tagtype:
        # Read a length encoded string
        length = read_tag(stream, TAG_SHORT).short
        some_bytes = next_bytes(stream, length)
        string = str(some_bytes, 'utf-8')
        tag = Tag(tagtype, None, string=string, bytearray=some_bytes)
    elif TAG_LIST == tagtype: 
        # Read a length encoded list of unnamed tags
        list_tagtype = read_tag(stream, TAG_BYTE).byte
        list_len = read_tag(stream, TAG_INT).int
        tag_list = [read_tag(stream, list_tagtype) for x in range(list_len)]
        tag = Tag(tagtype, None, list=tag_list, item_type=list_tagtype) 
    elif TAG_COMPOUND == tagtype:
        # Read a bunch of named tags until TAG_END
        compound = []
        next_tag_type = None
        while next_tag_type != TAG_END:
            next_tag_type = next(stream)
            sub_tag = read_named_tag(stream, next_tag_type)
            compound.append(sub_tag)
        tag = Tag(tagtype, None, compound=compound)
    else:
        raise ValueError('bad tag type: "%x"' % tagtype)
    return tag

def write_tag (file, tag):
    file.write(struct.pack('c', bytes((tag.tagtype,))))
    write_tag_payload(file, tag)

def write_named_tag (file, tag):
    write_tag(file, Tag(TAG_BYTE, byte=tag.tagtype))
    if TAG_END == tag.tagtype:
        return
    if tag.name is None:
        raise ValueError('tag has no name')
    write_tag(file, Tag(TAG_STRING, string=tag.name))
    write_tag_payload(file, tag)

def write_tag_payload (file, tag):
    tagtype = tag.tagtype
    if TAG_END == tagtype:
        pass # No payload for TAG_END
    elif TAG_BYTE == tagtype:
        byte = struct.pack('c', bytes((tag.byte,)))
        file.write(byte)
    elif TAG_SHORT == tagtype:
        short = struct.pack('>h', tag.short)
        file.write(short)
    elif TAG_INT == tagtype:
        integer = struct.pack('>i', tag.int)
        file.write(integer)
    elif TAG_LONG == tagtype:
        long_ = struct.pack('>q', tag.long)
        file.write(long_)
    elif TAG_FLOAT == tagtype:
        float_ = struct.pack('>f', tag.float)
        file.write(float_)
    elif TAG_DOUBLE == tagtype:
        double = struct.pack('>d', tag.double)
        file.write(double)
    elif TAG_BYTEARRAY == tagtype:
        # Bytearray: length, bytes[length]
        file.write(bytes(len(tag.bytearray)))
        file.write(tag.bytearray)
    elif TAG_STRING == tagtype:
        # String: short length, bytes[length]
        write_tag(file, Tag(TAG_SHORT, short=len(tag.string)))
        file.write(str.encode(tag.string, 'utf-8'))
    elif TAG_LIST == tagtype: 
        # Write a length encoded list of unnamed tags
        write_tag(file, Tag(TAG_INT, int=len(tag.list)))
        write_tag(file, Tag(TAG_BYTE, byte=tag.item_type))
        for subtag in tag.list:
            write_tag_payload(file, subtag)
    elif TAG_COMPOUND == tagtype:
        # Write all named subtags
        for subtag in tag.compound:
            write_named_tag(file, subtag)
        # Tag_compound must end with Tag_end
        if subtag.tagtype != TAG_END:
            write_tag(file, Tag(TAG_END))
    else:
        raise ValueError('bad tag type: "%s"' % tagtype)

def read_named_tag (stream, tagtype): 
    if tagtype == TAG_END:
        return Tag(TAG_END)
    name_tag = read_tag(stream, TAG_STRING) 
    the_tag = read_tag(stream, tagtype) 
    the_tag.name = name_tag.string
    return the_tag

class NBTFile:

    def __init__(self, filename):
        # Unzip the file
        self.filename = filename
        with gzip.open(self.filename, 'rb') as f:
            self.data = f.read() 

        self.stream = iter(self.data) 

        # Read the root TAG_COMPOUND tag
        if TAG_COMPOUND != next(self.stream):
            raise ValueError('NBT file doesn\'t start with %s', name_tag_type(TAG_COMPOUND))
        self.compound = read_named_tag(self.stream, TAG_COMPOUND)

