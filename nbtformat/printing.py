from .constants import *
from .full import *

def print_tag(tag: TagPayload | NamedTag, indent=0, indent_str='  ', within_list=False, _name=''): 
    '''Print out an NBT tag and all of its contents in the same way examples are given in the original NBT specification.'''
    if not isinstance(tag, (NamedTag, TagPayload)):
        raise TypeError(f"`tag` is not a `TagPayload` or a `NamedTag`, it is of type '{type(tag)}'")
    
    if isinstance(tag, NamedTag):
        # Unwrap named tag as a name argument
        print_tag(tag.payload, indent, indent_str, within_list, _name=tag.name)
        return

    if tag.tag_kind == TAG_END:
        print(end = indent_str * (indent - 1))
        print(end="}")
        return
    
    # Print type and possibly the tag's name
    print(end = indent_str * indent)
    tag_type_name = tag.kind_name
    if _name and (not within_list):
        print(end=f"{tag_type_name}(\"{_name}\"): ")
    else:
        print(end=f"{tag_type_name}: ")

    # Print the tag data payload
    if tag.tag_kind in (TAG_BYTE, TAG_SHORT, TAG_INT, TAG_LONG):
        print(end=str(tag.val_int))
    elif tag.tag_kind in (TAG_FLOAT, TAG_DOUBLE):
        print(end=str(tag.val_float))
    elif tag.tag_kind == TAG_STRING:
        print(end=f"\"{tag.val_str}\"")
    elif tag.tag_kind == TAG_BYTE_ARRAY:
        if len(tag) > 10:
            print(end=f"[{len(tag)} bytes...]")
        else:
            print(end="[ ")
            for b in tag.val_list:
                print(end = f"{b:02X} ")
            print(end="]")
    elif tag.tag_kind == TAG_LIST:
        inner_type_name = tag_kind_to_str(tag._list_item_kind)
        print(f"{len(tag)} entries of type {inner_type_name} {{")
        for tag_i in tag.val_list:
            print_tag(tag_i, indent = indent + 1, indent_str = indent_str, within_list = True)
        print(end = indent_str * indent)
        print(end="}")
    elif tag.tag_kind == TAG_COMPOUND:
        print(f"{len(tag)} entries {{")
        for tag_name, tag_val in tag.val_comp.items():
            print_tag(tag_val, indent = indent + 1, indent_str = indent_str, _name=tag_name)
        print(end = indent_str * (indent))
        print(end="}")
    elif tag.tag_kind in (TAG_INT_ARRAY, TAG_LONG_ARRAY):
        item_type = 'ints' if tag.tag_kind == TAG_INT_ARRAY else 'longs'
        if len(tag) > 10:
            print(end=f"[{len(tag)} {item_type}...]")
        else:
            print(end=str(tag.val_list))
    else:
        raise TypeError(f"cannot print tag kind {tag.tag_kind}")
    # Newline
    print()
    