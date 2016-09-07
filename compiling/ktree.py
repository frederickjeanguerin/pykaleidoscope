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


class IrResult(SeqMixin, namedtuple("_IrResult", "irval type seq calleeseq")):
    """ Represent an IR LLVM result
    """
    def __init__(self, irval, type, seq, calleeseq):
        pass


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

    def to_ir(self, builder):
        llvm_op = self.fun
        irargs = (arg.to_ir(builder).irval for arg in self.args)
        return IrResult(llvm_op.gen_fun(builder, *irargs, llvm_op.name),
            self.type, self.seq, self.calleeseq)



class KIdentity (KTree, namedtuple("_KCall", "arg type seq calleeseq")):
    """ An Identity call through which returns its single argument. """

    def __init__(self, arg, type, seq, calleeseq):
        pass

    def to_code(self):
        return self.arg.to_code()

    def to_ir(self, builder):
        return self.arg.to_ir(builder)


class KVal (KTree, namedtuple("Kval", "val type seq")):

    def __init__(self, val, type, seq):
        pass

    def to_code(self):
        return str(self.val)

    def to_ir(self, builder):
        return IrResult(self.type(self.val), self.type, self.seq, self.seq)
    

