from collections import namedtuple,deque
import numpy as np
from utility import decodeCube, encodeCube, moveTable, move, CubeState


def generateGraph():
    totleNum=np.math.factorial(7)*np.power(3,6)
    graph=[]
    for cubeNum in range(totleNum):
        cube=decodeCube(cubeNum)
        childrenList=tuple(encodeCube(*move(cube,movement)) for movement in moveTable.values())
        graph.append(childrenList)
    return graph

def bfs(graph:np.ndarray,startPoint:int)->np.ndarray:
    previousPoint=-1*np.ones(len(graph),dtype=int)
    array=deque([startPoint])
    while array:
        vertex=array.popleft()
        for nextState in graph[vertex]:
            if previousPoint[nextState]==-1:
                previousPoint[nextState]=vertex
                array.append(nextState)

    return previousPoint

def generatePreList():
    graph=generateGraph()
    resolvedCubeNum=encodeCube(np.arange(7),np.zeros(7))
    return bfs(graph,resolvedCubeNum)

def getPreList():
    try:
        previousList=np.load("previousList.npy")
    except:
        previousList=generatePreList()
        np.save("previousList.npy",previousList)

    finally:
        return previousList

def solve(cube:CubeState)->list:
    preList=getPreList()
    solvedCubeNum=encodeCube(np.arange(7),np.zeros(7))
    currentCubeNum = encodeCube(*cube)
    solveStep=[]
    moveTableKeys=list(moveTable.keys())
    while currentCubeNum!=solvedCubeNum:
        possibleNextCubeNum=[encodeCube(*move(cube,movement)) for movement in moveTable.values()]
        currentCubeNum=preList[currentCubeNum]
        moveIndex=possibleNextCubeNum.index(currentCubeNum)
        solveStep.append(moveTableKeys[moveIndex])
        cube=decodeCube(currentCubeNum)
    return solveStep

# def solveByIDFS(cube:)


if __name__ == '__main__':
    a=getPreList()