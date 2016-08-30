from .indenter import *

class Node(SourceMixin):

    def dump(self, indentlevel = 0, indent = 2):
        return dump(self.flatten(), indentlevel, indent)


class Seq(Node):

    def __init__(self, exprs, first = None, last = None):
        assert isinstance(exprs, list)
        self.exprs = exprs
        assert first or last or len(exprs) > 0
        self.first_token = first or exprs[0].first_token
        self.last_token = last or exprs[-1].last_token   

    def flatten(self):
        return flatten(self.exprs)


class Call(Node):

    def __init__(self, callee, args, first_token, last_token):
        assert isinstance(callee, (Token, Call))
        self.callee = callee
        assert isinstance(args, list)
        self.args = args
        self.first_token = first_token
        self.last_token = last_token

    def flatten(self):
        return [self.__class__.__name__, 
            flatten(self.callee), 
            *flatten(self.args)]



def flatten(node):

    if isinstance(node, Node):
        return node.flatten()

    elif isinstance(node, list):
        if len(node) == 0:
            return tuple()
        return [flatten(elem) for elem in node]

    elif isinstance(node, Token):
        return node.text

    else:
        return node        


def dump(flattened, indentlevel=0, indent = 2):

    # if not a list, return the element
    if not isinstance(flattened, list):
        return " "*indentlevel + str(flattened) + "\n"

    if len(flattened) == 1:
        return dump(flattened[0])

    # else if a list with no sublist, return the list on just a single line
    if all((not isinstance(elem, list) for elem in flattened)):
        return " "*indentlevel + " ".join((str(elem) for elem in flattened)) + "\n"

    # otherwise, spread on many lines 
    s = ""   
    s += dump(str(flattened[0]), indentlevel, indent)
    for elem in flattened[1:]:
        s += dump(elem, indentlevel + indent, indent)
    return s        


