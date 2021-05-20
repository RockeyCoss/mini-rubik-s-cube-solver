import numpy as np
from utility import decodeCube, encodeCube, moveTable, move
# use IDA*
# f(n)=g(n)+h(n)
manhattanDistance = np.array([
   # 0  1  2  3  4  5  6
    [0, 1, 2, 2, 1, 2, 3],
    [1, 0, 1, 3, 2, 1, 2],
    [2, 1, 0, 2, 3, 2, 1],
    [2, 3, 2, 0, 1, 2, 1],
    [1, 2, 3, 1, 0, 1, 2],
    [2, 1, 2, 2, 1, 0, 1],
    [3, 2, 1, 1, 2, 1, 0],
])
solvedState=[np.arange(7),np.zeros(7,dtype=int)]
[2,3,1,0,4,5,6]
def heuristicH(currentCube:[np.ndarray,np.ndarray])->float:
    # h(n)=max(blocks' 3D manhattan distance, orientation recovery distance)
    permutation , orientation=currentCube
    blockDis=np.sum(manhattanDistance[permutation,np.arange(6)])/4
    orienDis=np.sum(orientation)/4
    return np.max(blockDis,orienDis)

def isSolved(currentCube:[np.ndarray, np.ndarray])->bool:
    global solvedState
    return currentCube[0]==solvedState[0] and currentCube[1]==solvedState[1]
def solve(cube:[np.ndarray, np.ndarray])->list:
    if isSolved(cube):
        return []
    maxDepth=1
    ancesChoice=None
    preChoice=None

def dps(maxLength:int,cube:[np.ndarray, np.ndarray]):
    pass

