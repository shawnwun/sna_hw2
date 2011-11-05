import sys;
import os;
import networkx as nx;
import random;
import math;
from networkx import *;
import operator
#0 = susceptible
#1 = infected
#2 = recovered
#3 = immuned

MODEL_NAME = "LLT"

BIRTH = 0.5
DICE = 6

MAX_PER_NODE = 5

def main(argv=None):

    if len(sys.argv) < 4:
        print "ERROR!! Usage: python llt_model_p2.py cleanGraphPath infectedPath blocklistPath";
        exit();
    
    inputFile = sys.argv[1];
    infectFile = sys.argv[2];
    blockFile = file(sys.argv[3],'r');

    block = True;
    """
    if len(sys.argv) == 5:
        if sys.argv[4] == "-b":
            block = True;
    """
    lltGraph = readGraph(inputFile);
    [lltGraph, infected] = addInfectNodes(infectFile, lltGraph);

    blocklist = []
    while True:
	line = blockFile.readline()
	if len(line)==0:
	    break
	node = line.replace("\n", "");
	blocklist.append(node)

    [lltGraph, blockList] = addBlockNodes(lltGraph, blocklist);

    inf = list(infected);

    allInfected = runSim(lltGraph, infected);
    infSum = len(allInfected);
        
    print infSum/(1* float(lltGraph.number_of_nodes()));
    
        
    

def runSim(lltGraph, infected):    
    allInfected = [];    

    allInfected.extend(infected);
        
    iCount = 0;
    #print infected
    while (True):
        newInfect = [];
        newRecover = [];

        s = 0;
        i = 0;
        r = 0;

	#finding next infected nodes
        for infectN in infected:
            #find the neighbors of infected nodes
            neighborList = lltGraph.neighbors(infectN);
            
            for n, attr in lltGraph.nodes_iter(True):
                if n in neighborList:
                    st = attr['status'];

                    #if node status is susceptible, try to infect
                    if (st == 0):
                        rand = random.random();
                        if (rand < BIRTH):
			    #print 'infect'
			    rand = random.randrange(0,DICE)
			    attr['date'] = rand+1
                            newInfect.append(n);
			    lltGraph.add_node(n,status=1,date=rand+1)

            #try to recover
	    lltGraph.node[infectN]['date'] -= 1
	    if lltGraph.node[infectN]['date']==0:
		newRecover.append(infectN)
		lltGraph.add_node(infectN, status=2, date=0);

        #update infected list
        infected = [];
        for n, attr in lltGraph.nodes_iter(True):
            if (attr['status'] == 0):
                s+=1;
            if (attr['status'] == 1):
                i+=1;
                infected.append(n);
            if (attr['status'] == 2):
                r+=1;

        #print lltGraph.nodes(True);
        print "Iter: %d, new infect: %d, new recover: %d, s: %d, i: %d, r:%d" %(iCount, len(newInfect), len(newRecover), s, i, r);
        iCount+=1;

        for n in infected:
            if not (n in allInfected):
                allInfected.append(n);
        
        if (i == 0):
            break;

    return allInfected;


def fact(n):
    r = 1
    while(n>1):
	r = r * n
	n -= 1
    return r


def addBlockNodes(g, blocklist):
    #print blocklist
    for n in blocklist: 
	g.add_node(n, status=3);   
              
    #print g.number_of_nodes()
    return [g, blocklist];


def getDegreeList(g):
    degToNode = {};
    for n, degree in g.degree_iter():
        if degree in degToNode:
            nodeList = degToNode[degree];
            nodeList.append(n);
            degToNode[degree] = nodeList;
        else:
            nodeList = [];
            nodeList.append(n);
            degToNode[degree] = nodeList;
    return degToNode;
        

def addInfectNodes(infectFilePath, g):
    inputFh = open(infectFilePath, 'r');
    infected = []
    
    for line in inputFh:
        infectedNode = line.replace("\n", "");

        if infectedNode in g:           
	    rand = random.randrange(0,DICE) 
            g.add_node(infectedNode, status = 1, date = rand+1);
            infected.append(infectedNode);
            #g[infectedNode]['status'] = 1;
        
    inputFh.close();

    return [g, infected];

def readGraph(filePath):
    inputFh = open(filePath, 'r');

    diGraph = nx.DiGraph();

    for line in inputFh:
        line = line.replace("\n", "");
        splitLine = line.partition("\t");

        if (len(splitLine) == 3):
            node1 = splitLine[0];
            node2 = splitLine[2];
        
            diGraph.add_node(node1, status = 0, date=0);
            diGraph.add_node(node2, status = 0, date=0);
            diGraph.add_edge(node1, node2);        

    inputFh.close();

    return diGraph;

if __name__ == "__main__":
    sys.exit(main());
