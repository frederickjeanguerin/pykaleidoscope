# lib imports
import sys
import pdb
import colorama
from termcolor import colored, cprint
colorama.init()

# local imports
from code_error import *
from lexing import lexer
from parsing import indenter, parser, nodes


LEX = {"lex", "lexer"}
INDENT = {"indent", "indenter"}
PARSE = {"parse", "parser"}
DEBUG = {"debug"}

OPTIONS = DEBUG
MODULES = LEX | INDENT | PARSE
ALL = OPTIONS | MODULES 

def eval(codestr, modules):
    # print("codestr: ", repr(codestr))

    # lexing
    tokens = list(lexer.tokens_from(codestr))
    if modules & LEX:
        for t in tokens:
            cprint("   " + repr(t), 'green')
    modules -= LEX
    if not modules:
        return
        
    # indenting
    stmts = list(indenter.stmts_from(iter(tokens)))
    if modules & INDENT:
        for stmt in stmts:
            cprint(stmt.dump(2, 3).rstrip('\n'), 'cyan') 
    modules -= INDENT
    if not modules:
        return

    # parsing
    asts = [ parser.ast_from(stmt) for stmt in stmts ]
    if modules & PARSE:
        for ast in asts:
            cprint(nodes.flatten(ast), 'yellow') 
            # cprint(ast.dump(2, 3), 'blue') 
    modules -= PARSE
    if not modules:
        return

    print("Unimplemented operations:", modules)    



def repl(modules):
    cprint("Type 'exit' or 'quit' to terminate.", 'yellow')
    codestr = ""
    while not codestr in ['exit', 'quit']:
        if codestr:
            try:
                eval(codestr, set(modules))
            except CodeError as err:
                print(err)
        cprint("K> " , 'yellow', end="")
        codestr = input()
        while codestr[-1] == "\\":
            cprint(" > ", 'yellow', end="")
            codestr = codestr[:-1] + "\n" + input()
            

def run():

    if len(sys.argv) >= 2 :
        modules = set(sys.argv[1:])
        unexpected = modules - ALL 
        if unexpected :
            print("Unexpected modules in", modules)    
        else:
            repl(modules)    

    else:
        repl(PARSE)    


if __name__ == '__main__':

    run()

