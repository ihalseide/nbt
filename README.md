# nbt

This is a Python libary for working with Named Binary Tag (NBT) files and data structures.

## Named Binary Tags

For the specification for NBT, see the file "Named Binary Tags.txt", which is taken from Markus Perrson's [original specification](https://web.archive.org/web/20110723210920/http://www.minecraft.net/docs/NBT.txt).

## Example usage

```python
from nbt import NamedTag, TagCompound, TagFloat, print_tag

# Create a NBT tag from scratch
x = NamedTag("Position data", TagCompound([
    NamedTag("x", TagFloat(3.0)),
    NamedTag("y", TagFloat(-12.43)),
    NamedTag("z", TagFloat(88.31)),
]))

# Write NBT compound tag to a file
with open("example 1.nbt", "wb") as f_out:
    x.write_to_file(f_out)

# Read a NBT tag from a file (assuming it is not gzipped)
with open("example 2.nbt", "rb") as f_in:
    y = NamedTag.read_from_file(f_in)

# Print NBT data in a readable form
print_tag(y)
```