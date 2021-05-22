import numpy as np
from utility import decodeCube, encodeCube, moveTable, move, MoveItem, CubeState
from typing import List, Tuple

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
oppositeOperation = {
    'U': "U",
    "U'": "U",
    "R": "R'",
    "R'": "R",
    "F": "F'",
    "F'": "F",
    "R2":"R2",
    "F2":"F2"
}
moveTablePhaseTwo = {
    # U
    'U': MoveItem(permutation=np.array([0, 1, 2, 6, 3, 4, 5]), orientation=np.array([0, 0, 0, 0, 0, 0, 0])),
    # U'
    "U'": MoveItem(permutation=np.array([0, 1, 2, 4, 5, 6, 3]), orientation=np.array([0, 0, 0, 0, 0, 0, 0])),
    # R2
    "R2": MoveItem(permutation=np.array([5, 4, 2, 3, 1, 0, 6]), orientation=np.array([0, 0, 0, 0, 0, 0, 0])),
    # F2
    "F2": MoveItem(permutation=np.array([0, 6, 5, 3, 4, 2, 1]), orientation=np.array([0, 0, 0, 0, 0, 0, 0])),
}
solvedState = CubeState([np.arange(7), np.zeros(7, dtype=int)])


# Phase one utility functions
def isPhaseOneAchieved(currentCube: CubeState) -> bool:
    return (currentCube.orienSequence == np.zeros(7)).all()


def phaseOneH(currentCube: CubeState) -> float:
    _, orientation = currentCube
    orienDis = np.sum(orientation) / 4
    return orienDis


# Phase two utility functions
def phaseTwoH(currentCube: CubeState) -> float:
    permutation, orientation = currentCube
    blockDis = np.sum(manhattanDistance[permutation, np.arange(7)]) / 4
    return blockDis


def isCompletelySolved(currentCube: CubeState) -> bool:
    global solvedState
    return currentCube == solvedState


def solve(cube: CubeState,phaseOneNum=1) -> List[str]:
    if isCompletelySolved(cube):
        return []

    # record the times of a movement being chose
    choseTime = 0
    # phase one
    # from <R,U,F> to <U,R2,F2>

    # phaseOneSolutionNum=0
    # phaseOneSolution=[]

    for maxDepth in range(1, 20):
        movementLog = []
        solved, phaseOneCube = phaseOneDps(maxDepth, 0, cube, movementLog, 0)
        if solved:
            break
    if (movementLog == []):
        raise Exception("can't solve the rubik's cube")
    print(movementLog,phaseOneCube)
    # phase two
    # from <U,R2,F2> to <I>
    if isCompletelySolved(phaseOneCube):
        return movementLog
    for maxDepth in range(1, 20):
        solved,phaseTwoCube = phaseTwoDps(maxDepth,0,cube,movementLog,0)
    if solved:
        return movementLog
    else:
        raise Exception("can't solve the rubik's cube")


def phaseOneDps(maxDepth: int, currentDepth: int, cube: CubeState, movementLog: List[str], choseTime: int) -> Tuple[
    bool, CubeState]:
    global moveTable, oppositeOperation

    if isPhaseOneAchieved(cube):
        return True, cube
    # exceed max depth, prune
    if currentDepth >= maxDepth:
        return False, cube

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

        if currentDepth + phaseOneH(newCube) > maxDepth:
            continue

        movementLog.append(movementName)
        judge, newCube = phaseOneDps(maxDepth, currentDepth + 1, newCube, movementLog, choseTime)
        if judge:
            return True, newCube
        else:
            movementLog.pop()
            continue

    return False, cube


def phaseTwoDps(maxDepth: int, currentDepth: int, cube: CubeState, movementLog: List[str], choseTime: int) -> Tuple[
    bool, CubeState]:
    global moveTablePhaseTwo, oppositeOperation

    if isCompletelySolved(cube):
        return True, cube
    # exceed max depth, prune
    if currentDepth >= maxDepth:
        return False, cube

    preChoiceOpposite = oppositeOperation[movementLog[-1]] if len(movementLog) > 0 else None

    length = len(movementLog)
    for movementName in moveTablePhaseTwo:
        deltaDepth=1 if movementName=='U' or movementName=="U'" else 2
        movement = moveTablePhaseTwo[movementName]
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

        heuristicDis=currentDepth + phaseTwoH(newCube)
        if heuristicDis > maxDepth:
            continue

        movementLog.append(movementName)
        judge, newCube = phaseTwoDps(maxDepth, currentDepth + deltaDepth, newCube, movementLog, choseTime)
        if judge:
            return True, newCube
        else:
            movementLog.pop()
            continue

    return False, cube
