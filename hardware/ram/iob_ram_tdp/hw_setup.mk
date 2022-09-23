ifeq ($(filter iob_ram_tdp, $(HW_MODULES)),)

# Add to modules list
HW_MODULES+=iob_ram_tdp

# Sources
SRC+=$(BUILD_VSRC_DIR)/iob_ram_tdp.v

# Copy the osurces to the build directory 
$(BUILD_VSRC_DIR)/iob_ram_tdp.v: $(LIB_DIR)/hardware/ram/iob_ram_tdp/iob_ram_tdp.v
	cp $< $(BUILD_VSRC_DIR)

endif