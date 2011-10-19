import sys;
import os;
import networkx as nx;
import random;
import math;
from networkx import *;

#0 = susceptible
#1 = infected
#2 = recovered
#3 = immuned

MODEL_NAME = "SIR";

BIRTH = 0.5;
DEATH = 0.5;

MAX_PER_NODE = 5;

def main(argv=None):

    if len(sys.argv) < 4:
        print "ERROR!! Usage: python sir_model_p2.py cleanGraphPath infectedPath outputFilePath -b";
        exit();
    
    inputFile = sys.argv[1];
    infectFile = sys.argv[2];
    outFileName = sys.argv[3];

    block = False;

    if len(sys.argv) == 5:
        if sys.argv[4] == "-b":
            block = True;

    sirGraph = readGraph(inputFile);
    [sirGraph, infected] = addInfectNodes(infectFile, sirGraph);

    for i in range(1, 6):
        g = sirGraph.copy();
        inf = list(infected);
        blockPerc = float(i/100.0);

        infSum = 0;
        for j in range (0, 1):
            g = sirGraph.copy();
            inf = list(infected);

            if (block):
                [g, blockList] = addBlockNodes(g, inf, blockPerc);
            
            print "%.2f, %d" % (blockPerc, j);
            allInfected = runSim(g, infected);
            infSum += len(allInfected);
        
        print "%.2f: %.2f" % (blockPerc, infSum/(1* float(g.number_of_nodes())));
    
        outputFile =  outFileName + "_" + str(blockPerc) + ".txt";
        
        outputFh = open(outputFile, 'w');

        for n in blockList:
            outputFh.write(n + "\n");

        outputFh.close();
    

def runSim(sirGraph, infected):    
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
            neighborList = sirGraph.neighbors(infectN);            
            
            for n, attr in sirGraph.nodes_iter(True):
                if n in neighborList:
                    st = attr['status'];

                    #if node status is susceptible, try to infect
                    if (st == 0):
                        rand = random.random();
                
                        if (rand < BIRTH):
                            newInfect.append(n);


            #try to recover
            rand = random.random();
            if (rand < DEATH):                            
                newRecover.append(infectN);

        #update status in graph
        for n in newInfect:
            sirGraph.add_node(n, status=1);

        for n in newRecover:
            sirGraph.add_node(n, status=2);

        #update infected list
        infected = [];
        for n, attr in sirGraph.nodes_iter(True):            
            if (attr['status'] == 0):
                s+=1;                
            if (attr['status'] == 1):
                i+=1;
                infected.append(n);
            if (attr['status'] == 2):
                r+=1;
        #print sirGraph.nodes(True);
        #print "Iter: %d, new infect: %d, new recover: %d, s: %d, i: %d, r:%d" %(iCount, len(newInfect), len(newRecover), s, i, r);
        iCount+=1;

        for n in infected:
            if not (n in allInfected):
                allInfected.append(n);
        
        if (i == 0):
            break;


    return allInfected;
    


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
            g.add_node(infectedNode, status = 1);
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

            
            diGraph.add_node(node1, status = 0);
            diGraph.add_node(node2, status = 0);
            diGraph.add_edge(node1, node2);        

    inputFh.close();

    return diGraph;

if __name__ == "__main__":
    sys.exit(main());
