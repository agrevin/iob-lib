`timescale 1ns / 1ps
`include "iob_lib.vh"

module iob_split
  #(
    parameter DATA_W = 0,
    parameter ADDR_W = 0,
    parameter N = 0
   )
   (
`include "iob_split_i_iob_port.vh"
`include "iob_split_o_iob_port.vh"
`include "iob_clkenrst.vh"
    );

   localparam  NBITS=$clog2(N)+($clog2(N)==0);

   wire [NBITS-1:0] sel, sel_reg;
   assign sel = addr_i[ADDR_W-2 -: NBITS];

   //avalid demux
   iob_demux #(.DATA_W(1), .N(N)) iob_demux_avalid
     (
      .sel_i(sel),
      .data_i(avalid_i),
      .data_o(avalid_o)
      );
   
   //addr demux
   iob_demux #(.DATA_W(ADDR_W), .N(N)) iob_demux_addr
     (
      .sel_i(sel),
      .data_i(addr_i),
      .data_o(addr_o)
      );
   
   //wstrb demux
   iob_demux #(.DATA_W(DATA_W/8), .N(N)) iob_demux_wstrb
     (
      .sel_i(sel),
      .data_i(wstrb_i),
      .data_o(wstrb_o)
      );
   
   //wdata demux
   iob_demux #(.DATA_W(DATA_W/8), .N(N)) iob_demux_wdata
     (
      .sel_i(sel),
      .data_i(wdata_i),
      .data_o(wdata_o)
      );
   
   //ready mux
   iob_mux #(.DATA_W(DATA_W/8), .N(N)) iob_demux_ready
     (
      .sel_i(sel),
      .data_i(ready_i),
      .data_o(ready_o)
      );
   
   //rdata mux
   iob_mux #(.DATA_W(DATA_W/8), .N(N)) iob_mux_rdata
     (
      .sel_i(sel_reg),
      .data_i(rdata_i),
      .data_o(rdata_o)
      );
   

   //rvalid mux
   iob_mux #(.DATA_W(DATA_W/8), .N(N)) iob_mux_rvalid
     (
      .sel_i(sel_reg),
      .data_i(rvalid_i),
      .data_o(rvalid_o)
      );
         
   iob_reg #(.DATA_W(), .RST_VAL(0)) sel_reg0
      (
       .clk_i(clk_i),
       .arst_i(arst),
       .cke_i(cke_i),
       .data_i(sel),
       .data_o(sel_reg)
       );
   
endmodule
