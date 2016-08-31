# lib imports
import sys
import pdb
import colorama
from termcolor import colored, cprint
colorama.init()

# local imports
from code_error import *
from lexing import lexer
from parsing import indenter, parser, seq
import irgenerator, optimizer, executer

LEX     = {"lex", "lexer"}
INDENT  = {"indent", "indenter"}
PARSE   = {"parse", "parser"}
IR      = {"ir", "codegen"}
OPTIM   = {"optim", "optimize"}
EXEC    = {"exec", "run"}
DEBUG   = {"debug"}

OPTIONS = DEBUG
MODULES = LEX | INDENT | PARSE | IR | OPTIM | EXEC
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
    seqs = [ parser.seq_from(stmt) for stmt in stmts ]
    if modules & PARSE:
        for seq in seqs:
            cprint(seq.to_code(), 'blue') 
    modules -= PARSE
    if not modules:
        return

    # ir codegen
    codegens = [ irgenerator.irgen(seq) for seq in seqs ]
    if modules & IR:
        for codegen in codegens:
            cprint(codegen, 'magenta') 
    modules -= IR
    if not modules:
        return

    # ir optimization
    optimods = [ optimizer.optimize(codegen) for codegen in codegens ]
    if modules & OPTIM:
        for optimod in optimods:
            cprint(optimod, 'cyan') 
    modules -= OPTIM
    if not modules:
        return

    # code execution
    results = [ executer.exec(optimod) for optimod in optimods ]
    if modules & EXEC:
        for result in results:
            cprint(result, 'green') 
    modules -= EXEC
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
        repl(EXEC)    


if __name__ == '__main__':

    run()

