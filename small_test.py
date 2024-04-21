import nbt
from nbt.nbt import *
import gzip

print("creating")
x = NamedTag("small test!", TagCompound([
    NamedTag("a", TagString("string #1")),
    NamedTag("b", TagString("string #2")),
    NamedTag("c", TagString("string #3")),
]))
print(x)

print("writing")
with open("small_test.nbt", "wb") as f:
    x.write_to_file(f)

print("reading")
with open("small_test.nbt", "rb") as f:
    y = NamedTag.read_from_file(f)
print(y)