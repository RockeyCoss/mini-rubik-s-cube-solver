import numpy as np
from utility import decodeCube, encodeCube, moveTable, move, MoveItem, CubeState, infoPrint
from typing import List, Tuple

# utility
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
    "R2": "R2",
    "F2": "F2"
}
insertMapping = {
    "U": ["U"],
    "U'": ["U'"],
    "R2": ['R', 'R'],
    "F2": ['F', 'F']
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
continueFlag = True


def setContinueFlagFalse(*args, **kwargs):
    global continueFlag
    continueFlag = False


class NotifyList(list):
    def __init__(self, maxNum):
        self.maxNum = maxNum
        self.callBacks = []

    def addCallBack(self, func):
        self.callBacks.append(func)

    def removeCallBack(self, func):
        self.callBacks.remove(func)

    def append(self, __object) -> None:
        super(NotifyList, self).append(__object)
        if len(self) >= self.maxNum:
            for func in self.callBacks:
                func(self)

    def forceCallBackCall(self):
        for func in self.callBacks:
            func(self)


# Phase one utility functions
def isPhaseOneAchieved(currentCube: CubeState) -> bool:
    return (currentCube.orienSequence == np.zeros(7)).all()


def phaseOneH(currentCube: CubeState) -> float:
    _, orientation = currentCube
    orienDis = np.where(orientation > 0)[0].shape[0] / 4
    return orienDis


# Phase two utility functions
def phaseTwoH(currentCube: CubeState) -> float:
    permutation, orientation = currentCube
    blockDis = np.sum(manhattanDistance[permutation, np.arange(7)]) / 4
    return blockDis


def isCompletelySolved(currentCube: CubeState) -> bool:
    global solvedState
    return currentCube == solvedState


@infoPrint("二阶段IDA*算法")
def solve(cube: CubeState, phaseOneNum=1) -> List[str]:
    if isCompletelySolved(cube):
        return []

    phaseOneSolutionList = NotifyList(phaseOneNum)
    phaseOneSolutionList.addCallBack(setContinueFlagFalse)
    cubeStateList = []
    # record the times of a movement being chose
    # phase one
    # from <R,U,F> to <U,R2,F2>

    # phaseOneSolutionNum=0
    # phaseOneSolution=[]
    for maxDepth in range(1, 20):
        movementLog = []
        phaseOneDps(maxDepth, 0, cube, movementLog, 0, phaseOneSolutionList, cubeStateList)
        if phaseOneSolutionList:
            break
    if not phaseOneSolutionList:
        raise Exception("can't solve the rubik's cube")

    # phase two
    # from <U,R2,F2> to <I>
    solutionStepList = []
    for movementLog, phaseOneCube in zip(phaseOneSolutionList, cubeStateList):
        phaseOneLength = len(movementLog)
        if isCompletelySolved(phaseOneCube):
            return movementLog
        for maxDepth in range(1, 20):
            solved, phaseTwoCube = phaseTwoDps(maxDepth, 0, phaseOneCube, movementLog, 0)
            if solved:
                # R R2->R'
                if len(movementLog) > phaseOneLength:
                    if ((movementLog[phaseOneLength - 1] == "R" or movementLog[phaseOneLength - 1] == "R'") and \
                        movementLog[phaseOneLength] == "R") or (
                            (movementLog[phaseOneLength - 1] == "F" or movementLog[phaseOneLength - 1] == "F'") and \
                            movementLog[phaseOneLength] == "F"):
                        movementLog.pop(phaseOneLength + 1)
                        movementLog.pop(phaseOneLength)
                        phaseOneLastMovement = movementLog.pop(phaseOneLength - 1)
                        movementLog.insert(phaseOneLength - 1, oppositeOperation[phaseOneLastMovement])
                solutionStepList.append(movementLog)
        if not solutionStepList:
            raise Exception("can't solve the rubik's cube")
        solutionLengths = [len(stepsLog) for stepsLog in solutionStepList]
        shortestIndex = solutionLengths.index(min(solutionLengths))
        return solutionStepList[shortestIndex]


def phaseOneDps(maxDepth: int, currentDepth: int, cube: CubeState, movementLog: List[str], choseTime: int,
                phaseOneSolutionList: NotifyList, cubeStateList: List[CubeState]) -> None:
    global moveTable, oppositeOperation, continueFlag
    if not continueFlag:
        return

    if isPhaseOneAchieved(cube):
        phaseOneSolutionList.append(movementLog.copy())
        cubeStateList.append(cube.__copy__())
        if not movementLog:
            phaseOneSolutionList.forceCallBackCall()
        return
    # exceed max depth, prune
    if currentDepth >= maxDepth:
        return

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
        phaseOneDps(maxDepth, currentDepth + 1, newCube, movementLog, choseTime,phaseOneSolutionList,cubeStateList)
        if not continueFlag:
            return
        else:
            movementLog.pop()

    return


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
        deltaDepth = 1 if movementName == 'U' or movementName == "U'" else 2
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

        heuristicDis = currentDepth + phaseTwoH(newCube)
        if heuristicDis > maxDepth:
            continue

        movementLog.extend(insertMapping[movementName])
        judge, newCube = phaseTwoDps(maxDepth, currentDepth + deltaDepth, newCube, movementLog, choseTime)
        if judge:
            return True, newCube
        else:
            movementLog.pop()
            if movementName == 'R2' or movementName == 'F2':
                movementLog.pop()
            continue

    return False, cube
