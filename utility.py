from collections import namedtuple
from typing import List
import vpython as vp
import numpy as np
import time

MoveItemBase = namedtuple("MoveItem", ["permutation", "orientation"])
CubeStateBase = namedtuple("CubeState", ["blockSequence", "orienSequence"])
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
    'U': "U'",
    "U'": "U",
    "R": "R'",
    "R'": "R",
    "F": "F'",
    "F'": "F",
    "R2": "R2",
    "F2": "F2"
}


class MoveItem(MoveItemBase):
    def __new__(cls, permutation: np.ndarray, orientation: np.ndarray, copy=True):
        if copy:
            return super(MoveItem, cls).__new__(cls, permutation=permutation.copy(), orientation=orientation.copy())
        else:
            return super(MoveItem, cls).__new__(cls, permutation=permutation, orientation=orientation)

    def __eq__(self, other):
        if other is not None:
            return (self[0] == other[0]).all() and (self[1] == other[1]).all()
        else:
            return False


class CubeState(CubeStateBase):

    def __new__(cls, *args, blockSequence: np.ndarray = None, orienSequence: np.ndarray = None, copy=True, **kwargs):
        if len(args) == 1 and (type(args[0]) == list or type(args[0]) == tuple):
            if copy:
                return super(CubeState, cls).__new__(cls, blockSequence=args[0][0].copy(),
                                                     orienSequence=args[0][1].copy())
            else:
                return super(CubeState, cls).__new__(cls, blockSequence=args[0][0],
                                                     orienSequence=args[0][1])
        else:
            if copy:
                return super(CubeState, cls).__new__(cls, blockSequence=blockSequence.copy(),
                                                     orienSequence=orienSequence.copy())
            else:
                return super(CubeState, cls).__new__(cls, blockSequence=blockSequence,
                                                     orienSequence=orienSequence)

    def __eq__(self, other):
        if other is not None:
            return (self[0] == other[0]).all() and (self[1] == other[1]).all()
        else:
            return False

    def __copy__(self):
        return CubeState(blockSequence=self.blockSequence, orienSequence=self.orienSequence)


def rankPermutation(p: np.ndarray):
    p = p.copy()
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


def encodeCube(cube: CubeState) -> int:
    pie, q = cube
    perNum = rankPermutation(pie)
    return int(perNum * np.power(3, 6) + np.sum(q[:6] * np.array([np.power(3, i) for i in range(5, -1, -1)])))


def decodeCube(cubeNum: int) -> CubeState:
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
    orientation.append((2 * (sum(orientation) % 3)) % 3)
    return CubeState([permutation, np.array(orientation, dtype=int)], copy=False)


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


def move(cube: CubeState, movement: MoveItem) -> [np.ndarray, np.ndarray]:
    newPermutation = cube.blockSequence[movement.permutation]
    newOrientation = np.mod((cube.orienSequence[movement.permutation] + movement.orientation), 3)
    return CubeState([newPermutation, newOrientation], copy=False)

def infoPrint(prompt:str):
    def infoPrint(func):
        def wrapFunc(*args,**kwargs):
            start=time.clock()
            result=func(*args,**kwargs)
            end=time.clock()
            vp.scene.append_to_caption(f"time consumed:{end-start:.5f}s ")
            vp.scene.append_to_caption(prompt+":")
            for step in result:
                vp.scene.append_to_caption(step+" ")
            vp.scene.append_to_caption('\n')
            return result
        return wrapFunc
    return infoPrint


