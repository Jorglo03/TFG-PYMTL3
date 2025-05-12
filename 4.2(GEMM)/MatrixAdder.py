from pymtl3 import * 
from VectorAdder import VectorAdder

class MatrixAdder(Component):
    def construct(s, N=3, M=3): # N ciclos de calculo
        s.C = [ [ InPort( 8 ) for _ in range(M) ] for _ in range(N) ]
        s.D = [ [ InPort( 8 ) for _ in range(M) ] for _ in range(N) ]
        s.count = InPort(bits_necesarios(N))
        s.Res = [ [ OutPort( 8 ) for _ in range(M) ] for _ in range(N) ]

        s.vectorAdder = VectorAdder(N)


        # @update 
        # def up():
        #     for i in range(N):
        #         for j in range(M):
        #             s.Res[i][j] @= s.C[i][j] + s.D[i][j]
        @update
        def update_values():
            for j in range(M):
                s.vectorAdder.A[j] @= s.C[s.count][j]
                s.vectorAdder.B[j] @= s.D[s.count][j]
                s.Res[s.count][j] @= s.vectorAdder.C[j]
        
    # def line_trace(s):
    #     return f"{[[c.uint() for c in row] for row in s.C]} {[[d.uint() for d in row] for row in s.D]} {[[r.uint() for r in row] for row in s.Res]}"
    
def bits_necesarios(N):
    import math
    return math.ceil(math.log2(N+1))


if __name__ == "__main__":
    dut = MatrixAdder(2, 2)
    dut.elaborate()
    dut.apply(DefaultPassGroup(linetrace=True))
    dut.sim_reset()
    for i in range(2):
        for j in range(2):
            dut.C[i][j] @= 1
            dut.D[i][j] @= 1
    dut.reset @= 0
    dut.sim_tick()
    dut.sim_tick()
    for i in range(2):
        for j in range(2):
            dut.C[i][j] @= 2
            dut.D[i][j] @= 2
    dut.sim_tick()
    dut.sim_tick()
    dut.sim_tick()