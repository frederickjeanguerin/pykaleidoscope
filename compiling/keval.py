from .executer import exec
from .optimizer import optimize
from .ircoder import *
from parsing.parser import *

def eval(codestr):
    """ Evals a single instruction in the current context
        Raises an error if more than one statement is present"""
    return exec(optimize(ir_from(parse(codestr))))

def evals_gen(codestr):
    """Yield results for every statement in codestr"""
    return (exec(optimize(ir_from(seq))) for seq in seqs_gen(codestr))
            
