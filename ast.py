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

_ANONYMOUS = "_ANONYMOUS."

class Prototype(Node):
    def __init__(self, name, argnames):
        self.name = name
        self.argnames = argnames

    _anonymous_count = 0

    @classmethod
    def Anonymous(klass):
        klass._anonymous_count += 1
        return Prototype(_ANONYMOUS + str(klass._anonymous_count), [])     

    def is_anonymous(self):
        return self.name.startswith(_ANONYMOUS)    

    def flatten(self):
        return [self.__class__.__name__, self.name, '(' + ' '.join(self.argnames) + ')']    


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

    num = Number(100)
    var = Variable('var')
    bin1 = Binary("+", num, var)
    bin2 = Binary("*", bin1, bin1)
    call1 = Call('add', [num, var])
    call2 = Call('max', [call1, bin1])
    proto1 = Prototype('add', ['x', 'y'])
    proto2 = Prototype.Anonymous()
    fun = Function(proto1, Binary('+', Variable("x"), Variable('y')))

    data = [
        num, 
        var, 
        bin1, 
        bin2, 
        call1, 
        call2, 
        proto1,
        proto2, 
        fun,
        num]

    for elem in data:
        print(elem.flatten())
        print(elem.dump())
        print()
