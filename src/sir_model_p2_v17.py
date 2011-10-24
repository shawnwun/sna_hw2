import sys;
import os;
import networkx as nx;
import random;
import math;
from networkx import *;

'''
    Generate block list base on node's fan in and fan out. Block those with high fanOut/fanIn. Incremental update.
'''

#0 = susceptible
#1 = infected
#2 = recovered
#3 = immuned

MODEL_NAME = "SIR";

BIRTH = 0.5;
DEATH = 0.5;

def main(argv=None):

    if len(sys.argv) < 5:
        print "ERROR!! Usage: python sir_model_p2_v8.py cleanGraphPath infectedPath outputFilePath alpha runsToAve";
        exit();

    inputFile = sys.argv[1];
    infectFile = sys.argv[2];
    outFileName = sys.argv[3];
    alpha = float(sys.argv[4]);

    sirGraph = readGraph(inputFile);
    [sirGraph, infected] = addInfectNodes(infectFile, sirGraph);
    [fanInDict, fanOutDict] = getTransDict(sirGraph, infected, alpha);

    print alpha;

    #print transDict;
    
    if len(sys.argv) == 6:
        runsToAve = int(sys.argv[5]);
    else:
        runsToAve = 1;

    for i in range(0, 6):
        g = sirGraph.copy();
        inf = list(infected);
        blockPerc = float(i/100.0);
        fanInCpy = fanInDict.copy();
        fanOutCpy = fanOutDict.copy();

        infSum = 0;
        for j in range (0, runsToAve):
            g = sirGraph.copy();
            inf = list(infected);

            if (block):
                [g, blockList] = addBlockNodes(g, fanInCpy, fanOutCpy, blockPerc, alpha);
            
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

def getMaxKey(fanInDict, fanOutDict, alpha):
    maxKey = -1;
    maxList = [];

    for node in fanInDict:
        pre = fanInDict[node];
        suc = fanOutDict[node];

        countPre = len(pre);
        countSuc = len(suc);

        score = countPre * alpha + (1-alpha) * countSuc;

        if score > maxKey:
            maxList = [];
            maxList.append(node);
            maxKey = score;
        elif score == maxKey:
            maxList.append(node);

    return [maxKey, maxList];

def updateDict(fanInDict, fanOutDict, blockNode):

    del fanInDict[blockNode];
    del fanOutDict[blockNode];
        
    for node in fanInDict:
        preList = fanInDict[node];

        if blockNode in preList:
            preList.remove(blockNode);
            fanInDict[node] = preList;
            print "rm %d from %d" % (int(blockNode), int(node));

    for node in fanOutDict:
        sucList = fanOutDict[node];

        if blockNode in sucList:
            sucList.remove(blockNode);
            fanOutDict[node] = sucList;
            print "rm %d from %d" % (int(blockNode), int(node));

    return [fanInDict, fanOutDict];

def addBlockNodes(g, fanInDict, fanOutDict, blockPercent, alpha):
    blockCount = int (math.floor(g.number_of_nodes() * blockPercent));
    
    blockList = [];        
    
    while len(blockList) < blockCount:                
        [maxScore, maxList] = getMaxKey(fanInDict, fanOutDict, alpha);

        print maxScore;
        print maxList;
                
        if maxScore < 0:
            break;

        rand = random.randint(0, len(maxList)-1);

        blockNode = maxList[rand];

        blockList.append(blockNode);
        g.add_node(blockNode, status=3);

        [fanInDict, fanOutDict] = updateDict(fanInDict, fanOutDict, blockNode);

        if len(blockList) >= blockCount:
            break;

            
    return [g, blockList];

def getTransDict(g, infectedList, alpha):
    
    fanInDict = {};
    fanOutDict = {};
    for node in g.nodes_iter():
        if node in infectedList:
            continue;
        
        predecessors = g.predecessors(node);
        successors = g.successors(node);

        cleanPreList = [];
        for pre in predecessors:
            if pre in infectedList:
                continue;

            cleanPreList.append(pre);

        cleanSucList = [];
        for suc in successors:
            if suc in infectedList:
                continue;

            cleanSucList.append(suc);

    
        

        fanInDict[node] = cleanPreList;
        fanOutDict[node] = cleanSucList;

    return [fanInDict, fanOutDict];

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
