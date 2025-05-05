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
                s.out @= -s.in0
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


if __name__ == '__main__':
    alu = ALU()
    translate(alu)