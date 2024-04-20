from .nbt import *

def print_tag(tag: Tag, indent=0, indent_str='    ', within_list=False): 
    '''Print out an NBT tag and all of its contents, except for TAG_BYTE_ARRAY.'''
    tag_type = tag.kind 
    namestr = tag.get_name_str()
    if namestr:
        namestr = f"\"{namestr}\""

    # Indent the line
    print(indent_str * indent, end='') 

    if TagKind.END == tag_type:
        print('(end)')
        print('    ' * (indent - 1), '}', sep='')
    elif TagKind.BYTE == tag_type:
        print(end="byte")
        if not within_list: print(end=f" {namestr} =")
        print(f" {tag.val_int}")
    elif TagKind.SHORT == tag_type:
        print(end="short")
        if not within_list: print(end=f" {namestr} =")
        print(f" {tag.val_int}")
    elif TagKind.INT == tag_type:
        print(end="int")
        if not within_list: print(end=f" {namestr} =")
        print(f" {tag.val_int}")
    elif TagKind.LONG == tag_type:
        print(end="long")
        if not within_list: print(end=f" {namestr} =")
        print(f" {tag.val_int}")
    elif TagKind.FLOAT == tag_type:
        print(end="float")
        if not within_list: print(end=f" {namestr} =")
        print(f" {tag.val_float}")
    elif TagKind.DOUBLE == tag_type:
        print(end="double")
        if not within_list: print(end=f" {namestr} =")
        print(f" {tag.val_float}")
    elif TagKind.STRING == tag_type:
        print(end=f"string [{tag.get_length()}]")
        if not within_list: print(end=f" {namestr} =")
        print(f" \"{tag.val_str}\"")
    elif TagKind.LIST == tag_type:
        element_kind = TagKind.to_str(tag.get_item_kind())[4:]
        element_count = tag.get_length()
        print(end=f"list<{element_kind}> [{element_count}]")
        print(f" {namestr} = ""{")
        for sub_tag in tag.val_list:
            print_tag(sub_tag, indent + 1, within_list=True)
        print(indent_str * indent, '}', sep='')
    elif TagKind.BYTE_ARRAY == tag_type:
        length = tag.get_length()
        row_width = 20
        print(end=f"byte_array [{length}]")
        if not within_list: print(end=f" {namestr} =")
        print(" {")
        print(indent_str * (indent + 1), end='') 
        for i, b in enumerate(tag.val_bytes):
            print(str(b), end=' ')
            if (i > 0) and (i % row_width == 0) and (i != len(tag.val_bytes) - 1):
                print()
                print(indent_str * (indent + 1), end='') 
        print()
        print(indent_str * indent, '}', sep='')
    elif TagKind.COMPOUND == tag_type:
        print(end="compound")
        if not within_list: print(end=f" {namestr} =")
        print(" {")                          
        for sub_tag in tag.val_list:
            print_tag(sub_tag, indent + 1)
        # Ending gets printed by TAG_END
        #print(indent_str * indent, '}', sep='')
    elif TagKind.INT_ARRAY == tag_type:
        print(end=f"int_array [{tag.get_length()}]")
        if not within_list: print(end=f" {namestr} =")
        print(" {")  
        print(',\n'.join(str(t.val_int) for t in tag.val_list))
        print(indent_str * indent, '}', sep='')
    elif TagKind.LONG_ARRAY == tag_type:
        print(end=f"long_array [{tag.get_length()}]")
        if not within_list: print(end=f" {namestr} =")
        print(" {") 
        print(',\n'.join(str(t.val_int) for t in tag.val_list))
        print(indent_str * indent, '}', sep='')
    else:
        raise ValueError('unknown tag type')

