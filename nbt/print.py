from .constants import *
from .full import *

def tag_get_print_name(tag_kind: int) -> str:
    return TAG_NAMES[tag_kind]

def print_tag(tag: TagDataABC | NamedTag, indent=0, indent_str='  ', within_list=False, _name=''): 
    '''Print out an NBT tag and all of its contents in a mostly readable format, for debugging.'''
    if isinstance(tag, NamedTag):
        # Unwrap named tag as a name argument
        print_tag(tag.payload, indent, indent_str, within_list, _name=tag.name)
    elif isinstance(tag, TagDataABC):
        if isinstance(tag, TagEnd):
            print(end = indent_str * (indent - 1))
            print(end="}")
            return
        
        # Print type and possibly the tag's name
        print(end = indent_str * indent)
        tag_type_name = tag_get_print_name(tag.kind)
        if _name and not within_list:
            print(end=f"{tag_type_name}(\"{_name}\"): ")
        else:
            print(end=f"{tag_type_name}: ")

        if isinstance(tag, (TagByte, TagShort, TagInt, TagLong, TagFloat, TagDouble)):
            print(end=str(tag.value))
        elif isinstance(tag, TagString):
            print(end=f"\"{tag.value}\"")
        elif isinstance(tag, TagByteArray):
            if tag.element_count > 10:
                print(end=f"[{tag.element_count} bytes]")
            else:
                print(end="[ ")
                for b in tag.value:
                    print(end = f"{b:02X} ")
                print(end="]")
        elif isinstance(tag, TagList):
            inner_type_name = tag_kind_to_str(tag.element_kind_tag.value)
            print(f"{tag.element_count} entries of type {inner_type_name} {{")
            for tag_i in tag.value:
                print_tag(tag_i, indent = indent + 1, indent_str = indent_str, within_list = True)
            print(end = indent_str * indent)
            print(end="}")
        elif isinstance(tag, TagCompound):
            print(f"{tag.element_count} entries {{")
            for tag_j in tag.value:
                print_tag(tag_j, indent = indent + 1, indent_str = indent_str)
        elif isinstance(tag, TagIntArray):
            if tag.element_count > 10:
                print(end=f"[{tag.element_count} ints]")
            else:
                print(end=str(tag.value))
        elif isinstance(tag, TagLongArray):
            if tag.element_count > 10:
                print(end=f"[{tag.element_count} longs]")
            else:
                print(end=str(tag.value))
        else:
            raise TypeError("`tag` sub-type of `TagDataABC` is not implemented for printing")
        # Newline
        print()
    else:
        raise TypeError("`tag` is not a `TagDataABC` or a `NamedTag`")