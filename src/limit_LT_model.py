import sys;
import os;
import networkx as nx;
import random;
from networkx import *;

#0 = susceptible
#1 = infected
#2 = recovered

MODEL_NAME = "LLT";
#OUTPUT_DIR = "../part_a";

BIRTH = 0.5;
DICE = 6;

def main(argv=None):

    if len(sys.argv) < 4:
        print "ERROR!! Usage: python limit_LT_model_p1.py cleanGraphPath infectedPath outputFilePath";
        exit();
    
    inputFile = sys.argv[1];
    infectFile = sys.argv[2];
    outFileName = sys.argv[3];

    allInfected = [];
    

    lltGraph = readGraph(inputFile);
    [lltGraph, infected] = addInfectNodes(infectFile, lltGraph);

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


            #try to recover
	    lltGraph[infectN][date] -= 1
	    if lltGraph[infectN][date]==0:
                newRecover.append(infectN);

        #update status in graph
        for n in newInfect:
            lltGraph.add_node(n, status=1);

        for n in newRecover:
            lltGraph.add_node(n, status=2);

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

    #if not os.path.exists(OUTPUT_DIR):
    # os.makedirs(OUTPUT_DIR);

    outputFile = outFileName;
    #OUTPUT_DIR + "/" + MODEL_NAME + "_" + outFileName;

    outputFh = open(outputFile, 'w');

    for n in allInfected:
        outputFh.write(n + "\n");

    outputFh.close();
    

def addInfectNodes(infectFilePath, g):
    inputFh = open(infectFilePath, 'r');
    infected = []
    
    for line in inputFh:
        infectedNode = line.replace("\n", "");

        if infectedNode in g:
	    rand = random.randrange(0,6)
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
            
            diGraph.add_node(node1, {'status':0,'date':0}, None );
            diGraph.add_node(node2, {'status':0,'date':0}, None );
            diGraph.add_edge(node1, node2);

    inputFh.close();

    return diGraph;

if __name__ == "__main__":
    sys.exit(main());

