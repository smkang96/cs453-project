import ast
import astor
import coverage
from os.path import abspath
from random import randint
import sys

from individual import *
from util import *
from ga import *

test_candidate = sys.argv[1]

if test_candidate == 'isbn-validate' :
    fname = abspath('venv/lib/python3.7/site-packages/stdnum/isbn.py')
    modname = 'stdnum.isbn' # for external library module
    cname = ''
    mutname = 'validate'

if test_candidate == 'sut' :
    fname = abspath('sut.py')
    modname = ''
    cname = 'C'
    mutname = 'f' 

analyzer = Analyzer(fname, cname)
ge = GeneticEnvironment(fname, cname, mutname, modname)
ge.evolve()

'''
ind = Individual(
    fname, cname,
    [],
    [],
    mutname,
    [ArgInput('int', randint(-10, 10)) for _ in range(2)])
'''