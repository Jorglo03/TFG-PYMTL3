from pymtl3 import *
from pymtl3.stdlib.test_utils import run_test_vector_sim

# Suma dos vectores de longitud N
class VectorAdder(Component):
    def construct(s, N): 
        s.A = [ InPort( 8 ) for _ in range(N) ]
        s.B = [ InPort( 8 ) for _ in range(N) ]
        s.C = [ OutPort( 8 ) for _ in range(N) ]
        
        @update
        def compute_sum():
            for i in range(N):
                s.C[i] @= s.A[i] + s.B[i]
    
    # rastreo de línea
    def line_trace(s):
        return f"A={[int(a) for a in s.A]} B={[int(b) for b in s.B]} C={[int(c) for c in s.C]}"

def test_vector_adder():
    import random
    N = 3  # Longitud del vector
    
    test_vector_table = [tuple(f'A[{i}]' for i in range(N)) + tuple(f'B[{i}]' for i in range(N)) + tuple(f'C[{i}]*' for i in range(N))]
    for _ in range(20):
        A = [random.randint(1, 10) for _ in range(N)]  # Vector aleatorio
        B = [random.randint(1, 10) for _ in range(N)]  # Vector aleatorio
        C = [A[i] + B[i] for i in range(N)]  # Resultado esperado

        test_vector_table.append(A + B + C)

    run_test_vector_sim(VectorAdder(N), test_vector_table, cmdline_opts=None)
    print("Todas las pruebas se completaron correctamente.")


test_vector_adder()
