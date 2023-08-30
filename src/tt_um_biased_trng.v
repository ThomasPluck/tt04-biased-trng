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
    parameter NUM_OSCILLATORS = 6;
    parameter OSCILLATOR_LENGTH = 7;

    // Instantiate ring oscillator
    wire osc;
    multiple_ring_oscillators #(.NUM_OSCILLATORS(NUM_OSCILLATORS), .OSCILLATOR_LENGTH(OSCILLATOR_LENGTH)) ring_osc_inst(.ena(ena), .osc(osc));


    // Control signals for VDAC
    reg [BITWIDTH:0] i_data = 0;
    wire vdac_out;
    vdac #(.BITWIDTH(BITWIDTH)) vdac_inst(.i_data(i_data), .i_enable(ena), .vout_notouch_(vdac_out));

    // Instantiate bias
    wire bias_out;
    bias bias_inst(.BUF(osc), .CTRL(vdac_out), .OUT(bias_out));  // CTRL will be connected later

    // Setting up control for VDAC based on the provided description
    assign i_data[0] = ui_in[1];
    assign i_data[1] = ui_in[1];
    assign i_data[2] = ui_in[1];
    assign i_data[3] = ui_in[1];
    assign i_data[4] = ui_in[2];
    assign i_data[5] = ui_in[2];
    assign i_data[6] = ui_in[3];
    assign i_data[7] = ui_in[0];

    // Instantiate two D flip-flops with reset
    wire dff1_out, dff2_out;
    dffsr_cell dff1(.clk(clk), .d(bias_out), .s(1'b0), .r(rst_n), .q(dff1_out), .notq());
    dffsr_cell dff2(.clk(clk), .d(dff1_out), .s(1'b0), .r(rst_n), .q(dff2_out), .notq());
    and2_with_delay out_and(.A(ena), .B(dff2_out), .Y(uo_out[0]));

    // Tie unused wires low
    assign uo_out[7:1] = 7'b0;
    assign uio_out = 8'b0;
    assign uio_oe = 8'b0;

endmodule
