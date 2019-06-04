'''Implementation of individual class'''

class String(str):
    pass

class ArgInput(object):
    def __init__(self, input_type, input_val):
        self._type = input_type
        self._val = input_val

    def type(self):
        return self._type

    def val(self):
        return self._val

class MethodCall(object):
    def __init__(self, method_name, inputs):
        self._method_name = method_name
        self._inputs = list(inputs)

    def method_name(self):
        return self._method_name

    def inputs(self):
        return self._inputs

class Individual(object):
    def __init__(self, file_name, class_name, const_list, method_list, mut_name, mut_list, mod_name):
        self._file_name = file_name   # abspath
        self._class_name = class_name # for constructor
        self._const_list = const_list
        self._method_list = method_list
        self._mut_name = mut_name
        self._mut_list = mut_list
        self._mod_name = mod_name

    def file_name(self):
        return self._file_name

    def mut_name(self):
        return self._mut_name

    def run(self):
        mod_name = self._file_name[:-3].split('/')[-1]
        s = ''
        s += f'''
import importlib.util
spec = importlib.util.spec_from_file_location('{mod_name}', '{self._file_name}')
SUT = importlib.util.module_from_spec(spec)
spec.loader.exec_module(SUT)\n
'''

        if self._class_name :
            s += 'obj = SUT.%s(%s)\n' % (self._class_name, ', '.join(str(e.val()) for e in self._const_list))
            for mc in self._method_list:
                s += 'obj.%s(%s)\n' % (mc.method_name(), ', '.join(str(e.val()) for e in mc.inputs()))
            s += 'obj.%s(%s)' % (self._mut_name, ', '.join(str(e.val()) for e in self._mut_list))

        else:
            for mc in self._method_list:
                s += 'SUT.%s(%s)\n' % (mc.method_name(), ', '.join(str(e.val()) for e in mc.inputs()))
            s += 'SUT.%s(%s)' % (self._mut_name, ', '.join(str(e.val()) for e in self._mut_list))

        # add fitness func I guess
        print(s)
        try:
            exec(s)
        except:
            pass
        return s

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

if __name__ == "__main__":
    i = Individual('String', [ArgInput('int', 1)], [MethodCall('index', [ArgInput('str', "'1'")])], 'split', [])
    i.run()

