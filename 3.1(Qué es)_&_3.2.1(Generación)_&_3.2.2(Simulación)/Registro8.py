from pymtl3 import *

class Registro8(Component):
    def construct(s):
        # Entradas
        s.in_  = InPort(8)
        s.en   = InPort()     # Señal de habilitación (enable)
        s.out  = OutPort(8)

        # Registro sincrónico: actualiza solo en flanco de reloj
        @update_ff
        def reg_ff():
            if s.reset:          # Si está en reset, salida en 0
                s.out <<= 0
            elif s.en:           # Si está habilitado, guarda el valor de entrada
                s.out <<= s.in_

from pymtl3.stdlib.test_utils import run_test_vector_sim

def run_test_registro(dut):
    # Ciclo 0: Activar reset
    dut.reset @= 1  # Activar reset
    print(f"Ciclo 0: reset = {dut.reset}, in_ = {dut.in_}, en = {dut.en}, out = {dut.out}")
    dut.sim_tick()  # Un ciclo de reloj
    assert dut.out == 0, f"Fallo en Ciclo 0: esperado out = 0, obtenido out = {int(dut.out)}"

    # Ciclo 1: Ingreso de valor en_ = 42 y habilitación en = 1
    dut.reset @= 0  # Desactivar reset
    dut.in_ @= 42  # Asignar valor 42 a in_
    dut.en @= 1    # Activar habilitación
    print(f"Ciclo 1: reset = {dut.reset}, in_ = {dut.in_}, en = {dut.en}, out = {dut.out}")
    dut.sim_tick()  # Un ciclo de reloj
    assert dut.out == 42, f"Fallo en Ciclo 1: esperado out = 42, obtenido out = {int(dut.out)}"

    # Ciclo 2: Ingreso de valor en_ = 55 y habilitación en = 1
    dut.in_ @= 55  # Asignar valor 55 a in_
    dut.en @= 1    # Mantener habilitación
    print(f"Ciclo 2: reset = {dut.reset}, in_ = {dut.in_}, en = {dut.en}, out = {dut.out}")
    dut.sim_tick()  # Un ciclo de reloj
    assert dut.out == 55, f"Fallo en Ciclo 2: esperado out = 55, obtenido out = {int(dut.out)}"

    # Ciclo 3: Ingreso de valor en_ = 77 y habilitación en = 0 (deshabilitar)
    dut.in_ @= 77  # Asignar valor 77 a in_
    dut.en @= 0    # Deshabilitar
    print(f"Ciclo 3: reset = {dut.reset}, in_ = {dut.in_}, en = {dut.en}, out = {dut.out}")
    dut.sim_tick()  # Un ciclo de reloj
    assert dut.out == 55, f"Fallo en Ciclo 3: esperado out = 55 (no cambia), obtenido out = {int(dut.out)}"

    # Ciclo 4: Ingreso de valor en_ = 99 y habilitación en = 1
    dut.in_ @= 99  # Asignar valor 99 a in_
    dut.en @= 1    # Activar habilitación
    print(f"Ciclo 4: reset = {dut.reset}, in_ = {dut.in_}, en = {dut.en}, out = {dut.out}")
    dut.sim_tick()  # Un ciclo de reloj
    assert dut.out == 99, f"Fallo en Ciclo 4: esperado out = 99, obtenido out = {int(dut.out)}"

    print("Todos los ciclos pasaron correctamente.")

def test_registro8():
    dut = Registro8()
    dut.apply( DefaultPassGroup(vcdwave="registro8_test") )  # Aplica el grupo de paso por defecto
    dut.sim_reset()  # Reset de la simulación
    
    # NO SE MUESTRAN LOS CICLOS DEL dut.sim_reset() PARA REDUCIR SALIDA

    # Test de registro con diferentes entradas, habilitación y reset
    run_test_registro( dut )        # Esperado, debería almacenar el último valor válido

test_registro8()
