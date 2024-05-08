from nbt import NamedTag, TagCompound, TagFloat, TagDouble
from nbt.printing import print_tag

# Create a NBT tag from scratch
x = NamedTag("Position data", TagCompound({
    "x": TagFloat(3.0),
    "y": TagFloat(-12.43),
    "z": TagDouble(88.31),
}))

# Write NBT compound tag to a file
with open("example 1.nbt", "wb") as f_out:
    x.write_to_file(f_out)
    # Print NBT data in a readable form
    print_tag(x)