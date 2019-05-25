import ast
import astor
import coverage
from os.path import abspath
from random import randint

from individual import *
from util import *
from ga import *


fname = abspath('sut.py')
modname = 'sut'
cname = 'C'

analyzer = Analyzer(fname, cname)

ge = GeneticEnvironment(fname, 'C', 'f')

ind = Individual(
        fname, cname,
        [],
        [],
        'f',
        [ArgInput('int', randint(-10, 10)) for _ in range(2)])
