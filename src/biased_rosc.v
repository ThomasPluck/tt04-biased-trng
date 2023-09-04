`timescale 1ns/10ps

module ring_osc(input ena, output osc);

    localparam NUM_INVERTERS = 150; // must be an even number

    // setup loop of inverters
    wire [NUM_INVERTERS-1:0] delay_in, delay_out;
    wire osc_out;

    genvar i;
    generate
        for (i = 0; i < NUM_INVERTERS; i = i + 1) begin : inv_gen
            sky130_fd_sc_hd__inv_1 idelay_i (.A(delay_in[i]), .Y(delay_out[i]));
        end
    endgenerate

    assign delay_in = {delay_out[NUM_INVERTERS-2:0], osc_out};
    sky130_fd_sc_hd__nand2_1 nand(.A(ena), .B(delay_out[NUM_INVERTERS-1]), .Y(osc_out));
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