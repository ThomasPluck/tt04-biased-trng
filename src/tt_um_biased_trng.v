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
    parameter BITWIDTH = 6;
    parameter NUM_OSCILLATORS = 15;
    parameter OSCILLATOR_LENGTH = 6;

    // Instantiate ring oscillator
    wire osc;
    multiple_ring_oscillators #(.NUM_OSCILLATORS(NUM_OSCILLATORS), .OSCILLATOR_LENGTH(OSCILLATOR_LENGTH)) ring_osc_inst(.ena(ena), .final_osc(osc));


    // Control signals for VDAC
    reg [BITWIDTH:0] i_data = 0;
    wire vdac_out;
    vdac #(.BITWIDTH(BITWIDTH)) vdac_inst(.i_data(i_data), .i_enable(ena), .vout_notouch_(vdac_out));

    // Instantiate bias
    wire bias_out;
    bias bias_inst(.BUF(osc), .CTRL(vdac_out), .OUT(bias_out));

    // Setting up control for VDAC based on the provided description
    assign i_data[5:0] = ui_in[5:0];

    // Instantiate two D flip-flops with reset
    wire dff1_out, dff2_out;
    sky130_fd_sc_hd__dfrtp_1 dff1(.CLK(clk), .D(bias_out), .RESET_B(rst_n), .Q(dff1_out));
    sky130_fd_sc_hd__dfrtp_1 dff2(.CLK(clk), .D(dff1_out), .RESET_B(rst_n), .Q(dff2_out));
    sky130_fd_sc_hd__and2_1 out_and(.A(ena), .B(dff2_out), .X(uo_out[0]));

    // Tie unused wires low
    assign uo_out[7:6] = 2'b0;
    assign uo_out[7:1] = 7'b0;
    assign uio_out = 8'b0;
    assign uio_oe = 8'b0;

endmodule
