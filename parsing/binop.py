from enum import *
from collections import namedtuple

@unique
class Associativity(Enum):
    UNDEFINED = 0
    LEFT = 1
    RIGHT = 2 

BinOpInfo = namedtuple('BinOpInfo', ['precedence', 'associativity'])

BUILTIN_OP = {
    ':': BinOpInfo(1, Associativity.LEFT),  
    '=': BinOpInfo(2, Associativity.RIGHT), # Assignment
    '&': BinOpInfo(5, Associativity.LEFT),  # Logical and
    '|': BinOpInfo(5, Associativity.LEFT),  # Logical or
    '<': BinOpInfo(10, Associativity.LEFT), 
    '>': BinOpInfo(10, Associativity.LEFT), 
    '?': BinOpInfo(10, Associativity.LEFT), # Equality 
    '+': BinOpInfo(20, Associativity.LEFT), 
    '-': BinOpInfo(20, Associativity.LEFT), 
    '/': BinOpInfo(40, Associativity.LEFT),
    '*': BinOpInfo(40, Associativity.LEFT),
    '%': BinOpInfo(40, Associativity.LEFT),
    '^': BinOpInfo(50, Associativity.RIGHT)  # Exponentiation
    }


def builtin_operators():
    return sorted(BUILTIN_OP.keys())  

_binop_map = dict(BUILTIN_OP)

def get(op):
    return _binop_map.get(op) 

def set(op, precedence, associativity):
    _binop_map[op] = BinOpInfo(precedence, associativity)
