'''Implementation of individual class'''
from typing import List
import traceback as tb
import sys


class String(str):
    pass

class ArgInput(object):
    def __init__(self, input_type, input_val):
        self._type: str = input_type
        self._val = input_val

    def type(self) -> str:
        return self._type

    def val(self):
        return self._val

class MethodCall(object):
    def __init__(self, method_name, inputs):
        self._method_name = method_name
        self._inputs: List[ArgInput] = list(inputs)

    def method_name(self) -> str:
        return self._method_name

    def inputs(self) -> List[ArgInput]:
        return self._inputs

class Individual(object):
    def __init__(self, file_name, class_name, const_list, method_list, mut_name, mut_list, mod_name):
        self._file_name: str = file_name   # abspath
        self._class_name: str = class_name # for constructor
        self._const_list: List[ArgInput] = const_list
        self._method_list: List[MethodCall] = method_list
        self._mut_name: str = mut_name
        self._mut_list: List[ArgInput] = mut_list
        self._mod_name: str = mod_name

    def file_name(self):
        return self._file_name

    def mut_name(self):
        return self._mut_name

    def prefix(self):
        mod_name = self._file_name[:-3].split('/')[-1]
        prefix = f'''
import importlib.util
spec = importlib.util.spec_from_file_location('{mod_name}', '{self._file_name}')
SUT = importlib.util.module_from_spec(spec)
spec.loader.exec_module(SUT)\n
'''
        return prefix

    def body(self):
        s = ''
        if self._class_name:
            s += 'obj = SUT.%s(%s)\n' % (self._class_name, ', '.join(str(e.val()) for e in self._const_list))
            for mc in self._method_list:
                s += 'obj.%s(%s)\n' % (mc.method_name(), ', '.join(str(e.val()) for e in mc.inputs()))
            s += 'obj.%s(%s)' % (self._mut_name, ', '.join(str(e.val()) for e in self._mut_list))

        else:
            for mc in self._method_list:
                s += 'SUT.%s(%s)\n' % (mc.method_name(), ', '.join(str(e.val()) for e in mc.inputs()))
            s += 'SUT.%s(%s)' % (self._mut_name, ', '.join(str(e.val()) for e in self._mut_list))
        return s

    def code(self):
        return self.prefix() + self.body()

    def run(self):
        exec(self.code())

    def analyze_err(self, stack) -> MethodCall:
        # traverse stack, find the point at which failure occurred in exec(<string>)
        err_line = 0
        for i in range(len(stack)-1, 0, -1):
            s = stack[i]
            if s.filename == '<string>':
                err_line = s.lineno
        assert err_line > 0
        return self.call_at_line(err_line)

    def call_at_line(self, lineno: int) -> MethodCall:
        prefix_lines = self.prefix().split('\n')
        prefix_len = len(prefix_lines) if prefix_lines[-1] != '' else len(prefix_lines)-1
        constructor_len = 1 if self._class_name else 0
        call_lineno = lineno - prefix_len - constructor_len
        # TODO: dirty
        if call_lineno == 0: # possible iff the call is constructor call
            return MethodCall('__init__', self._const_list)
        if 1 <= call_lineno <= len(self._method_list):
            return self._method_list[call_lineno-1]
        if call_lineno == len(self._method_list)+1: # mut
            return MethodCall(self._mut_name, self._mut_list)
        assert False

    # ((func_name, (type name, ...)), ...)
    def to_comb(self):
        call_seq = []
        call_seq.append(('__init__', to_type_comb(self._const_list)))
        for m in self._method_list:
            call_seq.append((m.method_name(), to_type_comb(m.inputs())))
        call_seq.append((self._mut_name, to_type_comb(self._mut_list)))
        return tuple(call_seq)

    def get_method_seq(self):
        return self._method_list

    def set_method_seq(self, new_list):
        self._method_list = new_list[:]

    def get_const_inputs(self):
        return self._const_list

    def set_const_inputs(self, new_inputs):
        self._const_list = new_inputs[:]

    def get_mut_inputs(self):
        return self._mut_list

    def set_mut_inputs(self, new_inputs):
        self._mut_list = new_inputs[:]

def to_type_comb(inputs: List[ArgInput]):
    return tuple(map(lambda x: x.type(), inputs))

if __name__ == "__main__":
    i = Individual('String', [ArgInput('int', 1)], [MethodCall('index', [ArgInput('str', "'1'")])], 'split', [])
    i.run()


