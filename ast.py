
from ast_base import *

# AST hierarchy

Binary      = newexpr('Binary', 'op lhs rhs')
Call        = newexpr('Call', 'callee args')
For         = newexpr('For', 'id_name, start_expr, end_expr, step_expr, body')
If          = newexpr('If', 'cond_expr then_expr else_expr')
Number      = newexpr("Number", 'val') 
Unary       = newexpr('Unary', 'op rhs')
Variable    = newexpr('Variable', 'name')
VarIn       = newexpr('VarIn', 'vars body') 

_ANONYMOUS = "_ANONYMOUS."

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

    _anonymous_count = 0

    @classmethod
    def Anonymous(klass):
        klass._anonymous_count += 1
        return Prototype(_ANONYMOUS + str(klass._anonymous_count), [])     

    def is_anonymous(self):
        return self.name.startswith(_ANONYMOUS)    

    def flatten(self):
        flattened = [self.__class__.__name__, self.name, '(' + ' '.join(self.argnames) + ')']
        if self.prec != DEFAULT_PREC:
            return flattened + [self.prec]
        else :
            return flattened       

class Function(Node):
    def __init__(self, proto, body):
        self.proto = proto
        self.body = body

    def is_anonymous(self):
        return self.proto.is_anonymous()    

    @staticmethod    
    def Anonymous(body):
        return Function(Prototype.Anonymous(), body)

    def flatten(self):
        return [self.__class__.__name__, self.proto.flatten(), self.body.flatten()]    


if __name__ == '__main__':

    f = Call("f", [Variable('x'), Number(8)])
    print(f.flatten())    
    print(f.dump())    

    g = Call("g", [ ])
    print(g.flatten())    
    print(g.dump())    

