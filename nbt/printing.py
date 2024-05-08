from .constants import *
from .full import *

def print_tag(tag: TagPayload | NamedTag, indent=0, indent_str='  ', within_list=False, _name=''): 
    '''Print out an NBT tag and all of its contents in the same way examples are given in the original NBT specification.'''
    if isinstance(tag, NamedTag):
        # Unwrap named tag as a name argument
        print_tag(tag.payload, indent, indent_str, within_list, _name=tag.name)
    elif isinstance(tag, TagPayload):
        if tag.tag_kind == TAG_END:
            print(end = indent_str * (indent - 1))
            print(end="}")
            return
        
        # Print type and possibly the tag's name
        print(end = indent_str * indent)
        tag_type_name = tag.kind_name
        if _name and not within_list:
            print(end=f"{tag_type_name}(\"{_name}\"): ")
        else:
            print(end=f"{tag_type_name}: ")

        # Print the tag data payload
        if tag.tag_kind in (TAG_BYTE, TAG_SHORT, TAG_INT, TAG_LONG, TAG_FLOAT, TAG_DOUBLE):
            print(end=str(tag.value))
        elif tag.tag_kind == TAG_STRING:
            print(end=f"\"{tag.value}\"")
        elif tag.tag_kind == TAG_BYTE_ARRAY:
            if len(tag) > 10:
                print(end=f"[{len(tag)} bytes]")
            else:
                print(end="[ ")
                for b in tag.value:
                    print(end = f"{b:02X} ")
                print(end="]")
        elif tag.tag_kind == TAG_LIST:
            inner_type_name = tag_kind_to_str(tag._list_item_kind)
            print(f"{len(tag)} entries of type {inner_type_name} {{")
            for tag_i in tag.value:
                print_tag(tag_i, indent = indent + 1, indent_str = indent_str, within_list = True)
            print(end = indent_str * indent)
            print(end="}")
        elif tag.tag_kind == TAG_COMPOUND:
            print(f"{len(tag)} entries {{")
            for tag_j in tag.value:
                print_tag(tag_j, indent = indent + 1, indent_str = indent_str)
            print(end = indent_str * (indent))
            print(end="}")
        elif tag.tag_kind == TAG_INT_ARRAY:
            if len(tag) > 10:
                print(end=f"[{len(tag)} ints]")
            else:
                print(end=str(tag.value))
        elif tag.tag_kind == TAG_LONG_ARRAY:
            if len(tag) > 10:
                print(end=f"[{len(tag)} longs]")
            else:
                print(end=str(tag.value))
        else:
            raise TypeError("`tag` sub-type of `TagDataABC` is not implemented for printing")
        # Newline
        print()
    else:
        raise TypeError(f"`tag` is not a `TagPayload` or a `NamedTag`, it is of type '{type(tag)}'")