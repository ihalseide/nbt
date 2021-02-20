import nbt 
from nbt import TAG_END, TAG_BYTE, TAG_SHORT, TAG_INT, TAG_LONG, TAG_FLOAT, TAG_DOUBLE, TAG_STRING, TAG_LIST, TAG_BYTEARRAY, TAG_COMPOUND

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
        print('list %s[%d]%s =' % (nbt.name_tag_type(tag.item_type), len(tag.list), namestr))
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
    else:
        raise ValueError('unknown tag type')

if __name__ == '__main__':
    import sys 
    if len(sys.argv) < 2:
        print('Usage:', sys.argv[0], '[filename]')
        sys.exit(-1) 
    filename = sys.argv[1]
    file = nbt.NBTFile(filename)
    print_tag(file.compound) 
