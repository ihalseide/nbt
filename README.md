# nbt-explorer

Python libary for working with Named Binary Tag (NBT) files and data structures.

## Named Binary Tags

For the specification for NBT, see the file "Named Binary Tags.txt", which is taken from Markus Perrson's [original specification](https://web.archive.org/web/20110723210920/http://www.minecraft.net/docs/NBT.txt).

## Example usage

```python
from nbt import NamedTag, TagCompound, TagFloat
x = NamedTag("Position data", TagCompound([
    NamedTag("x", TagFloat(3.0)),
    NamedTag("y", TagFloat(-12.43)),
    NamedTag("z", TagFloat(88.31)),
]))
```