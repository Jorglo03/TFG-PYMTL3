from pymtl3 import *
from pymtl3.passes.backends.verilog import VerilogTranslationPass
from pymtl3.datatypes import clog2, mk_bits, sext, Bits1

class ProductoEscalarSecuencial( Component ):
    def construct( s, nelems, nbits):
        s.nelems = nelems
        s.a = [InPort( nbits ) for _ in range(nelems)]
        s.b = [InPort( nbits ) for _ in range(nelems)]

        s.n_bits_out = nbits * 2 + clog2(nelems)
        OutBits = mk_bits( s.n_bits_out)
        s.result = OutPort( OutBits )
        
        # Señales de control
        s.en = InPort(Bits1)
        s.valid = OutPort(Bits1)

        # Contador
        IdxBits = mk_bits(clog2(nelems + 1))
        s.acc = Wire(OutBits)
        s.idx = Wire(IdxBits)
        s.product_extended = Wire(OutBits)

        # Estados 
        StateBits = mk_bits(2)
        s.state = Wire(StateBits)
        s.STATE_IDLE = mk_bits(2)(0)
        s.STATE_CALC = mk_bits(2)(1)
        s.STATE_DONE = mk_bits(2)(2)

        @update_ff
        def up_state():
            if s.reset:
                s.state <<= s.STATE_IDLE
                s.acc <<= 0
                s.idx <<= 0
            else:
                if s.state == s.STATE_IDLE:
                    if s.en:
                        s.state <<= s.STATE_CALC
                        s.idx <<= 0
                        s.acc <<= 0
                elif s.state == s.STATE_CALC:
                    s.acc <<= s.acc + s.product_extended
                    if s.idx < s.nelems:
                        s.idx <<= s.idx + 1
                        if s.idx == s.nelems - 1:
                            s.state <<= s.STATE_DONE
            
                elif s.state == s.STATE_DONE:
                    s.state <<= s.STATE_IDLE
                    s.idx <<= 0
        @update
        def up_result():
            s.result @= s.acc
            s.valid @= (s.state == s.STATE_DONE)

            idx_val = s.idx
            current_a = mk_bits(nbits)(0)
            current_b = mk_bits(nbits)(0)
            if idx_val < s.nelems:
                current_a @= s.a[idx_val]
                current_b @= s.b[idx_val]

            product_intermediate = current_a * current_b
            s.product_extended @= sext(product_intermediate, s.n_bits_out)


    def line_trace( s ):
        st_str = "I" if s.state == s.STATE_IDLE else \
                 "C" if s.state == s.STATE_CALC else \
                 "D"
        return (f"[{st_str}] en:{s.en} idx:{int(s.idx):2d} "
                f"acc:{int(s.acc.int()):<5d} | " 
                f"res:{int(s.result.int()):<5d}({int(s.valid)})")
    
    
def run_test( dut, test_name, vec_a, vec_b, expected ):

    nelems = dut.nelems
    print(f"\n--- {test_name}: A={vec_a}, B={vec_b}, Esperado={expected} ---")
    print(" Ciclo | Trace")
    print("--------|------------------------------------------------------")

    for i in range(nelems):
        dut.a[i] @= vec_a[i]
        dut.b[i] @= vec_b[i]
    dut.en @= 0
    dut.sim_eval_combinational()
    print(f" Load  | {dut.line_trace()}")

    # Ciclo 0: Habilitar
    dut.en @= 1
    dut.sim_tick()
    print(f"  0    | {dut.line_trace()}") # Estado debe pasar a CALC

    # Ciclos 1 a nelems: Calcular
    dut.en @= 0
    for i in range(nelems):
        dut.sim_tick()
        if i == nelems - 1:
            print(f" {i+1:<5d}* | {dut.line_trace()}") # Muestra progreso del cálculo
        else:
            print(f" {i+1:<5d} | {dut.line_trace()}") # Muestra progreso del cálculo
    
    # Ciclo nelems + 1: Resultado debería estar válido
    #print(f" {nelems+1:<5d}*| {dut.line_trace()}") 

    assert dut.valid == 1, f"ERROR: valid no es 1 en ciclo {nelems + 1}"
    assert dut.result.int() == expected, f"ERROR: Resultado incorrecto en ciclo {nelems+1}. Esperado={expected}, Obtenido={int(dut.result)}"
    print(f" Resultado OK en ciclo {nelems }!")

    # Avanzar para ver la vuelta a IDLE
    dut.sim_tick()
    print(f" {nelems+1:<5d}* | {dut.line_trace()}")

    # Ciclo nelems + 2: Comprobar que valid es 0
    dut.sim_eval_combinational()
    print(f" {nelems+2:<5d}| {dut.line_trace()}")
    assert dut.valid == 0, f"ERROR: valid no es 0 en ciclo {nelems + 2}"


NELEMS = 3
NBITS = 8

def test_pe_seq_caso1_mezcla():
    dut = ProductoEscalarSecuencial(NELEMS, NBITS)
    dut.apply( DefaultPassGroup() )
    dut.sim_reset()
    run_test( dut, "Test 1 (Mezcla Pos/Neg)",
              vec_a=[1, -2, 3], vec_b=[-4, 5, -6], expected=-32 )

def test_pe_seq_caso2_negativos():
    dut = ProductoEscalarSecuencial(NELEMS, NBITS)
    dut.apply( DefaultPassGroup() )
    dut.sim_reset()
    run_test( dut, "Test 2 (Todos Negativos)",
              vec_a=[-10, -5, -1], vec_b=[-2, -4, -8], expected=48 )

def test_pe_seq_caso3_limites():
    dut = ProductoEscalarSecuencial(NELEMS, NBITS + 1)
    dut.apply( DefaultPassGroup() )
    dut.sim_reset()
    run_test( dut, "Test 3 (Límites NBITS=8)",
              vec_a=[127, -128, 1], vec_b=[1, -1, -128], expected=127 )

def test_pe_seq_caso4_ceros():
    dut = ProductoEscalarSecuencial(NELEMS, NBITS)
    dut.apply( DefaultPassGroup() )
    dut.sim_reset()
    run_test( dut, "Test 4 (Ceros)",
              vec_a=[0, 0, 0], vec_b=[10, -20, 30], expected=0 )

def test_pe_seq_caso5_resultado_grande():
    dut = ProductoEscalarSecuencial(NELEMS, NBITS + 1)
    dut.apply( DefaultPassGroup() )
    dut.sim_reset()
    run_test( dut, "Test 5 (Resultado > 127)",
              vec_a=[100, 10, 5], vec_b=[2, 10, 6], expected=330 )

if __name__ == '__main__':
    test_pe_seq_caso1_mezcla()
    test_pe_seq_caso2_negativos()
    test_pe_seq_caso3_limites()
    test_pe_seq_caso4_ceros()
    test_pe_seq_caso5_resultado_grande()

    print("\n--- FIN DE EJECUCIÓN DIRECTA ---")
