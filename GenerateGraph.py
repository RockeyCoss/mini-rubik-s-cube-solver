from collections import namedtuple,deque
import numpy as np


def rankPermutation(p: np.ndarray):
    p=p.copy()
    pM1 = p.argsort()
    rankResult = 0
    for index in range(p.shape[0] - 1, 0, -1):
        s = p[index]
        p[index], p[pM1[index]] = p[pM1[index]], p[index]
        pM1[s], pM1[index] = pM1[index], pM1[s]
        rankResult += s * np.math.factorial(index)
    return rankResult


def unrankPermutation(r: int, n: int) -> np.ndarray:
    p = np.array(list(range(n)))
    while n > 0:
        factorial = np.math.factorial(n - 1)
        s = int(r // factorial)
        p[n - 1], p[s] = p[s], p[n - 1]
        n -= 1
        r %= factorial
    return p


def encodeCube(pie: np.ndarray, q: np.ndarray) -> int:
    perNum = rankPermutation(pie)
    return int(perNum * np.power(3, 6) + np.sum(q[:6] * np.array([np.power(3, i) for i in range(5, -1, -1)])))


def decodeCube(cubeNum: int) -> (np.ndarray, np.ndarray):
    perNum, remain = divmod(cubeNum, np.power(3, 6))
    permutation = unrankPermutation(perNum, 7)
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


MoveItem = namedtuple("MoveItem", ["permutation", "orientation"])
moveTable = {
    # U
    'U': MoveItem(permutation=np.array([0, 1, 2, 6, 3, 4, 5]), orientation=np.array([0, 0, 0, 0, 0, 0, 0])),
    # U'
    "U'": MoveItem(permutation=np.array([0, 1, 2, 4, 5, 6, 3]), orientation=np.array([0, 0, 0, 0, 0, 0, 0])),
    # R
    "R": MoveItem(permutation=np.array([4, 0, 2, 3, 5, 1, 6]), orientation=np.array([1, 2, 0, 0, 2, 1, 0])),
    # R'
    "R'": MoveItem(permutation=np.array([1, 5, 2, 3, 0, 4, 6]), orientation=np.array([1, 2, 0, 0, 2, 1, 0])),
    # F
    "F": MoveItem(permutation=np.array([0, 5, 1, 3, 4, 6, 2]), orientation=np.array([0, 1, 2, 0, 0, 2, 1])),
    # F'
    "F'": MoveItem(permutation=np.array([0, 2, 6, 3, 4, 1, 5]), orientation=np.array([0, 1, 2, 0, 0, 2, 1])),
}

def move(cube:[np.ndarray,np.ndarray],movement:MoveItem)->[np.ndarray,np.ndarray]:
    newPermutation=cube[0][movement.permutation]
    newOrientation=np.mod((cube[1][movement.permutation]+movement.orientation),3)
    return [newPermutation,newOrientation]

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

def solveByGraph(cube:[np.ndarray,np.ndarray])->None:
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

# def solveByID(cube:[np.ndarray,np.ndarray])->None:
#     for depth in range(11):
#         currentD=0
#         moveList=[]
#         lastMovement=None
#         for movement in moveTable.values():
#             if movement!=lastMovement:


# def dfs(cube:[np.ndarray,np.ndarray],lastMovement,moveList,depth,maxDepth):
#     if cube[0]==np.arange(7) and cube[1]==np.zeros(7,dtype=cube[1].dtype):
#         return moveList
#     for moveName in moveTable:
#         if moveTable[moveName] != lastMovement:
#             newCube=move(cube,moveTable[moveName])
#             moveList.append(moveName)

if __name__ == '__main__':
    a=getPreList()