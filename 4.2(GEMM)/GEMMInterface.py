from pymtl3 import *
from MatrixAdder import MatrixAdder
from MatrixMultiplicator import MatrixMultiplicator
from ScalarMatrixMultiplicator import ScalarMatrixMultiplicator
from pymtl3.passes.backends.verilog import VerilogTranslationPass
class GEMMInterface(Component): #N x M ciclos
    def construct(s, N=3, M=3, K=3):
        s.alpha = InPort(8)
        s.beta = InPort(8)
        s.A = [ [ InPort( 8 ) for _ in range(K) ] for _ in range(N) ]
        s.B = [ [ InPort( 8 ) for _ in range(M) ] for _ in range(K) ]
        s.C = [ [ InPort( 8 ) for _ in range(M) ] for _ in range(N) ]
        s.D = [ [ OutPort( 8 ) for _ in range(M) ] for _ in range(N) ]

        s.countRow = Wire(bits_necesarios(N))
        s.countCol = Wire(bits_necesarios(M))

        s.scalarMatrixMultiplicatorAlpha = ScalarMatrixMultiplicator(N, M)
        s.scalarMatrixMultiplicatorBeta = ScalarMatrixMultiplicator(N, K)
        s.matrixAdder = MatrixAdder(N, M)
        s.matrixMultiplicator = MatrixMultiplicator(N, M, K)

        s.scalarMatrixMultiplicatorAlpha.count //= s.countRow
        s.scalarMatrixMultiplicatorBeta.count //= s.countRow
        s.matrixAdder.count //= s.countRow
        s.matrixMultiplicator.countRow //= s.countRow
        s.matrixMultiplicator.countCol //= s.countCol


        s.scalarMatrixMultiplicatorAlpha.alpha //= s.beta
        s.scalarMatrixMultiplicatorBeta.alpha //= s.alpha

        for i in range(N):
            for j in range(M):
                s.scalarMatrixMultiplicatorAlpha.A[i][j] //= s.C[i][j]
                s.scalarMatrixMultiplicatorBeta.A[i][j] //= s.A[i][j]
                s.matrixMultiplicator.A[i][j] //= s.scalarMatrixMultiplicatorBeta.C[i][j]
                s.matrixMultiplicator.B[i][j] //= s.B[i][j]
                s.matrixAdder.D[i][j] //= s.matrixMultiplicator.D[i][j]
                s.matrixAdder.C[i][j] //= s.scalarMatrixMultiplicatorAlpha.C[i][j]
                s.matrixAdder.Res[i][j] //= s.D[i][j]

        @update_ff
        def count_register():
            if s.reset:
                s.countRow <<= 0
                s.countCol <<= 0
            else:
                if s.countCol == M - 1:
                    s.countCol <<= 0
                    if s.countRow == N - 1:
                        s.countRow <<= 0
                    else:
                        s.countRow <<= s.countRow + 1
                else:
                    s.countCol <<= s.countCol + 1
                
    
    def line_trace(s):
        return f"{[[d.uint() for d in row] for row in s.D]}"
        

def bits_necesarios(N):
    import math
    return math.ceil(math.log2(N+1))

def gemm(alpha, A, B, beta, C):
    M = len(A)       # Número de filas de A
    K = len(A[0])    # Número de columnas de A (y número de filas de B)
    N = len(B[0])    # Número de columnas de B

    # Inicializar la matriz de resultado con los valores de C escalados por beta
    result = [[beta * C[i][j] for j in range(N)] for i in range(M)]

    # Realizar la operación GEMM
    for i in range(M):
        for j in range(N):
            for k in range(K):
                result[i][j] += alpha * A[i][k] * B[k][j]

    return result

def translate(alu):
    import os

    module_name = "GEMMUnit" 

    if os.path.exists(module_name):
        os.remove(module_name)

    alu.elaborate()
    alu.set_metadata(VerilogTranslationPass.explicit_module_name, module_name)
    alu.set_metadata(VerilogTranslationPass.enable, True)
    

    alu.apply(VerilogTranslationPass())

    os.rename(module_name + "__pickled.v", module_name + ".v")
    print("Código Verilog generado correctamente\n")


if __name__ == "__main__":
    alpha = 2.0
    beta = 1.0

    A = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ]
    B = [
        [9, 8, 7],
        [6, 5, 4],
        [3, 2, 1]
    ]
    C = [
        [1, 1, 1],
        [1, 1, 1],
        [1, 1, 1]
    ]

    result = gemm(alpha, A, B, beta, C)

    # Imprimir el resultado
    print("Resultado de la operación GEMM:")
    for row in result:
        print(row)

    N, M, K = 3,3, 3
    dut = GEMMInterface(N, M, K)
    translate(dut)
    dut.elaborate()
    dut.apply(DefaultPassGroup(linetrace=True))
    dut.sim_reset()
    dut.alpha @= alpha
    dut.beta @= beta
    for i in range(N):
        for j in range(K):
            dut.A[i][j] @= A[i][j]
    for i in range(K):
        for j in range(M):
            dut.B[i][j] @= B[i][j]
    for i in range(N):
        for j in range(M):
            dut.C[i][j] @= C[i][j]
    # dut.reset @= 1
    # dut.sim_tick()
    # dut.reset @= 0
    for i in range(N*M):
        dut.sim_tick()
