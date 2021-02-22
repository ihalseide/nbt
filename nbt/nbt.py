import gzip, sys, struct

# Note on tag types:
# TAG_INT_ARRAY and TAG_LONG_ARRAY were added after Notch's original specification

# Tag types and names 
TAG_NAMES = [
    'TAG_END',
    'TAG_BYTE',
    'TAG_SHORT',
    'TAG_INT',
    'TAG_LONG',
    'TAG_FLOAT',
    'TAG_DOUBLE',
    'TAG_BYTE_ARRAY',
    'TAG_STRING',
    'TAG_LIST',
    'TAG_COMPOUND',
    'TAG_INT_ARRAY',
    'TAG_LONG_ARRAY',
]

ALL_TAGS = (TAG_END,
TAG_BYTE,
TAG_SHORT,
TAG_INT,
TAG_LONG,
TAG_FLOAT,     
TAG_DOUBLE,     
TAG_BYTE_ARRAY, 
TAG_STRING,     
TAG_LIST,       
TAG_COMPOUND,   
TAG_INT_ARRAY,  
TAG_LONG_ARRAY) = range(len(TAG_NAMES))

def name_tag_type (tag_type):
    try:
        return TAG_NAMES[tag_type]
    except (IndexError, TypeError):
        raise ValueError('unknown tag type')

class Tag: 
    def __init__ (self, tag_type, name=None):
        self.tag_type = tag_type
        # Name is a TAG_STRING
        self.name = name
        # Data will be the correct type based on self.tag_type
        self.data = None
        # Only used for list, string, bytearray, int_array, and long_array
        self.length = None
        # Only used for list
        self.item_type = None

    def __repr__ (self):
        try:
            typename = name_tag_type(self.tag_type)
        except ValueError:
            typename = 'unknown'
        if self.name is None:
            return '<Tag(%s)>' % (typename)
        else:
            return '<Tag(%s, name="%s")>' % (typename, str(self.name.data))

class NBTFile: 
    def __init__(self, filename):
        # Unzip the file
        self.filename = filename
        with gzip.open(self.filename, 'rb') as file:
            # Read the root TAG_COMPOUND tag
            self.compound = read_named_tag(file)
            if TAG_COMPOUND != self.compound.tag_type:
                expected = name_tag_type(TAG_COMPOUND)
                found = name_tag_type(self.compound.tag_type)
                raise ValueError('a NBT file must start with a "%s" but begins with a "%s" instead' %(expected, found)) 

def read_named_tag (file): 
    tag_type = file.read(1)[0]
    if tag_type == TAG_END:
        # TAG_END is an exception to the rule and cannot be named
        return Tag(TAG_END)
    name = read_tag(file, TAG_STRING) 
    tag = read_tag(file, tag_type) 
    tag.name = name
    return tag

def read_tag (file, tag_type):
    tag = Tag(tag_type)
    if TAG_END == tag_type:
        # TAG_END has no payload to read
        tag.data = None
    elif TAG_BYTE == tag_type:
        tag.data = file.read(1)
    elif TAG_SHORT == tag_type:
        tag.data = struct.unpack('>h', file.read(2))[0]
    elif TAG_INT == tag_type:
        tag.data = struct.unpack('>i', file.read(4))[0]
    elif TAG_LONG == tag_type:
        tag.data = struct.unpack('>q', file.read(8))[0]
    elif TAG_FLOAT == tag_type:
        tag.data = struct.unpack('>f', file.read(4))[0]
    elif TAG_DOUBLE == tag_type:
        tag.data = struct.unpack('>d', file.read(8))[0]
    elif TAG_BYTE_ARRAY == tag_type:
        # Read a length encoded bytearray
        tag.length = read_tag(file, TAG_INT)
        tag.data = file.read(tag.length.data)
    elif TAG_STRING == tag_type:
        # Read a length encoded string
        tag.length = read_tag(file, TAG_SHORT)
        tag.data = str(file.read(tag.length.data), 'utf-8') 
    elif TAG_LIST == tag_type: 
        # Read a length encoded list of unnamed tags
        tag.item_type = read_tag(file, TAG_BYTE)
        tag.length = read_tag(file, TAG_INT)
        tag.data = [read_tag(file, tag.item_type.data[0]) for x in range(tag.length.data)]
    elif TAG_COMPOUND == tag_type:
        # Read a bunch of named tags until TAG_END
        compound = []
        item = 'start'
        while (item == 'start') or (item.tag_type != TAG_END):
            item = read_named_tag(file)
            compound.append(item)
        tag.data = compound
    elif TAG_INT_ARRAY == tag_type:
        # Read int length, and then int[length]
        tag.length = read_tag(file, TAG_INT)
        tag.data = [read_tag(file, TAG_INT) for x in range(tag.length)]
    elif TAG_LONG_ARRAY == tag_type:
        # Read int length, and then long[length]
        tag.length = read_tag(file, TAG_INT)
        tag.data = [read_tag(file, TAG_LONG) for x in range(tag.length)]
    else:
        raise ValueError('unknown tag type: %s' % tag_type)
    return tag

def write_named_tag (file, tag):
    # Write tag type
    file.write(bytes((tag.tag_type,)))
    # Write name
    if TAG_END != tag.tag_type:
        # TAG_END cannot be named
        write_tag(file, tag.name)
    # Write payload
    write_tag(file, tag)

def write_tag (file, tag):
    tag_type = tag.tag_type
    if TAG_END == tag_type:
        # TAG_END has no payload to write
        pass 
    elif TAG_BYTE == tag_type:
        byte = struct.pack('>c', tag.data)
        file.write(byte)
    elif TAG_SHORT == tag_type:
        short = struct.pack('>h', tag.data)
        file.write(short)
    elif TAG_INT == tag_type:
        integer = struct.pack('>i', tag.data)
        file.write(integer)
    elif TAG_LONG == tag_type:
        long_ = struct.pack('>q', tag.data)
        file.write(long_)
    elif TAG_FLOAT == tag_type:
        float_ = struct.pack('>f', tag.data)
        file.write(float_)
    elif TAG_DOUBLE == tag_type:
        double = struct.pack('>d', tag.data)
        file.write(double)
    elif TAG_BYTE_ARRAY == tag_type:
        # Bytearray: int length, bytes[length]
        write_tag(file, tag.length)
        file.write(tag.data)
    elif TAG_STRING == tag_type:
        # String: short length, bytes[length]
        write_tag(file, tag.length)
        file.write(str.encode(tag.data, 'utf-8'))
    elif TAG_LIST == tag_type: 
        # Write a length encoded list of unnamed tags
        write_tag(file, tag.item_type)
        write_tag(file, tag.length)
        for item in tag.data:
            write_tag(file, item)
    elif TAG_COMPOUND == tag_type:
        # Write all named subtags
        item = None
        for item in tag.data:
            write_named_tag(file, item)
        # Add a TAG_END if the compound didn't end with it already
        # because TAG_COMPOUND must end with TAG_END
        if item.tag_type != TAG_END:
            write_named_tag(file, Tag(TAG_END))
    elif TAG_INT_ARRAY == tag_type:
        # Bytearray: int length, bytes[length]
        write_tag(file, tag.length)
        for int_tag in tag.data:
            write_tag(file, int_tag)
    elif TAG_LONG_ARRAY == tag_type:
        # Bytearray: int length, bytes[length]
        write_tag(file, tag.length)
        for long_tag in tag.data:
            write_tag(file, long_tag)
    else:
        raise ValueError('unknown tag type')

def print_tag (tag, indent=0, indent_str='    ', bytearraysize=64): 
    tag_type = tag.tag_type 
    namestr = ' "%s"' %(tag.name.data if tag.name is not None else '')

    print(indent_str * indent, end='') 
    if TAG_END == tag_type:
        print('end')
        print('    ' * (indent - 1), '}', sep='')
    elif TAG_BYTE == tag_type:
        print('byte%s = %X' % (namestr, int(tag.data[0])))
    elif TAG_SHORT == tag_type:
        print('short%s = %d' % (namestr, tag.data))
    elif TAG_INT == tag_type:
        print('int%s = %d' % (namestr, tag.data))
    elif TAG_LONG == tag_type:
        print('long%s = %d' % (namestr, tag.data))
    elif TAG_FLOAT == tag_type:
        print('float%s = %f' % (namestr, tag.data))
    elif TAG_DOUBLE == tag_type:
        print('double%s = %f' % (namestr, tag.data))
    elif TAG_STRING == tag_type:
        print('string [%d]%s = "%s"' % (tag.length.data, namestr, tag.data))
    elif TAG_LIST == tag_type:
        print('list %s[%d]%s = {' % (name_tag_type(tag.item_type.tag_type), tag.length.data, namestr))
        for sub_tag in tag.data:
            print_tag(sub_tag, indent + 1)
        print('    ' * indent, '}', sep='')
    elif TAG_BYTE_ARRAY == tag_type:
        print('byte array [%d]%s = {' % (tag.length.data, namestr))
        hex_stream = iter(tag.data.hex().upper())
        i = 1
        print(end=indent_str * (indent + 1)) 
        while char := next(hex_stream, None):
            print(end=char)
            if i > (bytearraysize - 1):
                print()
                print(end='    ' * (indent + 1)) 
                i = 0
            i += 1
        print()
        print(indent_str * indent, '}', sep='')
    elif TAG_COMPOUND == tag_type:
        print('compound {%d}%s = {' % (len(tag.data) - 1, namestr))
        for sub_tag in tag.data:
            print_tag(sub_tag, indent + 1)
    elif TAG_INT_ARRAY == tag_type:
        print('int array [%d]%s = {' % (tag.length.data, namestr))
        print(',\n'.join(str(t.data) for t in tag.data))
        print(indent_str * indent, '}', sep='')
    elif TAG_LONG_ARRAY == tag_type:
        print('long array [%d]%s = {' % (tag.length.data, namestr))
        print(',\n'.join(str(t.data) for t in tag.data))
        print(indent_str * indent, '}', sep='')
    else:
        raise ValueError('unknown tag type')

