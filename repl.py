import copy, colorama, llvmlite, sys
from importlib import reload
from termcolor import colored, cprint
colorama.init()

import parsing, codegen, codexec, lexing.lexer
from lexing.source import Source


class ReloadException(Exception): pass

VERSION = "0.1.3"

EXAMPLES = [
    'def add(a b) a + b',
    'add(1, 2)',
    'add(add(1,2), add(3,4))',
    'max(1,2)',        
    'max(max(1,2), max(3,4))',
    'factorial(5)',
    'def alphabet(a b) ( for x = 64 + a, x < 64 + b + 1 in putchard(x) ) - 64',
    'alphabet(1,26)'
]

USAGE = """
USAGE: From the K> prompt, either type some kaleidoscope code or 
    enter one the following special commands (all preceded by a dot sign):

    .example      : Run some code examples.
    .exit or exit : Stop and exit the program.
    .functions    : List all available language functions and operators 
    .help or help : Show this message. 
    .options      : Print the actual options settings. 
    .reload or .. : Reload the python code and restart the REPL from scratch. 
    .reset        : Reset the interpreting engine. 
    .test or test : Run unit tests.       
    .version      : Print version information.      
    .<file>       : Run the given file .kal        
    .<option>     : Toggle the given option on/off.

These commands are also available directly from the command line, for example: 

    kal 2 + 3
    kal test
    kal .myfile.kal
    
On the command line, the initial dot sign can be replaced with a double dash: 
    
    kal --test
    kal --myfile.kal
    """

history = []

def errprint(msg):
    cprint(msg, 'red', file=sys.stderr)

def print_eval(k, code, options = dict()):
    """Evaluate the given code with evaluator engine k using the given options.
    Print the evaluation results. """
    results = k.eval_generator(code, options);
    try:
        for result in results :
            if not result.value is None:
                cprint(result.value, 'green')
            else:
                history.append(result.ast)
                    
            if options.get('verbose'):
                print()
                # print(colored(result.ast.dump(), 'blue'), '\n')
                cprint(result.rawIR, 'green')
                print()
                cprint(result.optIR, 'magenta')
                print()
    except parsing.ParseError as err:
        message, token = err.args
        errprint('Parse error: {} {}'.format(colored(message,'white'), colored(token, 'blue')))
    except codegen.CodegenError as err:
        errprint('Eval error: ' + str(err))
        # Reset the interpreter because codegen is now corrupted.
        k.reset(history)
    except Exception as err:
        errprint(str(type(err)) + ' : ' + str(err))
        print(' Aborting... ')
        raise

def run_tests():
    import unittest
    tests = unittest.defaultTestLoader.discover(".", "*.py")    
    unittest.TextTestRunner().run(tests)


def print_funlist(funlist):
    for func in funlist:
        description = "{:>6} {:<20} ({})".format(
            'extern' if func.is_declaration else '   def',
            func.name,
            ' '.join((arg.name for arg in func.args)) 
        )
        cprint(description, 'yellow')


def print_functions(k):
    # Operators
    print(colored('\nBuiltin operators:', 'blue'), *parsing.builtin_operators())

    # User vs extern functions
    sorted_functions = sorted(k.codegen.module.functions, key=lambda fun: fun.name)
    user_functions = filter(lambda f : not f.is_declaration, sorted_functions)
    extern_functions = filter(lambda f : f.is_declaration, sorted_functions)

    cprint('\nUser defined functions and operators:\n', 'blue')
    print_funlist(user_functions)

    cprint('\nExtern functions:\n', 'blue')
    print_funlist(extern_functions)

def run_repl_command(k, command, options):
    if command in options:
        options[command] = not options[command]
        print(command, '=', options[command])
    elif command in ['example', 'examples']:
        run_examples(k, EXAMPLES, options)
    elif command in ['functions']:
        print_functions(k)                  
    elif command in ['help', '?', '']:
        print(USAGE)                  
    elif command in ['options']:
        print(options)                  
    elif command in ['quit', 'exit', 'stop']:
        sys.exit()
    elif command in ['reload', '.']:
        reload(lexing.lexer)
        reload(parsing)
        reload(codegen)
        reload(codexec)
        raise ReloadException()
    elif command in ['repl']:
        pass
    elif command in ['reset']:
        reload(parsing)
        k.reset()
        history = []
    elif command in ['test', 'tests']:
        run_tests()
    elif command in ['version']:
        print('Python :', sys.version)
        print('LLVM   :', '.'.join((str(n) for n in llvmlite.binding.llvm_version_info)))
        print('pykal  :', VERSION)
        cprint('\nFree software by Frederic Guerin', 'magenta')
    elif command :
        # Here the command should be a filename, open it and run its content
        filename = command  
        try: 
            with open(filename) as file:
                print_eval(k, Source(filename, file.read()), options)
        except FileNotFoundError:
            errprint("File not found: " + filename)

def run_command(k, command, options):
    print(colorama.Fore.YELLOW, end='')
    if not command:
        pass
    elif command in ['help', 'quit', 'exit', 'stop', 'test']:
        run_repl_command(k, command, options)
    elif command[0] == '.':
        run_repl_command(k, command[1:], options)
    else:
        # command is a kaleidoscope code snippet so run it
        print_eval(k, Source("prompt",command), options)
    print(colorama.Style.RESET_ALL, end='')

def run_examples(k, commands, options):
    for command in commands:
        print('K>', command)
        print_eval(k, Source("examples", command), options)    

def enter_repl(k, options):
    cprint('Type help or a command to be interpreted', 'green')
    command = ""
    while not command in ['exit', 'quit']:
        run_command(k, command, options)
        print("K> ", end="")
        command = input().strip()

def run(optimize = True, llvmdump = False, noexec = False, parseonly = False, verbose = False):

    options = locals()
    k = codexec.KaleidoscopeEvaluator('basiclib.kal')

    # If some arguments passed in, run that command then exit        
    if len(sys.argv) >= 2 :
        command = ' '.join(sys.argv[1:]).replace('--', '.')
        if command not in ['.repl', 'repl'] :
            run_command(k, command, options)
            return

    enter_repl(k, options)


if __name__ == '__main__':

    import kal
    kal.run()

