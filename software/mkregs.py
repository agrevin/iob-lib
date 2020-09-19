#!/usr/bin/python2.7
#
#    Build Latex tables of verilog module interface signals and registers
#

import sys
import os.path
import re

def write_mapping(name_map, width_map, init_val_map, type_map):
    #write output file
    fout = open ('sw_reg_gen.v', 'w')

    fout.write("//This file was generated by script swreg2regmap.py\n\n")

    fout.write("//write registers\n")
    for i in range(len(name_map)):
        if (type_map[i] == "`W_TYP" or type_map[i] == "`RW_TYP"):
            fout.write("`REG_ARE(clk, rst, valid & wstrb & (address == " + str(i) + "), " + str(init_val_map[i]) + ", " + str(name_map[i]) + ", wdata[" + str(width_map[i]) + "-1:0])\n")
            pass
        pass
        
    fout.write("\n\n//read registers\n")
    fout.write("`SIGNAL(rdata_int,`DATA_W)\n")
    fout.write("`SIGNAL2OUT(rdata, rdata_int)\n\n")

    fout.write("always @* begin\n")
    fout.write("   rdata_int = `DATA_W'd0;\n")
    fout.write("   case(address)\n")
    for i in range(len(name_map)):
        if (type_map[i] == "`R_TYP" or type_map[i] == "`RW_TYP"):
            fout.write("     " + str(i) + ": rdata_int = " + str(name_map[i]) + " | `DATA_W'd0;\n")
            pass
        pass
    fout.write("     default: rdata_int = `DATA_W'd0;\n")
    fout.write("   endcase\n")
    fout.write("end\n")

    fout.close()
    return

def write_weights(name_map, width_map):
    fout = open('sw_reg_w.vh', 'w')

    fout.write("\n\n//registers width\n")
    for i in range(len(name_map)):
        fout.write("`define " + str(name_map[i]) + "_W " + str(width_map[i]) + "\n")
        
    fout.close()
    return


def swreg_parse (program) :
    name_map = []
    width_map = []
    init_val_map = []
    type_map = []
    for line in program :
        subline = re.sub('\[|\]|:|,|//|\;',' ', line)
        subline = re.sub('\(',' ',subline, 1)
        subline = re.sub('\)',' ', subline, 1)

        flds = subline.split()
        if not flds : continue #empty line
        #print flds[0]
        if ('SWREG_' in flds[0]): #software accessible registers
            reg_name = flds[1] #register name
            reg_width = flds[2] #register width
            reg_init_val = flds[3] #register init val

            #register type
            if '_RW' in flds[0]:
                reg_type = '`RW_TYP'
            elif '_W' in flds[0]:
                reg_type = '`W_TYP'
            else:
                reg_type = '`R_TYP'


            name_map.append(reg_name)
            width_map.append(reg_width)
            init_val_map.append(reg_init_val)
            type_map.append(reg_type)
        else: continue #not a recognized macro

    write_mapping(name_map, width_map, init_val_map, type_map)
    write_weights(name_map, width_map)

    return

def main () :
    #parse command line
    if len(sys.argv) != 2:
        print "Usage: ./swreg2regmap.py infile"
        quit()
    else:
        infile = sys.argv[1]
        
    #parse input file
    fin = open (infile, 'r')
    program = fin.readlines()
    fin.close()
    swreg_parse (program)

if __name__ == "__main__" : main ()