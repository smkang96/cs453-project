import ast
import astor
import coverage
from os.path import abspath
from random import randint

from individual import *


# TODO: extend to full analyzer: args, types
# TODO: proper class info, method info type
# FIXME: expects only numeric plain args
class Collector(ast.NodeVisitor):

    def __init__(self):
        self.classes = {}  # class name |-> method name |-> (start line, end line, num_args)

    def visit_ClassDef(self, c):
        self.classes[c.name] = {}
        self.generic_visit(c)

    def visit_FunctionDef(self, m):
        def endline(n):
            if hasattr(n, 'finalbody'):
                return endline(n.finalbody[-1])
            if hasattr(n, 'orelse'):
                return endline(n.orelse[-1])
            if hasattr(n, 'body'):
                return endline(n.body[-1])
            return n.lineno
        start = m.lineno
        end = endline(m)
        self.classes[m.parent.name][m.name] = (start, end, len(m.args.args) - 1) # self



fname = abspath('sut.py')
tree = astor.parse_file(fname)

# make parent pointers
tree.parent = None
for node in ast.walk(tree):
    for child in ast.iter_child_nodes(node):
        child.parent = node

# collect class, method info
collector = Collector()
collector.visit(tree)
c_info = collector.classes

# build very simple individuals for each class, method
# i = Individual('String', [ArgInput('int', 1)], [MethodCall('index', [ArgInput('str', "'1'")])], 'split', [])
individuals = {}
for c, m_info in c_info.items():
    individuals[c] = {}
    for m, (_, _, n_args) in m_info.items():
        if m != "__init__":
            individuals[c][m] = Individual(
                    c,
                    [ArgInput('int', randint(-10, 10)) for _ in range(c_info[c]['__init__'][2])],
                    [], # FIXME: empty method list, for now
                    m,
                    [ArgInput('int', randint(-10, 10)) for _ in range(n_args)])

# monitor coverage and run each individual
cov = coverage.Coverage(branch=True)
cov.start()
for c, m_inds in individuals.items():
    for m, ind in m_inds.items():
        ind.exec()
cov.stop()
cov.save()
d = cov.get_data()

analysis = cov._analyze(fname)
bstats = analysis.branch_stats() # branch line |-> (total, taken)
bcov = {} # class name |-> method name |-> branch coverage
for c, m_info in c_info.items():
    bcov[c] = {}
    for m, (start, end, _) in m_info.items():
        total = 0
        taken = 0
        for b_line, (_total, _taken) in bstats.items():
            if start <= b_line < end:
                total += _total
                taken += _taken
        bcov[c][m] = taken / total if total else -1
