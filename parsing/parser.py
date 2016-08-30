import pdb
from . import binop
from .parser_feeder import *
from .seq import *


class CantEatAnymoreSignal(Exception):
    pass

def seq_from(stmt):
    """Given a stmt, returns an Abstract Syntax Tree representing it."""
    f = ParserFeeder(stmt)
    seq = _parse_items(f)
    # All tokens should have been eaten after parsing the list
    if not f.match(None):
        f.throw()   
    return Seq(seq)

def _parse_items(f):
    """ Parse a possibly empty sequence of expression """    
    items = list()
    try:
        while True:
            if(f.match(Block)):
                f.throw("Block construct not yet supported")
            else:     
                # items.append(_parse_binop(f))
                items.append(_parse_item(f))
    except CantEatAnymoreSignal:
        pass
    return items

def _parse_item(f):
    return _parse_atom(f)

def _parse_atom(f):

    if f.match('('): 
        if f.is_left_glued and not f.previous.match('('):
            f.throw("Token {} may not directly follow {}".format(f.current, f.previous))

        first, items, last = _parse_paren(f)

        if f.is_left_glued and not f.match(')'):
            f.throw("Token {} may not directly follow {}".format(f.current, f.previous))
        
        return Seq(items, first, last)

    elif f.match(Wordlike):
        return f.eat(Wordlike)    

    # elif f.match(Wordlike):
    #     callee = f.eat(Wordlike)
    #     while f.match('(') and f.is_left_glued:
    #         first, liste, last = _parse_paren(f)
    #         callee = Call(callee, liste, callee.first_token, last)
    #     return callee

    else:
        raise CantEatAnymoreSignal


def _parse_paren(f):

    return f.eat('('), _parse_items(f), f.eat(')')



# _NOT_A_BINOP = binop.BinOpInfo(-1, binop.Associativity.UNDEFINED) 

# def _binop_info(f):
#     """ Return a BinOpInfo about the current token.
#         If not an operator, return a precedence of -1 
#         and undefined associativy.
#         Raise an error if the operator is not defined.
#     """
#     if f.match(TokenKind.OPERATOR) and f.current.text not in PUNCTUATORS:
#         if f.postfix or f.prefix:
#             return _NOT_A_BINOP
#         return binop.info(f.current.text) \
#             or f.throw("Undefined binary operator") 
#     return _NOT_A_BINOP
    

# def _parse_binary(f):
#     lhs = _parse_unarian(f)
#     # Start with precedence 0 because we want to bind any operator to the
#     # expression at this point.
#     return _parse_binop_rhs(f, 0, lhs)


# def _parse_binary_rhs(f, expr_prec, lhs):
#     """Parse the right-hand-side of a binary expression.
#     expr_prec: minimal precedence to keep going (precedence climbing).
#     lhs: AST of the left-hand-side.
#     """
#     while True:
#         cur_prec, cur_assoc = _binop_info(f)
#         # If this is a binary operator with precedence lower than the
#         # currently parsed sub-expression, bail out. If it binds at least
#         # as tightly, keep going.
#         # Note that the precedence of non-binary is defined to be -1,
#         # so this condition handles cases when the expression ended.
#         if cur_prec < expr_prec:
#             return lhs
#         op = f.current.text
#         f.eat(TokenKind.OPERATOR) 
#         rhs = _parse_unarian(f)

#         next_prec, next_assoc = _binop_info(f)
#         # There are four options:
#         # 1. next_prec > cur_prec: we need to make a recursive call
#         # 2. next_prec == cur_prec and operator is left-associative: 
#         #    no need for a recursive call, the next
#         #    iteration of this loop will handle it.
#         # 3. next_prec == cur_prec and operator is right-associative:
#         #    make a recursive call 
#         # 4. next_prec < cur_prec: no need for a recursive call, combine
#         #    lhs and the next iteration will immediately bail out.
#         if cur_prec < next_prec:
#             rhs = _parse_binop_rhs(f, cur_prec + 1, rhs)

#         if cur_prec == next_prec and next_assoc == binop.Associativity.RIGHT:
#             rhs = _parse_binop_rhs(f, cur_prec, rhs)

#         # Merge lhs/rhs
#         lhs = Call("binary" + op, NewSeq([lhs, rhs]))


# def _parse_unarian(f):
#     if f.match(Operator) and f.is_right_glued():
#         return Call(f.current.text + '___', _parse_atom(f))        
#     else:
#         return _parse_atom(f)





