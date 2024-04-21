from .nbt import *

def tag_get_print_name(tag_kind: int) -> str:
    kind_str = TAG_NAMES[tag_kind]
    return kind_str[:5].upper() + kind_str[5:]

def print_tag(tag: TagDataABC | NamedTag, indent=0, indent_str='  ', within_list=False): 
    '''Print out an NBT tag and all of its contents in a mostly readable format.'''
    raise NotImplementedError()