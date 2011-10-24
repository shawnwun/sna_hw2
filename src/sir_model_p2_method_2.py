import sys;
import os;
import networkx as nx;
import random;
import math;
from networkx import *;

'''
    Generate block node list based on node's span, the total number of nodes it can reach using DFS. Incremental update
'''


#0 = susceptible
#1 = infected
#2 = recovered
#3 = immuned

MODEL_NAME = "SIR";

BIRTH = 0.5;
DEATH = 0.5;

DEPTH = sys.maxint;

def main(argv=None):

    if len(sys.argv) < 5:
        print "ERROR!! Usage: python sir_model_p2_method_2.py cleanGraphPath infectedPath outputFilePath (max or depth #) runsToAve";
        exit();

    inputFile = sys.argv[1];
    infectFile = sys.argv[2];
    outFileName = sys.argv[3];

    dep = sys.argv[4];

    if (dep == "max"):
        DEPTH = sys.maxint;
    else:
        DEPTH = int(dep);

    if len(sys.argv) == 6:
        runsToAve = int(sys.argv[5]);
    else:
        runsToAve = 1;

    print "Depth: %d" % DEPTH;

    sirGraph = readGraph(inputFile);
    [sirGraph, infected] = addInfectNodes(infectFile, sirGraph);
    spanDict = getSpanDict(sirGraph, infected);

    for i in range(0, 6):
        g = sirGraph.copy();
        inf = list(infected);
        blockPerc = float(i/100.0);

        infSum = 0;
        for j in range (0, runsToAve):
            g = sirGraph.copy();
            inf = list(infected);
            nodeToSpanDict = spanDict.copy();

    
            [g, blockList] = addBlockNodes(g, nodeToSpanDict, blockPerc);
            
            print "%.2f, %d, immune wanted: %d, count: %d" % (blockPerc, j, math.floor(g.number_of_nodes() * blockPerc), len(blockList));
            allInfected = runSim(g, infected);
            infSum += len(allInfected);
        
        print "%.2f: %.2f" % (blockPerc, infSum/(runsToAve* float(g.number_of_nodes())));
    
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
    
def getMaxSpan(nodeToPathDict):
    maxSpan = -1;
    maxSpanNodeList = [];

    for node in nodeToPathDict:
        paths = nodeToPathDict[node];

        allNodeList = [];
        
        for key in paths:
            path = paths[key];
            for pathNode in path:
                if not (pathNode in allNodeList):
                    allNodeList.append(pathNode);

        if len(allNodeList) > maxSpan:
            maxSpanNodeList = [];
            maxSpanNodeList.append(node);
            maxSpan = len(allNodeList);
        elif len(allNodeList) == maxSpan:
            maxSpanNodeList.append(node);

    return [maxSpan, maxSpanNodeList];

def updatePathDict(nodeToPathDict, blockNode):

    del nodeToPathDict[blockNode];

    #print "remove %d" % int(blockNode);
    
    for node in nodeToPathDict:
        paths = nodeToPathDict[node];

        for key in paths:
            path = paths[key];

            if blockNode in path:
                cleanPathList = [];
                for pathNode in path:
                    if pathNode == blockNode:
                        break;

                    cleanPathList.append(pathNode);

                if len(cleanPathList) == 0:
                    paths.remove(key);
                else:
                    paths[key] = cleanPathList;
                
        nodeToPathDict[node] = paths;

    return nodeToPathDict;

def addBlockNodes(g, nodeToPathDict, blockPercent):
    blockCount = int (math.floor(g.number_of_nodes() * blockPercent));
    
    blockList = [];            
        
    while len(blockList) < blockCount:                
        [maxSpan, maxSpanNodeList] = getMaxSpan(nodeToPathDict);

        if (maxSpan < 0):
            break;
                
        rand = random.randint(0, len(maxSpanNodeList)-1);

        blockNode = maxSpanNodeList[rand];

        blockList.append(blockNode);
        g.add_node(blockNode, status=3);

        nodeToPathDict = updatePathDict(nodeToPathDict, blockNode);

        if len(blockList) >= blockCount:
            break;

            
    return [g, blockList];

def getSpanDict(g, infectedList):
    nodeToSpanDict = {}

    for node in g.nodes_iter():

        if node in infectedList:
            continue;
        
        paths = shortest_path(g, node);            
        
        for key in paths.iterkeys():            
            pathList = paths[key];
            cleanPathList = [];
            currLevel = 0;

            for pathNode in pathList:
                if currLevel >= DEPTH:
                    break;
                    
                #if any node in the path is already infected, break
                if (pathNode in infectedList):
                    break;
                    
                cleanPathList.append(pathNode);

                currLevel+=1;
            paths[key] = cleanPathList;

        nodeToSpanDict[node] = paths;

    return nodeToSpanDict;

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
