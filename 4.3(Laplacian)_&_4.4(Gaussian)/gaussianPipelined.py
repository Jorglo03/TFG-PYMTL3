from pymtl3 import *
from pymtl3.stdlib.basic_rtl import Reg, Mux  
from pymtl3.datatypes import clog2, mk_bits, b1, Bits1, Bits8
from pymtl3.passes.backends.verilog import VerilogTranslationPass

SInt12 = mk_bits(12)

class GaussianPipelined( Component ): 
    def construct( s, x_size, y_size ):
        ROW_BITS = clog2(y_size) if y_size > 1 else 1
        COL_BITS = clog2(x_size) if x_size > 1 else 1

        # Puertos
        s.pixel_in  = InPort(8)
        s.pixel_out = OutPort(8)
        s.valid_out = OutPort(1)

        # Wires
        s.line_buffer1 = [ Wire(8) for _ in range(x_size) ]
        s.line_buffer2 = [ Wire(8) for _ in range(x_size) ]
        s.line_buffer3 = [ Wire(8) for _ in range(x_size) ]
        s.row_count    = Wire( ROW_BITS )
        s.col_count    = Wire( COL_BITS )
        s.col_delayed  = Wire( COL_BITS )
        # Pipeline Register
        s.reg_gauss_sum       = Wire( SInt12 )
        s.reg_is_valid      = Wire( Bits1 )
        s.reg_row_idx       = Wire( ROW_BITS )
        s.reg_col_idx       = Wire( COL_BITS )

        # Stage 1 -> Regs
        s.s1_gauss_sum_w       = Wire( SInt12 ) 
        s.s1_is_valid_w      = Wire( Bits1 )
        s.s1_row_idx_w       = Wire( ROW_BITS )
        s.s1_col_idx_w       = Wire( COL_BITS )
        
        @update_ff
        def up_line_buffers():
            if s.reset:
                for i in range(x_size):
                    s.line_buffer1[i] <<= 0
                    s.line_buffer2[i] <<= 0
                    s.line_buffer3[i] <<= 0
            else:
                current_row = s.row_count
                current_col = s.col_count
                if current_row == 0: s.line_buffer1[current_col] <<= s.pixel_in
                elif current_row == 1: s.line_buffer2[current_col] <<= s.pixel_in
                elif current_row == 2: s.line_buffer3[current_col] <<= s.pixel_in
                else:
                    if current_col == 0:
                        for i in range(x_size):
                            s.line_buffer1[i] <<= s.line_buffer2[i]
                            s.line_buffer2[i] <<= s.line_buffer3[i]
                    s.line_buffer3[current_col] <<= s.pixel_in

        @update_ff
        def up_counts():
            if s.reset:
                s.row_count <<= 0
                s.col_count <<= 0
            else:
                s.col_delayed <<= s.col_count
                current_row = s.row_count
                current_col = s.col_count
                if current_col == x_size - 1:
                    s.col_count <<= 0
                    if current_row == y_size - 1: s.row_count <<= 0
                    else: s.row_count <<= current_row + 1
                else:
                    s.col_count <<= current_col + 1
                    s.row_count <<= current_row

        # Pipeline Stage 1:  Calculo aplicando la mascara 
        # Calcula suma SInt12, validez, coords -> wires intermedios s.s1_*
        @update
        def pipeline_stage1_calc(): 
            s.s1_gauss_sum_w  @= SInt12(0) 
            s.s1_is_valid_w @= b1(0)
            s.s1_row_idx_w  @= 0
            s.s1_col_idx_w  @= 0
            is_valid_stage1 = b1(0)

            current_row = s.row_count
            current_col = s.col_count
            col_delayed = s.col_delayed
            if ( (current_row >= 2) &
                 (col_delayed >= 1) &
                 (col_delayed < x_size - 1) ):

                is_valid_stage1 = b1(1)
                
                tl = s.line_buffer1[col_delayed - 1]
                t  = s.line_buffer1[col_delayed    ]
                tr = s.line_buffer1[col_delayed + 1]
                l  = s.line_buffer2[col_delayed - 1]
                cen= s.line_buffer2[col_delayed    ]
                r  = s.line_buffer2[col_delayed + 1]
                bl = s.line_buffer3[col_delayed - 1]
                b  = s.line_buffer3[col_delayed]
                br = s.pixel_in

                # Extender a Bits12 para la suma
                tl_12 = zext(tl, 12)
                t_12 = zext(t, 12)
                tr_12 = zext(tr, 12)
                l_12 = zext(l, 12)
                cen_12 = zext(cen, 12)
                r_12 = zext(r, 12)
                bl_12 = zext(bl, 12)
                b_12 = zext(b, 12)
                br_12 = zext(br, 12)

                # Aplicar kernel Gaussiano y sumar (resultado Bits12) 
                # Kernel: [[1, 2, 1], [2, 4, 2], [1, 2, 1]]
                gauss_sum_b12 = (tl_12) + (t_12 << 1) + (tr_12) + (l_12 << 1)   + (cen_12 << 2) + (r_12 << 1) + (bl_12)       + (b_12 << 1) + (br_12)
                # Asignar resultados a wires intermedios
                gauss_sum_b12 = gauss_sum_b12 >> 4 

                s.s1_gauss_sum_w  @= gauss_sum_b12 
                s.s1_is_valid_w @= is_valid_stage1
                s.s1_row_idx_w  @= current_row
                s.s1_col_idx_w  @= col_delayed #current_col

        # Captura los valores de los wires intermedios s.s1_* en los wires s.reg_*
        @update_ff
        def update_pipeline_regs():
            if s.reset:
                s.reg_gauss_sum  <<= 0 
                s.reg_is_valid <<= 0
                s.reg_row_idx  <<= 0
                s.reg_col_idx  <<= 0
            else:
                s.reg_gauss_sum  <<= s.s1_gauss_sum_w
                s.reg_is_valid <<= s.s1_is_valid_w
                s.reg_row_idx  <<= s.s1_row_idx_w
                s.reg_col_idx  <<= s.s1_col_idx_w

        # Pipeline Stage 2: Clamping y output
        # Lee los wires s.reg_*, realiza clamping, asigna salidas s.pixel_out/s.valid_out
        @update
        def pipeline_stage2_clamp_output():
            # defaults
            s.pixel_out @= Bits8(0)
            s.valid_out @= b1(0)

            if s.reg_is_valid:
                s.valid_out @= b1(1)

                registered_gauss_sum = s.reg_gauss_sum 

                is_neg = registered_gauss_sum[11]
                upper_bits = registered_gauss_sum[8:12]
                is_pos_overflow = ~is_neg & (upper_bits != 0)

                clamped_val_b8 = Bits8(0) 
                if is_neg == b1(1):
                    clamped_val_b8 = Bits8(0)
                elif is_pos_overflow == b1(1):
                    clamped_val_b8 = Bits8(255)
                else: 
                    clamped_val_b8 = trunc(registered_gauss_sum, 8)

                s.pixel_out @= clamped_val_b8


    def line_trace( s ):
        # Input y contadores (leen wires)
        in_str = f"IN:{s.pixel_in!s:3s} @({s.row_count!s:>2s},{s.col_count!s:>2s})"

        # Valores intermedios de S1 (leen wires s.s1_*)
        s1_in_val_char = "V" if s.s1_is_valid_w else "-"
        s1_in_str = f"->S1[{s1_in_val_char}] " \
                    f"SumIn:{s.s1_gauss_sum_w!s:5s} " \
                    f"Rin:{s.s1_row_idx_w!s:>2s} " \
                    f"Cin:{s.s1_col_idx_w!s:>2s}" 

        # Valores registrados (leen wires s.reg_*)
        s1_out_val_char = "V" if s.reg_is_valid else "-"
        s1_out_str = f"S1->[{s1_out_val_char}] " \
                     f"SumRg:{s.reg_gauss_sum!s:5s} " \
                     f"Rrg:{s.reg_row_idx!s:>2s} " \
                     f"Crg:{s.reg_col_idx!s:>2s}"

        # Salidas finales (leen wires s.pixel_out, s.valid_out)
        out_val_char = "V" if s.valid_out else "-"
        out_str = f"OUT[{out_val_char}] Px:{s.pixel_out!s:3s}"

        return f"{in_str} | {s1_in_str} | {s1_out_str} | {out_str}"

    
def translate(alu):
    import os

    module_name = "GaussianFilter" 

    if os.path.exists(module_name):
        os.remove(module_name)

    alu.elaborate()
    alu.set_metadata(VerilogTranslationPass.explicit_module_name, module_name)
    alu.set_metadata(VerilogTranslationPass.enable, True)
    

    alu.apply(VerilogTranslationPass())

    os.rename(module_name + "__pickled.v", module_name + ".v")
    print("Código Verilog generado correctamente\n")

#translate(GaussianPipelined(x_size=100, y_size=100))