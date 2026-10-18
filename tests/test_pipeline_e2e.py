from pathlib import Path
import unittest
from noyaba.lexer import Lexer
from noyaba.parser import parse
from noyaba.compiler import Compiler
from noyaba.vm import VM

ROOT = Path(__file__).parents[1]

class SourceToBytecodeE2E(unittest.TestCase):
    def run_file(self, name):
        source = (ROOT / 'examples' / 'e2e' / name).read_text()
        tokens = Lexer(source).tokens()
        ast = parse(source)
        chunk = Compiler().compile(ast)
        vm = VM(); vm.run(source)
        return tokens, ast, chunk, vm.output

    def test_variables_and_operators_file(self):
        tokens, ast, chunk, output = self.run_file('variables.noy')
        self.assertEqual(output, ['5', '8'])
        self.assertTrue(any(t.line == 1 for t in tokens))
        self.assertTrue(any(i.line == 1 for i in chunk.code))

    def test_functions_and_recursion_file(self):
        _, _, chunk, output = self.run_file('functions.noy')
        self.assertEqual(output, ['120'])
        self.assertTrue(any(i.op.name == 'CALL' for i in chunk.code))

    def test_loops_and_conditions_file(self):
        _, _, chunk, output = self.run_file('loops.noy')
        self.assertEqual(output, ['6', 'OK'])
        self.assertTrue(any(i.op.name == 'JUMP' for i in chunk.code))

    def test_runtime_constructs_file(self):
        _, _, _, output = self.run_file('runtime.noy')
        self.assertEqual(output, ['20', '10', '7', '10'])

    def test_public_runner_contract(self):
        source = (ROOT / 'examples' / 'e2e' / 'variables.noy').read_text()
        vm = VM(); self.assertEqual(vm.run(source), ['5', '8'])

if __name__ == '__main__': unittest.main()
