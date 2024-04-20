#!/usr/bin/env python3

if __name__ == '__main__':
    import nbt, sys, gzip

    if len(sys.argv) != 3:
        print('Usage:', sys.argv[0], '[input filename]' '[output filename]')
        sys.exit(-1) 

    filename_in = sys.argv[1]
    filename_out = sys.argv[2]

    data = nbt.NBTFile(filename_in)

    # .bin file is uncompressed
    with open('%s.bin' % filename_out, 'wb') as outfile:
        nbt.write_named_tag(outfile, data.nbt)

    # nbt file is compressed with gzip
    with gzip.open(filename_out, 'wb') as outfile:
        nbt.write_named_tag(outfile, data.nbt)
