import sys
import colorama
from termcolor import colored
colorama.init()
import parsing, codegen, codexec

commands = [
    'def add(a b) a + b',
    'add(1, 2)',
    'add(add(1,2), add(3,4))',
    'max(1,2)',        
    'max(max(1,2), max(3,4))',
    'factorial(5)',
    'def alphabet(a b) ( for x = 64 + a, x < 64 + b + 1 in putchard(x) ) - 64',
    'alphabet(1,26)'
]

USAGE = """USAGE: 
    run --help   : show this message 
    run --test   : run the unit tests       
    run file     : run the selected file .kal then exit        
    run command  : run the command then exit       
    run          : start the REPL """

def repl(optimize = True, llvmdump = False, noexec = False, parseonly = False, verbose = False):

    options = locals()
    
    k = codexec.KaleidoscopeEvaluator()

    def print_eval(command, options = dict()):
        try:
            for result in k.eval_generator(command, options):
                if not result.value is None:
                    print(colored(result.value, 'green'))
                if options.get('verbose'):
                    print()
                    # print(colored(result.ast.dump(), 'blue'), '\n')
                    print(colored(result.rawIR, 'green'), '\n')
                    print(colored(result.optIR, 'magenta'), '\n')

        except parsing.ParseError as err:
            print(colored('Parse error: ' + str(err), "red"))                    
        except codegen.CodegenError as err:
            print(colored('Eval error: ' + str(err), 'red'))
        except RuntimeError as err:
            print(colored('Internal error: ' + str(err), 'red'))

    # Load basic language library
    try:
        FILE = 'basiclib.kal' 
        with open(FILE) as file:
            print_eval(file.read())
    except FileNotFoundError:
        print(colored("Could not charge basic libairy:", red), FILE)

    # If some arguments passed in, open the file or execute the command then exit        
    if len(sys.argv) >= 2 :
        arg = ' '.join(sys.argv[1:])
        if arg in ['help', '-help', '--help', '-h', '-?', '?']:
            print(USAGE)
        elif arg in ['test', '-test', '--test', 'tests', '-t']:
            import unittest
            tests = unittest.defaultTestLoader.discover(".", "*.py")    
            unittest.TextTestRunner().run(tests)
        else:
            try: 
                with open(arg) as file:
                    print_eval(file.read(), options)
            except FileNotFoundError:
                print_eval(arg, options)
        return

    # Execute all predefined commands before entering the REPL
    for command in commands:
        print('K>', command)
        print_eval(command, options)

    REPL_HELP = """
    exit, quit:     Stop and exit the program.
    help, ?:        Print this message. 
    options:        Print the actual REPL setting. 
    <option_name>:  Settings are toggled by entering the option name.
    <command>:      Other instructions are passed to Kaleidoscope. 
    """    

    # Enter a REPL loop
    print(colored('Type help or a command to be interpreted', 'yellow'))
    command = ""
    while not command in ['exit', 'quit']:
        if command in options:
            options[command] = not options[command]
            print(command, '=', options[command])
        elif command in ['options']:
            print(colored(options, 'yellow'))                  
        elif command in ['help', '?']:
            print(colored(REPL_HELP, 'yellow'))                  
        elif command :  
            print_eval(command, options)
        else:
            # command is empty so
            pass    
        print("K> ", end="")
        command = input().strip()


if __name__ == '__main__':

    repl()    