'''
Create-read-write test for the nbt module.
'''

import nbt
import gzip
from nbt import NamedTag, TagCompound, TagString, TagShort
from nbt.printing import print_tag

do_read = True
do_write = True

print("Creating...")
# <EditMe>
# test whatever for the value of x
x = NamedTag("root", TagCompound({
    'x': TagString('X value'),
    'short value lol': TagShort(555555)
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