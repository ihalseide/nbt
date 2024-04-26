#!/usr/bin/env python3

import gzip, sys
import nbt

# Get argument
if len(sys.argv) != 2:
    print('usage:', sys.argv[0], 'filename')
    sys.exit(1)
filename = sys.argv[1]

try:
    try:
        # Try the file as a compressed file
        with gzip.open(filename, "rb") as f1:
            data1 = nbt.NamedTag.read_from_file(f1)
            nbt.print_tag(data1)
    except gzip.BadGzipFile:
        # Try the file as uncompressed file
        print(f"WARNING: the file \"{filename}\" is not a gzipped file. Now trying to read the file as uncompressed...")
        with open(filename, "rb") as f2:
            data2 = nbt.NamedTag.read_from_file(f2)
            nbt.print_tag(data2)
except FileNotFoundError as e:
    print(e)
