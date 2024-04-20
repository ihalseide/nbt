from .nbt import *

def print_tag (tag: Tag, indent=0, indent_str='    '): 
    '''Print out an NBT tag and all of its contents, except for TAG_BYTE_ARRAY.'''
    tag_type = tag.kind 
    namestr = tag.get_name_str()
    namestr = f"\"{namestr}\""

    print(indent_str * indent, end='') 

    if TagKind.END == tag_type:
        print('(end)')
        print('    ' * (indent - 1), '}', sep='')
    elif TagKind.BYTE == tag_type:
        print(f"byte {namestr} = {tag.val_int}")
    elif TagKind.SHORT == tag_type:
        print('short %s = %d' % (namestr, tag.val_int))
    elif TagKind.INT == tag_type:
        print('int %s = %d' % (namestr, tag.val_int))
    elif TagKind.LONG == tag_type:
        print('long %s = %d' % (namestr, tag.val_int))
    elif TagKind.FLOAT == tag_type:
        print('float %s = %f' % (namestr, tag.val_float))
    elif TagKind.DOUBLE == tag_type:
        print('double %s = %f' % (namestr, tag.val_float))
    elif TagKind.STRING == tag_type:
        print('string [%d] %s = "%s"' % (tag.get_length(), namestr, tag.val_str))
    elif TagKind.LIST == tag_type:
        print('list %s [%d] %s = {' % (TagKind.to_str(tag.get_item_kind()), tag.get_length(), namestr))
        for sub_tag in tag.val_list:
            print_tag(sub_tag, indent + 1)
        print('    ' * indent, '}', sep='')
    elif TagKind.BYTE_ARRAY == tag_type:
        # Don't print byte arrays because they tend to contain lots of binary data
        print('bytearray [%d] %s = {' % (tag.get_length(), namestr))
        print(', '.join(str(t) for t in tag.val_bytes))
        print(indent_str * indent, '}', sep='')
    elif TagKind.COMPOUND == tag_type:
        print('compound (%d) %s = {' % (len(tag.val_list) - 1, namestr))
        for sub_tag in tag.val_list:
            print_tag(sub_tag, indent + 1)
        print(indent_str * indent, '}', sep='')
    elif TagKind.INT_ARRAY == tag_type:
        print('int array [%d] %s = {' % (tag.get_length(), namestr))
        print(',\n'.join(str(t.val_int) for t in tag.val_list))
        print(indent_str * indent, '}', sep='')
    elif TagKind.LONG_ARRAY == tag_type:
        print('long array [%d] %s = {' % (tag.get_length(), namestr))
        print(',\n'.join(str(t.val_int) for t in tag.val_list))
        print(indent_str * indent, '}', sep='')
    else:
        raise ValueError('unknown tag type')

