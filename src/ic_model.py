from networkx import *
import math
import random

# prob = 0.8
def ic_model_ori(graph, sources, prob):

	stack= list(sources)
	infected = list(sources)
	tried = []
	
	# diffusion process
	while len(stack)>0:
		#print len(infected) 
		temp = stack.pop()
		if tried.count(temp)==0:
			for nei in graph.neighbors(temp):
				if random.random()<=prob and infected.count(nei)==0:
					infected.append(nei)
					stack.append(nei)
		tried.append(temp)

	return infected

def ic_model_inc(graph, sources, prob, thre):
	
	stack = list(sources)
	infected = list(sources)
	tried = []

	while len(stack)>0:
		temp = stack.pop()
		if tried.count(temp)==0:
			for nei in graph.neighbors(temp):
				if random.random()<=prob and infected.count(nei)==0:
					infected.append(nei)
					stack.append(nei)
		tried.append(temp)
		if len(infected)>=thre:
			break

	return min(len(infected), thre)
