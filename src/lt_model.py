from networkx import *
import math 
import random

def lt_model(graph, source, thres):
    
	nodes_dict={}
	stack = source
	activated = source

	for n in graph.nodes_iter():
		if not(n in nodes_dict):
 			nodes_dict[n]={'level':0}

	while len(stack)>0:
		node = stack.pop()
		for nei in graph.neighbors(node):
			nodes_dict[nei]['level']+=graph.in_degree(nei)
			if nodes_dict[nei]['level']>=thres and activated.count(nei)==0:
				activated.append(nei)
				stack.append(nei)

	return activated
