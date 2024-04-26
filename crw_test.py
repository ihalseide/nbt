'''
Create-read-write test.
'''

import nbt
import gzip
from nbt import NamedTag, TagCompound, TagString
from nbt import print_tag

print("Creating...")
x = NamedTag("root", TagCompound([
    
]))
print("x =", x)
print_tag(x)

print("Writing...")
with open("small_test.nbt", "wb") as f1:
    x.write_to_file(f1)
del x

print("Reading...")
with open("small_test.nbt", "rb") as f2:
    y = NamedTag.read_from_file(f2)
print("y =", y)
print_tag(y)