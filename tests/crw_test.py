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
    'short': TagShort(44),
    'int': TagInt(7),
    'long': TagLong(71),
    'string X': TagString('X value'),
    'float': TagFloat(3.14159),
    'double': TagDouble(3.14159),
    'list': TagList(TAG_DOUBLE, [
        TagDouble(1.0),
    ]),
}))
# </EditMe>

print("x =", x)
print_tag(x)

if do_write:
    print("Writing...")
    with open("small_test.nbt", "wb") as f1:
        x.write_to_file(f1)

if do_read:
    print("Reading...")
    with open("small_test.nbt", "rb") as f2:
        y = NamedTag.read_from_file(f2)

    print("y =", y)
    print_tag(y)