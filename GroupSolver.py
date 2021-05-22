import numpy as np
from utility import decodeCube, encodeCube, moveTable, move, MoveItem, CubeState
from typing import List

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
oppositeOperation={
    'U': "U",
    "U'": "U",
    "R": "R'",
    "R'": "R",
    "F": "F'",
    "F'": "F",
}
solvedState = CubeState([np.arange(7), np.zeros(7, dtype=int)])


# Phase one utility functions
def isPhaseOneAchieved(currentCube: CubeState) -> bool:
    return (currentCube.orienSequence==np.zeros(7)).all()


def phaseOneH(currentCube: CubeState) -> float:
    _, orientation = currentCube
    orienDis = np.sum(orientation) / 4
    return orienDis


# Phase two utility functions
def heuristicH(currentCube: CubeState) -> float:
    # h(n)=max(blocks' 3D manhattan distance, orientation recovery distance)
    permutation, orientation = currentCube
    blockDis = np.sum(manhattanDistance[permutation, np.arange(6)]) / 4
    orienDis = np.sum(orientation) / 4
    return np.max(blockDis, orienDis)


def isCompletelySolved(currentCube: CubeState) -> bool:
    global solvedState
    return currentCube==solvedState


def solve(cube: CubeState) -> list:
    if isCompletelySolved(cube):
        return []

    ancesChoice = None
    # record the times of a movement being chose
    choseTime = 0
    # phase one
    # from <R,U,F> to <U,R2,F2>
    for maxDepth in range(1, 20):
        movementLog=[]
        phaseOneDps(maxDepth,0,cube,movementLog,0)


def phaseOneDps(maxDepth: int,currentDepth:int,cube: CubeState,movementLog:List[str],choseTime:int)->bool:
    global moveTable,oppositeOperation

    if isPhaseOneAchieved(cube):
        return True
    # exceed max depth, prune
    if currentDepth >= maxDepth:
        return False

    preChoiceOpposite=oppositeOperation[movementLog[-1]] if len(movementLog)>0 else None

    length = len(movementLog)
    for movementName in moveTable:
        movement=moveTable[movementName]
        # R R', prune
        if movementName==preChoiceOpposite:
            continue
        if length==0 or (length!=0 and movementLog[-1]!=movementName):
            choseTime=1
        else:
            choseTime+=1
        # R R R = R', prune
        if choseTime==3:
            continue
        newCube=move(cube,movement)
        # achieved!

        if currentDepth+phaseOneH(newCube)>maxDepth:
            continue

        movementLog.append(movementName)
        judge=phaseOneDps(maxDepth,currentDepth+1,newCube,movementLog,choseTime)
        if judge:
            return True
        else:
            movementLog.pop()
            continue

    return False







