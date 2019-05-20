#!/usr/bin/python

import numpy as np # for sampling without replacement
import random
import copy

'''Test Case Generator for Python'''

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

class GeneticEnvironment(object):
    def __init__(self, cut_name, mut_name, 
                 gen_num = 50, pop_size = 50, mutate_rate = 0.2,
                 crossover_rate = 1.0, fit_weight_param = 0.5,
                 tournament_size = 4):
        self._cut_name = cut_name
#	self._analyzer = Analyzer(cut_name)
        self._mut_name = mut_name
        self._gen_num = gen_num
        self._pop_size = pop_size
        self._mutate_rate = mutate_rate
        self._crossover_rate = crossover_rate
        self._fit_weight_param = fit_weight_param
        self._tournament_size = tournament_size

    def _sample_init_pop(self):
        raise NotImplementedError

    def _tournament_sel(self, indiv_list, rep = False):
        chosens = []
        scorebook = {idv[0]:idv[1] for idv in indiv_list}
        idv_names = list(scorebook.keys())
        while len(idv_names) != 0:
            try:
                competitors = np.random.choice(idv_names, size=4, replace=rep)
            except ValueError:
                competitors = idv_names[:] 
            for indiv_name in competitors:
                i_idx = idv_names.index(indiv_name)
                del idv_names[i_idx]
            chosen_one = max(competitors, key=lambda x: scorebook[x])
            chosens.append(chosen_one)
        return chosens

    def evolve(self):
        '''returns best individuals'''
        init_pop = self._sample_init_pop()
        curr_pop = init_pop
        for gen_idx in range(self._gen_num):
            curr_pop_score = []

            # evaluate individuals
            for individual in curr_pop:
                indiv_score = individual.score()
                curr_pop_score.append((individual, indiv_score))
	    sel_indivs = self._tournament_sel(self._tournament_size)
            
            # crossover (the paper isn't very clear here) & mutation
            new_gen = sel_indivs[:]
            while len(new_gen) < self._pop_size:
                parents = np.random.choice(sel_indivs, size=2, replace=True)
                new_indiv = self._crossover(parents[0], parents[1])
                if np.random.uniform() < self._mutate_rate:
                    new_indiv = mutate(new_indiv)
                new_gen.append(new_indiv)

            # cleanup
            curr_pop = new_gen[:]
        return curr_pop # end after given number of iterations

	def _crossover(self, father, mother):
		children_method_seq = self._cut_and_splice_crossover(father.get_method_seq(), mother.get_method_seq())
		children_const_inputs = self._single_point_crossover(father.get_const_inputs(), mother.get_const_inputs())

		child1 = copy.deepcopy(father)
		child1.set_method_seq(children_method_seq[0])
		child1.set_const_inputs(children_const_inputs[0])

		child2 = copy.deepcopy(mother)
		child2.set_method_seq(children_method_seq[1])
		child2.set_const_inputs(children_const_inputs[1])

		return (child1, child2)

	def _cut_and_splice_crossover(self, father, mother):
		# for method call lists
		index1 = random.randint(1, len(father) - 1)
		index2 = random.randint(1, len(mother) - 1)

		child1 = father[:index1] + mother[index2:]
		child2 = mother[:index2] + father[index1:]

		return (child1, child2)
	
	def _single_point_crossover(self, father, mother):
		# for argument lists
		index = random.randint(1, min(len(father), len(mother)) - 1)

		child1 = father[:index] + mother[index:]
		child2 = mother[:index] + father[index:]

		return (child1, child2)

#ge = GeneticEnvironment('apple', 'pear')	
#print(ge._tournament_sel(list((i, i) for i in range(50))))










