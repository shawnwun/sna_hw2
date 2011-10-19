from networkx import *
import lt_model
import ic_model

def greedy_block (graph, sources):
	block_nodes= []
	new_graph = graph.copy()
	temp_node=0	

	while len(block_nodes) < (int)(graph.number_of_nodes()*0.05):
		curr = len(ic_model.ic_model_ori(new_graph, sources, 0.8))
		for i in new_graph:
			if sources.count(i)==0:
				temp_graph = new_graph.copy()
				temp_graph.remove_node(i)
				temp = ic_model.ic_model_inc(temp_graph, sources, 0.8, curr)
				if temp < curr:
					curr = temp
					temp_node = i
		block_nodes.append(temp_node)
		print len(block_nodes)
		new_graph.remove_node(temp_node)
		temp_node=0

	return block_nodes
