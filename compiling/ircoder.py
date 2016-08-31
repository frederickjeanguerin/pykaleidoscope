from collections import namedtuple
import re
import llvmlite.ir as ir

from parsing.seq import *

KResult = namedtuple("_KResult", "value type seq")

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


def ir_from(seq):
    """ Generate an IR of the code in seq.
        Returns a module with a "main" function having that code.
    """
    # Create a module to insert the IR code in
    module = ir.Module()

    # Create a main(): double function
    funcname = "main"
    functype = ir.FunctionType(_F64, [])
    func = ir.Function(module, functype, funcname)

    # Create the entry BB in the function and set a new builder to it.
    bb_entry = func.append_basic_block('entry')
    builder = ir.IRBuilder(bb_entry)    

    # Generate IR code and value corresponding to the sequence
    rawresult = _gen_seq(seq, builder)
    # Cast result to float
    mainresult = _cast(rawresult, _F64, builder)
    # And make the main function return that value
    builder.ret(mainresult.value)

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
        return _gen_number(seq, builder)

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

    # Get requested llvm operation     
    llvm_op_info = _LLVM_OPS.get(callee.llvm_op)
    if not llvm_op_info:
        _raise(callee, "Unsupported or undefined LLVM operation")
    llvm_fun, ret_type, *arg_types = llvm_op_info

    # Verify that the correct number of arguments are passed in    
    if not seq.len == len(arg_types)+1:
        _raise(callee, 
            "({}) arguments expected but ({}) given for callee".format(len(arg_types), seq.len - 1))    

    # Compute arguments
    rawargs = (_gen_seq(arg, builder) for arg in seq.items[1:])
    # Cast arguments to expected types    
    args = [_cast(rawarg, arg_types[i], builder).value for i, rawarg in enumerate(rawargs)]    

    # Compute the function call and return that value
    return KResult(llvm_fun(builder, *args, 'addop'), ret_type, callee)

def _gen_number(number, builder):
    """Converts a float string value into an IR double constant value"""
    assert isinstance(number, Number)
    try:
        # Integer
        if re.match(r"^[0-9]*$", number.text):
            value = int(number.text)
            if -2**32 <= value <= 2**32:
                return KResult(_I32(value), _I32, number)
            else:
                _raise(number, "Integer too big to fit in 32 bits")

        # Floating point    
        return KResult(_F64(float(number.text)), _F64, number)

    except ValueError:
        _raise(number, "Invalid number format")    


def _cast(result, expected_type, builder):
    # If same type, just return the result
    if result.type == expected_type:
        return result

    # If promotion possible, make it    
    if result.type == _I32 and expected_type == _F64:
        return KResult(builder.sitofp(result.value, _F64), _F64, result.seq)
    
    # Otherwise : ERROR        
    _raise(result.seq, "Type mismatch error, expecting {} but got {} for".format(expected_type, result.type))


_F64 = ir.DoubleType()

_I32 = ir.IntType(32)

_LLVM_OPS = {

    "fadd" : ( ir.IRBuilder.fadd, _F64, _F64, _F64 ),
    "fmul" : ( ir.IRBuilder.fmul, _F64, _F64, _F64 ),
    "fsub" : ( ir.IRBuilder.fsub, _F64, _F64, _F64 ),
    "fdiv" : ( ir.IRBuilder.fdiv, _F64, _F64, _F64 ),
    "frem" : ( ir.IRBuilder.frem, _F64, _F64, _F64 ),
}