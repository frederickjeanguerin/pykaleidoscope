import llvmlite.ir as ir

from parsing.seq import *

class CodegenError(CodeError):

    def __init__(self, msg, seq_or_token):
        self.msg = msg
        assert isinstance(seq_or_token, (Seq, Token))
        self.target = seq_or_token

    def __str__(self):
        return self.msg
                    

def _raise(seq_or_token, msg = None):
    msg = msg or "Cannot generate code for"
    msg = msg + ": " + str(seq_or_token)
    raise CodegenError(msg, seq_or_token)


def _irdouble(number):
    """Converts a float string value into an IR double constant value"""
    assert isinstance(number, Number)
    try:
        return ir.Constant(ir.DoubleType(), float(number.text))
    except ValueError:
        _raise(number, "Invalid float value")    

def ir_from(seq):
    """ Generate an IR of the code in seq.
        Returns a module with a "main" function having that code.
    """
    # Create a module to insert the IR code in
    module = ir.Module()

    # Create a main(): double function
    funcname = "main"
    functype = ir.FunctionType(ir.DoubleType(), [])
    func = ir.Function(module, functype, funcname)

    # Create the entry BB in the function and set a new builder to it.
    bb_entry = func.append_basic_block('entry')
    builder = ir.IRBuilder(bb_entry)    

    # Generate IR code and value corresponding to the sequence
    retval = _gen_seq(seq, builder)
    # And make the main function return that value
    builder.ret(retval)

    return module


def _gen_seq(seq, builder):

    # import pdb
    # pdb.set_trace()

    # If a generating for a token, 
    # it must be a number and 
    # just return the value of that number
    if seq.match(Token):
        if not seq.match(Number):
            _raise(seq, "Number expected in place of")
        return _irdouble(seq)

    # Otherwise we are generating for a sequence    
    assert seq.match(Seq)

    # The sequence must not be empty
    if seq.len == 0:
        _raise(seq, "Non empty sequence expected in place of")

    # if there is just one element in the sequence, 
    # return the value of that element    
    if seq.len == 1:
        return _gen_seq(seq.items[0], builder)

    # Otherwise the seq is a function call 
    # with callee first    
    callee = seq.items[0]

    # At this moment, only builtin llvm operations are permitted    
    if not callee.match(LlvmIdentifier):
        _raise(callee, "Llvm identifier expected for callee")

    # At this moment, only addition is permitted    
    if not callee.match("%fadd"):
        _raise(callee, "Unsupported or undefined LLVM operation")

    # Verify there are 2 arguments    
    if not seq.len == 3:
        _raise(callee, "Two (2) arguments expected for callee")    

    # Compute arguments    
    arg1 = _gen_seq(seq.items[1], builder)    
    arg2 = _gen_seq(seq.items[2], builder)    

    # Compute the function call and return that value
    return builder.fadd(arg1, arg2, 'addop')
