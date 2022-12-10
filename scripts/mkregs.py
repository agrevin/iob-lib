#!/usr/bin/env python3
#
#    mkregs.py: build Verilog software accessible registers and software getters and setters
#

import sys
from math import ceil, log
from latex import write_table

cpu_n_bytes = 4
core_addr_w = None
config = None

def boffset(n, n_bytes):
    return 8*(n%n_bytes)

def bfloor(n, log2base):
    base = int(2**log2base)
    if n%base == 0:
        return n
    return base*int(n/base)

def bceil(n, log2base):
    base = int(2**log2base)
    n = compute_n_bits_value(n)
    #print(f"{n} of {type(n)} and {base}")
    if n%base == 0:
        return n
    else:
        return int(base*ceil(n/base))

def gen_wr_reg(row, f):
    name = row['name']
    rst_val = row['rst_val']
    n_bits = row['n_bits']
    n_items = row['n_items']
    n_bytes = bceil(n_bits, 3)/8
    addr = row['addr']
    addr_w = int(ceil(log(n_items*n_bytes,2)))
    auto = row['autologic']

    f.write(f"\n\n//NAME: {name}; TYPE: {row['type']}; WIDTH: {n_bits}; RST_VAL: {rst_val}; ADDR: {addr}; SPACE (bytes): {2**addr_w}; AUTO: {auto}\n\n")

    #compute wdata with only the needed bits
    f.write(f"`IOB_WIRE({name}_wdata, {n_bits})\n")
    f.write(f"assign {name}_wdata = iob_wdata_i[{boffset(addr,cpu_n_bytes)}+:{n_bits}];\n")

    #check if address in range
    f.write(f"`IOB_WIRE({name}_addressed, 1)\n")
    f.write(f"assign {name}_addressed = ((waddr >= {addr}) && (waddr < {addr+2**addr_w}));\n")

    #generate register logic
    if auto: #generate register
        f.write(f"`IOB_WIRE({name}_wen, 1)\n")
        f.write(f"assign {name}_wen = (iob_avalid_i) & ((|iob_wstrb_i) & {name}_addressed);\n")
        f.write(f"iob_reg_ae #({n_bits},{rst_val}) {name}_datareg (clk_i, arst_i, {name}_wen, {name}_wdata, {name}_o);\n")
    else: #output wdata and wen; ready signal has been declared as a port
        f.write(f"assign {name}_o = {name}_wdata;\n")
        f.write(f"assign {name}_wen_o = ({name}_ready_i & iob_avalid_i) & ((|iob_wstrb_i) & {name}_addressed);\n")

    #compute write enable

    #compute address for register range
    if n_items > 1:
        f.write(f"assign {name}_addr_o = iob_addr_i[{addr_w}-1:0];\n")

def gen_rd_reg(row, f):
    name = row['name']
    rst_val = row['rst_val']
    n_bits = row['n_bits']
    n_items = row['n_items']
    n_bytes = bceil(n_bits, 3)/8
    addr = row['addr']
    addr_last = int(addr + (n_items-1)*n_bytes)
    addr_w = int(ceil(log(n_items*n_bytes,2)))
    addr_w_base = max(log(cpu_n_bytes,2), addr_w)
    auto = row['autologic']

    f.write(f"\n\n//NAME: {name}; TYPE: {row['type']}; WIDTH: {n_bits}; RST_VAL: {rst_val}; ADDR: {addr}; SPACE (bytes): {2**addr_w}; AUTO: {auto}\n\n")

    #generate register logic
    if not auto: #generate register
        f.write(f"`IOB_WIRE({name}_addressed, 1)\n")
        f.write(f"assign {name}_addressed = ((iob_addr_i >= {addr}) && (iob_addr_i < {addr+2**addr_w}));\n")
        f.write(f"assign {name}_ren_o = ({name}_ready_i & iob_avalid_i) & ((~|iob_wstrb_i) & {name}_addressed);\n")

    #compute address for register range
    if n_items > 1:
        f.write(f"assign {name}_addr_o = iob_addr_i[{addr_w}-1:0];\n")

# generate ports for swreg module
def gen_port(table, f):
    for row in table:
        name = row['name']
        n_bits = row['n_bits']
        n_items = row['n_items']
        n_bytes = bceil(n_bits, 3)/8
        addr_w = int(ceil(log(row['n_items']*n_bytes,2)))
        auto = row['autologic']
 
        
        if row['type'] == 'W':
            f.write(f"\t`IOB_OUTPUT({name}_o, {n_bits}),\n")
            if not auto:
                f.write(f"\t`IOB_OUTPUT({name}_wen_o, 1),\n")
        elif row['type'] == 'R':
            f.write(f"\t`IOB_INPUT({name}_i, {n_bits}),\n")
            if not auto:
                f.write(f"\t`IOB_OUTPUT({name}_ren_o, 1),\n")
                f.write(f"\t`IOB_INPUT({name}_rvalid_i, 1),\n")
        if not auto:
            f.write(f"\t`IOB_INPUT({name}_ready_i, 1),\n")
        if n_items > 1:
            f.write(f"\t`IOB_OUTPUT({name}_addr_o, {addr_w}),\n")

# generate wires to connect instance in top module
def gen_inst_wire(table, f):
    for row in table:
        name = row['name']
        n_bits = row['n_bits']
        n_items = row['n_items']
        n_bytes = bceil(n_bits, 3)/8
        addr_w = int(ceil(log(n_items*n_bytes,2)))
        auto = row['autologic']
        rst_val = row['rst_val']

        if row['type'] == 'W':
            f.write(f"`IOB_WIRE({name}, {n_bits})\n")
            if not auto:
                f.write(f"`IOB_WIRE({name}_wen, 1)\n")
        else:
            f.write(f"`IOB_WIRE({name}, {n_bits})\n")
            if not row['autologic']:
                f.write(f"`IOB_WIRE({name}_rvalid, 1)\n")
                f.write(f"`IOB_WIRE({name}_ren, 1)\n")
            else:
                f.write(f"`IOB_WIRE({name}_int, {n_bits})\n")
        if not auto:
            f.write(f"`IOB_WIRE({name}_ready, 1)\n")
        if n_items > 1:
            f.write(f"`IOB_WIRE({name}_addr, {addr_w})\n")
    f.write("\n")

# generate portmap for swreg instance in top module
def gen_portmap(table, f):
    for row in table:
        name = row['name']
        n_bits = row['n_bits']
        n_items = row['n_items']
        n_bytes = bceil(n_bits, 3)/8
        addr_w = int(ceil(log(row['n_items']*n_bytes,2)))
        auto = row['autologic']

        if row['type'] == 'W':
            f.write(f"\t.{name}_o({name}),\n")
            if not auto:
                f.write(f"\t.{name}_wen_o({name}_wen),\n")
        else:
            f.write(f"\t.{name}_i({name}),\n")
            if not auto:
                f.write(f"\t.{name}_ren_o({name}_ren),\n")
                f.write(f"\t.{name}_rvalid_i({name}_rvalid),\n")
        if not auto:
            f.write(f"\t.{name}_ready_i({name}_ready),\n")
        if n_items > 1:
            f.write(f"\t.{name}_addr_o({name}_addr),\n")


def write_hwcode(table, out_dir, top):

    #
    # SWREG INSTANCE
    #

    f_inst = open(f"{out_dir}/{top}_swreg_inst.vh", "w")
    f_inst.write("//This file was generated by script mkregs.py\n\n")

    # connection wires
    gen_inst_wire(table, f_inst)

    f_inst.write(f'{top}_swreg_gen #(\n')
    f_inst.write(f'\t`include "{top}_inst_params.vh"\n')
    f_inst.write("\n) swreg_0 (\n")
    gen_portmap(table, f_inst)
    f_inst.write('\t`include "iob_s_portmap.vh"\n')
    f_inst.write('\t`include "iob_clkenrst_portmap.vh"')
    f_inst.write("\n);\n")

    #
    # SWREG MODULE
    #

    f_gen = open(f"{out_dir}/{top}_swreg_gen.v", "w")
    f_gen.write("//This file was generated by script mkregs.py\n\n")

    # time scale
    f_gen.write("`timescale 1ns / 1ps\n\n")

    # iob library
    f_gen.write(f'`include "iob_lib.vh"\n')
    
    # macros
    f_gen.write(f'`include "{top}_conf.vh"\n')
    f_gen.write(f'`include "{top}_swreg_def.vh"\n\n')

    # declaration
    f_gen.write(f'module {top}_swreg_gen\n')

    # parameters
    f_gen.write("#(\n")
    f_gen.write(f'`include "{top}_params.vh"\n')
    f_gen.write(")\n")
    f_gen.write("(\n")

    # ports
    gen_port(table, f_gen)
    f_gen.write('\t`include "iob_s_port.vh"\n')
    f_gen.write('\t`include "iob_clkenrst_port.vh"\n')
    f_gen.write(");\n\n")

    #write address
    f_gen.write("\n//write address\n")

    #extract address byte offset
    f_gen.write(f"`IOB_WIRE(byte_offset, $clog2(DATA_W/8))\n")
    f_gen.write(f"iob_wstrb2byte_offset #(DATA_W/8) bo_inst (iob_wstrb_i, byte_offset);\n")

    #compute write address
    f_gen.write(f"`IOB_WIRE(waddr, ADDR_W)\n")
    f_gen.write(f"assign waddr = `IOB_WORD_ADDR(iob_addr_i) + byte_offset;\n")

    # insert write register logic
    for row in table:
        if row['type'] == 'W':
            gen_wr_reg(row, f_gen)


    # insert read register logic
    for row in table:
        if row['type'] == 'R':
            gen_rd_reg(row, f_gen)

    #
    # RESPONSE SWITCH
    #
    f_gen.write("\n\n//RESPONSE SWITCH\n")

    # use variables to compute response
    f_gen.write(f"\n`IOB_VAR(rdata_int, {8*cpu_n_bytes})\n")
    f_gen.write(f"\n`IOB_WIRE(rdata_nxt, {8*cpu_n_bytes})\n")

    f_gen.write(f"`IOB_VAR(rvalid_int, {cpu_n_bytes})\n")
    f_gen.write(f"`IOB_WIRE(rvalid_nxt, 1)\n")

    f_gen.write(f"`IOB_VAR(wready_int, {cpu_n_bytes})\n")
    f_gen.write(f"`IOB_VAR(rready_int, {cpu_n_bytes})\n")
    f_gen.write(f"`IOB_WIRE(ready_nxt, 1)\n\n")

    f_gen.write("`IOB_COMB begin\n")

    f_gen.write(f"\trdata_int = {8*cpu_n_bytes}'d0;\n")
    f_gen.write(f"\twready_int = {cpu_n_bytes}'d0;\n")
    f_gen.write(f"\trready_int = {cpu_n_bytes}'d0;\n\n")

    #read register response
    for row in table:
        name = row['name']
        addr = row['addr']
        n_bits = row['n_bits']
        n_items = row['n_items']
        n_bytes = int(bceil(n_bits, 3)/8)
        addr_last = int(addr + (n_items-1)*n_bytes)
        addr_w = int(ceil(log(n_items*n_bytes,2)))
        addr_w_base = max(log(cpu_n_bytes,2), addr_w)
        auto = row['autologic']

        if row['type'] == 'R':
            f_gen.write(f"\tif((`IOB_WORD_ADDR(iob_addr_i) >= {bfloor(addr, addr_w_base)}) && (`IOB_WORD_ADDR(iob_addr_i) <= {bfloor(addr_last, addr_w_base)})) ")
            f_gen.write(f"begin\n")
            f_gen.write(f"\t\trdata_int[{boffset(addr, cpu_n_bytes)}+:{8*n_bytes}] = {name}_i|{8*n_bytes}'d0;\n")
            if auto:
                f_gen.write(f"\t\trready_int[{addr%cpu_n_bytes}+:{n_bytes}] = "+'{'+f"{n_bytes}"+'{'+"1'b1"+"}};\n")
                f_gen.write(f"\t\trvalid_int[{addr%cpu_n_bytes}+:{n_bytes}] = "+'{'+f"{n_bytes}"+'{'+"1'b1"+"}};\n")
            else:
                f_gen.write(f"\t\trready_int[{addr%cpu_n_bytes}+:{n_bytes}] = "+'{'+f"{n_bytes}"+'{'+f"{name}_ready_i"+"}};\n")
                f_gen.write(f"\t\trvalid_int[{addr%cpu_n_bytes}+:{n_bytes}] = "+'{'+f"{n_bytes}"+'{'+f"{name}_rvalid_i"+"}};\n")
            f_gen.write(f"end\n\n")

    #write register response
    for row in table:
        name = row['name']
        addr = row['addr']
        n_bits = row['n_bits']
        n_items = row['n_items']
        n_bytes = int(bceil(n_bits, 3)/8)
        addr_w = int(ceil(log(n_items*n_bytes,2)))
        addr_w_base = max(log(cpu_n_bytes,2), addr_w)
        auto = row['autologic']

        if row['type'] == 'W':
            # get wready
            f_gen.write(f"\tif((waddr >= {addr}) && (waddr < {addr + 2**addr_w}))\n")
            if auto:
                f_gen.write(f"\t\twready_int[{addr%cpu_n_bytes}+:{n_bytes}] = "+'{'+f"{n_bytes}"+'{'+"1'b1"+"}};\n\n")
            else:
                f_gen.write(f"\t\twready_int[{addr%cpu_n_bytes}+:{n_bytes}] =  "+'{'+f"{n_bytes}"+'{'+f"{name}_ready_i"+"}};\n\n")

    f_gen.write("end //IOB_COMB\n\n")

    #determine if peripheral is being accessed
    f_gen.write("wire accessed = iob_avalid_i & iob_ready_o;\n")

    #ready output (always down after an access to allow new state to propagate to output in the next cycle)
    f_gen.write("//ready output\n")
    f_gen.write("assign ready_nxt = ~accessed & ((iob_wstrb_i != 0)? |wready_int: |rready_int);\n")
    f_gen.write("iob_reg_ae #(1,0) ready_reg_inst (clk_i, arst_i, en_i, ready_nxt, iob_ready_o);\n\n")

    #rvalid output
    f_gen.write("//rvalid output\n")
    f_gen.write("assign rvalid_nxt =  (~accessed) & (|rvalid_int);\n")
    f_gen.write("iob_reg_ae #(1,0) rvalid_reg_inst (clk_i, arst_i, en_i, rvalid_nxt, iob_rvalid_o);\n\n")
 
    #rdata output
    f_gen.write("//rdata output\n")
    f_gen.write(f"iob_reg_ae #({8*cpu_n_bytes},0) rdata_reg_inst (clk_i, arst_i, en_i, rdata_int, iob_rdata_o);\n\n")

    f_gen.write("endmodule\n")
    f_gen.close()
    f_inst.close()


def write_hwheader(table, out_dir, top):
    f_def = open(f"{out_dir}/{top}_swreg_def.vh", "w")
    f_def.write("//This file was generated by script mkregs.py\n\n")
    f_def.write("//used address space width\n")
    addr_w_prefix = f"{top}_swreg".upper()
    f_def.write(f"`define {addr_w_prefix}_ADDR_W {core_addr_w}\n\n")
    f_def.write("//address macros\n")
    macro_prefix = f"{top}_".upper()
    f_def.write("//addresses\n")
    for row in table:
        name = row['name']
        n_bits = row['n_bits']
        n_bytes = bceil(n_bits, 3)/8
        n_items = row['n_items']
        addr_w = int(ceil(log(n_items*n_bytes,2)))
        f_def.write(f"`define {macro_prefix}{name}_ADDR {row['addr']}\n")
        if n_items>1:
            f_def.write(f"`define {macro_prefix}{name}_ADDR_W {addr_w}\n")
        if type(n_bits)==int:
            f_def.write(f"`define {macro_prefix}{name}_W {n_bits}\n\n")
        elif n_bits != f"{name}_W":
            f_def.write(f"`define {macro_prefix}{name}_W `{macro_prefix}{n_bits}\n\n")
        else:
            f_def.write("\n")
    f_def.close()


# Get C type from swreg n_bytes
# uses unsigned int types from C stdint library
def swreg_type(name, n_bytes):
    type_dict = {1: "uint8_t", 2: "uint16_t", 4: "uint32_t", 8: "uint64_t"}
    try:
        type_try = type_dict[n_bytes]
    except:
        print(f"Error: register {name} has invalid number of bytes {n_bytes}.")
    return type_try


def write_swheader(table, out_dir, top):
    fswhdr = open(f"{out_dir}/{top}_swreg.h", "w")

    core_prefix = f"{top}_".upper()

    fswhdr.write("//This file was generated by script mkregs.py\n\n")
    fswhdr.write(f"#ifndef H_{core_prefix}SWREG_H\n")
    fswhdr.write(f"#define H_{core_prefix}SWREG_H\n\n")
    fswhdr.write("#include <stdint.h>\n\n")

    fswhdr.write("//Addresses\n")
    for row in table:
        name = row['name']
        if row["type"] == "W":
            fswhdr.write(f"#define {core_prefix}{name} {row['addr']}\n")
        if row["type"] == "R":
            fswhdr.write(f"#define {core_prefix}{name} {row['addr']}\n")

    fswhdr.write("\n//Data widths (bit)\n")
    for row in table:
        name = row['name']
        n_bits = row['n_bits']
        n_bytes = int(bceil(n_bits, 3)/8)
        if row["type"] == "W":
            fswhdr.write(f"#define {core_prefix}{name}_W {n_bytes*8}\n")
        if row["type"] == "R":
            fswhdr.write(f"#define {core_prefix}{name}_W {n_bytes*8}\n")

    fswhdr.write("\n// Base Address\n")
    fswhdr.write(f"void {core_prefix}INIT_BASEADDR(uint32_t addr);\n")

    fswhdr.write("\n// Core Setters and Getters\n")
    for row in table:
        name = row['name']
        n_bits = row['n_bits']
        n_items = row['n_items']
        n_bytes = bceil(n_bits, 3)/8
        addr_w = int(ceil(log(n_items*n_bytes,2)))
        if row["type"] == "W":
            sw_type = swreg_type(name, n_bytes)
            addr_arg = ""
            if addr_w / n_bytes > 1:
                addr_arg = ", int addr"
            fswhdr.write(f"void {core_prefix}SET_{name}({sw_type} value{addr_arg});\n")
        if row["type"] == "R":
            sw_type = swreg_type(name, n_bytes  )
            addr_arg = ""
            if addr_w / n_bytes > 1:
                addr_arg = "int addr"
            fswhdr.write(f"{sw_type} {core_prefix}GET_{name}({addr_arg});\n")

    fswhdr.write(f"\n#endif // H_{core_prefix}_SWREG_H\n")

    fswhdr.close()


def write_swcode(table, out_dir, top):
    fsw = open(f"{out_dir}/{top}_swreg_emb.c", "w")
    core_prefix = f"{top}_".upper()
    fsw.write("//This file was generated by script mkregs.py\n\n")
    fsw.write(f'#include "{top}_swreg.h"\n\n')
    fsw.write("\n// Base Address\n")
    fsw.write("static int base;\n")
    fsw.write(f"void {core_prefix}INIT_BASEADDR(uint32_t addr) {{\n")
    fsw.write("\tbase = addr;\n")
    fsw.write("}\n")

    fsw.write("\n// Core Setters and Getters\n")

    for row in table:
        name = row['name']
        n_bits = row['n_bits']
        n_items = row['n_items']
        n_bytes = bceil(n_bits, 3)/8
        addr_w = int(ceil(log(n_items*n_bytes,2)))
        if row["type"] == "W":
            sw_type = swreg_type(name, n_bytes)
            addr_arg = ""
            addr_arg = ""
            addr_shift = ""
            if addr_w / n_bytes > 1:
                addr_arg = ", int addr"
                addr_shift = f" + (addr << {int(log(n_bytes, 2))})"
            fsw.write(f"void {core_prefix}SET_{name}({sw_type} value{addr_arg}) {{\n")
            fsw.write(f"\t(*( (volatile {sw_type} *) ( (base) + ({core_prefix}{name}){addr_shift}) ) = (value));\n")
            fsw.write("}\n\n")
        if row["type"] == "R":
            sw_type = swreg_type(name, n_bytes)
            addr_arg = ""
            addr_shift = ""
            if addr_w / n_bytes > 1:
                addr_arg = "int addr"
                addr_shift = f" + (addr << {int(log(n_bytes, 2))})"
            fsw.write(f"{sw_type} {core_prefix}GET_{name}({addr_arg}) {{\n")
            fsw.write(f"\treturn (*( (volatile {sw_type} *) ( (base) + ({core_prefix}{name}){addr_shift}) ));\n")
            fsw.write("}\n\n")
    fsw.close()

# check if address is aligned 
def check_alignment(addr, addr_w):
    if addr % (2**addr_w) != 0:
        sys.exit(f"Error: address {addr} with span {2**addr_w} is not aligned")

# check if address overlaps with previous
def check_overlap(addr, addr_type, read_addr, write_addr):
    if addr_type == "R" and addr < read_addr:
        sys.exit(f"Error: read address {addr} overlaps with previous addresses")
    elif addr_type == "W" and addr < write_addr:
        sys.exit(f"Error: write address {addr} overlaps with previous addresses")

def compute_n_bits_value(n_bits):
        if type(n_bits)==int:
            return n_bits
        else:
            for param in config:
                if param['name']==n_bits:
                    try:
                        return int(param['val'])
                    except:
                        return int(param['max'])
        sys.exit(f"Error: register 'n_bits':'{n_bits}' is not well defined.")

# compute address
def compute_addr(table, no_overlap):
    read_addr = 0
    write_addr = 0

    tmp = []

    for row in table:
        addr = row['addr']
        addr_type = row['type']
        n_bits = row['n_bits']
        n_items = row['n_items']
        n_bytes = bceil(n_bits, 3)/8
        addr_w = int(ceil(log(n_items*n_bytes,2)))
        if addr >= 0: #manual address
            check_alignment(addr, addr_w)
            check_overlap(addr, addr_type, read_addr, write_addr)
            addr_tmp = addr
        elif addr_type == 'R': #auto address
            read_addr = bceil(read_addr, addr_w)
            addr_tmp = read_addr
        elif addr_type == 'W':
            write_addr = bceil(write_addr, addr_w)
            addr_tmp = write_addr
        if no_overlap:
            addr_tmp = max(read_addr, write_addr)

        #save address temporarily in list
        tmp.append(addr_tmp);

        #update addresses
        addr_tmp+= 2**addr_w
        if addr_type == 'R':
            read_addr = addr_tmp
        elif addr_type == 'W':
            write_addr = addr_tmp
        if no_overlap:
            read_addr = addr_tmp
            write_addr = addr_tmp

    #update reg addresses
    for i in range(len(tmp)):
        table[i]['addr']=tmp[i]

            
    #update core address space size
    global core_addr_w
    core_addr_w = int(ceil(log(max(read_addr, write_addr), 2)))

    return table


# Generate TeX tables of registers
# regs: list of tables containing registers, as defined in <corename>_setup.py
# regs_with_addr: list of all registers, where 'addr' field has already been computed
def generate_regs_tex(regs, regs_with_addr, out_dir):
    for table in regs:
        tex_table = []
        for reg in table['regs']:
            tex_table.append([reg['name'].replace('_','\_'), reg['type'],
                             # Find address of matching register in regs_with_addr list
                             next(register['addr'] for register in regs_with_addr if register['name'] == reg['name']),
                             reg['n_bits'], reg['rst_val'], reg['descr']])

        write_table(f"{out_dir}/{table['name']}_swreg",tex_table)
