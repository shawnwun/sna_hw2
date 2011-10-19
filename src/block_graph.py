from networkx import *

def degree_block(graph, source):
	
	block_nodes=[]
	count = 0
	cent = degree_centrality(graph)
	values = cent.values()
	values.sort(reverse=True)
	
	# other centrality measures: in_degree_centrality ; out_degree_centrality
	# betweenness_centrality ; closeness_centrality
	
	print values[150]
	while len(block_nodes) < (int)(graph.number_of_nodes()*0.05):
		for i in cent.keys():	
			if len(block_nodes) >= (int)(graph.number_of_nodes()*0.05):
				break
			if float(cent[i]) == float(values[count]):
				if source.count(i)==0:
					block_nodes.append(i)
					count += 1
				else:
					count += 1		

	#for n in block_nodes:
	#	print cent[n]
	return block_nodes

def deg_clo_block(graph, source, ratio):
	
	block_nodes = []
	count = 0
	deg = degree_centrality(graph)
	clo = closeness_centrality(graph)
	values_deg = deg.values().sort()
	values_clo = clo.values().sort()

	while count < (int)(graph.number_of_nodes()*ratio*0.05):
		for i in deg.keys():
			if count >= (int)(graph.number_of_nodes()*ratio*0.05):
				break
			if deg[i] == values_deg[count] and source.count(i) ==0:
				block_nodes.append(i)
				count += 1
			elif deg[i] == values_deg[count] and source.count(i)>0:
				count += 1

	count = 0

	while count < (int)(graph.number_of_nodes()*(1-ratio)*0.05):
		for i in clo.keys():
			if count >= (int)(graph.number_of_nodes()*(1-ratio)*0.05):
				break
			if clo[i] == values_clo[count] and source.count(i) == 0:
				block_nodes.append(i)
				count += 1
			elif clo[i] == values_clo[count] and source.count(i)>0:
				count += 1
	
	return block_nodes	

def deg_bet_block(graph, source, ratio):
	
	block_nodes = []
	count = 0
	deg = degree_centrality(graph)
	bet = betweenness_centrality(graph)
	values_deg = deg.values().sort()
	values_bet = bet.values().sort()

        while count < (int)(graph.number_of_nodes()*ratio*0.05):
                for i in deg.keys():
                        if count >= (int)(graph.number_of_nodes()*ratio*0.05):
                                break
                        if deg[i] == values_deg[count] and source.count(i) ==0:
                                block_nodes.append(i)
                                count += 1
                        elif deg[i] == values_deg[count] and source.count(i)>0:
                                count += 1

        count = 0

        while count < (int)(graph.number_of_nodes()*(1-ratio)*0.05):
                for i in bet.keys():
                        if count >= (int)(graph.number_of_nodes()*(1-ratio)*0.05):
                                break
                        if bet[i] == values_bet[count] and source.count(i) == 0:
                                block_nodes.append(i)
                                count += 1
                        elif bet[i] == values_bet[count] and source.count(i)>0:
                                count += 1

        return block_nodes

