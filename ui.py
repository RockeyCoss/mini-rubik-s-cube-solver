import vpython as vp
import numpy as np

import IDAStar2Phase
import IDAStarSolver
from utility import MoveItem
import utility
import GraphSolver

vp.scene.width = 700
vp.scene.height = 700
positionBlock = {}
moveButtonList = []
solveStepSequence=[]
cube = utility.CubeState([np.arange(7), np.zeros(7, dtype=int)])
faces = {
    'red': (vp.color.red, (1, 0, 0)),
    'blue': (vp.color.blue, (0, 0, 1)),
    'yellow': (vp.color.yellow, (0, 1, 0)),
    'white': (vp.color.white, (0, -1, 0)),
    'orange': (vp.color.orange, (-1, 0, 0)),
    'green': (vp.color.green, (0, 0, -1))
}
operations = {"R": vp.vector(1, 0, 0), "R'": vp.vector(1, 0, 0),
              "U": vp.vector(0, 1, 0), "U'": vp.vector(0, 1, 0),
              "F": vp.vector(0, 0, 1), "F'": vp.vector(0, 0, 1),
              "D": vp.vector(0, -1, 0), "D'": vp.vector(0, -1, 0),
              "L": vp.vector(-1, 0, 0), "L'": vp.vector(-1, 0, 0),
              "B": vp.vector(0, 0, -1), "B'": vp.vector(0, 0, -1),
              }
moveTable = {
    'U': MoveItem(permutation=np.array([0, 1, 2, 6, 3, 4, 5]), orientation=np.array([0, 0, 0, 0, 0, 0, 0])),
    "U'": MoveItem(permutation=np.array([0, 1, 2, 4, 5, 6, 3]), orientation=np.array([0, 0, 0, 0, 0, 0, 0])),
    "R": MoveItem(permutation=np.array([4, 0, 2, 3, 5, 1, 6]), orientation=np.array([1, 2, 0, 0, 2, 1, 0])),
    "R'": MoveItem(permutation=np.array([1, 5, 2, 3, 0, 4, 6]), orientation=np.array([1, 2, 0, 0, 2, 1, 0])),
    "F": MoveItem(permutation=np.array([0, 5, 1, 3, 4, 6, 2]), orientation=np.array([0, 1, 2, 0, 0, 2, 1])),
    "F'": MoveItem(permutation=np.array([0, 2, 6, 3, 4, 1, 5]), orientation=np.array([0, 1, 2, 0, 0, 2, 1])),

    "D": MoveItem(permutation=np.array([0, 1, 2, 6, 3, 4, 5]), orientation=np.array([0, 0, 0, 0, 0, 0, 0])),
    "D'": MoveItem(permutation=np.array([0, 1, 2, 4, 5, 6, 3]), orientation=np.array([0, 0, 0, 0, 0, 0, 0])),
    "L": MoveItem(permutation=np.array([4, 0, 2, 3, 5, 1, 6]), orientation=np.array([1, 2, 0, 0, 2, 1, 0])),
    "L'": MoveItem(permutation=np.array([1, 5, 2, 3, 0, 4, 6]), orientation=np.array([1, 2, 0, 0, 2, 1, 0])),
    "B": MoveItem(permutation=np.array([0, 5, 1, 3, 4, 6, 2]), orientation=np.array([0, 1, 2, 0, 0, 2, 1])),
    "B'": MoveItem(permutation=np.array([0, 2, 6, 3, 4, 1, 5]), orientation=np.array([0, 1, 2, 0, 0, 2, 1])),

}

def disableButton(func):
    def wrapFunc(*args,**kwargs):
        for button in moveButtonList:
            button.disabled = True
        result=func(*args,**kwargs)
        for button in moveButtonList:
            button.disabled = False
        return result
    return wrapFunc


def updateCubeState(axis, angle):
    global cube, positionBlock, moveTable
    whitePos = [abs(i) for i in positionBlock["white"].pos.value]
    orangePos = [abs(i) for i in positionBlock["orange"].pos.value]
    whiteDirection = [0] * 3
    whiteIndex = whitePos.index(max(whitePos))
    yellowIndex = orangePos.index(max(orangePos))
    whiteDirection[whiteIndex] = positionBlock["white"].pos.value[whiteIndex]
    whiteDirection = vp.vector(*whiteDirection)
    orangeDirection = [0] * 3
    orangeDirection[yellowIndex] = positionBlock["orange"].pos.value[yellowIndex]
    orangeDirection = vp.vector(*orangeDirection)

    movement = None
    judge180 = lambda pos, axis: vp.dot(pos, axis) < -0.9
    judge90 = lambda pos, axis: vp.fabs(vp.dot(pos, axis)) < 0.1
    judge0 = lambda pos, axis: vp.dot(pos, axis) > 0.9

    if judge90(whiteDirection, axis) and judge90(orangeDirection, axis):
        # F or B
        if angle == vp.pi / 2:
            movement = "F'"
        else:
            movement = "F"
    elif judge90(whiteDirection, axis) and judge180(orangeDirection, axis):
        if angle == vp.pi / 2:
            movement = "R'"
        else:
            movement = "R"
    elif judge180(whiteDirection, axis) and judge90(orangeDirection, axis):
        if angle == vp.pi / 2:
            movement = "U'"
        else:
            movement = "U"
    elif judge90(whiteDirection, axis) and judge0(orangeDirection, axis):
        if angle == vp.pi / 2:
            movement = "L'"
        else:
            movement = "L"
    elif judge0(whiteDirection, axis) and judge90(orangeDirection, axis):
        if angle == vp.pi / 2:
            movement = "D'"
        else:
            movement = "D"
    cube = utility.move(cube, moveTable[movement])


def rotateAnimationFactory(operation, fps=24):
    @disableButton
    def rotateAnimation(b):
        global cube, squares, operations, moveButtonList
        angle = vp.pi / 2 if "'" in operation else -vp.pi / 2
        axis = vp.vector(operations[operation])
        origin = vp.vector(0, 0, 0)
        angleFrame = angle / fps
        updateCubeState(axis, angle)
        for _ in vp.arange(0, angle, angleFrame):
            vp.rate(fps)
            for square in squares:
                if vp.dot(square.pos, axis) >= 0:
                    square.rotate(angle=angleFrame, axis=axis, origin=origin)

    return rotateAnimation


def rotateCubeAnimation(operation, fps=24):
    global cube, squares, operations
    angle = vp.pi if '2' in operation else vp.pi / 2 if "'" in operation else -vp.pi / 2
    axis = vp.vector(operations[operation])
    origin = vp.vector(0, 0, 0)
    angleFrame = angle / fps
    for _ in vp.arange(0, angle, angleFrame):
        vp.rate(fps)
        for square in squares:
            if vp.dot(square.pos, axis) >= 0:
                square.rotate(angle=angleFrame, axis=axis, origin=origin)
    cube = utility.move(cube, moveTable[operation])


def regularizeRubiksCube():
    whitePos: vp.vector = positionBlock["white"].pos
    orangePos: vp.vector = positionBlock["orange"].pos
    fps = 24
    # make positionBlock's white square facing down
    if whitePos.y >= -0.9:
        origin = vp.vector(0, 0, 0)
        if whitePos.y >= 0.9:
            axis = vp.vector(0, 0, 1)
            angle = vp.pi
            angleFrame = angle / fps
            for _ in vp.arange(0, angle, angleFrame):
                vp.rate(fps)
                for square in squares:
                    square.rotate(angle=angleFrame, axis=axis, origin=origin)
        else:
            angle = vp.pi / 2
            positionValue = [abs(i) for i in whitePos.value]
            pointingVec = [0] * 3
            index = positionValue.index(max(positionValue))
            pointingVec[index] = whitePos.value[index]
            pointingVec = vp.vector(*pointingVec)
            axis = vp.cross(pointingVec, vp.vector(0, -1, 0))
            angleFrame = angle / fps
            for _ in vp.arange(0, angle, angleFrame):
                vp.rate(fps)
                for square in squares:
                    square.rotate(angle=angleFrame, axis=axis, origin=origin)

    # make positionBlock's orange square facing left
    if orangePos.x >= -0.9:
        origin = vp.vector(0, 0, 0)
        if orangePos.x >= 0.9:
            axis = vp.vector(0, 1, 0)
            angle = vp.pi
            angleFrame = angle / fps
            for _ in vp.arange(0, angle, angleFrame):
                vp.rate(fps)
                for square in squares:
                    square.rotate(angle=angleFrame, axis=axis, origin=origin)
        else:
            angle = vp.pi / 2
            positionValue = [abs(i) for i in orangePos.value]
            pointingVec = [0] * 3
            index = positionValue.index(max(positionValue))
            pointingVec[index] = orangePos.value[index]
            pointingVec = vp.vector(*pointingVec)
            axis = vp.cross(pointingVec, vp.vector(-1, 0, 0))
            angleFrame = angle / fps
            for _ in vp.arange(0, angle, angleFrame):
                vp.rate(fps)
                for square in squares:
                    square.rotate(angle=angleFrame, axis=axis, origin=origin)

@disableButton
def solveByGraphButton(b):
    global cube, positionBlock, squares, moveButtonList

    regularizeRubiksCube()
    # solve
    currentCube = cube.__copy__()
    solveSteps = GraphSolver.solve(currentCube)

    global solveStepSequence
    solveStepSequence = solveSteps

    for step in solveSteps:
        rotateCubeAnimation(step)


@disableButton
def solveByIDAStar2PhaseButton(b):
    global cube, positionBlock, squares, moveButtonList
    regularizeRubiksCube()
    # solve
    currentCube = cube.__copy__()
    solveSteps = IDAStar2Phase.solve(currentCube)

    global solveStepSequence
    solveStepSequence=solveSteps

    for step in solveSteps:
        rotateCubeAnimation(step)


@disableButton
def solveByIDAStarButton(b):
    global cube, positionBlock, squares, moveButtonList
    regularizeRubiksCube()
    # solve
    currentCube = cube.__copy__()
    solveSteps = IDAStarSolver.solve(currentCube)

    global solveStepSequence
    solveStepSequence = solveSteps

    for step in solveSteps:
        rotateCubeAnimation(step)

@disableButton
def rewindToPostSolve(b):
    global solveStepSequence
    for step in reversed(solveStepSequence):
        rotateCubeAnimation(step,fps=10)


if __name__ == '__main__':

    squares = []
    for color, normalVector in faces.values():
        for x in (-0.5, 0.5):
            for y in (-0.5, 0.5):
                square = vp.box(color=color, pos=vp.vector(x, y, 1), length=0.98, height=0.98, width=0.05)
                cosine = vp.dot(vp.vector(0, 0, 1), vp.vector(*normalVector))
                axis = (vp.cross(vp.vector(0, 0, 1), vp.vector(*normalVector))
                        if cosine == 0 else vp.vector(1, 0, 0))
                square.rotate(angle=vp.acos(cosine), origin=vp.vector(0, 0, 0), axis=axis)
                squares.append(square)
                if color == vp.color.white and x == -0.5 and y == -0.5:
                    positionBlock["white"] = square
                elif color == vp.color.orange and x == -0.5 and y == -0.5:
                    positionBlock["orange"] = square

        vp.scene.lights.append(vp.distant_light(direction=vp.vector(*normalVector), color=vp.color.gray(0.3)))

    for operation in operations:
        fps = 24
        button = vp.button(text=f" {operation} ", pos=vp.scene.caption_anchor,
                           bind=rotateAnimationFactory(operation, fps))
        moveButtonList.append(button)
        vp.scene.append_to_caption("   ")

    vp.scene.append_to_caption("\n\n")
    vp.scene.append_to_caption("            ")

    button = vp.button(text=f"状态图法求解", pos=vp.scene.caption_anchor, bind=solveByGraphButton)
    moveButtonList.append(button)

    vp.scene.append_to_caption("     ")
    button = vp.button(text=f"IDA*2阶段算法求解", pos=vp.scene.caption_anchor, bind=solveByIDAStar2PhaseButton)
    moveButtonList.append(button)

    vp.scene.append_to_caption("     ")
    button = vp.button(text=f"IDA*算法求解", pos=vp.scene.caption_anchor, bind=solveByIDAStarButton)
    moveButtonList.append(button)

    vp.scene.append_to_caption("     ")
    button = vp.button(text=f"回到求解前状态", pos=vp.scene.caption_anchor, bind=rewindToPostSolve)
    moveButtonList.append(button)

    vp.scene.append_to_caption("\n")
