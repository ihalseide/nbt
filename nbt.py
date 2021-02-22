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
        tagname = name_tag_type(self.tagtype)
        if self.name is None:
            return '<Tag(%s)>' % (tagname)
        else:
            return '<Tag(%s, name="%s")>' % (tagname, self.name) 

    @property
    def data (self):
        tagtype = self.tagtype
        if TAG_END == tagtype:
            return None
        elif TAG_BYTE == tagtype:
            return self.byte
        elif TAG_SHORT == tagtype:
            return self.short
        elif TAG_INT == tagtype:
            return self.int
        elif TAG_LONG == tagtype:
            return self.long
        elif TAG_FLOAT == tagtype:
            return self.float
        elif TAG_DOUBLE == tagtype:
            return self.double
        elif TAG_STRING == tagtype:
            return self.string
        elif TAG_LIST == tagtype:
            return self.list
        elif TAG_BYTEARRAY == tagtype:
            return self.bytearray
        elif TAG_COMPOUND == tagtype:
            return self.compound
        else:
            raise ValueError('unknown tag')

    @data.setter
    def data (self, value):
        tagtype = self.tagtype
        if TAG_END == tagtype:
            pass
        elif TAG_BYTE == tagtype:
            self.byte = value
        elif TAG_SHORT == tagtype:
            self.short = value
        elif TAG_INT == tagtype:
            self.int = value
        elif TAG_LONG == tagtype:
            self.long = value
        elif TAG_FLOAT == tagtype:
            self.float = value
        elif TAG_DOUBLE == tagtype:
            self.double = value
        elif TAG_STRING == tagtype:
            self.string = value
        elif TAG_LIST == tagtype:
            self.list = value
        elif TAG_BYTEARRAY == tagtype:
            self.bytearray = value
        elif TAG_COMPOUND == tagtype:
            self.compound = value
        else:
            raise ValueError('unknown tag')

def read_named_tag (file): 
    tagtype = file.read(1)[0]
    if tagtype == TAG_END:
        # TAG_END is an exception to the rule and cannot be named
        return Tag(TAG_END)
    name = read_tag(file, TAG_STRING) 
    tag = read_tag(file, tagtype) 
    tag.name = name
    return tag

def read_tag (file, tagtype):
    tag = Tag(tagtype)
    if TAG_END == tagtype:
        # TAG_END has no payload to read
        tag.data = None
    elif TAG_BYTE == tagtype:
        tag.data = file.read(1)
    elif TAG_SHORT == tagtype:
        tag.data = struct.unpack('>h', file.read(2))[0]
    elif TAG_INT == tagtype:
        tag.data = struct.unpack('>i', file.read(4))[0]
    elif TAG_LONG == tagtype:
        tag.data = struct.unpack('>q', file.read(8))[0]
    elif TAG_FLOAT == tagtype:
        tag.data = struct.unpack('>f', file.read(4))[0]
    elif TAG_DOUBLE == tagtype:
        tag.data = struct.unpack('>d', file.read(8))[0]
    elif TAG_BYTEARRAY == tagtype:
        # Read a length encoded bytearray
        tag.length = read_tag(file, TAG_INT)
        tag.data = file.read(tag.length.data)
    elif TAG_STRING == tagtype:
        # Read a length encoded string
        tag.length = read_tag(file, TAG_SHORT)
        tag.data = str(file.read(tag.length.data), 'utf-8') 
    elif TAG_LIST == tagtype: 
        # Read a length encoded list of unnamed tags
        tag.item_type = read_tag(file, TAG_BYTE)
        tag.length = read_tag(file, TAG_INT)
        tag.data = [read_tag(file, tag.item_type.data[0]) for x in range(tag.length.data)]
    elif TAG_COMPOUND == tagtype:
        # Read a bunch of named tags until TAG_END
        compound = []
        item = 'start'
        while (item == 'start') or (item.tagtype != TAG_END):
            item = read_named_tag(file)
            compound.append(item)
        tag.data = compound
    else:
        raise ValueError('unknown tag type: %s' % tagtype)
    return tag

def write_named_tag (file, tag):
    # Write tag type
    file.write(bytes((tag.tagtype,)))
    # Write name
    if TAG_END != tag.tagtype:
        # TAG_END cannot be named
        write_tag(file, tag.name)
    # Write payload
    write_tag(file, tag)

def write_tag (file, tag):
    tagtype = tag.tagtype
    if TAG_END == tagtype:
        # TAG_END has no payload to write
        pass 
    elif TAG_BYTE == tagtype:
        byte = struct.pack('>c', tag.byte)
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
        # Bytearray: int length, bytes[length]
        write_tag(file, tag.length)
        file.write(tag.bytearray)
    elif TAG_STRING == tagtype:
        # String: short length, bytes[length]
        write_tag(file, tag.length)
        file.write(str.encode(tag.string, 'utf-8'))
    elif TAG_LIST == tagtype: 
        # Write a length encoded list of unnamed tags
        write_tag(file, tag.length)
        write_tag(file, tag.item_type)
        for item in tag.list:
            write_tag(file, item)
    elif TAG_COMPOUND == tagtype:
        # Write all named subtags
        for item in tag.compound:
            write_named_tag(file, item)
        # Add a TAG_END if the compound didn't end with it already
        # because TAG_COMPOUND must end with TAG_END
        if item.tagtype != TAG_END:
            write_named_tag(file, Tag(TAG_END))
    else:
        raise ValueError('unknown tag type: "%s"' % tagtype)

class NBTFile: 
    def __init__(self, filename):
        # Unzip the file
        self.filename = filename
        with gzip.open(self.filename, 'rb') as file:
            # Read the root TAG_COMPOUND tag
            self.compound = read_named_tag(file)
            if TAG_COMPOUND != self.compound.tagtype:
                expected = name_tag_type(TAG_COMPOUND)
                found = name_tag_type(self.compound.tagtype)
                raise ValueError('a NBT file must start with a "%s" but begins with a "%s" instead' %(expected, found))

