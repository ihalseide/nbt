'''
Create-read-write test for the nbt module.
'''

from nbt import *
from nbt.printing import print_tag

do_read = True
do_write = True

print("Creating...")
# <EditMe>
# test whatever for the value of x
x = NamedTag("root", TagCompound({
    'byte': TagByte(-12),
    'string X': TagString('X value'),
    'short': TagShort(44),
    'int': TagInt(7),
    'long': TagLong(71),
    'double': TagDouble(3.14159),
    'list': TagList(TagDouble, [
        TagDouble(1.0),
    ])
}))
# </EditMe>

print("x =", x.value)
print_tag(x)

if do_write:
    print("Writing...")
    with open("small_test.nbt", "wb") as f1:
        x.write_to_file(f1)

if do_read:
    print("Reading...")
    with open("small_test.nbt", "rb") as f2:
        y = NamedTag.read_from_file(f2)

    print("y =", y.value)
    print_tag(y)