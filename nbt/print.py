from .nbt import *

def print_tag (tag, indent=0, indent_str='    '): 
    '''Print out an NBT tag and all of its contents, except for TAG_BYTE_ARRAY.'''
    tag_type = tag.tag_type 
    namestr = (' "%s"' % tag.name.value) if tag.name is not None else ''

    print(indent_str * indent, end='') 

    if TAG_END == tag_type:
        print('(end)')
        print('    ' * (indent - 1), '}', sep='')
    elif TAG_BYTE == tag_type:
        print('byte%s = %d' % (namestr, tag.value))
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
        # Don't print byte arrays because they tend to contain lots of binary data
        print('byte array [%d]%s = { ... }' % (tag.length.value, namestr))
    elif TAG_COMPOUND == tag_type:
        print('compound (%d)%s = {' % (len(tag.value) - 1, namestr))
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

