from pymtl3 import *
from ScalarVectorMultiplicator import ScalarVectorMultiplicator

class ScalarMatrixMultiplicator(Component): # N ciclos de calculo
    def construct(s, N=3, M=3): 

        s.alpha = InPort(8)
        s.A = [ [ InPort( 8 ) for _ in range(M) ] for _ in range(N) ]
        s.count = InPort(bits_necesarios(N))

        s.C = [ [ OutPort( 8 ) for _ in range(M) ] for _ in range(N) ]

        s.vectorMultiplicator = ScalarVectorMultiplicator(M)

        s.vectorMultiplicator.alpha //= s.alpha


        @update
        def update_values():
            for j in range(M):  # Conectar fila a vectorMultiplicator
                s.vectorMultiplicator.A[j] @= s.A[s.count][j]
                s.C[s.count][j] @= s.vectorMultiplicator.C[j] # No se si tendría que ir dentro de update_ff



    # def line_trace(s):
    #     return f"{s.alpha.uint()} {[[a.uint() for a in row] for row in s.A]} {[[c.uint() for c in row] for row in s.C]} "
def bits_necesarios(N):
    import math
    return math.ceil(math.log2(N+1))

if __name__ == "__main__":
    dut = ScalarMatrixMultiplicator(2, 2)
    dut.elaborate()
    dut.apply(DefaultPassGroup(linetrace=True))
    dut.sim_reset()
    dut.alpha @= 2
    #dut.enable @= 1
    for i in range(2):
        for j in range(2):
            dut.A[i][j] @= 1
    #dut.reset @= 1
    dut.reset @= 0
    dut.sim_tick()
    
    dut.sim_tick()
    for i in range(2):
        for j in range(2):
            dut.A[i][j] @= 2
    dut.sim_tick()
    dut.sim_tick()
    dut.sim_tick()
    
    dut.sim_tick()
    dut.sim_tick()
    dut.sim_tick()
    dut.sim_tick()
    dut.sim_tick()

    print([[i.uint() for i in r] for r in dut.C])