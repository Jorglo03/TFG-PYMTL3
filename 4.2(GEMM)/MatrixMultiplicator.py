from pymtl3 import * 
from PartialMul import PartialMul

class MatrixMultiplicator(Component): # N * M ciclos para multiplicar dos matrices
    def construct(s, N=3, M=3, K=3):
        s.A = [ [ InPort( 8 ) for _ in range(K) ] for _ in range(N) ]
        s.B = [ [ InPort( 8 ) for _ in range(M) ] for _ in range(N) ]
        s.D = [ [ OutPort( 8 ) for _ in range(M) ] for _ in range(N) ]
        
        s.partialMul = PartialMul(K)
        s.countRow = InPort(bits_necesarios(N))
        s.countCol = InPort(bits_necesarios(M))

        @update
        def update_values():
            for j in range(K):
                s.partialMul.A[j] @= s.A[s.countRow][j]
                s.partialMul.B[j] @= s.B[j][s.countCol]
            s.D[s.countRow][s.countCol] @= s.partialMul.C

    def line_trace(s):
        return f"{[[a.uint() for a in row] for row in s.A]} {[[b.uint() for b in row] for row in s.B]} {[[d.uint() for d in row] for row in s.D]}"
    
def bits_necesarios(N):
    import math
    return math.ceil(math.log2(N+1))

def matrix_multiply(A, B):
    # Inicializar la matriz de resultado con ceros
    result =  [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

    # Realizar la multiplicación de matrices
    for i in range(3):
        for j in range(3):
            for k in range(3):
                result[i][j] += A[i][k] * B[k][j]

    return result



if __name__ == "__main__":
    # Definir las matrices de entrada
    A = [[1, 2, 4], [5, 3, 4], [4, 7, 5]]
    B = [[5, 6, 6], [7, 8, 2], [2, 2, 3]]
    # Multiplicar las matrices
    result = matrix_multiply(A, B)

    # Imprimir el resultado
    print("Resultado de la multiplicación de matrices:")
    for row in result:
        print(row)
    dut = MatrixMultiplicator(3, 3)
    dut.elaborate()
    dut.apply(DefaultPassGroup(linetrace=True))
    dut.sim_reset()

    for i in range(3):
        for j in range(3):
            dut.A[i][j] @= A[i][j]
            dut.B[i][j] @= B[i][j]
   
    dut.reset @= 0
    dut.sim_tick()
    dut.sim_tick()
    dut.sim_tick()
    dut.sim_tick()
    dut.sim_tick()
    dut.sim_tick()

    dut.sim_tick()
    dut.sim_tick()
    dut.sim_tick()
    dut.sim_tick()
    dut.sim_tick()
    dut.sim_tick()
    dut.sim_tick()
    dut.sim_tick()
    dut.sim_tick()
    dut.sim_tick()
    dut.sim_tick()
    dut.sim_tick()

