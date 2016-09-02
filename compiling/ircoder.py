from collections import namedtuple
import re

from parsing.seq import *
from .constants import *

KResult = namedtuple("_KResult", "value type seq")
IrResult = namedtuple("_IrResult", "module type")

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
        Returns a (module, return_type) with 
        a "main" function having that code.
    """
    # Create a module to insert the IR code in
    module = ir.Module()

    # Create a main(): double function
    funcname = "main"
    functype = ir.FunctionType(F64, [])
    func = ir.Function(module, functype, funcname)

    # Create the entry BB in the function and set a new builder to it.
    bb_entry = func.append_basic_block('entry')
    builder = ir.IRBuilder(bb_entry)    

    # Generate IR code and value corresponding to the sequence
    rawresult = _gen_seq(seq, builder)
    # Cast result to float
    mainresult = _cast(rawresult, F64, builder)
    # And make the main function return that value
    builder.ret(mainresult.value)

    return IrResult(module, rawresult.type)


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
        content = seq.items[0]
        if seq.first_token.match('(') and content.match(Token):
            _raise(content, "Element does not need to be enclosed in parenthesis")
        return _gen_seq(content, builder)

    # Otherwise the seq is a function call 
    # with callee first    
    callee = seq.items[0]

    # At this moment, only builtin llvm operations are permitted    
    if not callee.match(LlvmIdentifier):
        _raise(callee, "Llvm identifier expected for callee")

    # Get requested llvm operation     
    llvm_op = LLVM_OPS.get(callee.llvm_opname)
    if not llvm_op:
        _raise(callee, "Unsupported or undefined LLVM operation")

    # Verify that the correct number of arguments are passed in
    expected_num_of_args = len(llvm_op.arg_types)
    received_num_of_args = seq.len - 1     
    if not received_num_of_args == expected_num_of_args:
        _raise(callee, 
            "({}) arguments expected but ({}) given for callee".format(expected_num_of_args, received_num_of_args))    

    # Compute arguments
    rawargs = (_gen_seq(arg, builder) for arg in seq.items[1:])
    # Cast arguments to expected types    
    args = [_cast(rawarg, llvm_op.arg_types[i], builder).value for i, rawarg in enumerate(rawargs)]    

    # Compute the function call and return that value
    return KResult(llvm_op.gen_fun(builder, *args, callee.llvm_opname), llvm_op.ret_type, callee)

def _gen_number(number, builder):
    """Converts a float string value into an IR double constant value"""
    assert isinstance(number, Number)
    try:
        # Integer
        if re.match(r"^[0-9]*$", number.text):
            value = int(number.text)
            if -2**(INT_SIZE-1) < value < 2**(INT_SIZE-1):
                return KResult(INT(value), INT, number)
            else:
                _raise(number, "Integer too big to fit in only {} bits".format(INT_SIZE))

        # Floating point    
        return KResult(F64(float(number.text)), F64, number)

    except ValueError:
        _raise(number, "Invalid number format")    


def _cast(result, expected_type, builder):
    # If same type, just return the result
    if result.type == expected_type:
        return result

    # If promotion possible, make it    
    if result.type == INT and expected_type == F64:
        return KResult(builder.sitofp(result.value, F64), F64, result.seq)
    
    # Otherwise : ERROR        
    _raise(result.seq, "Type mismatch error, expecting {} but got {} for".format(expected_type, result.type))


