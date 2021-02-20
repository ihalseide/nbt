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
            return '<Tag(%s, name=%s)>' % (tagname, self.name) 

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


def print_tag (tag, indent=0, bytearraysize=64): 
    tagtype = tag.tagtype 
    namestr = ' "%s"'%tag.name if tag.name is not None else ''

    print(end='    ' * indent) 
    if TAG_END == tagtype:
        print('end')
    elif TAG_BYTE == tagtype:
        print('byte%s = %x' % (namestr, tag.byte))
    elif TAG_SHORT == tagtype:
        print('short%s = %d' % (namestr, tag.short))
    elif TAG_INT == tagtype:
        print('int%s = %d' % (namestr, tag.int))
    elif TAG_LONG == tagtype:
        print('long%s = %d' % (namestr, tag.long))
    elif TAG_FLOAT == tagtype:
        print('float%s = %f' % (namestr, tag.float))
    elif TAG_DOUBLE == tagtype:
        print('double%s = %f' % (namestr, tag.double))
    elif TAG_STRING == tagtype:
        print('string%s = "%s"' % (namestr, tag.string))
    elif TAG_LIST == tagtype:
        print('list %s[%d]%s =' % (name_tag_type(tag.item_type), len(tag.list), namestr))
        for sub_tag in tag.list:
            print_tag(sub_tag, indent+1)
    elif TAG_BYTEARRAY == tagtype:
        print('bytearray [%d]%s =' % (len(tag.bytearray), namestr))
        hex_stream = iter(tag.bytearray.hex().upper())
        i = 1
        print(end='    ' * (indent + 1)) 
        while char := next(hex_stream, None):
            print(end=char)
            if i > (bytearraysize - 1):
                print()
                print(end='    ' * (indent + 1)) 
                i = 0
            i += 1
        print()
    elif TAG_COMPOUND == tagtype:
        print('compound {%d}%s =' % (len(tag.compound) - 1, namestr))
        for sub_tag in tag.compound:
            print_tag(sub_tag, indent+1)

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
    # Write the tag type
    file.write(bytes([tag.tagtype]))
    # Now the payload
    write_tag_payload(file, tag)

def write_named_tag (file, tagtype, value, name):
    pass

def write_tag_payload (file, tag):
    tagtype = tag.tagtype
    if TAG_END == tagtype:
        # No payload for TAG_END
        pass
    elif TAG_BYTE == tagtype:
        byte = struct.pack('c', value)
        file.write(byte)
    elif TAG_SHORT == tagtype:
        short = struct.pack('>h', value)
        file.write(short)
    elif TAG_INT == tagtype:
        integer = struct.pack('>i', value)
        file.write(integer)
    elif TAG_LONG == tagtype:
        long_ = struct.pack('>q', value)
        file.write(long_)
    elif TAG_FLOAT == tagtype:
        float_ = struct.pack('>f', value)
        file.write(float_)
    elif TAG_DOUBLE == tagtype:
        double = struct.pack('>d', value)
        file.write(double)
    elif TAG_BYTEARRAY == tagtype:
        # Bytearray: length, bytes[length]
        list_ = bytearray(value)
        length = len(list_)
        write_tag(file, TAG_INT, length)
        file.write(list_)
    elif TAG_STRING == tagtype:
        # String: short length, bytes[length]
        list_ = str.encode(value)
        length = len(list_)
        write_tag(file, TAG_SHORT, length)
        file.write(list_)
    elif TAG_LIST == tagtype: 
        # Write a length encoded list of unnamed tags
        if elementtype is None:
            raise ValueError('elementtype required for %s' % name_tag_type(tagtype))
        list_ = list(value)
        length = len(list_)
        write_tag(file, Tag(TAG_BYTE, byte=elementtype))
        write_tag(file, Tag(TAG_INT, int=length))
        for subtag in tag.list:
            write_tag_payload(file, subtag)
    elif TAG_COMPOUND == tagtype:
        list_ = list(value)
        for named_tag in list_:
            write_named_tag(file, named_tag)
        # Terminate with a TAG_END, which has no value
        write_tag(TAG_END, None)
    else:
        raise ValueError('bad tag type: "%x"' % tagtype)

def read_named_tag (stream, tagtype): 
    if tagtype == TAG_END:
        return Tag(TAG_END)
    name_tag = read_tag(stream, TAG_STRING) 
    the_tag = read_tag(stream, tagtype) 
    the_tag.name = name_tag.string
    return the_tag

class NBTFile:

    def __init__(self, filename):
        self.filename = filename
        with gzip.open(self.filename, 'rb') as f:
            self.data = f.read() 
        self.stream = iter(self.data) 
        if TAG_COMPOUND == next(self.stream):
            self.compound = read_named_tag(self.stream, TAG_COMPOUND)
        else:
            raise ValueError('NBT file doesn\'t start with %s', name_tag_type(TAG_COMPOUND))

