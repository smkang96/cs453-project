import ast
import astor
import random
import string
from os.path import abspath
from typing import List, Tuple

from individual import ArgInput, MethodCall, Individual

class ArgInfo():
    def __init__(self, name):
        self._name = name
        # self._annot = annot  # type annotation

    def name(self):
        return self._name


class FuncInfo(object):
    def __init__(self, name, arg_infos, lines):
        self._name: str = name
        self._arg_info: List[ArgInfo] = arg_infos
        # is this func def defined at top level
        self._is_top = len(arg_infos) == 0 \
                       or arg_infos[0].name() not in ['self', 'cls']
        self._lines: Tuple[int,int] = lines

    def name(self):
        return self._name

    # # of args excluding self or cls
    def arg_num(self):
        return len(self._arg_info) if self._is_top else len(self._arg_info) - 1

    def lines(self):
        return self._lines

# TODO: per file? per class? ~> non-methods?
# TODO: extend to full analyzer: args, types
class Analyzer(ast.NodeVisitor):

    def __init__(self, file_name, class_name=''):
        self._file_name: str = abspath(file_name)
        self._class_name: str = class_name
        self._func_list: List[FuncInfo] = []

        tree = astor.parse_file(self._file_name)
        tree.parent = None
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node
        self.visit(tree)

    def visit_ClassDef(self, c):
        if c.name == self._class_name:
            self.generic_visit(c)

    def visit_FunctionDef(self, m: ast.FunctionDef):
        # a function def is not necessarily a method def
        # is method <-> self._class_name != ''
        if isinstance(m.parent, ast.ClassDef) != (self._class_name != ''):
            return

        assert m.args.vararg is None
        assert m.args.kwonlyargs == []
        assert m.args.kw_defaults == []
        assert m.args.kwarg is None
        # assert m.args.defaults == []

        def endline(n):
            if hasattr(n, 'finalbody') and len(n.finalbody) > 0:
                return endline(n.finalbody[-1])
            if hasattr(n, 'orelse') and len(n.orelse) > 0:
                return endline(n.orelse[-1])
            if hasattr(n, 'body'):
                return endline(n.body[-1])
            return n.lineno
        start = m.lineno
        end = endline(m)
        arg_infos = list(map(lambda arg: ArgInfo(arg.arg), m.args.args))
        self._func_list.append(FuncInfo(m.name, arg_infos, (start, end)))

    def funcs(self) -> List[FuncInfo]:
        '''returns the methods in the class, a list of FuncInfo objs'''
        return self._func_list

    def func_info(self, func_name) -> FuncInfo:
        for func in self._func_list:
            if func.name() == func_name:
                return func
        assert False

    def num_methods(self):
        return len(self._func_list)


class RandomTestGenerator(object):
    '''provides random inputs for functions'''
    def __init__(self, file_name, cut_name, mut_name, analyzer, mod_name = None, str_max_len = 10, int_max_val = 100,
                 float_max_val = 100., max_fseq_num = 5):
        self._analyzer: Analyzer = analyzer
        self._file_name = abspath(file_name)
        self._mut_name = mut_name
        self._cut_name = cut_name
        self._mod_name = mod_name
        self._str_max_len = str_max_len
        self._int_max_val = int_max_val
        self._float_max_val = float_max_val
        self._max_fseq_num = max_fseq_num

    def _rand_int(self):
        rand_val = random.randint(-self._int_max_val, self._int_max_val)
        return ArgInput('int', rand_val)

    def _rand_str(self):
        ingredient_str = string.printable[:-3]
        ingredient_num = len(ingredient_str)
        rand_str_len = random.randint(1, self._str_max_len)
        ret_str = ''
        for c_idx in range(rand_str_len):
            rand_idx = random.randint(0, ingredient_num-1)
            ret_str += ingredient_str[rand_idx]
        return ArgInput('str', '"' + ret_str + '"')

    def _rand_float(self):
        rand_val = 2*self._float_max_val*random.random()-self._float_max_val
        return ArgInput('float', rand_val)

    def type_same_new_val(self, input_node):
        input_type = input_node.type()
        if input_type == 'int':
            return self._rand_int()
        elif input_type == 'str':
            return self._rand_str()
        else:
            return self._rand_float()

    def any_rand_input(self):
        arg_type = random.randint(0, 2)
        if arg_type == 0:
            return self._rand_int()
        elif arg_type == 1:
            return self._rand_str()
        elif arg_type == 2:
            return self._rand_float()

    def any_rand_call(self, all_funcs = None):
        if all_funcs is None:
            all_funcs = self._analyzer.funcs()
        rand_func = random.choice(all_funcs)
        rand_func_args = self.fill_args(rand_func.name())
        return MethodCall(rand_func.name(), rand_func_args)


    def fill_args(self, func_name):
        num_args = self._analyzer.func_info(func_name).arg_num()
        arg_list = [None] * num_args
        for i in range(num_args):
            arg_list[i] = self.any_rand_input()
        return arg_list

    def fill_method_seq(self):
        func_calls = []
        all_funcs = self._analyzer.funcs()
        num_calls = random.randint(0, self._max_fseq_num)
        for i in range(num_calls):
            rand_func_call = self.any_rand_call(all_funcs)
            func_calls.append(rand_func_call)
        return func_calls

    def make_individual(self):
        class_name = self._cut_name
        constructor_args = self.fill_args('__init__') if class_name else []
        method_calls = self.fill_method_seq()
        mut_name = self._mut_name
        mut_list = self.fill_args(mut_name)
        file_name = self._file_name
        mod_name = self._mod_name
        return Individual(file_name, class_name, constructor_args, method_calls, mut_name, mut_list, mod_name)
