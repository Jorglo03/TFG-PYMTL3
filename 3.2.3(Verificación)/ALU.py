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

    if os.path.exists(module_name + ".v"):
        os.remove(module_name + ".v")

    alu.elaborate()
    alu.set_metadata(VerilogTranslationPass.explicit_module_name, module_name)
    alu.set_metadata(VerilogTranslationPass.enable, True)
    

    alu.apply(VerilogTranslationPass())

    os.rename(module_name + "__pickled.v", module_name + ".v")
    print("Código Verilog generado correctamente\n")


if __name__ == '__main__':
    alu = ALU()
    translate(alu)

     # Test 1: ADD
    dut = ALU()
    dut.vcd_timescale = "1ns"
    dut.apply(DefaultPassGroup(textwave="test"))
    dut.sim_reset()
    dut.in0 @= 10
    dut.in1 @= 5
    dut.fn  @= 0
    dut.sim_tick()
    result = int(dut.out.int())
    print(f"ALU(10, 5, fn=0) => {result} (expected 15)", "Correcto" if result == 15 else "X")

    # Test 2: SUB
    dut.sim_reset()
    dut.in0 @= 10
    dut.in1 @= 5
    dut.fn  @= 1
    dut.sim_tick()
    result = int(dut.out.int())
    print(f"ALU(10, 5, fn=1) => {result} (expected 5)", "Correcto" if result == 5 else "X")

    # Test 3: AND
    dut.sim_reset()
    dut.in0 @= 10
    dut.in1 @= 5
    dut.fn  @= 2
    dut.sim_tick()
    result = int(dut.out.int())
    print(f"ALU(10, 5, fn=2) => {result} (expected 0)", "Correcto" if result == 0 else "X")

    # Test 4: NEG
    dut.sim_reset()
    dut.in0 @= 10
    dut.in1 @= 0
    dut.fn  @= 3
    dut.sim_tick()
    result = int(dut.out.int())
    print(f"ALU(10, 0, fn=3) => {result} (expected -10)", "Correcto" if result == -10 else "X")

    dut.print_textwave()