from collections import namedtuple
import numpy as np


def rankPermutation(p: np.ndarray):
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
        s = r // factorial
        p[n - 1], p[s] = p[s], p[n - 1]
        n -= 1
        r %= factorial
    return p


def encodeCube(pie: np.ndarray, q: np.ndarray) -> int:
    perNum = rankPermutation(pie)
    return perNum ** np.power(3, 6) + np.sum(q[:6] * np.array([np.power(3, i) for i in range(5, -1, -1)]))


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
    return permutation,np.array(orientation)


MoveItem = namedtuple("MoveItem", ["permutation", "orientation"])
moveTable = {
    # U
    'u': MoveItem(permutation=np.array([0, 1, 2, 6, 3, 4, 5]), orientation=np.array([0, 0, 0, 0, 0, 0, 0])),
    # U'
    "u'": MoveItem(permutation=np.array([0, 1, 2, 4, 5, 6, 4]), orientation=np.array([0, 0, 0, 0, 0, 0, 0])),
    # R
    "r": MoveItem(permutation=np.array([4, 0, 2, 3, 5, 1, 6]), orientation=np.array([1, 2, 0, 0, 2, 1, 0])),
    # R'
    "r'": MoveItem(permutation=np.array([1, 5, 2, 3, 0, 4, 6]), orientation=np.array([1, 2, 0, 0, 2, 1, 0])),
    # F
    "f": MoveItem(permutation=np.array([0, 5, 1, 3, 4, 6, 2]), orientation=np.array([0, 1, 2, 0, 0, 2, 1])),
    # F'
    "f'": MoveItem(permutation=np.array([0, 2, 6, 3, 4, 1, 5]), orientation=np.array([0, 1, 2, 0, 0, 2, 1])),
}

for k in range(10 - 1, 0, -1):
    print(k)

