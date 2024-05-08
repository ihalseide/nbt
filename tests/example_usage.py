from nbt import NamedTag, TagCompound, TagFloat
from nbt.printing import print_tag

# Create a NBT tag from scratch
x = NamedTag("Position data", TagCompound({
    "x": TagFloat(3.0),
    "y": TagFloat(-12.43),
    "z": TagFloat(88.31),
}))

# Write NBT compound tag to a file
with open("example 1.nbt", "wb") as f_out:
    x.write_to_file(f_out)
    # Print NBT data in a readable form
    print_tag(x)

# Read a NBT tag from a file (assuming file "example 2.nbt" exists and is not gzipped)
with open("example 2.nbt", "rb") as f_in:
    y = NamedTag.read_from_file(f_in)
    # Print NBT data in a readable form
    print_tag(y)