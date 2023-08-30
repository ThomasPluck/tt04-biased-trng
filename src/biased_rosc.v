`timescale 1ns/10ps
`include "cells.v"

module inv_with_delay(input A,output Y);
  `ifdef COCOTB_SIM
  assign #0.02 Y = ~A; // pick a fairly quick delay from the tt_025C_1v80 liberty file
                       // the actualy delay per stage is going to be slower
  `else
  sky130_fd_sc_hd__inv_1 inv(.A(A),.Y(Y));
  `endif
endmodule

module and2_with_delay(input A,input B,output Y);
  `ifdef COCOTB_SIM
  assign #0.05 Y = ~(A & B);
  `else
  sky130_fd_sc_hd__and2_1 and2(.A(A),.B(B),.Y(Y));
  `endif
endmodule

module nand2_with_delay(input A,input B,output Y);
  `ifdef COCOTB_SIM
  assign #0.05 Y = ~(A & B);
  `else
  sky130_fd_sc_hd__nand2_1 nand2(.A(A),.B(B),.Y(Y));
  `endif
endmodule

module ring_osc(input ena,output osc);

  localparam NUM_INVERTERS = 150; //  must be an even number
  
  // setup loop of inverters
  // http://svn.clairexen.net/handicraft/2015/ringosc/ringosc.v
  wire [NUM_INVERTERS-1:0] delay_in, delay_out;
  wire osc_out;
  inv_with_delay idelay [NUM_INVERTERS-1:0] (
        .A(delay_in),
        .Y(delay_out)
    );
  assign delay_in = {delay_out[NUM_INVERTERS-2:0], osc_out};
  nand2_with_delay nand2_with_delay(.A(ena),.B(delay_out[NUM_INVERTERS-1]),.Y(osc_out));
  assign osc = osc_out;
endmodule

module multiple_ring_oscillators#(
    parameter NUM_OSCILLATORS = 5, // Number of oscillators
    parameter OSCILLATOR_LENGTH = 7 // Length for all oscillators
)(
    input ena, 
    output final_osc
);

    // Instantiate multiple ring oscillators with the same specified length
    genvar i;
    generate
        for(i = 0; i < NUM_OSCILLATORS; i=i+1) begin: multiple_ring_osc
            ring_osc #(OSCILLATOR_LENGTH) ro(.ena(ena), .osc(final_osc));
        end
    endgenerate

endmodule

module bias(input BUF, input CTRL, output OUT);
  wire buffer, tri2sq, ctrl, bias, out;

  assign buffer = BUF;
  assign ctrl = CTRL;
  assign out = OUT;

  sky130_fd_sc_hd__inv_2 ctrl_inv(.A(ctrl), .Y(bias));
  sky130_fd_sc_hd__inv_2 out_inv(.A(bias), .Y(out));
  sky130_fd_sc_hd__inv_4 buf_inv(.A(buffer), .Y(tri2sq));
  sky130_fd_sc_hd__inv_2 tri_inv(.A(tri2sq), .Y(bias));

endmodule