#include "VALU_Custom.h"  // Archivo generado por Verilator
#include "verilated.h"
#include <iostream>
#include <verilated_vcd_c.h>  // Incluir para manejar las trazas VCD

int main(int argc, char** argv) {
    Verilated::commandArgs(argc, argv);  // Inicializar Verilator
    VALU_Custom* alu = new VALU_Custom;

    // Configurar la traza
    Verilated::traceEverOn(true);
    VerilatedVcdC* tfp = new VerilatedVcdC;
    alu->trace(tfp, 99);  // 99 indica el nivel de detalles de la traza
    tfp->open("dump.vcd");  // Archivo de salida VCD

    // Definir casos de prueba
    struct TestCase {
        int in0, in1, fn, expected;
    };

    TestCase testCases[] = {
        {3, 2, 0, 5},
        {5, 3, 1, 2},
        {6, 3, 2, 2},
        {4, 0, 3, (256 - 4)}
    };

    // Ejecutar pruebas
    for (const auto& test : testCases) {
        alu->in0 = test.in0;
        alu->in1 = test.in1;
        alu->fn  = test.fn;
        alu->eval();  // Ejecutar la ALU en Verilator
        tfp->dump(Verilated::time());  // Volcar el estado al archivo VCD con el tiempo siguiente
        Verilated::timeInc(1);  // Incrementar el tiempo de simulación

        if (alu->out == test.expected) {
            std::cout << "Prueba " << test.in0 << ", " << test.in1 
                      << ", " << test.fn << " -> OK\n";
        } else {
            std::cerr << "Fallo en prueba " << test.in0 << ", " << test.in1 
                      << ", " << test.fn << ": esperado " << test.expected 
                      << ", obtenido " << int(alu->out) << "\n";
        }
    }
    alu->eval();  // Ejecutar la ALU en Verilator
        tfp->dump(Verilated::time());  // Volcar el estado al archivo VCD con el tiempo siguiente
    Verilated::timeInc(1);  // Incrementar el tiempo de simulación

    tfp->close();  // Cerrar el archivo VCD
    delete alu;    // Liberar memoria
    return 0;
}
