from .tokens import *

import unittest

class TestTok(unittest.TestCase):

    def test_token(self):
        t = Token.mock("alpha")
        self.assertEqual(t.text, "alpha")
        self.assertTrue(t.match(Token, "alpha"))

        t = Identifier.mock("alpha")
        self.assertTrue(t.match(Identifier, "alpha"))
