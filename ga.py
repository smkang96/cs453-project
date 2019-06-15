import numpy as np # for sampling without replacement
import random
from copy import deepcopy
import string
import coverage
import traceback as tb
import sys
from typing import List, Tuple, Dict, Set, Any

from individual import *
from util import *
'''Test Case Generator for Python'''



class GeneticEnvironment(object):
    def __init__(self, f_name, cut_name, mut_name, mod_name,
                 gen_num = 50, pop_size = 50, mutate_rate = 0.2,
                 crossover_rate = 1.0, fit_weight_param = 0.5,
                 tournament_size = 4):
        self._cut_name = cut_name
        self._analyzer = Analyzer(f_name, cut_name)
        self._mut_name = mut_name
        self._mod_name = mod_name
        self._gen_num = gen_num
        self._pop_size = pop_size
        self._mutate_rate = mutate_rate
        self._crossover_rate = crossover_rate
        self._fit_weight_param = fit_weight_param
        self._tournament_size = tournament_size
        self._rtest_generator = RandomTestGenerator(f_name, cut_name, mut_name, self._analyzer, mod_name)
        # Set[((func_name, (type name, ...)), ...)]
        self._err_seq: Set[Any] = set()

    def add_err_seq(self, ind):
        self._err_seq.add(ind.to_comb())

    def is_err_seq(self, ind):
        return ind.to_comb() in self._err_seq

    def _sample_init(self):
        while True:
            ind = self._rtest_generator.make_individual()
            if not self.is_err_seq(ind):
                return ind

    def _sample_init_pop(self):
        return [self._sample_init() for _ in range(self._pop_size)]

    def _tournament_sel(self, indiv_list, rep=False):
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
        max_indiv_score = 0
        curr_pop_score = []

        for gen_idx in range(self._gen_num):
            curr_pop_score = []

            while len(curr_pop_score) < self._pop_size:
                print("gen:", gen_idx, ", pop:", len(curr_pop_score), ", err:", len(self._err_seq))
                while True:
                    indiv = self._sample_init()
                    try:
                        indiv_score = self.evaluate(indiv)
                    except (TypeError, AttributeError) as e:
                        # discard TypeError indiv and re-sample
                        self.add_err_seq(indiv)
                        continue
                    except (IndexError, ValueError):
                        indiv_score = 0
                    break
                if self.is_err_seq(indiv):
                    print(indiv.to_comb())
                max_indiv_score = indiv_score if indiv_score > max_indiv_score else max_indiv_score
                curr_pop_score.append((indiv, indiv_score))
                curr_pop_score = list(filter(lambda s: not self.is_err_seq(s[0]), curr_pop_score))

            for i, (indiv,_) in enumerate(curr_pop_score):
                if self.is_err_seq(indiv):
                    print(i, indiv.to_comb())
                    self.evaluate(indiv)
                    assert False

            sel_indivs = self._tournament_sel(curr_pop_score)

            # crossover (the paper isn't very clear here) & mutation
            new_gen = sel_indivs[:]
            while len(new_gen) < self._pop_size:
                parents = np.random.choice(sel_indivs, size=2, replace=False)
                new_indiv = self._crossover(parents[0], parents[1])
                for indiv in new_indiv:
                    if np.random.uniform() < self._mutate_rate:
                        if self.is_err_seq(indiv):
                            print(indiv.to_comb())
                            assert False
                        indiv = self._mutation(indiv)
                    new_gen.append(indiv)

            if max_indiv_score > 0.99:
                print('max individual score :', max_indiv_score)
                return list(map(lambda s: s[0], curr_pop_score)), max_indiv_score

        print('max individual score :', max_indiv_score)
        return list(map(lambda s: s[0], curr_pop_score)), max_indiv_score

    def evaluate(self, ind) -> float:
        # monitor coverage and run each individual
        cov = coverage.Coverage(branch=True)
        cov.start()
        ind.run()
        cov.stop()
        cov.save()

        analysis = cov._analyze(ind.file_name())
        stats = analysis.branch_stats()  # branch line |-> (total, taken)
        start, end = self._analyzer.func_info(ind.mut_name()).lines()
        total = 0
        taken = 0
        for b_line, (_total, _taken) in stats.items():
            if start <= b_line <= end:
                total += _total
                taken += _taken
        # analysis.branch_stats() is empty if there is no branch
        return taken / total if total > 0 else 1

    def _crossover(self, father, mother):
        children_method_seq = self._cut_and_splice_crossover(father.get_method_seq(), mother.get_method_seq())
        children_const_inputs = self._single_point_crossover(father.get_const_inputs(), mother.get_const_inputs())
        children_mut_inputs = self._single_point_crossover(father.get_mut_inputs(), mother.get_mut_inputs())

        for i in range(100):
            child1 = deepcopy(father)
            child1.set_method_seq(children_method_seq[0])
            child1.set_const_inputs(children_const_inputs[0])
            child1.set_mut_inputs(children_mut_inputs[0])
            if not self.is_err_seq(child1):
                break
            if i == 99:
                child1 = deepcopy(father)

        for i in range(100):
            child2 = deepcopy(mother)
            child2.set_method_seq(children_method_seq[1])
            child2.set_const_inputs(children_const_inputs[1])
            child2.set_mut_inputs(children_mut_inputs[1])
            if not self.is_err_seq(child2):
                break
            if i == 99:
                child2 = deepcopy(mother)

        return (child1, child2)

    def _cut_and_splice_crossover(self, father, mother):
        # for method call lists
        index1 = random.randint(0, len(father) )
        index2 = random.randint(0, len(mother) )

        child1 = father[:index1] + mother[index2:]
        child2 = mother[:index2] + father[index1:]

        return (child1, child2)

    def _single_point_crossover(self, father, mother):
        # for argument lists
        index = random.randint(0, min(len(father), len(mother)) )

        child1 = mother[:index] + father[index:]
        child2 = father[:index] + mother[index:]

        return (child1, child2)

    def _mutation(self, indiv):
        while True:
            mutated = deepcopy(indiv)
            if mutated.get_const_inputs():
                children_const_inputs = self._make_input_mutation('__init__', mutated.get_const_inputs())
                mutated.set_const_inputs(children_const_inputs)

            if mutated.get_method_seq():
                children_method_seq = self._make_method_mutation(mutated.get_method_seq())
                mutated.set_method_seq(children_method_seq)

            children_mut_inputs = self._make_input_mutation(mutated.mut_name(), mutated.get_mut_inputs())
            mutated.set_mut_inputs(children_mut_inputs)
            if not self.is_err_seq(mutated):
                return mutated

    def _make_method_mutation(self, method_seq):
        # for method call lists
        addorremove = random.randint(0, 1)
        if addorremove == 0:
            index = random.randint(0, len(method_seq) - 1)
            new_call = self._rtest_generator.any_rand_call()
            child = method_seq[:index] + [new_call] + method_seq[index:]
        else:
            index = random.randint(0, len(method_seq) - 1)
            child = method_seq[:index] + method_seq[(index+1):]
        return child

    def _make_input_mutation(self, func_name: str, arg_seq: List[ArgInput]):
        # for argument lists
        mutated = arg_seq[:]
        change_idx = random.randint(0, len(arg_seq) - 1)
        runprob = random.randint(0, 1)
        if runprob == 0:
            child = self._rtest_generator.any_rand_input()
            mutated[change_idx] = child
            # if not self._rtest_generator.is_err_comb(func_name, mutated):
            #     return mutated
        else:
            child = self._rtest_generator.same_type_new_val(mutated[change_idx])
            mutated[change_idx] = child
            # return mutated
        return mutated

#ge = GeneticEnvironment('apple', 'pear')
#print(ge._tournament_sel(list((i, i) for i in range(50))))
