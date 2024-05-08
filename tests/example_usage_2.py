from nbt import NamedTag
from nbt.printing import print_tag

# Read a NBT tag from a file (assuming file "example 1.nbt" already exists and is not gzipped)
with open("example 1.nbt", "rb") as f_in:
    y = NamedTag.read_from_file(f_in)
    # Print NBT data in a readable form
    print_tag(y)