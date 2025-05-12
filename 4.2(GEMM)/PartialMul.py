from pymtl3 import *
from pymtl3.stdlib.test_utils import run_test_vector_sim

class PartialMul(Component):
    def construct(s, N=3): 
        s.A = [ InPort( 8 ) for _ in range(N) ]
        s.B = [ InPort( 8 ) for _ in range(N) ]
        s.C = OutPort( 8 )
        
        s.Aux = Wire(8)
        @update
        def compute_mul():
            s.Aux @= 0
            for k in range(N):
                s.Aux @= s.Aux + s.A[k] * s.B[k]
            s.C @= s.Aux

    # def line_trace(s):
    #     return f"{[a.uint() for a in s.A]} {[b.uint() for b in s.B]} {s.C.uint()}"
    
def test_partial_mul():
    import random
    N = 3  # Longitud del vector
    
    test_vector_table = [tuple(f'A[{i}]' for i in range(N)) + tuple(f'B[{i}]' for i in range(N)) + ('C*',)]
    for _ in range(20):
        A = [random.randint(1, 10) for _ in range(N)]  # Vector aleatorio
        B = [random.randint(1, 10) for _ in range(N)]  # Vector aleatorio
        C = sum(A[i] * B[i] for i in range(N))  # Resultado esperado

        test_vector_table.append(tuple(A) + tuple(B) + (C,))  # Convertir listas en tuplas

    run_test_vector_sim(PartialMul(N), test_vector_table, cmdline_opts=None)

test_partial_mul()