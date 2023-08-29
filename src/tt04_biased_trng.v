`include "cells.v"
`include "vdac.v"
`include "biased_rosc.v"

module tb_ring_osc_vdac;

    // Parameters
    parameter BITWIDTH = 6;

    // Clock signal
    reg clk = 0;
    always #5 clk = ~clk;  // Assuming a 10ns clock period

    // Instantiate ring oscillator
    reg nrst = 1;
    wire osc;
    ring_osc ring_osc_inst(.nrst(nrst), .osc(osc));

    // Instantiate bias
    wire bias_out;
    bias bias_inst(.BUF(osc), .CTRL(), .OUT(bias_out));  // CTRL will be connected later

    // Control signals for VDAC
    reg [BITWIDTH-1:0] i_data = 0;
    reg i_enable = 1;
    wire vdac_out;
    vdac vdac_inst(.i_data(i_data), .i_enable(i_enable), .vout_notouch_(vdac_out));

    // Connecting VDAC to bias
    assign bias_inst.CTRL = vdac_out;

    // Setting up control for VDAC based on the provided description
    reg out1, out2, out3;
    assign i_data[0] = out1;
    assign i_data[1] = out1;
    assign i_data[2] = out1;
    assign i_data[3] = out1;
    assign i_data[4] = out2;
    assign i_data[5] = out2;
    assign i_data[6] = out3;

    // Instantiate two D flip-flops
    wire dff1_out, dff2_out;
    dff_cell dff1(.clk(clk), .d(bias_out), .q(dff1_out), .notq());
    dff_cell dff2(.clk(clk), .d(dff1_out), .q(dff2_out), .notq());

    // Test sequence
    initial begin
        #10 nrst = 0;  // Reset release
        #20 out1 = 1;
        #30 out2 = 1;
        #40 out3 = 1;
        #50 i_enable = 0;  // Disable VDAC
        #60 i_enable = 1;  // Enable VDAC
        #100 $finish;
    end

endmodule
