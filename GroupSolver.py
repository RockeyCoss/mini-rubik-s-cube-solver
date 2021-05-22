import numpy as np
from utility import decodeCube, encodeCube, moveTable, move, MoveItem, CubeState

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
solvedState = CubeState([np.arange(7), np.zeros(7, dtype=int)])


# Phase one utility functions
def isPhaseOneAchieved(currentCube: CubeState) -> bool:
    return (currentCube.orienSequence==np.zeros(7)).all()


def phaseOneH(currentCube: [np.ndarray, np.ndarray]) -> float:
    _, orientation = currentCube
    orienDis = np.sum(orientation) / 4
    return orienDis


# Phase two utility functions
def heuristicH(currentCube: [np.ndarray, np.ndarray]) -> float:
    # h(n)=max(blocks' 3D manhattan distance, orientation recovery distance)
    permutation, orientation = currentCube
    blockDis = np.sum(manhattanDistance[permutation, np.arange(6)]) / 4
    orienDis = np.sum(orientation) / 4
    return np.max(blockDis, orienDis)


def isCompletelySolved(currentCube: CubeState) -> bool:
    global solvedState
    return currentCube==solvedState


def solve(cube: [np.ndarray, np.ndarray]) -> list:
    if isCompletelySolved(cube):
        return []

    ancesChoice = None
    # record the times of a movement being chose
    choseTime = 0
    # phase one
    # from <R,U,F> to <U,R2,F2>
    for maxDepth in range(1, 20):
        movementLog = []
        # for movement in moveTable:
        #     length = len(movement)
        #     if length == 0 or length != 0 and movementLog[-1] != movement:
        #         choseTime = 1
        #     else:
        #         choseTime += 1


def phaseOneDps(maxDepth: int,currentDepth:int,cube: [np.ndarray, np.ndarray],movementLog:list,choseTime:int,preChoice:MoveItem):
    global moveTable
    # exceed max depth, prune
    if currentDepth>maxDepth:
        return
    for movement in moveTable:
        # R R', prune
        if movement==preChoice:
            continue
        length=len(movement)
        if length==0 or length!=0 and movementLog[-1]!=movement:
            choseTime=1
        else:
            choseTime+=1
        # R R R = R', prune
        if choseTime==3:
            return
        newCube=






