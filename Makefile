# (c) 2022-Present IObundle, Lda, all rights reserved
#
# This makefile simulates the hardware modules in this repo
#

SHELL=bash
export

#build here
LIB_DIR:=.
BUILD_VSRC_DIR:=./hardware/src
BUILD_SIM_DIR:=.
	
PYTHON_EXEC:=/usr/bin/env python3 -B

all: sim

# Default module
MODULE ?= iob_ram_2p
MODULE_DIR ?= $(shell find hardware -name $(MODULE))
ifeq ($(MODULE_DIR),)
$(info No such module $(MODULE))
endif

# Defines
DEFINE=-DADDR_W=10 -DDATA_W=32

VCD?=0
ifeq ($(VCD),1)
DEFINE+= -DVCD
endif

# Includes
INCLUDE=-Ihardware/include

# asymmetric memory present
IS_ASYM ?= 0

#
# Simulate with Icarus Verilog
#
VLOG=iverilog -W all -g2005-sv $(INCLUDE) $(DEFINE)

$(BUILD_VSRC_DIR):
	@mkdir $@

copy_srcs: $(BUILD_VSRC_DIR) 
	$(PYTHON_EXEC) ./scripts/lib_sim_setup.py $(MODULE) $(BUILD_VSRC_DIR)

sim: copy_srcs
	@echo "Simulating module $(MODULE)"
ifeq ($(IS_ASYM),0)
	$(VLOG) $(wildcard $(BUILD_VSRC_DIR)/*.v)
	@./a.out $(TEST_LOG)
else
	$(VLOG) -DW_DATA_W=32 -DR_DATA_W=8 $(wildcard $(BUILD_VSRC_DIR)/*.v)
	@./a.out $(TEST_LOG); if [ $(VCD) != 0 ]; then mv uut.vcd uut1.vcd; fi
	$(VLOG) -DW_DATA_W=8 -DR_DATA_W=32 $(wildcard $(BUILD_VSRC_DIR)/*.v)
	@./a.out $(TEST_LOG); if [ $(VCD) != 0 ]; then mv uut.vcd uut2.vcd; fi
	$(VLOG) -DW_DATA_W=8 -DR_DATA_W=8 $(wildcard $(BUILD_VSRC_DIR)/*.v)
	@./a.out $(TEST_LOG); if [ $(VCD) != 0 ]; then mv uut.vcd uut3.vcd; fi
endif
ifeq ($(VCD),1)
	@if [ ! `pgrep gtkwave` ]; then gtkwave uut.vcd; fi &
endif

clean:
	@rm -rf $(BUILD_VSRC_DIR)
	@rm -f *.v *.vh *.c *.h *.tex
	@rm -f *~ \#*\# a.out *.vcd *.pyc *.log

debug:

.PHONY: all sim clean debug
