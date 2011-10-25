import sys;
import os;
import networkx as nx;
import random;
import math;
from networkx import *;

'''
    Generate 5% block nodes based on out-degree of the non-infected nodes. Incremental update
'''


#0 = susceptible
#1 = infected
#2 = recovered
#3 = immuned

MODEL_NAME = "SIR";

BIRTH = 0.5;
DEATH = 0.5;

def main(argv=None):

    if len(sys.argv) < 4:
        print "ERROR!! Usage: python sir_model_p2_method_1.py cleanGraphPath infectedPath outputFilePath runsToAve";
        exit();
    
    inputFile = sys.argv[1];
    infectFile = sys.argv[2];
    outFileName = sys.argv[3];

    if len(sys.argv) == 5:
        runsToAve = int(sys.argv[4]);
    else:
        runsToAve = 1;

    sirGraph = readGraph(inputFile);
    [sirGraph, infected] = addInfectNodes(infectFile, sirGraph);
    nodeToNeiDict = getNodeToNeiDict(sirGraph, infected);

    for i in range(0, 6):
        g = sirGraph.copy();
        inf = list(infected);
        blockPerc = float(i/100.0);

        infSum = 0;
        for j in range (0, runsToAve):
            g = sirGraph.copy();
            inf = list(infected);
            nodeDegDict = nodeToNeiDict.copy();

            [g, blockList] = addBlockNodes(g, nodeDegDict, blockPerc);
            
            print "%.2f, %d, immune wanted: %d, count: %d" % (blockPerc, j, math.floor(g.number_of_nodes() * blockPerc), len(blockList));
            allInfected = runSim(g, infected);
            infSum += len(allInfected);
        
        print "%.2f: %.2f" % (blockPerc, infSum/(runsToAve* float(g.number_of_nodes())));
    
        outputFile =  outFileName + "_" + str(blockPerc) + ".txt";
        
        outputFh = open(outputFile, 'w');

        for n in blockList:
            outputFh.write(n + "\n");

        outputFh.close();
    
def getNodeToNeiDict(g, infectedList):
    nodeToNeiDict = {};

    for node in g:
        if not (node in infectedList):
            neighbors = g.neighbors(node);

            cleanList = [];
            for nei in neighbors:
                if not (nei in infectedList):
                    cleanList.append(nei);


            nodeToNeiDict[node] = cleanList;

    return nodeToNeiDict;

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


def getMaxDeg(nodeToNeiDict):
    maxDeg = -1;
    maxDegNodeList = [];

    for node in nodeToNeiDict:
        neiList = nodeToNeiDict[node];

        if len(neiList) > maxDeg:
            maxDegNodeList = [];
            maxDegNodeList.append(node);
            maxDeg = len(neiList);
        elif len(neiList) == maxDeg:
            maxDegNodeList.append(node);

    return [maxDeg, maxDegNodeList];
            
def updateDegDict(nodeToNeiDict, blockNode):

    del nodeToNeiDict[blockNode];

    #print "remove %d" % int(blockNode);
    
    for node in nodeToNeiDict:
        neiList = nodeToNeiDict[node];

        if blockNode in neiList:
            neiList.remove(blockNode);
            nodeToNeiDict[node] = neiList;
            #print "remove %d from %d" % (int(blockNode), int(node));

    return nodeToNeiDict;

def addBlockNodes(g, nodeToNeiDict, blockPercent):

    blockCount = int (math.floor(g.number_of_nodes() * blockPercent));
    
    blockList = [];        

    while (len(blockList) < blockCount):                
        [maxDeg, maxDegNodeList] = getMaxDeg(nodeToNeiDict);
        #print "max deg: %d" % maxDeg;
        #print maxDegNodeList;

        if maxDeg < 0:
            break;

        rand = random.randint(0, len(maxDegNodeList)-1);

        blockNode = maxDegNodeList[rand];

        blockList.append(blockNode);
        g.add_node(blockNode, status=3);

        nodeToNeiDict = updateDegDict(nodeToNeiDict, blockNode);

        if len(blockList) >= blockCount:
            break;
            
    
    return [g, blockList];

def getDegDict(g, infectedList):
    '''neighborList = [];
        
    for infectNode in infectedList:
        neighbors = g.neighbors(infectNode);

        for ne in neighbors:
            if not (ne in neighborList) and not (ne in infectedList):
                neighborList.append(ne);
    '''
    
    degToNode = {};

    for node in g.nodes_iter():

        if node in infectedList:
            continue;
        
        neighbors = g.neighbors(node);
        cleanNeiList = [];
        for n in neighbors:
            if not (n in infectedList):
                cleanNeiList.append(n);
        
        deg = len(cleanNeiList);
        if deg in degToNode:
            nodeList = degToNode[deg];
            nodeList.append(node);
            degToNode[deg] = nodeList;
        else:
            nodeList = [];
            nodeList.append(node);
            degToNode[deg] = nodeList;

    return degToNode;

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
