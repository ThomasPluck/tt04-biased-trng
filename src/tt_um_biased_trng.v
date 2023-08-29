`include "cells.v"
`include "vdac.v"
`include "biased_rosc.v"

`default_nettype none

module tt_um_biased_trng (
    input  wire [7:0] ui_in,    // Dedicated inputs - connected to the input switches
    output wire [7:0] uo_out,   // Dedicated outputs - connected to the 7 segment display
    input  wire [7:0] uio_in,   // IOs: Bidirectional Input path
    output wire [7:0] uio_out,  // IOs: Bidirectional Output path
    output wire [7:0] uio_oe,   // IOs: Bidirectional Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // will go high when the design is enabled
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

    // Parameters
    parameter BITWIDTH = 8;

    // Instantiate ring oscillator
    wire osc;
    ring_osc ring_osc_inst(.nrst(rst_n), .osc(osc));

    // Instantiate bias
    wire bias_out;
    bias bias_inst(.BUF(osc), .CTRL(), .OUT(bias_out));  // CTRL will be connected later

    // Control signals for VDAC
    reg [BITWIDTH-1:0] i_data = 0;
    wire vdac_out;
    vdac vdac_inst(BITWIDTH)(.i_data(i_data), .i_enable(ena), .vout_notouch_(vdac_out));

    // Connecting VDAC to bias
    assign bias_inst.CTRL = vdac_out;

    // Setting up control for VDAC based on the provided description
    assign i_data[0] = ui_in[0];
    assign i_data[1] = ui_in[0];
    assign i_data[2] = ui_in[0];
    assign i_data[3] = ui_in[0];
    assign i_data[4] = ui_in[1];
    assign i_data[5] = ui_in[1];
    assign i_data[6] = ui_in[2];

    // Instantiate two D flip-flops
    wire dff1_out;
    dff_cell dff1(.clk(clk), .d(bias_out), .q(dff1_out), .notq());
    dff_cell dff2(.clk(clk), .d(dff1_out), .q(uo_out[0]), .notq());

endmodule
