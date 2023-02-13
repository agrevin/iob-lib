# (c) 2022-Present IObundle, Lda, all rights reserved
#
# This makefile is used at build-time in $(BUILD_DIR)/software/embedded/Makefile
#

include ../../config_build.mk

MFLAGS=$(MFLAGS_BASE)$(MFLAG_M)$(MFLAG_C)
MFLAGS_BASE:=rv32i
ifeq ($(USE_MUL_DIV),1)
MFLAG_M=m
endif
ifeq ($(USE_COMPRESSED),1)
MFLAG_C=c
endif

#default compiler settings
TOOLCHAIN_PREFIX ?=riscv64-unknown-elf-
CC=$(TOOLCHAIN_PREFIX)gcc

CFLAGS ?=-Os -nostdlib -march=$(MFLAGS) -mabi=ilp32 --specs=nano.specs -Wcast-align=strict
LDFLAGS ?= -Wl,-Map,$(LDM),-Bstatic,-T,$(LDS),--strip-debug

LLIBS ?=-lgcc -lc -lnosys
INCLUDES ?=-I. -I../esrc

# include local build segment
# all previously defined variables can be overwritten in this file
ifneq ($(wildcard embed_build.mk),)
include embed_build.mk
endif

build: $(UTARGETS)

%.elf: $(HDR) $(SRC)
	$(CC) $(CFLAGS) $(INCLUDES) -Wl,-Bstatic,-T,$(LDS),--strip-debug $(DEFINES) -o $@ $(SRC) $(LLIBS)
	$(TOOLCHAIN_PREFIX)objcopy -O binary $@ $(*F).bin

clean:
	@rm -rf *.bin *.elf *.map *.hex

debug:
	@echo $(FW_SRC)
	@echo $(BOOT_SRC)
	@echo $(HDR)

.PHONY: build clean debug

