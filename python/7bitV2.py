import random

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
    
# ------------------------------------------
# s = A + B mod (2**n - K)
# A, B < 2**n - K - 1

k = 5
n = 7
for a in range(0, 2**n - k):
    for b in range(0, 2**n - k):
        A = a
        B = b
        S = (A + B) % (2**n - k)
        A = decToBin(A, 7)
        B = decToBin(B, 7)
        K = decToBin(k, 7)
        A.reverse()
        B.reverse()
        K.reverse()

        # K as fourth argument
        n0 = PreProcessingNode(A[0], B[0], ZeroNode(), K[0])
        n1 = PreProcessingNode(A[1], B[1], n0, K[1])
        n2 = PreProcessingNode(A[2], B[2], n1, K[2])
        n3 = PreProcessingNode(A[3], B[3], n2, K[3])
        n4 = PreProcessingNode(A[4], B[4], n3, K[4])
        n5 = PreProcessingNode(A[5], B[5], n4, K[5])
        n6 = PreProcessingNode(A[6], B[6], n5, K[6])

        pp11 = ParallelPrefixNode(n1, n0)
        pp12 = ParallelPrefixNode(n3, n2)
        pp13 = ParallelPrefixNode(n5, n4)

        pp21 = ParallelPrefixNode(n2, pp11)
        pp22 = ParallelPrefixNode(pp12, pp11)
        pp23 = ParallelPrefixNode(n6, pp13)

        pp31 = ParallelPrefixNode(n4, pp22)
        pp32 = ParallelPrefixNode(pp13, pp22)
        pp33 = ParallelPrefixNode(pp23, pp22)

        carry = not (pp33.getGprim() | pp33.getG())
        s0 = SumNode(n0, ZeroNode(), carry)
        s1 = SumNode(n1, n0, carry)
        s2 = SumNode(n2, pp11, carry)
        s3 = SumNode(n3, pp21, carry)
        s4 = SumNode(n4, pp22, carry)
        s5 = SumNode(n5, pp31, carry)
        s6 = SumNode(n6, pp32, carry)


        # n6   n5   n4   n3   n2   n1   n0
        #
        #      pp13      pp12      pp11
        #
        # pp23           pp22 pp21
        #
        # pp33 pp32 pp31
        # 
        # s6   s5   s4   s3   s2   s1   s0
        #
        # -----------------------------------------------------
        A.reverse()
        B.reverse()
        print("A, B: " + str(binToDec(A)) + ', ' + str(binToDec(B)))
        A.reverse()
        B.reverse()
        print("Wynik: ")
        print([s6.getS(), s5.getS(), s4.getS(), s3.getS(), s2.getS(), s1.getS(), s0.getS()])
        print(binToDec([s6.getS(), s5.getS(), s4.getS(), s3.getS(), s2.getS(), s1.getS(), s0.getS()]))
        print("Oczekiwany:")
        print(S)

        if(S != binToDec([s6.getS(), s5.getS(), s4.getS(), s3.getS(), s2.getS(), s1.getS(), s0.getS()])):
            exit()
        print()
        print()