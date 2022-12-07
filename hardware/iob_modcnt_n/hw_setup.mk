ifeq ($(filter iob_modcnt_n, $(HW_MODULES)),)

# Add to modules list
HW_MODULES+=iob_modcnt_n

# Submodules
include $(LIB_DIR)/hardware/iob_counter_n/hw_setup.mk

# Sources
SRC+=$(BUILD_VSRC_DIR)/iob_modcnt_n.v

# Copy the sources to the build directory 
$(BUILD_VSRC_DIR)/iob_modcnt_n.v: $(LIB_DIR)/hardware/iob_modcnt_n/iob_modcnt_n.v
	cp $< $(BUILD_VSRC_DIR)

endif