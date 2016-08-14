import sys
import copy
import colorama
from termcolor import colored
colorama.init()
import parsing, codegen, codexec

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

USAGE = """USAGE: 
    example    : Run some code examples.
    exit, quit : Stop and exit the program.
    help, ?    : Show this message 
    options    : Print the actual options. 
    reset      : Reset the interpreter. 
    test       : Run unit tests       
    <code>     : Compile and run the given code       
    <file>     : Run the selected file .kal        
    <option>   : Toggle the given option on/off."""

history = []

def print_eval(k, code, options = dict()):
    """Evaluate the given code with evaluator engine k using the given options.
    Print the evaluation results. """
    results = k.eval_generator(code, options);
    try:
        for result in result :
            if not result.value is None:
                print(colored(result.value, 'green'))
            else:
                history.append(result.ast)
                    
            if options.get('verbose'):
                print()
                # print(colored(result.ast.dump(), 'blue'), '\n')
                print(colored(result.rawIR, 'green'), '\n')
                print(colored(result.optIR, 'magenta'), '\n')
    except parsing.ParseError as err:
        print(colored('Parse error: ' + str(err), "red"))                    
    except codegen.CodegenError as err:
        print(colored('Eval error: ' + str(err), 'red'))
        # Reset the interpreter because codegen is now corrupted.
        k.reset(history)
    except Exception as err:
        print(colored(str(type(err)) + ' : ' + str(err), 'red'))
        print(colored(' Aborting... ', 'yellow'))
        raise

def run_tests():
    import unittest
    tests = unittest.defaultTestLoader.discover(".", "*.py")    
    unittest.TextTestRunner().run(tests)

def run_command(k, command, options):
    if command in options:
        options[command] = not options[command]
        print(command, '=', options[command])
    elif command in ['example', 'examples']:
        run_examples(k, EXAMPLES, options)
    elif command in ['help', '?']:
        print(colored(USAGE, 'yellow'))                  
    elif command in ['options']:
        print(colored(options, 'yellow'))                  
    elif command in ['quit', 'exit', 'stop']:
        sys.exit()
    elif command in ['reset']:
        k.reset()
        history = []
    elif command in ['test', 'tests']:
        run_tests()
    elif command :
        # If the command is a filename, open it and run its content  
        try: 
            with open(command) as file:
                command = file.read()
        except FileNotFoundError:
            pass
        print_eval(k, command, options)
    else:
        # command is empty so
        pass    

def run_examples(k, commands, options):
    for command in commands:
        print('K>', command)
        print_eval(k, command, options)    

def repl(optimize = True, llvmdump = False, noexec = False, parseonly = False, verbose = False):

    options = locals()
    k = codexec.KaleidoscopeEvaluator('basiclib.kal')

    # If some arguments passed in, run that command then exit        
    if len(sys.argv) >= 2 :
        command = ' '.join(sys.argv[1:])
        run_command(k, command, options)
    else:    
        # Enter a REPL loop
        print(colored('Type help or a command to be interpreted', 'yellow'))
        command = ""
        while not command in ['exit', 'quit']:
            run_command(k, command, options)
            print("K> ", end="")
            command = input().strip()


if __name__ == '__main__':

    repl()    