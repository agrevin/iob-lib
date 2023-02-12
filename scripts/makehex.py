#!/usr/bin/env python3

from sys import argv
import sys


def print_usage():
    usage_str = """
                Usage: ./makehex.py 1st_File 2nd_File 2nd_File_addr ... Firmware_Size > output
                The first file is the main file and its address is 0.
                """
    print(usage_str, file=sys.stderr)

def main():
    print("makehex.py")
    try:
        assert len(argv) % 2 == 1
    except:
        print_usage()
        exit(1)
    nFiles = int((len(argv)-3)/2)+1
    mem_size = 2**(int(argv[-1])) #hex file size
    binfile = [argv[1]] #binary file list
    binaddr = [0] #address list of included binary files
    bindata = [] #data of included binary files
    aux = []

    #create list of files and addresses
    for i in range(nFiles-1):
        try:
            binfile.append(argv[(i+1)*2])
        except:
            print_usage()
            exit(1)
        try:
            binaddr.append(int(argv[(i+1)*2+1], 16))
        except:
            print_usage()
            exit(1)
    #read files and store data continuously
    for i in range(nFiles):
        with open(binfile[i], "rb") as f:
            bindata.append(f.read())
        aux.append(0)

    #add padding to binary file if the size is not a multiple of 4
    for i in range(nFiles):
        while(len(bindata[i]) % 4 != 0):
            bindata[i] += b'0'

    for i in range(nFiles):
        try:
            assert binaddr[i]+len(bindata[i]) <= mem_size
        except:
            print("Error: File {} is too big for the memory size.".format(binfile[i]), file=sys.stderr)
            exit(1)

        try:
            assert (binaddr[i]+len(bindata[i])) % 4 == 0
        except:
            print("Error: File {} has an invalid size.".format(binfile[i]), file=sys.stderr)
            exit(1)

    valid = False
    for i in range(int(mem_size/4)):
        for j in range(nFiles):
            # If using the external memory than adress is 0x80..., but the place in the hex file sould not take into consideration the msb.
            aux[j] = i - int((binaddr[j] & ~(1<<31))/4)
            if (aux[j] < (len(bindata[j])/4)) and (aux[j] >= 0):
                w = bindata[j]
                print('%02x%02x%02x%02x' % (w[4*aux[j]+3], w[4*aux[j]+2], w[4*aux[j]+1], w[4*aux[j]+0]))
                valid = True
                break;
        if not valid:
            print("00000000")
        valid = False

main()
