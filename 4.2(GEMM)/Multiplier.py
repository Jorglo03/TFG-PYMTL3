from pymtl3 import *

class Multiplier(Component):
    def construct(s):
        s.a = InPort(8)
        s.b = InPort(8)
        s.result = OutPort(8)

        @update
        def multiply():
            # temp = 0
            # for i in range(8):
            #     if s.b[i] == 1:
            #         temp = temp + (s.a << i)
            # s.result @= temp
            s.result @= s.a * s.b

    # def line_trace(s):
    #     return f"a={s.a.uint()} b={s.b.uint()} result={s.result.uint()}"

if __name__ == "__main__":
    dut = Multiplier()
    dut.elaborate()
    dut.apply(DefaultPassGroup(linetrace=True))
    dut.sim_reset()

    test_cases = [
        (3, 4, 12),
        (5, 6, 30),
        (7, 8, 56),
        (9, 10, 90),
        (15, 15, 225),
    ]

    for a, b, expected in test_cases:
        dut.a @= a
        dut.b @= b
        dut.sim_tick()
        assert dut.result == expected, f"Error: a={a}, b={b}, expected={expected}, got={dut.result}"

    print("All tests passed!")