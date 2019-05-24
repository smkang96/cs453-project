#!/usr/bin/python
import random
import string

from individual import ArgInput, MethodCall, Individual

class Analyzer(object):
    class _FunctionInfo(object):
        def __init__(self, name, arg_info):
            self._name = name
            self._arg_info = arg_info

        def name(self):
            return self._name

        def arg_num(self):
            return len(self._arg_info)

    def __init__(self, class_name):
        self._func_list = self.funcs_in_class(class_name)

    def funcs_in_class(self, class_name):
        '''returns the methods in the class, a list of _FuncInfo objs'''
        raise NotImplementedError

    def func_arg_num(self, func_name):
        '''return function argument number given name'''
        i = 0
        while i != len(self._func_list):
            obj = self._func_list[i]
            if obj.name() == func_name:
                break
            i += 1
        if i == len(self._func_list):
            return -1
        else:
            return obj.arg_num()

    def num_methods(self):
        return len(self._func_list)

class RandomTestGenerator(object):
    '''provides random inputs for functions'''
    def __init__(self, cut_name, mut_name, analyzer, str_max_len = 10, int_max_val = 100, 
                 float_max_val = 100., max_fseq_num = 5):
        self._analyzer = analyzer
        self._mut_name = mut_name
        self._cut_name = cut_name
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
        return ArgInput('str', ret_str)

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
            all_funcs = self._analyzer.funcs_in_class()
        rand_func = random.choice(all_funcs)
        rand_func_args = self.fill_args(rand_func.name())
        return MethodCall(rand_func.name(), rand_func_args)


    def fill_args(self, func_name):
        num_args = self._analyzer.func_arg_num(func_name)
        arg_list = [None] * num_args
        for i in range(num_args):
        	arg_list[i] = self.any_rand_input()
        return arg_list

    def fill_method_seq(self):
        func_calls = []
        all_funcs = self._analyzer.funcs_in_class()
        for i in range(self._max_fseq_num):
            rand_func_call = self.any_rand_call(all_funcs)
            func_calls.append(rand_func_call)
        return func_calls

    def make_individual(self):
    	class_name = self._cut_name
    	constructor_args = self.fill_args('__init__')
    	method_calls = self.fill_method_seq()
    	mut_name = self._mut_name
    	mut_list = self.fill_args(mut_name)
    	return Individual(class_name, constructor_args, method_calls, mut_name, mut_list)