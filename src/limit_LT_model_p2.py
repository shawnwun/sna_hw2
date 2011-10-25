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
        print "ERROR!! Usage: python llt_model_p2.py cleanGraphPath infectedPath outputFilePath -b";
        exit();
    
    inputFile = sys.argv[1];
    infectFile = sys.argv[2];
    outFileName = sys.argv[3];

    block = False;

    if len(sys.argv) == 5:
        if sys.argv[4] == "-b":
            block = True;

    lltGraph = readGraph(inputFile);
    [lltGraph, infected] = addInfectNodes(infectFile, lltGraph);

    for i in range(1, 6):
        g = lltGraph.copy();
        inf = list(infected);
        blockPerc = float(i/100.0);

        infSum = 0;
        for j in range (0, 1):
            g = lltGraph.copy();
            inf = list(infected);

            if (block):
		#[g, blockList] = randomWalkBlocking(g, inf, blockPerc)
                [g, blockList] = addBlockNodes(g, inf, blockPerc);
            
            print "%.2f, %d" % (blockPerc, j);
            allInfected = runSim(g, infected);
            infSum += len(allInfected);
        
        print "%.2f: %.2f" % (blockPerc, infSum/(1* float(g.number_of_nodes())));
    
        outputFile =  outFileName + "_" + str(blockPerc) + ".txt";
        
        outputFh = open(outputFile, 'w');

	if block:
	    for n in blockList:
		outputFh.write(n + "\n");

        outputFh.close();
    

def runSim(lltGraph, infected):    
    allInfected = [];    

    allInfected.extend(infected);
        
    iCount = 0;

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

def randomWalkBlocking(g, infectedList, blockPercent):
    
    blockCount = int (math.floor(g.number_of_nodes() * blockPercent));
    blockList = []    

    subgraph = []
    for src in infectedList:
	subgraph.extend(g.neighbors(src))
	for nei in g.neighbors(src):
	    subgraph.extend(g.neighbors(nei))
    

    #calculate expectation of infection
    infectExpectation = {}
    for n in g:
	neighbors = g.neighbors(n)
	out_deg = g.out_degree(n)
	for nei in neighbors:
	    if nei in infectedList:
		out_deg -= 1
	e = 0
	for i in range(out_deg+1):
	    e += float(i) * float(fact(out_deg)/fact(i)/fact(out_deg-i)) * math.pow(BIRTH,out_deg)
	infectExpectation[n] = e
	#print out_deg, e

    # setup random walk
    infectProb = {}
    infusion = {}
    isDiffused = {}
    for n in g:
	infectProb[n] = 0
	infusion[n] = []
    for n in infectedList:
	infectProb[n] = 1.0

    # start random walk
    for iteration in range(175):
	# random diffusion
	#print iteration
	if iteration==0:
	    for n in infectedList:
		if not isDiffused.has_key(n) and not infectProb[n]==0:
		    neighbors = g.neighbors(n)
		    for nei in neighbors:
			infusion[nei].append(infectProb[n]*BIRTH)
		    isDiffused[n] = 1
	else:
	    for n in g:
		if not isDiffused.has_key(n) and not infectProb[n]==0:
		    neighbors = g.neighbors(n)
		    for nei in neighbors:
			infusion[nei].append(infectProb[n]*BIRTH)
		    isDiffused[n] = 1	

	# update self infect prob
	for n in g:
	    if not len(infusion[n])==0:
		myInfectProb = infectProb[n]
		nonInfectProb = 1.0
		for prob in infusion[n]:
		    nonInfectProb *= (1-prob)
		infectProb[n] = myInfectProb + (1-myInfectProb) * (1-nonInfectProb)
		#print infectProb[n], infusion[n]
		del infusion[n][:]
	
	if (iteration+1)%25==0:
	    isDiffused.clear()   
 
    # calculate expectation of infection for each node
    for n in g:
	infectExpectation[n] = infectExpectation[n] * infectProb[n]   
 
    sorted_nodes = sorted(infectExpectation.iteritems(), key=operator.itemgetter(1), reverse=True)
    for i in range(blockCount):
	if sorted_nodes[i][0] not in infectedList and sorted_nodes[i][0] in subgraph:
	    blockList.append(sorted_nodes[i][0])  
	    g.add_node(sorted_nodes[i][0],status=3)
	    #print sorted_nodes[i][0], infectProb[sorted_nodes[i][0]], infectExpectation[sorted_nodes[i][0]]
 
    return [g,blockList]





def addBlockNodes(g, infectedList, blockPercent):
    #degToNode = getDegreeList(g);

    degToNode = {};
    for n in infectedList:
        deg = g.out_degree(n);
        if deg in degToNode:
            nodeList = degToNode[deg];
            nodeList.append(n);
            degToNode[deg] = nodeList;
        else:
            nodeList = [];
            nodeList.append(n);
            degToNode[deg] = nodeList;

    blockCount = int (math.floor(g.number_of_nodes() * blockPercent));
    #blockCount = 1;
    
    blockList = [];
    #print infectedList;
    #print degToNode;
    
    while len(blockList) < blockCount:        


        #print "";
        #print "--------Max deg: %d" % maxDeg;
        #print "block list:";
        #print blockList;
                
        #print "infect list for degree";
        #print nodeList;
        neighborList = [];
        
        for infectNode in infectedList:
            neighbors = g.neighbors(infectNode);

            for ne in neighbors:
                if not (ne in neighborList) and not (ne in infectedList):
                    neighborList.append(ne);

            #print "neighbor list:";
            #print neighborList;
        neiDegToNode = {};

        for ne in neighborList:
            deg = g.out_degree(ne);
            if deg in neiDegToNode:
                nodeList = neiDegToNode[deg];
                nodeList.append(ne);
                neiDegToNode[deg] = nodeList;
            else:
                nodeList = [];
                nodeList.append(ne);
                neiDegToNode[deg] = nodeList;
        #print neiDegToNode;
        neiDegKeys = neiDegToNode.keys();
        neiDegKeys.sort();

        blockedForNode = 0;

        while (len(neiDegKeys) > 0):
            if blockedForNode >= MAX_PER_NODE:
                break;
                
            maxNeiDeg = neiDegKeys.pop();
            neiList = neiDegToNode[maxNeiDeg];

                #print "Infected Node: %s" % infectNode;
                #print neiList;
            for ne in neiList:
                if not (ne in blockList):
                    #print "Block neighbor: %s" % ne;
                    blockList.append(ne);
                    g.add_node(ne, status=3);
                    blockedForNode+=1;

                    if len(blockList) >= blockCount:
                        #print "Max Deg: %d" % maxDeg;
                        return [g, blockList];

            
    return [g, blockList];


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
