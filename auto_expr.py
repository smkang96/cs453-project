'''experiment script'''
import subprocess as sp
import multiprocessing as mp

all_exprs = [
	#'python3 main.py --class_file suts/Red-Black-Tree/rb_tree.py --class_name RedBlackTree --mut_name add',
	#'python3 main.py --class_file suts/Chessnut/game.py --class_name Game --mut_name apply_move',
	#'python3 main.py --class_file suts/Chessnut/board.py --class_name Board --mut_name set_position',
	#'python3 main.py --class_file suts/sunrise_sunset.py --class_name SunriseSunset --mut_name __init__',
	'python3 main.py --class_file suts/linked_list.py --class_name LinkedList --mut_name remove',
	#'python3 main.py --class_file suts/linked_list.py --class_name LinkedList --mut_name index',
	#'python3 main.py --class_file suts/line.py --mut_name intersect',
	#'python3 main.py --class_file suts/sut.py --class_name C --mut_name f',
	#'python3 main.py --class_file suts/triangle.py --class_name Triangle --mut_name testTriangle',
	#'python3 main.py --class_file suts/unionfind.py --class_name UnionFind --mut_name union',
	#'python3 main.py --class_file venv/lib/python3.6/site-packages/stdnum/isbn.py --mod_name stdnum.isbn --mut_name validate'
]

def shell_exec(cmd):
	final_expr = cmd + POSTAMBLE
	print('starting cmd: %s' % cmd)
	with open('temp', 'w') as noprint_file:
		sp.call(final_expr.split(), stdout=noprint_file)

#POSTAMBLE = ' --gen_num 1 --pop_size 10000'
POSTAMBLE = ' --gen_num 200'

pool = mp.Pool(4)
pool.map(shell_exec, all_exprs)
