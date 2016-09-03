from collections import namedtuple

from parsing.source_mixin import *


class SeqMixin (SourceMixin):
    """ Mix with a class that provides a seq property.
        Will provide first_token and last_token from that.
        And all SourceMixin properties as well. 
    """

    @property
    def first_token(self):
        return self.seq.first_token

    @property
    def last_token(self):
        return self.seq.last_token


class KTree(SeqMixin):
    """ Represent a call tree object.
        Such an object is ready for code generation or execution. 
        Common ancestor to KCall and KVal 
    """
    pass


class KCall (KTree, namedtuple("_KCall", "fun args type seq calleeseq")):

    def __init__(self, fun, args, type, seq, calleeseq):
        pass

    def to_code(self):
        return "(" + self.fun.name + " "  + " ".join((arg.to_code() for arg in self.args)) + ")"


class KVal (KTree, namedtuple("Kval", "val type seq")):

    def __init__(self, val, type, seq):
        pass

    def to_code(self):
        return str(self.val)


