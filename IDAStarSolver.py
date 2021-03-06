import numpy as np
from utility import decodeCube, encodeCube, moveTable, move, MoveItem, CubeState, infoPrint, manhattanDistance,oppositeOperation
from typing import List, Tuple

# use IDA*
# f(n)=g(n)+h(n)


solvedState = CubeState([np.arange(7), np.zeros(7, dtype=int)])


# Phase two utility functions
def heuristicH(currentCube: CubeState) -> float:
    permutation, orientation = currentCube
    blockDis = np.sum(manhattanDistance[permutation, np.arange(7)]) / 4
    orienDis = np.where(orientation > 0)[0].shape[0] / 4
    heuristic = max(orienDis, blockDis)
    if 0 < heuristic < 1:
        heuristic = 1
    return heuristic


def isCompletelySolved(currentCube: CubeState) -> bool:
    global solvedState
    return currentCube == solvedState


@infoPrint("IDA*算法")
def solve(cube: CubeState) -> List[str]:
    if isCompletelySolved(cube):
        return []

    for maxDepth in range(1, 20):
        movementLog = []
        solved = dps(maxDepth, 0, cube, movementLog, 0)
        if solved:
            return movementLog
    else:
        raise Exception("can't solve the rubik's cube")


def dps(maxDepth: int, currentDepth: int, cube: CubeState, movementLog: List[str], choseTime: int) -> bool:
    global moveTable, oppositeOperation

    if isCompletelySolved(cube):
        return True
    # exceed max depth, prune
    if currentDepth >= maxDepth:
        return False

    preChoiceOpposite = oppositeOperation[movementLog[-1]] if len(movementLog) > 0 else None

    length = len(movementLog)
    for movementName in moveTable:
        movement = moveTable[movementName]
        # R R', prune
        if movementName == preChoiceOpposite:
            continue
        if length == 0 or (length != 0 and movementLog[-1] != movementName):
            choseTime = 1
        else:
            choseTime += 1
        # R R R = R', prune
        if choseTime == 3:
            continue
        newCube = move(cube, movement)

        if currentDepth + heuristicH(newCube) > maxDepth:
            continue

        movementLog.append(movementName)
        judge = dps(maxDepth, currentDepth + 1, newCube, movementLog, choseTime)
        if judge:
            return True
        else:
            movementLog.pop()
            continue

    return False
