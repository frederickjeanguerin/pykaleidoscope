from collections import namedtuple

import llvmlite.ir as ir

class KType(namedtuple('_KType', 'irtype')):
    def __init__(self, irtype):
        pass

    def __hash__(self):
        return str(self.irtype).__hash__()

    def __repr__(self):
        return str(self.irtype)    

F64 = KType(ir.DoubleType())

INT_SIZE = 32

INT = KType(ir.IntType(INT_SIZE))

            