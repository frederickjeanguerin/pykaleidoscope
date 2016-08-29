from .lexer import *
import unittest

def _lex(codestr, _lambda = lambda x : x):
    return [_lambda(tok) for tok in tokens_from(codestr)]

def _lex_kind(codestr):
    return _lex(codestr, lambda x : x.__class__)

def _lex_text(codestr):
    return _lex(codestr, lambda x : str(x))

class TestLexer(unittest.TestCase):

    def _assert_sametok(self, tok1, tok2):
        self.assertEqual(tok1.text, tok2.text)
        self.assertEqual(tok1.kind, tok2.kind)

    def _assert_kinds(self, codestr, kinds):
        self.assertListEqual(_lex_kind(codestr), kinds + [EOF])

    def _assert_texts(self, codestr, texts):
        self.assertListEqual(_lex_text(codestr), texts + ['<EOF>'])

    def _assert_lex(self, codestr, expected_tokens):
        tokens = _lex(codestr)
        self.assertEqual(len(tokens), len(expected_tokens) + 1)
        for i, tok in enumerate(tokens[:-2]):
            self.assertTrue(tok.match(*expected_tokens[i]))
        self.assertTrue(tokens[-1].match(EOF))    

    def test_lexer_empty(self):
        self.assertEqual(_lex_kind(''), [EOF])

    def test_lexer_number(self):
        self._assert_kinds('1', [Number])
        self._assert_texts('1', ['1'])
        self._assert_kinds('12', [Number])
        self._assert_lex('.1519', [(Number, '.1519')])
        self._assert_lex('23.15', [(Number, '23.15')])
        self._assert_lex('1519.', [(Number, '1519.')])

    def test_lexer_iden(self):
        self._assert_lex('an_identifier', [(Identifier, 'an_identifier')])

    def test_operator_char(self):
        for char in "*$-/":
            self.assertTrue(is_operator_char(char))
        for char in " \n\t()a0_":
            self.assertFalse(is_operator_char(char))

    def test_lexer_operator(self):
        self._assert_lex('+', [(Operator, '+')])
        self._assert_lex('++', [(Operator, '++')])
        self._assert_lex(' ++ ', [(Operator, '++')])
        self._assert_lex(' >= ', [(Operator, '>=')])

    def test_lexer_punctuator(self):
        self._assert_lex('(', [(Punctuator, '(')])
        self._assert_lex('(((', [(Punctuator, '(')]*3)
                
    def test_lexer_simple_expr(self):
        self._assert_lex('a+1', [(Identifier, 'a'),(Operator, '+'),(Number,'1')])

    def test_token_kinds(self):
        self._assert_kinds(
            '10.1 def + (',
            [Number, Identifier, Operator, Punctuator])

        self._assert_kinds(
            '+- 1 2 22 22.4 a b2 C3d',
            [Operator, Number, Number, Number, Number,
             Identifier, Identifier, Identifier])

    def test_skip_whitespace_comments(self):
        self._assert_kinds(
            '''
            def foo # this is a comment
            # another comment
            \t\t\t10
            ''',
            [Identifier, Identifier, Number])

    def test_lineinfo(self):
        toks = _lex('   line1   \n   line2  line2   ')
        self.assertEqual(toks[1].text, 'line2')
        self.assertEqual(toks[1].lineno, 2)
        self.assertEqual(toks[1].colno, 4)
