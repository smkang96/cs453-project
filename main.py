import ast
import astor
import coverage
from os.path import abspath

class Collector(ast.NodeVisitor):

    def __init__(self):
        self.classes = {}  # class name |-> method name |-> (start line, end line)

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
        self.classes[m.parent.name][m.name] = (start, end)


fname = abspath('sut.py')
tree = astor.parse_file(fname)

# make parent pointers
tree.parent = None
for node in ast.walk(tree):
    for child in ast.iter_child_nodes(node):
        child.parent = node
collector = Collector()
collector.visit(tree)

cov = coverage.Coverage(branch=True)
cov.start()
import sut
sut.C().f(1, 1)
sut.C().f(1, 2)
cov.stop()
cov.save()
d = cov.get_data()

analysis = cov._analyze(fname)
bstats = analysis.branch_stats() # branch line |-> (total, taken)
bcov = {} # class name |-> method name |-> branch coverage
for c, m_lines in collector.classes.items():
    bcov[c] = {}
    for m, (start, end) in m_lines.items():
        total = 0
        taken = 0
        for b_line, (_total, _taken) in bstats.items():
            if start <= b_line < end:
                total += _total
                taken += _taken
        print(c, m, total, taken)
        bcov[c][m] = taken / total if total else -1



