from pymtl3 import *
from pymtl3.passes.backends.verilog import VerilogTranslationPass

class ALU(Component):
    def construct(s):
        
        s.in0 = InPort(8)
        s.in1 = InPort(8)
        s.fn  = InPort(2)
        s.out = OutPort(8)
    
        @update
        def up_alu():
            if s.fn == 0:
                s.out @= s.in0 + s.in1
            elif s.fn == 1:
                s.out @= s.in0 - s.in1
            elif s.fn == 2:
                s.out @= s.in0 & s.in1
            elif s.fn == 3:
                s.out @= ~s.in0 + 1
            else:
                s.out @= 0
        
def translate(alu):
    import os

    module_name = "ALU_Custom" 

    if os.path.exists(module_name + "__pickled.v"):
        os.remove(module_name + "__pickled.v")

    alu.elaborate()
    alu.set_metadata(VerilogTranslationPass.explicit_module_name, module_name)
    alu.set_metadata(VerilogTranslationPass.enable, True)
    

    alu.apply(VerilogTranslationPass())

    os.rename(module_name + "__pickled.v", module_name + ".v")
    print("Código Verilog generado correctamente\n")


def run_test(in0, in1, fn, expected):
    dut = ALU()
    dut.apply(DefaultPassGroup())
    dut.sim_reset()

    dut.in0 @= in0
    dut.in1 @= in1
    dut.fn  @= fn
    dut.sim_eval_combinational()

    result = int(dut.out.int())
    print(f"ALU({in0}, {in1}, fn={fn}) => {result} (expected {expected})", 
          "✓" if result == expected else "✗")

if __name__ == "__main__":
    print("Running ALU tests...\n")
    translate(ALU())
    run_test(10, 5, 0, 15)              # ADD
    run_test(10, 5, 1, 5)               # SUB
    run_test(10, 5, 2, 0)               # AND (0b1010 & 0b0101 = 0)
    run_test(10, 0, 3, -10)    # NEG (convert to 8-bit unsigned)
