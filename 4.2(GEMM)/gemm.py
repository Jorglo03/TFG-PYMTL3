from pymtl3 import *
from pymtl3.passes.backends.verilog import VerilogTranslationPass

class GEMMUnit(Component):
    def construct(s, M=3, K=3, N=3):  
        
        # Interfaces
        s.A = [ [ InPort( 8 ) for _ in range(K) ] for _ in range(M) ]
        s.B = [ [ InPort( 8 ) for _ in range(N) ] for _ in range(K) ]
        s.C = [ [ InPort( 8 ) for _ in range(M) ] for _ in range(N) ]
        s.alpha = InPort(8)
        s.beta  = InPort(8)
        s.D = [ [ OutPort( 8 ) for _ in range(N) ] for _ in range(M) ]     
        
        @update
        def compute_gemm():
            for i in range(M):
                for j in range(N):
                    acc = s.beta * s.C[i][j]  # Escalar C
                    for k in range(K):
                        acc = acc + s.alpha * s.A[i][k] * s.B[k][j]  # Producto de matrices
                    s.D[i][j] @= acc

    def line_trace(s):
        return f"{[[d.uint() for d in row] for row in s.D]}"


def translate(alu):
    import os

    module_name = "GEMMComb" 

    if os.path.exists(module_name + "__pickled.v"):
        os.remove(module_name + "__pickled.v")

    alu.elaborate()
    alu.set_metadata(VerilogTranslationPass.explicit_module_name, module_name)
    alu.set_metadata(VerilogTranslationPass.enable, True)
    

    alu.apply(VerilogTranslationPass())

    os.rename(module_name + "__pickled.v", module_name + ".v")
    print("Código Verilog generado correctamente\n")

def gemm(alpha, A, B, beta, C):
    # Obtener las dimensiones de las matrices de entrada
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

if __name__ == "__main__":
    # Definir los escalares
    alpha = 1.0
    beta = 2.0

    # Definir las matrices de entrada (3x3) con elementos más sencillos
    A = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ]
    C = [
        [9, 8, 7],
        [6, 5, 4],
        [3, 2, 1]
    ]
    B = [
        [1, 1, 1],
        [1, 1, 1],
        [1, 1, 1]
    ]

    # Realizar la operación GEMM
    result = gemm(alpha, A, B, beta, C)

    # Imprimir el resultado
    print("Resultado de la operación GEMM:")
    for row in result:
        print(row)
    N, M = 3, 3
    dut = GEMMUnit(N, M, 3)
    translate(dut)
    dut.elaborate()
    dut.apply(DefaultPassGroup(linetrace=True))
    dut.sim_reset()
    dut.alpha @= alpha
    dut.beta @= beta
    for i in range(N):
        for j in range(M):
            dut.A[i][j] @= A[i][j]
            dut.B[i][j] @= B[i][j]
            dut.C[i][j] @= C[i][j]
    #translate(gemm)
    dut.sim_tick()
    dut.sim_tick()
    #print(dut.result.uint())

    