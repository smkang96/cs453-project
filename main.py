import argparse

from individual import *
from util import *
from ga import *


'''
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

if test_candidate == 'triangle' :
    fname = abspath('triangle.py')
    modname = ''
    cname = 'Triangle'
    mutname = 'testTriangle'

'''

def main(parser):
    fname = abspath(parser.class_file)
    modname = parser.mod_name
    cname = parser.class_name
    mutname = parser.mut_name
    gen_num = parser.gen_nmum
    pop_size = parser.pop_size

    ge = GeneticEnvironment(fname, cname, mutname, modname, gen_num, pop_size)
    ge.evolve()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate Test Data.')
    parser.add_argument('--class_file', help='file containing class under test',
                        type=str)
    parser.add_argument('--class_name', help='name of class under test',
                        type=str)
    parser.add_argument('--mod_name', type=str)
    parser.add_argument('--mut_name', help='name of method under test',
                        type=str)
    parser.add_argument('--gen_num', help='number of generations (0 random)',
                        type=int, default=50)
    parser.add_argument('--pop_size', help='population size',
                        type=int, default=50)
    parser = parser.parse_args()
    main(parser)
