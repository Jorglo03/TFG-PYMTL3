//-------------------------------------------------------------------------
// ALU_Custom.v
//-------------------------------------------------------------------------
// This file is generated by PyMTL SystemVerilog translation pass.

// PyMTL Component ALU Definition
// Full name: ALU_noparam
// At \\wsl.localhost\Ubuntu\home\raul\TFG\code\src\ALU.py

module ALU_Custom
(
  input  logic [0:0] clk ,
  input  logic [1:0] fn ,
  input  logic [7:0] in0 ,
  input  logic [7:0] in1 ,
  input  logic [0:0] reset ,
  output logic [7:0] result 
);

  // PyMTL Update Block Source
  // At \\wsl.localhost\Ubuntu\home\raul\TFG\code\src\ALU.py:13
  // @update
  // def up_alu():
  //     if s.fn == 0:
  //         s.result @= s.in0 + s.in1
  //     elif s.fn == 1:
  //         s.result @= s.in0 - s.in1
  //     elif s.fn == 2:
  //         s.result @= s.in0 & s.in1
  //     elif s.fn == 3:
  //         s.result @= ~s.in0 + 1
  //     else:
  //         s.result @= 0
  
  always_comb begin : up_alu
    if ( fn == 2'd0 ) begin
      result = in0 + in1;
    end
    else if ( fn == 2'd1 ) begin
      result = in0 - in1;
    end
    else if ( fn == 2'd2 ) begin
      result = in0 & in1;
    end
    else if ( fn == 2'd3 ) begin
      result = ( ~in0 ) + 8'd1;
    end
    else
      result = 8'd0;
  end

endmodule
