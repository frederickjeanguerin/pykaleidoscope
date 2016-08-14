from collections import namedtuple

# AST hierarchy

class Node(object):
    def flatten(self):
        return [self.__class__.__name__, 'flatten unimplemented']            

    def dump(self, indent=0):
        return dump(self.flatten(), indent)

class Expr(Node):
    pass

class Number(Expr):
    def __init__(self, val):
        self.val = val

    def flatten(self):
        return [self.__class__.__name__, self.val]            


class Variable(Expr):
    def __init__(self, name):
        self.name = name

    def flatten(self):
        return [self.__class__.__name__, self.name]            

class Unary(Expr):
    def __init__(self, op, rhs):
        self.op = op
        self.rhs = rhs

    def flatten(self):
        return [self.__class__.__name__, self.op, self.rhs.flatten()]  

class Binary(Expr):
    def __init__(self, op, lhs, rhs):
        self.op = op
        self.lhs = lhs
        self.rhs = rhs

    def flatten(self):
        return [self.__class__.__name__, self.op, self.lhs.flatten(), self.rhs.flatten()]    

class Call(Expr):
    def __init__(self, callee, args):
        self.callee = callee
        self.args = args

    def flatten(self):
        return [self.__class__.__name__, self.callee, [arg.flatten() for arg in self.args] ]    

class If(Expr):
    def __init__(self, cond_expr, then_expr, else_expr):
        self.cond_expr = cond_expr
        self.then_expr = then_expr
        self.else_expr = else_expr

    def flatten(self):
        return [self.__class__.__name__, self.cond_expr.flatten(), self.then_expr.flatten(), self.else_expr.flatten() ]    


class For(Expr):
    def __init__(self, id_name, start_expr, end_expr, step_expr, body):
        self.id_name = id_name
        self.start_expr = start_expr
        self.end_expr = end_expr
        self.step_expr = step_expr
        self.body = body

    def flatten(self):
        return [
            self.__class__.__name__, 
            self.id_name, 
            self.start_expr.flatten(), 
            self.end_expr.flatten(),
            self.step_expr.flatten() if self.step_expr else ["No step"],
            self.body.flatten()
        ]    

class VarIn(Expr):
    def __init__(self, vars, body):
        # vars is a sequence of (name, expr) pairs
        self.vars = vars
        self.body = body

    def flatten(self):
        return [
            self.__class__.__name__, 
            [[var[0], var[1].flatten() if var[1] else None] for var in self.vars], 
            self.body.flatten()
        ]  

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


def dump(flattened, indent=0):
    s = " " * indent
    starting = True
    for elem in flattened:

        if not starting: 
            s += " "

        if isinstance(elem, list):
            if isinstance(elem[0], list) :
                s += dump(elem, indent)
            else:    
                s += '\n' + dump(elem, indent + 2)
        else:
            s += str(elem)
        starting = False
    return s;        

if __name__ == '__main__':

    print("Run the parsing module to test the AST stuff!")    

