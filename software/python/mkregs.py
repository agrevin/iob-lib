#!/usr/bin/python3
#
#    Build Latex tables of verilog module interface signals and registers
#

import sys
import os.path
import re
import math

regvfile_name = ''
corename = ''

def write_hw(name_map, width_map, init_val_map, type_map):
    #write output file
    global regvfile_name
    fout = open (regvfile_name+'_gen.vh', 'w')

    fout.write("//This file was generated by script mkregs.py\n\n")

    fout.write("\n\n//write registers\n")
    for i in range(len(name_map)):
        if ('ifdef' in name_map[i] or 'endif' in name_map[i]): fout.write("`" + str(name_map[i]) + "\n")
        if (type_map[i] == "`W_TYP"):
            fout.write("`REG_ARE(clk, rst, " + str(init_val_map[i]) + ", valid & wstrb & (address == " + str(i) + "), " + str(name_map[i]) + ", wdata[" + str(width_map[i]) + "-1:0])\n")
            pass
        pass

    fout.write("\n\n//read registers\n")
    fout.write("`VAR(rdata_int, DATA_W)\n")
    fout.write("`VAR(rdata_int2, DATA_W)\n")
    fout.write("`REG_ARE(clk, rst, 0, valid, rdata_int2, rdata_int)\n")
    fout.write("`VAR2WIRE(rdata_int2, rdata)\n\n")

    fout.write("always @* begin\n")
    fout.write("   rdata_int = 1'b0;\n")
    fout.write("   case(address)\n")
    for i in range(len(name_map)):
        if ('ifdef' in name_map[i] or 'endif' in name_map[i]): fout.write("`" + str(name_map[i]) + "\n")
        if (type_map[i] == "`R_TYP"):
            fout.write("     " + str(i) + ": rdata_int = " + str(name_map[i]) + ";\n")
            pass
        pass

    fout.write("     default: rdata_int = 1'b0;\n")
    fout.write("   endcase\n")
    fout.write("end\n")

    #ready signal   
    fout.write("`VAR(ready_int, 1)\n")
    fout.write("`REG_AR(clk, rst, 0, ready_int, valid)\n")
    fout.write("`VAR2WIRE(ready_int, ready)\n")
    
    fout.close()
    return

def write_hwheader(name_map, width_map):
    global regvfile_name
    global corename
    fout = open(regvfile_name+'_def.vh', 'w')

    fout.write("//This file was generated by script mkregs.py\n\n")

    fout.write("//address width\n")
    fout.write("`define "+ corename + "_ADDR_W " + str(int(math.ceil(math.log(len(name_map), 2)))) + "\n\n")

    fout.write("//address macros\n")
    for i in range(len(name_map)):
        if ('ifdef' in name_map[i] or 'endif' in name_map[i]): fout.write("`" + str(name_map[i]) + "\n")
        else: fout.write("`define " + str(name_map[i]) + "_ADDR " + str(i) + "\n")

    fout.write("\n//registers width\n")
    for i in range(len(name_map)):
        if ('ifdef' in name_map[i] or 'endif' in name_map[i]): fout.write("`" + str(name_map[i]) + "\n")
        else: fout.write("`define " + str(name_map[i]) + "_W " + str(width_map[i]) + "\n")

    fout.close()
    return

def write_swheader(name_map):
    global regvfile_name
    fout = open(regvfile_name+'.h', 'w')

    fout.write("//This file was generated by script mkregs.py\n\n")
    fout.write("//register address mapping\n")
    for i in range(len(name_map)):
        if ('ifdef' in name_map[i] or 'endif' in name_map[i]): fout.write("#" + str(name_map[i]) + "\n")
        else: fout.write("#define " + str(name_map[i]) + " " + str(i) + "\n")

    fout.close()
    return


def swreg_parse (program, hwsw):
    name_map = []
    width_map = []
    init_val_map = []
    type_map = []

    for line in program :
        if line.startswith("//"): continue #commented line

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
            if '_W' in flds[0]:
                reg_type = '`W_TYP'
                name_map.append(reg_name)
                width_map.append(reg_width)
                init_val_map.append(reg_init_val)
                type_map.append(reg_type)

            else:
                reg_type = '`R_TYP'
                name_map.append(reg_name)
                width_map.append(reg_width)
                init_val_map.append(reg_init_val)
                type_map.append(reg_type)

        elif ('ifdef' in flds[0] or 'endif' in flds[0]):
            if ('ifdef' in flds[0]): reg_name = 'ifdef' + ' ' + flds[1]
            else: reg_name = 'endif'
            name_map.append(reg_name)
            width_map.append('')
            init_val_map.append('')
            type_map.append('')

        else: continue #not a recognized macro

    if(hwsw == "HW"):
        write_hw(name_map, width_map, init_val_map, type_map)
        write_hwheader(name_map, width_map)

    elif(hwsw == "SW"):
        write_swheader(name_map)

    return

def main () :

    global regvfile_name
    global corename

    #parse command line
    if len(sys.argv) != 3:
        print("Usage: ./mkregs.py COREsw_reg.vh [HW|SW]")
        print(" COREsw_reg.vh:the software accessible registers definitions file")
        print(" [HW|SW]: use HW to generate the hardware files or SW to generate the software files")
        quit()
    else:
        regvfile_name = sys.argv[1]
        hwsw = sys.argv[2]

    #parse input file
    fin = open (regvfile_name, 'r')
    defsfile = fin.readlines()
    fin.close()

    regvfile_name = regvfile_name.split('/')[-1].split('.')[0]
    corename = regvfile_name.replace('sw_reg', '', 1)

    swreg_parse (defsfile, hwsw)

if __name__ == "__main__" : main ()
