`timescale 1ns / 1ps

module iob_sipo_reg #(
   parameter DATA_W = 21
) (

   `include "iob_clk_en_rst_port.vs"

   //serial input
   input s_i,

   //parallel output
   output [DATA_W-1:0] p_o
);

   wire [DATA_W-1:0] data;
   assign data = {p_o[DATA_W-2:0], s_i};

   iob_reg #(
      .DATA_W (DATA_W),
      .RST_VAL(0),
      .CLKEDGE("posedge")
   ) reg0 (
      `include "iob_clk_en_rst_portmap.vs"

      .data_i(data),
      .data_o(p_o)
   );

endmodule
