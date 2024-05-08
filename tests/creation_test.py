from nbt import *

x = NamedTag("Creation TEST", TagCompound({
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

with open("CreationTest.NBT", "wb") as f1:
    x.write_to_file(f1)