import sys
import colorama
from termcolor import colored
colorama.init()
import parsing, codegen, codexec

operators = [
    'def binary & 5 (P Q) if P then if Q then 1 else 0 else 0',        
    'def binary | 5 (P Q) if P then 1 else if Q then 1 else 0',        
    'def unary ! (P) if P then 0 else 1',
    'def unary - (x) 0 - x',
    'def binary > 10 (a b) b < a',        
    'def binary = 10 (a b) !(a < b) & !(b < a)',
    # unicode not yet supported        
    # 'def binary ≥ 10 (a b) !(a < b)',        
    # 'def binary ≤ 10 (a b) !(b < a)',
    # 'def binary ≠ 10 (a b) !(a = b)'	        
]


commands = [
    'def add(a b) a + b',
    'add(1, 2)',
    'add(add(1,2), add(3,4))',
    'def max(a b) if a < b then b else a',
    'max(1,2)',        
    'max(max(1,2), max(3,4))',
    'def factorial(n) if n < 2 then 1 else n * factorial(n-1)',
    'factorial(5)',
    'def alphabet(a b) ( for x = 64 + a, x < 64 + b + 1 in putchard(x) ) - 64',
    'alphabet(1,26)'
] + operators

def repl(optimize = True, llvmdump = False, noexec = False, parseonly = False):

    options = locals()
    
    k = codexec.KaleidoscopeEvaluator()

    def print_eval(command, options):
        try:
            for result in k.eval_generator(command, **options):
                if not result is None:
                    print(colored(result, 'green'))
        except parsing.ParseError as err:
            print(colored('Parse error: ' + str(err), "red"))                    
        except codegen.CodegenError as err:
            print(colored('Eval error: ' + str(err), 'red'))
        except RuntimeError as err:
            print(colored('Internal error: ' + str(err), 'red'))            

    if len(sys.argv) >= 2 :
        print_eval(' '.join(sys.argv[1:]), options)
        return

    # Execute all predefined commands
    for command in commands:
        print('K>', command)
        print_eval(command, options)

    # Then enter a simple REPL loop
    print(colored('Type exit or quit to stop the program', 'yellow'))
    command = ""
    while not command in ['exit', 'quit']:
        if command in options:
            options[command] = not options[command]
            print(command, '=', options[command])
        elif command in ['options']:
            print(colored(options, 'yellow'))                  
        elif command :  
            print_eval(command, options)
        else:
            # command is empty so
            pass    
        print("K> ", end="")
        command = input().strip()


if __name__ == '__main__':

    repl()    