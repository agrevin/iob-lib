ifeq ($(IS_FPGA),1)
FPGA_OBJ=$(FPGA_TOP).bit
else
FPGA_OBJ=$(FPGA_TOP).edif
endif

FPGA_LOG=vivado.log

FPGA_SERVER=$(VIVADO_SERVER)
FPGA_USER=$(VIVADO_USER)
FPGA_ENV:= bash $(VIVADOPATH)/settings64.sh
FPGA_PROG=$(FPGA_ENV) && $(VIVADOPATH)/bin/vivado -nojournal -log vivado.log -mode batch -source vivado/prog.tcl -tclargs $(NAME)_fpga_wrapper

# work-around for http://svn.clifford.at/handicraft/2016/vivadosig11
export RDI_VERBOSE = False

$(FPGA_OBJ): $(VSRC) $(VHDR) $(wildcard *.sdc)
	$(FPGA_ENV) && $(VIVADOPATH)/bin/vivado -nojournal -log vivado.log -mode batch -source vivado/build.tcl -tclargs $(NAME)_fpga_wrapper $(BOARD) "$(VSRC)" $(IS_FPGA) $(USE_EXTMEM)

vivado-clean:
	@rm -rf .Xil

.PHONY: vivado-clean
