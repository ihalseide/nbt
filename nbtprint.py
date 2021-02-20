import nbt, sys

if len(sys.argv) < 2:
    print('Usage:', sys.argv[0], '[filename]')
    sys.exit(-1)

filename = sys.argv[1]
file = nbt.NBTFile(filename)
nbt.print_tag(file.compound)

