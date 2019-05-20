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
    def __init__(self, class_name, const_list, method_list, mut_name, mut_list):
        self._class_name = class_name # for constructor
        self._const_list = const_list
        self._method_list = method_list
        self._mut_name = mut_name
        self._mut_list = mut_list

    def exec(self):
        test_str = ''
        test_str += 'obj = %s(%s)\n' % (self._class_name, ', '.join(str(e.val()) for e in self._const_list))
        for mc in self._method_list:
            test_str += 'obj.%s(%s)\n' % (mc.method_name(), ', '.join(str(e.val()) for e in mc.inputs()))
        test_str += 'obj.%s(%s)' % (self._mut_name, ', '.join(str(e.val()) for e in self._mut_list))

        # add fitness func I guess
        exec(test_str)

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

i = Individual('String', [ArgInput('int', 1)], [MethodCall('index', [ArgInput('str', "'1'")])], 'split', [])
i.exec()

