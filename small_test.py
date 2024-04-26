import nbt
from nbt.nbt import *

print("Creating...")
x = NamedTag("small test!", TagCompound([
    NamedTag("a", TagString("string #1")),
    NamedTag("b", TagString("string #2")),
    NamedTag("c", TagList(TAG_INT, [
        TagInt(42),
        TagInt(70),
        TagInt(-12),
    ])),
]))
print("x =", x)
nbt.print_tag(x)

print("Writing...")
with open("small_test.nbt", "wb") as f1:
    x.write_to_file(f1)
del x

print("Reading...")
with open("small_test.nbt", "rb") as f2:
    y = NamedTag.read_from_file(f2)
print("y =", y)
nbt.print_tag(y)