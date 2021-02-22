#!/usr/bin/env python3

import nbt

if __name__ == '__main__':
    import sys 
    if len(sys.argv) != 2:
        print('Usage:', sys.argv[0], '<filename>', file=sys.stderr)
        sys.exit(-1) 
    filename = sys.argv[1]
    data = nbt.NBTFile(filename)
    nbt.print_tag(data.compound) 
