from pymtl3 import *
from pymtl3.passes.backends.verilog import VerilogTranslationPass
from pymtl3.datatypes import clog2, mk_bits, sext, zext

class ProductoEscalar( Component ):
    def construct( s, nelems, nbits ):
        s.nelems = nelems
        s.a = [InPort( nbits ) for _ in range(nelems)]
        s.b = [InPort( nbits ) for _ in range(nelems)]

        s.n_bits_out = nbits * 2 + clog2(nelems)
        OutBits = mk_bits( s.n_bits_out)
        s.result = OutPort( OutBits )

        @update
        def compute():
            acc = mk_bits(s.n_bits_out)(0)  # Inicializa el acumulador a 0
            print("=== Cálculo paso a paso ===")
            for i in range(s.nelems):
                product = sext(s.a[i] * s.b[i], s.n_bits_out)
                acc = acc + product

                print(f"Paso {i}:")
                print(f"  Producto parcial: b[{i}] * a[{i}] = {product.int()}")
                print(f"  Acumulador parcial: {int(acc.int())}")
            s.result @= acc
            print(f"Resultado final del producto escalar: {int(acc.int())}")
            print("============================\n")


    def line_trace( s ):
        # Convierte los vectores de entrada Bits a enteros para mostrarlos
        in_a_str = ",".join( str(p.int()) for p in s.a )
        in_b_str = ",".join( str(p.int()) for p in s.b )
        # Convierte el resultado Bits a entero
        out_str = str(int(s.result.int()))
        return f"A:[{in_a_str}] * B:[{in_b_str}] = {out_str}"
    
def run_test( dut, vec_a, vec_b, expected ):
    """ Función auxiliar para ejecutar un caso de prueba """
    print(f"\nProbando: A={vec_a}, B={vec_b}")
    # Asignar entradas
    for i in range(dut.nelems):
        dut.a[i] @= vec_a[i]
        dut.b[i] @= vec_b[i]

    # Evaluar lógica combinacional
    dut.sim_eval_combinational()

    # Imprimir traza
    print(f"  Trace: {dut.line_trace()}")

    # Verificar resultado
    assert dut.result.int() == expected, f"Error! Esperado: {expected}, Obtenido: {int(dut.result.int())}"
    print(f"  Resultado: {int(dut.result.int())} == Esperado: {expected} -> OK")

# Test principal (se ejecuta si corres este script directamente)
if __name__ == '__main__':
    NELEMS = 3
    NBITS = 9

    # Instanciar el componente
    dut = ProductoEscalar( NELEMS, NBITS )

    # Elaborar el diseño (necesario antes de simular)
    dut.apply( DefaultPassGroup() )

    # Reiniciar la simulación
    dut.sim_reset()
    print("Simulación iniciada y reseteada.")

    # --- Caso de Prueba 1 ---
    vec_a1 = [1, 2, 3]
    vec_b1 = [4, 5, 6]
    # Esperado: 1*4 + 2*5 + 3*6 = 4 + 10 + 18 = 32
    expected1 = 32
    run_test( dut, vec_a1, vec_b1, expected1 )

    # --- Caso de Prueba 2 ---
    vec_a2 = [10, 20, 0]
    vec_b2 = [-5, 2, 99]
    # Esperado: 10*(-5) + 20*2 + 0*99 = -50 + 40 + 0 = 90
    expected2 = -10
    run_test( dut, vec_a2, vec_b2, expected2 )

    # --- Caso de Prueba 3 (Valores máximos para 9 bits) ---
    # Si NBITS=9, max val = 255
    # Ajusta esto si cambias NBITS
    if NBITS == 9:
        vec_a3 = [255, 1, -10]
        vec_b3 = [1, 255, 10]
        # Esperado: 255*1 + 1*255 + -10*10 = 255 + 255 - 100 = 410
        expected3 = 410
        run_test( dut, vec_a3, vec_b3, expected3 )

    print("\n¡Todas las pruebas pasaron!")