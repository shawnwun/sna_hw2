import sys
import ic_model
import lt_model
import greedy_block
import block_graph
from networkx import *

ratio = 0.0

def main():
	
	graph_path = sys.argv[1]
	source_path = sys.argv[2]
	graph = read_edgelist(graph_path, create_using=DiGraph(), nodetype=int)	
	sources = read_source(source_path)	

	#Part 1: diffusion phase
	#lt_model(graph)	
	infected = ic_model.ic_model_ori(graph, sources, 0.8)
	ratio = (float)(len(infected))/graph.number_of_nodes()	
	print ratio

	#Part 2: block phase
	block = block_graph.degree_block(graph, sources)
	#block = greedy_block.greedy_block(graph, sources)
	new_graph = graph
	for i in range(5):
		for b in block[(int)(i*0.2*len(block)):(int)((i+1)*0.2*len(block))]:
			new_graph.remove_node(b) 
		infected = ic_model.ic_model_ori(new_graph, sources, 0.8)
		ratio = (float)(len(infected))/graph.number_of_nodes()
		print ratio
#		file_name = '%s%d' % (sys.argv[2], i)
#		output(infected, file_name)

def read_source(path):
	source = []
	f = file(path, 'r')
	while True:
		line = f.readline()
		if line == '':
			break
		source.append(int(line))
	f.close()
	return source

def output(nodes, path):
	f = file(path, 'w')
	f.write('%d %d\n' % (len(nodes), ratio))	
	for i in nodes:
		f.write('%s\n' % i)

if __name__ == '__main__':
	sys.exit(main());
