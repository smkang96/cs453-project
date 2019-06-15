import numpy as np # for sampling without replacement
import random
import copy
import string
import coverage
import traceback as tb
import sys

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

    def _sample_init_pop(self):
        # raise NotImplementedError
        return [self._rtest_generator.make_individual() for _ in range(self._pop_size)]

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
        while True:
            init_pop = self._sample_init_pop()
            curr_pop = init_pop
            max_indiv_score = 0
            restart = False
            print("start")

            for gen_idx in range(self._gen_num):
                curr_pop_score = []

                # evaluate individuals
                for individual in curr_pop:
                    try:
                        indiv_score = self.evaluate(individual)
                    except (TypeError, AttributeError) as e:
                        exc_type, exc_value, exc_traceback = sys.exc_info()
                        #  print(exc_type, exc_value)
                        #  tb.print_tb(exc_traceback)
                        # print(repr(tb.extract_tb(exc_traceback)[1].name))
                        stack = tb.extract_tb(exc_traceback)
                        err_fn = stack[-1].name
                        lineno = stack[-2].lineno
                        # TODO: analyze lineno to figure out what method call caused the error
                        #  print(exc_value)
                        err_call = individual.analyze_err(stack)
                        self._rtest_generator.add_err_comb(err_call)
                        restart = True
                        indiv_score = -1
                    except IndexError:
                        indiv_score = 0

                    max_indiv_score = indiv_score if indiv_score > max_indiv_score else max_indiv_score
                    # TODO: don't add obviously useless individuals with negative score.
                    if indiv_score >= 0:
                        curr_pop_score.append((individual, indiv_score))

                print(gen_idx, len(curr_pop_score))
                # TODO: if too many useless individuals, just restart
                restart |= len(curr_pop_score) < 6
                if restart:
                    print("restart")
                    break

                sel_indivs = self._tournament_sel(curr_pop_score)

                # crossover (the paper isn't very clear here) & mutation
                new_gen = sel_indivs[:]
                while len(new_gen) < self._pop_size:
                    parents = np.random.choice(sel_indivs, size=2, replace=False)
                    new_indiv = self._crossover(parents[0], parents[1])
                    for indiv in new_indiv :
                        if np.random.uniform() < self._mutate_rate:
                            indiv = self._mutation(indiv)
                        new_gen.append(indiv)

                # cleanup
                curr_pop = new_gen[:]

            if restart:
                continue

            print('max individual score :', max_indiv_score)
            return curr_pop, max_indiv_score, curr_pop[:]

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

        child1 = copy.deepcopy(father)
        child1.set_method_seq(children_method_seq[0])
        child1.set_const_inputs(children_const_inputs[0])
        child1.set_mut_inputs(children_mut_inputs[0])

        child2 = copy.deepcopy(mother)
        child2.set_method_seq(children_method_seq[1])
        child2.set_const_inputs(children_const_inputs[1])
        child2.set_mut_inputs(children_mut_inputs[1])

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
        if indiv.get_const_inputs():
            children_const_inputs = self._make_input_mutation('__init__', indiv.get_const_inputs())
            indiv.set_const_inputs(children_const_inputs)

        if indiv.get_method_seq() :
            children_method_seq = self._make_method_mutation(indiv.get_method_seq())
            indiv.set_method_seq(children_method_seq)

        children_mut_inputs = self._make_input_mutation(indiv.mut_name(), indiv.get_mut_inputs())
        indiv.set_mut_inputs(children_mut_inputs)

        return indiv

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
        while True:
            change_idx = random.randint(0, len(arg_seq) - 1)
            runprob = random.randint(0, 1)
            if runprob == 0:
                child = self._rtest_generator.any_rand_input()
                arg_seq[change_idx] = child
                if not self._rtest_generator.is_err_comb(func_name, arg_seq):
                    break
            else:
                child = self._rtest_generator.same_type_new_val(arg_seq[change_idx])
                arg_seq[change_idx] = child
                break
        return arg_seq

#ge = GeneticEnvironment('apple', 'pear')
#print(ge._tournament_sel(list((i, i) for i in range(50))))
