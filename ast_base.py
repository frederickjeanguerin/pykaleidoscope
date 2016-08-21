from derivedtuple import derivedtuple

class Node(object):
    def flatten(self):
        return _flatten(self)            

    def dump(self, indent=0):
        return _dump(self.flatten(), indent)

class Expr(Node):
    pass


def newnode(typename, properties, *mixins):
    """Create a new nodetype as a named tuple which descends from Node.
       To add behavior, just add some mixins 
    """
    return derivedtuple(typename, properties, *mixins, Node)

def newexpr(typename, properties, *mixins):
    """Create a new nodetype as a named tuple which descends from Expr.
       To add behavior, just add some mixins 
    """
    return derivedtuple(typename, properties, *mixins, Expr)


def _flatten(node):

    if isinstance(node, tuple) and not type(node) is tuple:
        return [node.__class__.__name__] + [_flatten(item) for item in node]

    elif isinstance(node, list):
        return [_flatten(elem) for elem in node]

    else:
        return node        


def _dump(flattened, indent=0):
    s = " " * indent
    starting = True
    for elem in flattened:

        if not starting: 
            s += " "

        if isinstance(elem, list):
            if len(elem) == 0:
                s += '[]' 
            elif isinstance(elem[0], list):
                s += _dump(elem, indent)
            else:    
                s += '\n' + _dump(elem, indent + 2)
        else:
            s += str(elem)
        starting = False
    return s;        


#---- Some unit tests ----#

import unittest

class TestAstBase(unittest.TestCase):

    def test_newexpr(self):
        Number = newexpr('Number', 'val')

        n = Number(8)
        self.assertListEqual( n.flatten(), ["Number", 8] )
        self.assertEqual( n.dump(), "Number 8" )

        n = Number(None)
        self.assertListEqual( n.flatten(), ["Number", None] )
        self.assertEqual( n.dump(), "Number None" )

        Call = newexpr('Call', 'callee args')

        f = Call("f", [Number(90), Number(8)])
        self.assertListEqual( f.flatten(), 
            ['Call', 'f', [['Number', 90], ['Number', 8]]] )
        self.assertRegex( f.dump(), r"Call f\s+Number 90\s+Number 8"  )

        g = Call("g", [ ])
        self.assertListEqual( g.flatten(), 
            ['Call', 'g', []] )
        self.assertEqual( g.dump(), "Call g []" )

if __name__ == '__main__':
    unittest.main()            


