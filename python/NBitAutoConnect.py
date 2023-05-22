import random
import math

Bin = list[bool]

def decToBin(decimal_num: int, num_bits: int = 0) -> Bin: 
    binary_list = []
    while decimal_num > 0:
        remainder = decimal_num % 2
        binary_list.insert(0, bool(remainder))
        decimal_num //= 2
    
    while len(binary_list) < num_bits:
        binary_list.insert(0, False)
    
    return binary_list

def binToDec(binary_list: Bin) -> int:
    decimal_num = 0
    for i in range(len(binary_list)):
        if binary_list[i]:
            decimal_num += 2**(len(binary_list)-1-i)
    return decimal_num

class ZeroNode:
    P = False
    G = False
    Pprim = False
    Gprim = False
    BprimForNext = False

    def getG(self) -> bool:
        return self.G
    
    def getP(self) -> bool:
        return self.P
    
    def getGprim(self) -> bool:
        return self.Gprim
    
    def getPprim(self) -> bool:
        return self.Pprim
    
    def getBprimForNext(self) -> bool:
        return self.BprimForNext

class PreProcessingNode:
    G = False
    H = False
    P = False
    Gprim = False
    Hprim = False
    Pprim = False
    BprimForNext = False

    def __init__(self, A: bool, B: bool, prevNode, K: bool = False):
        self.G = A & B
        self.H = A ^ B
        self.P = A | B
        self.BprimForNext = self.P if K else self.G
        Aprim = not self.H if K else self.H
        Bprim = prevNode.getBprimForNext()
        self.Gprim = Aprim & Bprim
        self.Hprim = Aprim ^ Bprim
        self.Pprim = Aprim | Bprim

    def getG(self) -> bool:
        return self.G
    
    def getH(self) -> bool:
        return self.H
    
    def getP(self) -> bool:
        return self.P
    
    def getGprim(self) -> bool:
        return self.Gprim
    
    def getHprim(self) -> bool:
        return self.Hprim
    
    def getPprim(self) -> bool:
        return self.Pprim
    
    def getBprimForNext(self) -> bool:
        return self.BprimForNext
    

class ParallelPrefixNode:
    G = False
    P = False
    Gprim = False
    Pprim = False

    def __init__(self, currentNode: PreProcessingNode, previousNode: PreProcessingNode) -> None:
        self.currentNode = currentNode
        self.previousNode = previousNode
        self.P = self.currentNode.getP() & self.previousNode.getP()
        self.G = self.currentNode.getG() | (self.previousNode.getG() & self.currentNode.getP())
        self.Pprim = self.currentNode.getPprim() & self.previousNode.getPprim()
        self.Gprim = self.currentNode.getGprim() | (self.previousNode.getGprim() & self.currentNode.getPprim())

    def getG(self) -> bool:
        return self.G

    def getP(self) -> bool: 
        return self.P
    
    def getGprim(self) -> bool:
        return self.Gprim

    def getPprim(self) -> bool: 
        return self.Pprim
    
    def getPrevNode(self):
        return self.previousNode
    
    def getCurrentNode(self):
        return self.currentNode
    
class SumNode:
    S = False

    def __init__(self, hNode, gpNode, carry = False) -> None:
        self.hNode = hNode
        self.gpNode = gpNode
        if carry:
            self.S = self.hNode.getH() ^ self.gpNode.getG()
        else:
            self.S = self.hNode.getHprim() ^ self.gpNode.getGprim()


    def getS(self):
        return self.S
    
    def gethNode(self):
        return self.hNode
    
    def getgpNode(self):
        return self.gpNode
    
# ------------------------------------------
# s = A + B mod (128 - K)
# A, B < 128 - K - 1


def ModuloParralelPrefixSumator(A, B, K, numberOfBits: int):
    numberOfLevels = math.ceil(math.log2(numberOfBits - 1))
    preProcessingNodes = []
    parrallelPrefixNodes = []
    sumNodes = []

    for i in range(0, numberOfLevels):
        parrallelPrefixNodes.append([])
        gap = 2**i
        flag = False
        for j in range(0, numberOfBits):
            parrallelPrefixNodes[i].insert(0, flag)
            if j%gap == gap - 1:
                flag = not flag

    for i in reversed(range(0, numberOfBits)):
        prevNode = preProcessingNodes[0] if len(preProcessingNodes) > 0 else ZeroNode()
        preProcessingNodes.insert(0, PreProcessingNode(A[i], B[i], prevNode, K[i]))

    for i in range(0, numberOfLevels):
        for j in reversed(range(0, numberOfBits)):
            if not parrallelPrefixNodes[i][j]:
                continue
            pigiNode = False
            pigiPrevNode = False
            for k in range(0, numberOfLevels):
                if type(parrallelPrefixNodes[k][j]) == type(ParallelPrefixNode(ZeroNode(), ZeroNode())):
                    pigiNode = parrallelPrefixNodes[k][j]

                if type(parrallelPrefixNodes[k][j+1]) == type(ParallelPrefixNode(ZeroNode(), ZeroNode())):
                    pigiPrevNode = parrallelPrefixNodes[k][j+1]
                    if k == i:
                        pigiPrevNode = parrallelPrefixNodes[k][j+1].getPrevNode()

            if not pigiNode:
                pigiNode = preProcessingNodes[j]
            if not pigiPrevNode:
                pigiPrevNode = preProcessingNodes[j+1]

            parrallelPrefixNodes[i][j] = ParallelPrefixNode(pigiNode, pigiPrevNode)

    carryNode = parrallelPrefixNodes[numberOfLevels - 1][0]
    carry = not (carryNode.getGprim() | carryNode.getG())
    
    for i in range(0, numberOfBits):
        pigiNode = False
        if i < numberOfBits - 1:
            for k in range(0, numberOfLevels):
                if parrallelPrefixNodes[k][i+1]:
                    pigiNode = parrallelPrefixNodes[k][i+1]
        else:
            pigiNode = ZeroNode()
        if not pigiNode:
            pigiNode = preProcessingNodes[i+1]
        sumNodes.append(SumNode(preProcessingNodes[i], pigiNode, carry))

    result = []
    for i in range(numberOfBits):
        result.append(sumNodes[i].getS())

    return result

k = 13
nob = 10
a = 0
b = 115
# print(ModuloParralelPrefixSumator(decToBin(a, nob), decToBin(b, nob), decToBin(k, nob), nob))
# exit()
for a in range(0, 2**nob - k):
    for b in range(0, 2**nob - k):
        s = (a + b) % (2**nob - k)
        res = ModuloParralelPrefixSumator(decToBin(a, nob), decToBin(b, nob), decToBin(k, nob), nob)
        resNum = binToDec(res)
        print(a)
        print(b)
        print("Wynik:")
        print(res)
        print(resNum)
        print("Oczekiwane:")
        print(s)
        print()
        print()
        if resNum != s:
            exit()