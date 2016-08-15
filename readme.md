## Synopsis

This Python project implements the [Kaleidoscope](http://llvm.org/docs/tutorial/index.html) toy language as described on the LLVM tutorial (up to the part Mutable Variables). For that purpose, it uses the [llvmlite](http://llvmlite.readthedocs.io/en/latest/) python library. That project code is heavily inspired from the [pykaleidoscope project of eliben](https://github.com/eliben/pykaleidoscope). The main differences are the followings:

* The code is separated in logical modules (lexer, parser, codegenerator, etc.) instead of being all in a single file.
* Only the final tutorial step is presented, so there is no step files (1, 2, 3, 4, etc.)
* A simple command line REPL has been added to drive code interpretation.
* Code file can be runned.
* A basic language standard functions and operators library is automatically loaded before execution.
* The language has been modified a little bit...
  * For loops increments need to be specified like this `x + 1` instead of `1`.  This permits more expressive looping steps like iterating through the first 10 powers of 2 like this: `for x = 1, x < 1024, x * 2 in expr`.
  * The for loop condition is checked before body execution and not after, so there is no extra run. Hence the for loop behaves just like expected in any other programming language.
  * No semicolon `;` is needed as a separator between instructions.
  * No comma `,` is needed to separate variables in a `var` instruction. 

## Motivation

I made this project as a way to teach myself the basics of LLVM, and made it public as a way to show others what can be done because there is not much LLVM simple stuff out there on the Internet. And the official LLVM tutorial, being written in C++, is not that easy to follow if your are not acquainted with that language. 

## Installation and examples

Python needs to be installed first if not already available on your system. I used version 3.5 with  [miniconda3](http://conda.pydata.org/miniconda.html) under Windows, but any OS should work just fine. Then install llvmlite:
```
conda install llvmlite
```
There is no need to install LLVM on its own since the llvmlite install includes a subset of LLVM which is just fine for our purposes.

Then download the pykaleidoscope code in its own folder, open a command line in that folder and execute the `run.py` file to launch the kaleidoscope jit-compiler/interpreter. A prompt will show up like this `K>`. At the prompt, type `test`, to run the tests and make sure everything works well. Then, to get in touch with the power of this very simple language, run the `mandelbrot.kal` program by simply entering its name after the prompt. The pykaleidoscope REPL will load the program, compile it in memory and then run it, which will show a basic [Mandelbrot set](https://en.wikipedia.org/wiki/Mandelbrot_set). Well, I am not the author of that Mandelbrot stuff, since it comes from the original LLVM tutorial, but it is indeed quite a surprising realisation for such a simple language. 

```
K> test
... unit tests stuff showing up ...
K> mandelbrot.kal
... mandelbrot set showing up ...
K> 2 + 3     # or any other kaleidoscope code
5.0
K> exit
... return to command line from here ...
```   

Enjoy!