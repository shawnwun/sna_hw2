import networkx as nx

G = nx.Graph()   # or DiGraph, MultiGraph, MultiDiGraph, etc
G.add_node(1)
G.add_node('Hello')
G.number_of_nodes()


#G.add_node(1,size=10)
G.add_node(3,weight=0.4,UTM=('13S',382871,3972649))
