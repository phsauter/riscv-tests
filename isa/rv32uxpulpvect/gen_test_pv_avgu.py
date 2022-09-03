import numpy as np # for easy casting via uint32(), int16() etc
import os
import bitstring

import sys
sys.path.append("../scripts")
from pulp_test_gen import pulp_test_rr_op, pulp_test_r_uimm6_op

# common implementation for vector-avg (unsigned)
# for all element-sizes, with and without scalar-replication
# and for the cases where op2 is reg or imm6
def pv_avgu_op(op1: int, op2: int, e_bits: int, sc_mode: bool):
    bitstring.set_lsb0(True)
    bits1 = bitstring.pack('uint:32', op1)
    elements1 = [bits1[i:(i+e_bits)] for i in range(0,32,e_bits)]

    bits2 = bitstring.pack('uint:32', op2)
    if sc_mode is True:
        elements2 = [bits2[0:e_bits] for i in range(0,32,e_bits)]
    else:
        elements2 = [bits2[i:(i+e_bits)] for i in range(0,32,e_bits)]

    res = bitstring.BitArray()

    for pack in zip(elements1, elements2):
        elem1 = pack[0].unpack(f'uint:{e_bits}')[0]
        elem2 = pack[1].unpack(f'uint:{e_bits}')[0]

        res_e = elem1 + elem2
        res_bits = bitstring.pack(f'uint:{e_bits+1}', res_e)
        res_bits = res_bits[0:e_bits]
        res_bits.uint >>= 1

        res.append(res_bits[0:e_bits])
    
    return res.int


class pulp_test_pv_avgu(pulp_test_rr_op):
    def __init__(self):
        super().__init__("pv.avgu",  res_format  = "0x{:08x}", 
                                    src1_format = "0x{:08x}",
                                    src2_format = "0x{:08x}")

        self.minmax[0] = (0x00000000, +0xffffffff) # uint32
        self.minmax[1] = (0x00000000, +0xffffffff) # uint32
        self.e_bits = 16
        self.scalar_rep = False
        
        
    def operation(self, src1: int, src2: int) -> int:
        res = pv_avgu_op(src1, src2, self.e_bits, self.scalar_rep)
        
        return res


class pulp_test_pv_avgu_sci(pulp_test_r_uimm6_op):
    def __init__(self):
        super().__init__("pv.avgu.sci",  res_format  = "0x{:08x}", 
                                        src1_format = "0x{:08x}",
                                        imm1_format = "0x{:03x}")

        self.minmax[0] = (0x00000000, +0xffffffff) # uint32
        self.minmax[1] = (0x00, 0x03F) # uint6
        self.e_bits = 16
        self.scalar_rep = True
        
        
    def operation(self, src1: int, src2: int) -> int:
        res = pv_avgu_op(src1, src2, self.e_bits, self.scalar_rep)
        
        return res


if __name__ == '__main__':
    # avgu halfwords
    pv_avgu_h = pulp_test_pv_avgu()
    pv_avgu_h.mnemonic += '.h'
    pv_avgu_h.file_path = os.path.join(".", pv_avgu_h.mnemonic.replace('.', '_') + ".S")

    pv_avgu_h.add_arith_test(0x7f7e7d7c, 0x7b7a7978)
    pv_avgu_h.add_arith_test(0x00112233, 0x77665544)
    pv_avgu_h.gen_all_tests(15, 2)
    pv_avgu_h.write_asm()

    # avgu bytes
    pv_avgu_b = pulp_test_pv_avgu()
    pv_avgu_b.mnemonic += '.b'
    pv_avgu_b.e_bits = 8
    pv_avgu_b.file_path = os.path.join(".", pv_avgu_b.mnemonic.replace('.', '_') + ".S")

    pv_avgu_b.add_arith_test(0x7f7e7d7c, 0x7b7a7978)
    pv_avgu_b.add_arith_test(0x00112233, 0x77665544)
    pv_avgu_b.gen_all_tests(15, 2)
    pv_avgu_b.write_asm()

    # avgu halfwords (op2 is scalar)
    pv_avgu_sc_h = pulp_test_pv_avgu()
    pv_avgu_sc_h.mnemonic += '.sc.h'
    pv_avgu_sc_h.scalar_rep = True
    pv_avgu_sc_h.file_path = os.path.join(".", pv_avgu_sc_h.mnemonic.replace('.', '_') + ".S")

    pv_avgu_sc_h.add_arith_test(0x7f7e7d7c, 0x7b7a7978)
    pv_avgu_sc_h.add_arith_test(0x00112233, 0x77665544)
    pv_avgu_sc_h.gen_all_tests(15, 2)
    pv_avgu_sc_h.write_asm()

    # avgu bytes (op2 is scalar)
    pv_avgu_sc_b = pulp_test_pv_avgu()
    pv_avgu_sc_b.mnemonic += '.sc.b'
    pv_avgu_sc_b.e_bits = 8
    pv_avgu_sc_b.scalar_rep = True
    pv_avgu_sc_b.file_path = os.path.join(".", pv_avgu_sc_b.mnemonic.replace('.', '_') + ".S")

    pv_avgu_sc_b.add_arith_test(0x7f7e7d7c, 0x7b7a7978)
    pv_avgu_sc_b.add_arith_test(0x00112233, 0x77665544)
    pv_avgu_sc_b.gen_all_tests(15, 2)
    pv_avgu_sc_b.write_asm()

    # avgu halfwords (op2 is immediate)
    pv_avgu_sci_h = pulp_test_pv_avgu_sci()
    pv_avgu_sci_h.mnemonic += '.h'
    pv_avgu_sci_h.file_path = os.path.join(".", pv_avgu_sci_h.mnemonic.replace('.', '_') + ".S")

    pv_avgu_sci_h.add_arith_test(0x7f7e7d7c, 0x1F)
    pv_avgu_sci_h.add_arith_test(0x00112233, 0x10)
    pv_avgu_sci_h.gen_all_tests(15, 2)
    pv_avgu_sci_h.write_asm()

    # avgu bytes (op2 is immediate)
    pv_avgu_sci_b = pulp_test_pv_avgu_sci()
    pv_avgu_sci_b.mnemonic += '.b'
    pv_avgu_sci_b.e_bits = 8
    pv_avgu_sci_b.file_path = os.path.join(".", pv_avgu_sci_b.mnemonic.replace('.', '_') + ".S")

    pv_avgu_sci_b.add_arith_test(0x7f7e7d7c, 0x1F)
    pv_avgu_sci_b.add_arith_test(0x00112233, 0x10)
    pv_avgu_sci_b.gen_all_tests(15, 2)
    pv_avgu_sci_b.write_asm()