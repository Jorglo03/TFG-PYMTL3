from pymtl3 import *
from pymtl3.passes.backends.verilog import VerilogTranslationPass
from pymtl3.datatypes import clog2, mk_bits, sext, Bits1, bitstruct, b1

class ProductoEscalarPipelined( Component ):

    def construct( s, nelems, nbits = 8 ):
        s.nelems = nelems
        s.a = [InPort( nbits ) for _ in range(nelems)]
        s.b = [InPort( nbits ) for _ in range(nelems)]

        s.n_bits_out = nbits * 2 + clog2(nelems)
        OutBits = mk_bits( s.n_bits_out)
        s.result = OutPort( OutBits )
        
        # Registros para almacenar el resultado de la multiplicación
        s.regs_multiply = [Wire(OutBits) for _ in range(nelems)]

        s.num_levels = clog2(nelems)
        regs_sum_tree = []
        current_nelems = nelems
        s.num_regs = s.nelems >> 1
        for level in range(s.num_levels):
            num_regs = current_nelems >> 1
            next_level_regs = [Wire(OutBits) for _ in range(nelems)] #num_regs para simulacion, nelems para verilog (no permite traduccion si no)
            regs_sum_tree.append(next_level_regs)
            current_nelems = num_regs

        s.regs_sum_tree = regs_sum_tree

        @update_ff
        def stage_1_multiply():
            for i in range(s.nelems):
                s.regs_multiply[i] <<= sext(s.a[i] * s.b[i], s.n_bits_out)
            

        @update_ff
        def stage_2_sum_tree():
            regs_aux = s.nelems
            for i in range(s.num_levels):
                aux = (regs_aux >> 1) 
                for j in range(s.num_regs):
                    if j < aux :
                        if i == 0 :
                            s.regs_sum_tree[i][j] <<= s.regs_multiply[j*2] + s.regs_multiply[j*2 + 1]
                        else:
                            s.regs_sum_tree[i][j] <<= s.regs_sum_tree[i-1][j*2] + s.regs_sum_tree[i-1][j*2 + 1]
                regs_aux = aux
                    
        @update
        def set_output():
            s.result @= s.regs_sum_tree[ s.num_levels-1 ][0]

    def line_trace( s ):
        a_vals = ' '.join([ f"{int(x.int())}" for x in s.a ])
        b_vals = ' '.join([ f"{int(x.int())}" for x in s.b ])
        mult_vals = ' '.join([ f"{int(x.int())}" for x in s.regs_multiply ])
        tree_vals = ' '.join([ f"{int(x.int())}" for level in s.regs_sum_tree for x in level ])

        return f"A: {a_vals} | B: {b_vals} || Mult: {mult_vals} || Tree: {tree_vals} => Result: {int(s.result.int())}"


def translate(dut):
    import os

    module_name = "ProductoEscalarPipeline" 

    if os.path.exists(module_name + ".v"):
        os.remove(module_name + ".v")

    dut.elaborate()
    dut.set_metadata(VerilogTranslationPass.explicit_module_name, module_name)
    dut.set_metadata(VerilogTranslationPass.enable, True)
    

    dut.apply(VerilogTranslationPass())

    os.rename(module_name + "__pickled.v", module_name + ".v")
    print("Código Verilog generado correctamente\n")

def producto_escalar(v1, v2):

    resultado = 0
    for i in range(len(v1)):
        resultado += v1[i] * v2[i]
    
    return resultado

def set_data(dut, vec_a, vec_b):
    """ Función auxiliar para asignar datos a las entradas del DUT """
    for i in range(dut.nelems):
        dut.a[i] @= vec_a[i]
        dut.b[i] @= vec_b[i]

def test(dut, expected, n):

    for i in range(clog2(n)):
        dut.sim_tick()
    dut.sim_tick()
    # Verificar resultado
    assert dut.result.int() == expected, f"Error! Esperado: {expected}, Obtenido: {int(dut.result.int())}"
    print(f"  Resultado: {int(dut.result.int())} == Esperado: {expected} -> OK")


def test_pe_pipelined_caso1():
    dut = ProductoEscalarPipelined(4, 8)
    dut.apply(DefaultPassGroup(linetrace=True))
    dut.sim_reset()
    # --- Datos de Prueba ---
    inputs_a = [
        [1, 2, 3, 4],       # Ciclo 1 entrada -> Salida esperada en Ciclo 1+L
        [-1, -1, -1, -1],   # Ciclo 2 entrada -> Salida esperada en Ciclo 2+L
        [10, 0, -10, 0],    # Ciclo 3 entrada -> ...
        [5, 5, 5, 5],
        [1, 0, 1, 0]
    ]
    inputs_b = [
        [5, 6, 7, 8],       # -> 70
        [1, 2, 3, 4],       # -> -10
        [1, 1, 1, 1],       # -> 0
        [-1, -1, -1, -1],   # -> -20
        [0, 1, 0, 1]        # -> 0
    ]
    num_inputs = len(inputs_a)
    expected_outputs = [producto_escalar(a, b) for a, b in zip(inputs_a, inputs_b)]
    
    for i in range(num_inputs):
        set_data(dut, inputs_a[i], inputs_b[i])
        dut.sim_tick()
    dut.sim_tick()
    dut.sim_tick()
    dut.sim_tick()
        
    # Expected: [70, -10, 0, -20, 0]

def test1():
    import random
    dut = ProductoEscalarPipelined(4)
    dut.apply(DefaultPassGroup(linetrace=True))
    dut.sim_reset()
    vec_a = [1,2,3,4]
    vec_b = [5,6,7,8]
    set_data(dut, vec_a, vec_b)
    expected = producto_escalar(vec_a, vec_b)
    test(dut, expected, 4)
    dut.sim_tick()
    vec_c = [random.randint(-10, 10) for _ in range(4)]
    vec_d = [random.randint(-10, 10) for _ in range(4)]
    set_data(dut, vec_c, vec_d)
    expected = producto_escalar(vec_c, vec_d)
    test(dut, expected, 4)

    dut.sim_tick()

def test2():
    import random
    dut = ProductoEscalarPipelined(8, 16)
    dut.apply(DefaultPassGroup(linetrace=True))
    dut.sim_reset()
    vec_a = [1,2,3,4,5,6,7,8]
    vec_b = [9,10,11,12,13,14,15,16]
    
    set_data(dut, vec_a, vec_b)
    expected = producto_escalar(vec_a, vec_b)
    test(dut, expected, 8)
    vec_c = [random.randint(-10, 10) for _ in range(8)]
    vec_d = [random.randint(-10, 10) for _ in range(8)]
    set_data(dut, vec_c, vec_d)
    expected = producto_escalar(vec_c, vec_d)
    test(dut, expected, 8)

def test3():
    import random
    dut = ProductoEscalarPipelined(16, 16)
    dut.apply(DefaultPassGroup(linetrace=True))
    dut.sim_reset()
    vec_a = [1,2,3,4,5,6,7,8, 9,10,11,12,13,14,15,16]
    vec_b = [9,10,11,12,13,14,15,16, 17,18,19,20,21,22,23,24]
    
    set_data(dut, vec_a, vec_b)
    dut.sim_tick()
    vec_c = [random.randint(-10, 10) for _ in range(16)]
    vec_d = [random.randint(-10, 10) for _ in range(16)]
    set_data(dut, vec_c, vec_d)
    expected1 = producto_escalar(vec_a, vec_b)
    #test(dut, expected, 16)
    expected2 = producto_escalar(vec_c, vec_d)
    for i in range(clog2(16)):
        dut.sim_tick()
    assert dut.result.int() == expected1, f"Error! Esperado: {expected1}, Obtenido: {int(dut.result.int())}"
    print(f"  Resultado: {int(dut.result.int())} == Esperado: {expected1} -> OK")
    dut.sim_tick()
    assert dut.result.int() == expected2, f"Error! Esperado: {expected2}, Obtenido: {int(dut.result.int())}"
    print(f"  Resultado: {int(dut.result.int())} == Esperado: {expected2} -> OK")
    #test(dut, expected, 16)



# Ejecutar todos los tests
if __name__ == "__main__":
    test1()
    test2()
    test3()
    test_pe_pipelined_caso1()
    dut = ProductoEscalarPipelined(4)
    translate(dut)