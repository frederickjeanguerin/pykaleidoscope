from .executer import exec
from .optimizer import optimize
from .irbuilder import *
from parsing.parser import *

def eval_mod(mod, ret_type):
    result = exec(mod)
    if (ret_type == INT):
        result = int(result)
    else:
        assert ret_type == F64        
    return result

def eval(codestr):
    """ Evals a single instruction in the current context
        Raises an error if more than one statement is present"""
    module, ret_type = ir_from(check_expr(codestr))    
    return eval_mod(optimize(module), ret_type)

def evals_gen(codestr):
    """Yield results for every statement in codestr"""
    for kcall in kcalls_gen(codestr):
        module, ret_type = ir_from(kcall)    
        yield eval_mod(optimize(module), ret_type)
                    
