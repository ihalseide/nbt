#!/usr/bin/env python3

import gzip, sys
import nbt, nbt.printing

# Get argument
if len(sys.argv) != 2:
    print(f"usage: {sys.argv[0]} filename")
    sys.exit(1)
filename = sys.argv[1]

try:
    try:
        # Try the file as a compressed file
        with gzip.open(filename, "rb") as f1:
            tag1 = nbt.NamedTag.read_from_file(f1)
            nbt.printing.print_tag(tag1)
    except gzip.BadGzipFile:
        # Try the file as uncompressed file
        print(f"[WARNING]: the file \"{filename}\" is not a gzipped file. Now trying to read the file as uncompressed...")
        with open(filename, "rb") as f2:
            tag2 = nbt.NamedTag.read_from_file(f2)
            nbt.printing.print_tag(tag2)
    exit(0)
except FileNotFoundError as e:
    print(e)
    exit(1)
