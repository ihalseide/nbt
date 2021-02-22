import gzip, sys, struct

TAG_NAMES = [
    'TAG_end',
    'TAG_byte',
    'TAG_short',
    'TAG_int',
    'TAG_long',
    'TAG_float',
    'TAG_double',
    'TAG_byte_array',
    'TAG_string',
    'TAG_list',
    'TAG_compound',
    'TAG_int_array',
    'TAG_long_array',
]

(TAG_END,
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
TAG_LONG_ARRAY) = ALL_TAGS = range(len(TAG_NAMES))

def name_tag_type (tag_type):
    try:
        return TAG_NAMES[tag_type]
    except (IndexError, TypeError):
        raise ValueError('unknown tag type')

def is_list_tag_type (tag_type):
    return tag_type in (TAG_BYTE_ARRAY, TAG_STRING, TAG_LIST,
                        TAG_COMPOUND, TAG_INT_ARRAY, TAG_LONG_ARRAY)

def is_atom_tag_type (tag_type):
    return tag_type in (TAG_BYTE, TAG_SHORT, TAG_INT,
                        TAG_LONG, TAG_FLOAT, TAG_DOUBLE)

class Tag: 
    def __init__ (self, tag_type, name=None):
        self.tag_type = tag_type
        # Name is a TAG_STRING
        self.name = name
        # Data will be the correct type based on self.tag_type
        self.value = None
        # Only used for list, string, bytearray, int_array, and long_array
        self.length = None
        # Only used for list
        self.item_type = None

    def __getitem__ (self, key):
        if type(key) == int:
            # A non-compound list type index access
            if is_list_tag_type(self.tag_type):
                return self.value[key]
            else:
                raise ValueError('NBT tag must be a list type in order to get an item at an index')
        elif type(key) == str:
            if TAG_COMPOUND == self.tag_type:
                if type(key) != str:
                    raise TypeError('key must be an instance of str')
                if self.name.value == key:
                    return self
                for tag in self.value:
                    # Ignore end tags
                    if tag.tag_type == TAG_END:
                        continue
                    # Find named tags
                    if tag.name.value == key:
                        return tag 
                    # Recursively search the nested compound tags
                    if tag.tag_type == TAG_COMPOUND:
                        try:
                            return tag[key]
                        except KeyError:
                            continue
                raise KeyError()
            elif TAG_LIST == self.tag_type and self.item_type.value == TAG_COMPOUND:
                # List of compound tags
                for tag in self.value:
                    try:
                        return tag[key]
                    except KeyError:
                        continue
                raise KeyError()
            else:
                raise ValueError('NBT tag must be a TAG_COMPOUND or a TAG_LIST of TAG_COMPOUNDs to search for a str')
        else:
            raise TypeError('key must be an int or a str')

    def __setitem__ (self, key, value):
        pass

    def __repr__ (self):
        try:
            typename = name_tag_type(self.tag_type)
        except ValueError:
            return '<Unknown Tag %s>' % str(self.tag_type)

        result = '<Tag (%s' % typename

        if self.name is not None:
            result += ' name="%s"' % self.name.value

        if self.length is not None:
            result += ' length=%d' % self.length.value 
            # Item type only exists if length does too
            if self.item_type is not None:
                result += ' item_type=%s' % name_tag_type(self.item_type.value)

        result += ')>'
        return result

    def __bytes__ (self):
        tag_type = self.tag_type
        if TAG_END == tag_type: 
            return bytes()
        elif TAG_BYTE == tag_type:
            return struct.pack('>c', self.value)
        elif TAG_SHORT == tag_type:
            return struct.pack('>h', self.value)
        elif TAG_INT == tag_type:
            return struct.pack('>i', self.value)
        elif TAG_LONG == tag_type:
            return struct.pack('>q', self.value)
        elif TAG_FLOAT == tag_type:
            return struct.pack('>f', self.value)
        elif TAG_DOUBLE == tag_type:
            return struct.pack('>d', self.value)
        elif TAG_BYTE_ARRAY == tag_type:
            return bytes(self.length) + bytes(self.value)
        elif TAG_STRING == tag_type:
            return bytes(self.length) + bytes(self.value, 'utf-8')
        elif TAG_LIST == tag_type: 
            # Write a length encoded list of unnamed tags
            item_type = bytes(self.item_type.value)
            length = bytes(self.length)
            items_bytes = bytearray()
            for item in self.value:
                items_bytes += bytes(item)
            return bytes(item_type + length + items_bytes)
        elif TAG_COMPOUND == tag_type:
            items_bytes = bytearray()
            for item in self.value:
                # These are named tags, except for TAG_END
                items_bytes += bytes((item.tag_type,))
                if TAG_END != item.tag_type:
                    items_bytes += bytes(item.name)
                items_bytes += bytes(item)
            return bytes(items_bytes)
        elif tag_type in (TAG_LONG_ARRAY, TAG_INT_ARRAY):
            # TAG_LONG_ARRAY and TAG_INT_ARRAY both have the same pattern
            items_bytes = bytearray()
            items_bytes.append(bytes(self.length))
            for t in self.items:
                items_bytes += bytes(t)
            return bytes(items_bytes)
        else:
            raise ValueError('unknown tag type')

class NBTFile: 
    def __init__(self, filename):
        # Unzip the file
        self.filename = filename
        with gzip.open(self.filename, 'rb') as file:
            # Read the root TAG_COMPOUND tag
            toplevel = read_named_tag(file)
            if TAG_COMPOUND == toplevel.tag_type:
                self.compound = toplevel
            else:
                expected = name_tag_type(TAG_COMPOUND)
                found = name_tag_type(self.compound.tag_type)
                raise ValueError('a NBT file must start with a "%s" but begins with a "%s" instead' %(expected, found)) 

    def __repr__ (self):
        return '<NBTFile(filename="%s")>' % self.filename

    def __getitem__ (self, name):
        if type(name) != str:
            raise TypeError('name must be a instance of str')
        return self.compound[name]

    def __setitem__ (self, name, value):
        if type(name) != str:
            raise TypeError('name must be a instance of str')
        if type(value) != Tag:
            raise TypeError('value must be an instance of %s' %str(Tag))
        self.compound[name] = value

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
        pass
    elif TAG_BYTE == tag_type:
        # 1 byte
        tag.value = file.read(1)[0]
    elif TAG_SHORT == tag_type:
        # 2 byte short
        tag.value = struct.unpack('>h', file.read(2))[0]
    elif TAG_INT == tag_type:
        # 4 byte integer
        tag.value = struct.unpack('>i', file.read(4))[0]
    elif TAG_LONG == tag_type:
        # 8 byte long
        tag.value = struct.unpack('>q', file.read(8))[0]
    elif TAG_FLOAT == tag_type:
        # 4 byte float
        tag.value = struct.unpack('>f', file.read(4))[0]
    elif TAG_DOUBLE == tag_type:
        # 8 byte double
        tag.value = struct.unpack('>d', file.read(8))[0]
    elif TAG_BYTE_ARRAY == tag_type:
        # Read a length encoded bytearray
        tag.length = read_tag(file, TAG_INT)
        tag.value = file.read(tag.length.value)
    elif TAG_STRING == tag_type:
        # Read a length encoded string
        tag.length = read_tag(file, TAG_SHORT)
        tag.value = str(file.read(tag.length.value), 'utf-8') 
    elif TAG_LIST == tag_type: 
        # Read a length encoded list of unnamed tags
        tag.item_type = read_tag(file, TAG_BYTE)
        tag.length = read_tag(file, TAG_INT)
        tag.value = [read_tag(file, tag.item_type.value) for x in range(tag.length.value)]
    elif TAG_COMPOUND == tag_type:
        # Read a bunch of named tags until TAG_END
        compound = []
        item = 'start'
        while (item == 'start') or (item.tag_type != TAG_END):
            item = read_named_tag(file)
            compound.append(item)
        tag.value = compound
        # Add an extra length tag for consistency with the other list-like tags
        tag.length = Tag(TAG_INT)
        tag.length.value = len(compound)
    elif TAG_INT_ARRAY == tag_type:
        # Read int length, and then int[length]
        tag.length = read_tag(file, TAG_INT)
        tag.value = [read_tag(file, TAG_INT) for x in range(tag.length)]
    elif TAG_LONG_ARRAY == tag_type:
        # Read int length, and then long[length]
        tag.length = read_tag(file, TAG_INT)
        tag.value = [read_tag(file, TAG_LONG) for x in range(tag.length)]
    else:
        raise ValueError('unknown tag type: %s' % tag_type)
    return tag

def write_named_tag (file, tag):
    # Write tag type
    file.write(bytes(tag.tag_type))
    # Write name, but TAG_END cannot be named
    if TAG_END != tag.tag_type:
        write_tag(file, tag.name)
    # Write payload
    write_tag(file, tag)

def write_tag (file, tag):
    file.write(bytes(tag))

def print_tag (tag, indent=0, indent_str='    ', bytearraysize=64): 
    tag_type = tag.tag_type 
    namestr = ' "%s"' %(tag.name.value if tag.name is not None else '')

    print(indent_str * indent, end='') 
    if TAG_END == tag_type:
        print('end')
        print('    ' * (indent - 1), '}', sep='')
    elif TAG_BYTE == tag_type:
        print('byte%s = %X' % (namestr, int(tag.value)))
    elif TAG_SHORT == tag_type:
        print('short%s = %d' % (namestr, tag.value))
    elif TAG_INT == tag_type:
        print('int%s = %d' % (namestr, tag.value))
    elif TAG_LONG == tag_type:
        print('long%s = %d' % (namestr, tag.value))
    elif TAG_FLOAT == tag_type:
        print('float%s = %f' % (namestr, tag.value))
    elif TAG_DOUBLE == tag_type:
        print('double%s = %f' % (namestr, tag.value))
    elif TAG_STRING == tag_type:
        print('string [%d]%s = "%s"' % (tag.length.value, namestr, tag.value))
    elif TAG_LIST == tag_type:
        print('list %s[%d]%s = {' % (name_tag_type(tag.item_type.tag_type), tag.length.value, namestr))
        for sub_tag in tag.value:
            print_tag(sub_tag, indent + 1)
        print('    ' * indent, '}', sep='')
    elif TAG_BYTE_ARRAY == tag_type:
        print('byte array [%d]%s = {' % (tag.length.value, namestr))
        hex_stream = iter(tag.value.hex().upper())
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
        print('compound {%d}%s = {' % (len(tag.value) - 1, namestr))
        for sub_tag in tag.value:
            print_tag(sub_tag, indent + 1)
    elif TAG_INT_ARRAY == tag_type:
        print('int array [%d]%s = {' % (tag.length.value, namestr))
        print(',\n'.join(str(t.value) for t in tag.value))
        print(indent_str * indent, '}', sep='')
    elif TAG_LONG_ARRAY == tag_type:
        print('long array [%d]%s = {' % (tag.length.value, namestr))
        print(',\n'.join(str(t.value) for t in tag.value))
        print(indent_str * indent, '}', sep='')
    else:
        raise ValueError('unknown tag type')

