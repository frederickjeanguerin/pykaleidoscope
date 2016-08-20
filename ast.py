
from ast_base import *

# AST hierarchy

Binary      = newexpr('Binary', 'op lhs rhs')
Call        = newexpr('Call', 'callee args')
For         = newexpr('For', 'id_name, start_expr, end_expr, step_expr, body')
Function    = newnode('Function', 'proto body')
If          = newexpr('If', 'cond_expr then_expr else_expr')
Number      = newexpr("Number", 'val') 
Unary       = newexpr('Unary', 'op rhs')
Variable    = newexpr('Variable', 'name')
VarIn       = newexpr('VarIn', 'vars body') 

DEFAULT_PREC = 30

class Prototype(Node):
    def __init__(self, name, argnames, isoperator=False, prec=DEFAULT_PREC):
        self.name = name
        self.argnames = argnames
        self.isoperator = isoperator
        self.prec = prec

    def is_unary_op(self):
        return self.isoperator and len(self.argnames) == 1

    def is_binary_op(self):
        return self.isoperator and len(self.argnames) == 2

    def get_op_name(self):
        assert self.isoperator
        return self.name[-1]

    def flatten(self):
        flattened = [self.__class__.__name__, self.name, '(' + ' '.join(self.argnames) + ')']
        if self.prec != DEFAULT_PREC:
            return flattened + [self.prec]
        else :
            return flattened       




#---- Some unit tests ----#

import unittest

class TestSource(unittest.TestCase):

    def test_Function(self):
        p = Prototype("f", ['x', 'y'])
        f = Function(p, Number(10))
        self.assertEqual( f.proto, p )

if __name__ == '__main__':

    unittest.main()   
