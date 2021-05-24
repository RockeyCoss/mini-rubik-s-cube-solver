from collections import namedtuple,deque
import numpy as np
from utility import  moveTable, CubeState,  infoPrint
import utility
import tqdm

# faster function for graph generating:
def encodeCube(pie: np.ndarray, q: np.ndarray) -> int:
    perNum = utility.rankPermutation(pie)
    return int(perNum * np.power(3, 6) + np.sum(q[:6] * np.array([np.power(3, i) for i in range(5, -1, -1)])))


def decodeCube(cubeNum: int) -> (np.ndarray, np.ndarray):
    perNum, remain = divmod(cubeNum, np.power(3, 6))
    permutation = utility.unrankPermutation(perNum, 7)
    orientation = []
    for power in range(5, -1, -1):
        ori, remain = divmod(remain, np.power(3, power))
        orientation.append(ori)
    # (a + b) % p = (a % p + b % p) % p
    # (a - b) % p = (a % p - b % p) % p
    # (a * b) % p = (a % p * b % p) % p
    # sum(orientation)=k
    # (3-k%3)%3=(3%3-k%3)%3=(-k%3)%3=(-1%3*k%3)%3=(2*k%3)%3
    orientation.append((2*(sum(orientation) % 3)) % 3)
    return permutation,np.array(orientation,dtype=int)

def move(cube:[np.ndarray,np.ndarray], movement: utility.MoveItem)->[np.ndarray, np.ndarray]:
    newPermutation=cube[0][movement.permutation]
    newOrientation=np.mod((cube[1][movement.permutation]+movement.orientation),3)
    return [newPermutation,newOrientation]

def generateGraph():
    totleNum=np.math.factorial(7)*np.power(3,6)
    print("Generating Graph...")
    graph=[]
    for cubeNum in tqdm.trange(totleNum):
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

@infoPrint("状态图法")
def solve(cube:CubeState)->list:
    preList=getPreList()
    solvedCubeNum=utility.encodeCube(CubeState([np.arange(7),np.zeros(7)]))
    currentCubeNum = utility.encodeCube(cube)
    solveStep=[]
    moveTableKeys=list(moveTable.keys())
    while currentCubeNum!=solvedCubeNum:
        possibleNextCubeNum=[utility.encodeCube(utility.move(cube,movement)) for movement in moveTable.values()]
        currentCubeNum=preList[currentCubeNum]
        moveIndex=possibleNextCubeNum.index(currentCubeNum)
        solveStep.append(moveTableKeys[moveIndex])
        cube=utility.decodeCube(currentCubeNum)
    return solveStep

# def solveByIDFS(cube:)


if __name__ == '__main__':
    a=getPreList()