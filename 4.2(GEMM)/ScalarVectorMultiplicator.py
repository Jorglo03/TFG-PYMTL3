from pymtl3 import *
from pymtl3.stdlib.test_utils import run_test_vector_sim
from Multiplier import Multiplier
#Multiplica un vector de longitud N por un escalar alpha
class ScalarVectorMultiplicator(Component):
    def construct(s, N=3): 
        # Valorar si usar implementacion propia de un multiplicador o la que utilice la herramienta
        s.A = [ InPort( 8 ) for _ in range(N) ]
        s.C = [ OutPort( 8 ) for _ in range(N) ]
        s.alpha = InPort(8)
        
        s.multipliers = [ Multiplier() for _ in range(N) ]
        
        for i in range(N):
            s.multipliers[i].a //= s.alpha
            s.multipliers[i].b //= s.A[i]
            s.C[i] //= s.multipliers[i].result
        # @update
        # def compute_scalar_matrix_mul():
        #     for i in range(N):
        #         s.C[i] @= s.alpha * s.A[i]
    
    # def line_trace(s):
    #     return f"{s.alpha.uint()} {[a.uint() for a in s.A]} {[c.uint() for c in s.C]}"



def test_scalar_matrix_multiplication():
    import random
    N = 3  # Longitud del vector
    
    # Definir la tabla de test vectorial
    test_vector_table = [('alpha',) + tuple(f'A[{i}]' for i in range(N)) + tuple(f'C[{i}]*' for i in range(N))]

    # Generar casos de prueba aleatorios
    for _ in range(20):
        alpha = random.randint(1, 10)  # Valor escalar aleatorio
        A = [random.randint(0, 10) for _ in range(N)]  # Vector aleatorio
        C = [alpha * A[i] for i in range(N)]  # Resultado esperado

        test_vector_table.append([alpha] + A + C)

    # Ejecutar la simulación con los test vectors
    run_test_vector_sim(ScalarVectorMultiplicator(N), test_vector_table, cmdline_opts=None)

test_scalar_matrix_multiplication()