
from ast_base import *

# AST hierarchy

# Nodes (Statements) 

Function    = newnode('Function', 'proto body')
Prototype   = newnode("Prototype", 'name argnames')

# Expressions

Binary      = newexpr('Binary', 'op lhs rhs')
Call        = newexpr('Call', 'callee args')
For         = newexpr('For', 'id_name, start_expr, end_expr, step_expr, body')
If          = newexpr('If', 'cond_expr then_expr else_expr')
Number      = newexpr("Number", 'val') 
Unary       = newexpr('Unary', 'op rhs')
Variable    = newexpr('Variable', 'name')
VarIn       = newexpr('VarIn', 'vars body') 

#---- Some unit tests ----#

import unittest

class TestSource(unittest.TestCase):

    def test_Function(self):
        p = Prototype("f", ['x', 'y'])
        f = Function(p, Number(10))
        self.assertEqual( f.proto, p )

if __name__ == '__main__':

    unittest.main()   
