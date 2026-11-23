import resource
from resource import *
import copy
import numpy as np
from random import random, randint, shuffle
from math import factorial, e
import networkx as nx
from itertools import permutations

'''n=200

'''

# -3-2 1 1
f = 8
# example from irving
#less than allowed = 50
#otherwise 48

'''
m1 x
m2 x
m3 x
m4 no need
m5 x
m6 no need
m7 x
m8 x

f1 x
f2 --
f3 x
f4 --
f5 no need
f6 y m
f7 x
f8 y m
'''
'''malePref = "\
3,1,5,7,4,2,8,6\n\
6,1,3,4,8,7,5,2\n\
7,4,3,6,5,1,2,8\n\
5,3,8,2,6,1,4,7\n\
4,1,2,8,7,3,6,5\n\
6,2,5,7,8,4,3,1\n\
7,8,1,6,2,3,4,5\n\
2,6,7,1,8,3,4,5"

femalePref = "\
4,3,8,1,2,5,7,6\n\
3,7,5,8,6,4,1,2\n\
7,5,8,3,6,2,1,4\n\
6,4,2,7,3,1,5,8\n\
8,7,1,5,6,4,3,2\n\
5,4,7,6,2,8,3,1\n\
1,4,5,6,2,8,3,7\n\
2,5,4,3,7,8,1,6"'''

'''
m1 
m2 
m3 
m4 
m5 
m6 
m7 
m8 x counter example

f1 
f2 
f3 
f4 no need
f5 y
f6 y
f7 x counter example
f8 y
'''

# example from gusfield
malePref = "\
5,7,1,2,6,8,4,3\n\
2,3,7,5,4,1,8,6\n\
8,5,1,4,6,2,3,7\n\
3,2,7,4,1,6,8,5\n\
7,2,5,1,3,6,8,4\n\
1,6,7,5,8,4,2,3\n\
2,5,7,6,3,4,8,1\n\
3,8,4,5,7,2,6,1"

femalePref = "\
5,3,7,6,1,2,8,4\n\
8,6,3,5,7,2,1,4\n\
1,5,6,2,4,8,7,3\n\
8,7,3,2,4,1,5,6\n\
6,4,7,3,8,1,2,5\n\
2,8,5,4,6,3,7,1\n\
7,5,2,1,8,6,4,3\n\
7,4,1,5,2,3,6,8"


'''malePref = "\
4,3,5,2,1\n\
3,4,2,5,1\n\
2,5,1,4,3\n\
5,2,3,1,4\n\
1,2,3,4,5"


femalePref = "\
1,2,3,5,4\n\
4,3,5,2,1\n\
3,4,2,5,1\n\
3,2,4,5,1\n\
5,3,2,4,1"'''

'''malePref = "\
2,1,3,4\n\
3,1,2,4\n\
1,2,3,4\n\
1,4,2,3"


femalePref = "\
1,2,3,4\n\
3,1,2,4\n\
1,2,3,4\n\
1,2,3,4"'''

# This class allows you to generate random strict and complete preferences
class RandomPreferenceGenerator:
    def __init__(self, n):
        self.n = n
        self.prefString = ""

    def generate(self):
        for i in range(self.n):
            arr = np.arange(1, self.n+1)
            np.random.shuffle(arr)
            arrStr = [str(integer) for integer in arr]
            self.prefString += ",".join(list(arrStr)) + f"\n"
        return self.prefString[:-1]


'''malePref = RandomPreferenceGenerator(f).generate()
femalePref = RandomPreferenceGenerator(f).generate()'''

# This class performs all preprocessing and creates all data structures necessary for the algorithm to run
class IndividualGenerator:
    def __init__(self, n, mpref, wpref):
        '''if not (len(malePref.split()) == len(femalePref.split()) == n):
            print("The number of agents and the number of preferences given are inconsistent")
            return'''
        self.maleSet = []
        self.femaleSet = []
        for i in range(n):
            self.maleSet.append(Individual(i, "male", n, mpref))
            self.femaleSet.append(Individual(i, "female", n, wpref))

        # testing
        '''self.residentSet[0].preference.ranking = {0: [2, 1], 1: [0]}
        self.residentSet[1].preference.ranking = {0: [1], 1: [0], 2: [2]}
        self.residentSet[2].preference.ranking = {0: [0, 1, 2]}

        self.hospitalSet[0].preference.ranking = {0: [0, 1], 1: [2]}
        self.hospitalSet[1].preference.ranking = {0: [1], 1: [0, 2]}
        self.hospitalSet[2].preference.ranking = {0: [2, 1, 0]}'''


    # Check if all agents are engaged
    def allEngaged(self):
        for m in self.maleSet:
            if len(m.engagedWith) == 0:
                return False
        for f in self.femaleSet:
            if len(f.engagedWith) == 0:
                return False
        return True

    # engage a man and a woman
    def propose(self, man, woman):
        man.engagedWith.append(woman.index)
        woman.engagedWith.append(man.index)

    # find a man's Individual object via his index
    def findMan(self, index):
        return self.maleSet[index]

    # find a woman's Individual object via her index
    def findWoman(self, index):
        return self.femaleSet[index]

    # Delete a (m,w) pair from both agents' preference lists
    def deletePair(self, man, woman):
        #rint(resident.index, hospital.index)
        womanRank = man.preference.reverseRank[woman.index]
        manRank = woman.preference.reverseRank[man.index]
        womanRankList = np.copy(man.preference.ranking[womanRank])
        manRankList = np.copy(woman.preference.ranking[manRank])
        #print(womanRankList)
        #print(manRankList)
        womanRankList = np.delete(womanRankList, np.argwhere(womanRankList == woman.index))
        manRankList = np.delete(manRankList, np.argwhere(manRankList == man.index))
        womanRankList = np.append(womanRankList, -1)
        manRankList = np.append(manRankList, -1)

        '''print("TESTING")
        print(man.index, woman.index)
        print(manRankList)
        print(man.preference.ranking)'''

        man.preference.ranking[womanRank] = womanRankList
        woman.preference.ranking[manRank] = manRankList

    # remove an engagement between two agents
    def removeEngagement(self, man, woman):
        #print("remove engagement woman")
        #print(woman.engagedWith)
        man.engagedWith.remove(woman.index)
        woman.engagedWith.remove(man.index)
        #print(woman.engagedWith)
        return

    # check if any man has an empty preference list (if he has been rejected by all women)
    def emptyMaleList(self):
        for male in self.maleSet:
            if np.all(male.preference.ranking == -1):
                return True
        return False

    # check if any woman has an empty preference list (if she has been rejected by all men)
    def emptyFemaleList(self):
        for female in self.femaleSet:
            if np.all(female.preference.ranking == -1):
                return True
        return False

    def __str__(self):
        outputString = ''
        for male in self.maleSet:
            outputString += f'\nmale: {male.index}, {male.engagedWith}'
        outputString += f'\n'
        for female in self.femaleSet:
            outputString += f'\nfemale: {female.index}, {female.engagedWith}'
        return outputString

    '''def __str__(self):
        outputString = ''
        for male in self.residentSet:
            outputString += f'\nmale: {male.index}, {list(male.preference.ranking)}, {male.engagedWith}'
        outputString += f'\n'
        for female in self.hospitalSet:
            outputString += f'\nfemale: {female.index}, {list(female.preference.ranking)}, {female.engagedWith}'
        return outputString'''


# This class is the data structure which holds all the necessary information relating to a certain agent
class Individual:
    def __init__(self, index, sex, n, allPrefs):
        self.index = index  # index of male or female individual
        self.sex = sex  # sex of individual (male/female)
        self.engagedWith = []
        #self.preference = RandomRanking(n, 1)
        self.preference = Ranking(index, allPrefs)
        self.originalPreferenceText = "Preference:\n"
        '''for rank in self.preference.ranking:
            self.originalPreferenceText += "\n\t(Rank " + str(rank+1) + ":"
            for index in self.preference.ranking[rank]:
                if self.sex == "male":
                    self.originalPreferenceText += " w" + str(index+1) + ","
                else:
                    self.originalPreferenceText += " m" + str(index+1) + ","
            self.originalPreferenceText = self.originalPreferenceText[:-1]
            self.originalPreferenceText += ")"'''

     # Check if an agent is single
    def isFree(self):
        if len(self.engagedWith) == 0:
            return True
        return False

    # Get the head of an agent's preference list (the first potential valid partner)
    def getHead(self):
        index = 0
        while self.preference.getRankOccupants(index)[0] == -1:
            index += 1
        return self.preference.getRankOccupants(index)

    # Get the rank of an agent relative to the current Individual's preferences
    def getRank(self, index):
        return self.preference.getRank(index)

    def __str__(self):
        return f"{self.sex}{self.index}"

# This class can create randomly generated preferences for weak and complete preferences
class RandomRanking:
    def __init__(self, N, K):
        b = self.getBellNumber(N)
        self.ranking = np.zeros(1)
        self.unm = lambda n, m, b: ((m ** n) / (factorial(m) * b)) / e
        self.getRandomSet(N, b)


    def genBellNumbers(self, n):
        B = [0] * (n + 1)  # Bell Numbers
        # Stirling numbers of the second kind
        S = [[0] * (n + 1) for i in range(n + 1)]
        S[0][1] = 1
        B[0] = 1
        for i in range(1, n + 1):
            for j in range(1, i + 1):
                S[i][j] = S[i - 1][j] * j + S[i - 1][j - 1]
                B[i] += S[i][j]
            S[i - 1] = []  # clean Stirling numbers (ram management)
        return B

    def getBellNumber(self, n):
        B = self.genBellNumbers(n)
        return B[n]

    def getM(self, n, b):
        p = random()
        m = 0
        while (p > 0):
            p -= self.unm(n, m, b)
            m += 1
        return m

    # 1 - choose M from unm (getM)
    # 2 - Drop n labelled balls uniformly into M boxes
    # 3 - Form a set partition λ of [n] with i and j in the same block if and
    # only if balls i and j are in the same box

    def getRandomSet(self, n, b):
        m = self.getM(n, b)
        b = []
        maxBucket = 0
        for i in range(n):
            b += [randint(0, m - 1)]
            if b[-1] > maxBucket:
                maxBucket = b[i]

        '''norm = [-1] * m
        normC = 0
        for i in range(n):
            if norm[b[i]] < 0:
                norm[b[i]] = normC
                normC += 1
            b[i] = norm[b[i]]
            if b[i] > maxBucket:
                maxBucket = b[i]'''

        self.ranking = np.full(shape=(maxBucket + 1, 1), fill_value=-1, dtype=int)
        self.reverseRank = np.full(shape=n, fill_value=-1, dtype=int)
        for i in range(len(b)):
            self.reverseRank[i] = b[i]
            if self.ranking[b[i]][-1] == -1:
                self.ranking[b[i]][np.argmin(self.ranking[b[i]])] = i
            else:
                self.ranking = np.hstack((self.ranking, np.full((np.shape(self.ranking)[0], 1), -1)))
                self.ranking[b[i]][np.argmin(self.ranking[b[i]])] = i
        #return self.ranking
        print()
        print(self.ranking)
        self.ranking = np.delete(self.ranking, np.where(self.ranking[:, 0] == -1), axis=0)
        for i in range(len(self.ranking)):
            for j in self.ranking[i]:
                if j == -1:
                    continue
                print(j, i)
                self.reverseRank[j] = i
        print()
        print(self.ranking)
        print(self.reverseRank)
        print(len(self.ranking))

    def getRankOccupants(self, rank):
        return self.ranking[rank]

    def getRank(self, index):
        return self.reverseRank[index]

# This class can turn preferences (given in the PrefLib format) into arrays which can be inputted into the algorithm
class Ranking:
    def __init__(self, index, allPref):
        initRank = makeRanking(allPref.split()[index])
        self.reverseRank = np.full(len(allPref.split()), -1, dtype=int)

        row = np.zeros(0)
        arr = np.zeros(0, dtype=int)
        for i in initRank[0].split(","):
            #print(initRank[0])
            row = np.concatenate([row, [int(i)-1]])
            self.reverseRank[int(i)-1] = 0
        arr = np.concatenate([np.zeros(0), row])
        for i in range(1, len(initRank)):
            row = np.zeros(0)
            for j in initRank[i].split(","):
                row = np.append(row, [int(j)-1])
                self.reverseRank[int(j)-1] = i
            #print(row)
            if arr.ndim > 1:
                #print(np.shape(arr)[1] < row.size)
                if np.shape(arr)[1] < row.size:
                    arr = np.column_stack([arr, np.full((np.shape(arr)[0], row.size - np.shape(arr)[1]), -1)])
                if np.shape(arr)[1] > row.size:
                    row = np.concatenate([row, np.full(np.shape(arr)[1] - row.size, -1)])
                arr = np.vstack([arr, row])
            else:
                if np.shape(arr)[0] < row.size:
                    arr = np.column_stack([arr, np.full((np.shape(arr)[0], row.size - np.shape(arr)[0]), -1)])
                if np.shape(arr)[0] > row.size:
                    row = np.concatenate([row, np.full(np.shape(arr)[0] - row.size, -1)])
                arr = np.vstack([arr, row])
        arr = arr.astype(int)
        self.ranking = arr

    def getRankOccupants(self, rank):
        return self.ranking[rank]

    def getRank(self, index):
        return self.reverseRank[index]

# This his a helper function for the Ranking class
def makeRanking(prefStr):
    if prefStr.find("{") != -1:
        beginIndex = prefStr.find("{")
        endIndex = prefStr.find("}")
        outputArr = prefStr[:beginIndex].split(",")
        outputArr.remove("")
        outputArr.append(prefStr[beginIndex+1:endIndex])
        outputArr.extend(makeRanking(prefStr[endIndex+1:]))
        outputArr.remove("")
        return outputArr
    else:
        return prefStr.split(",")


# separate operation for populating and randomizing ranking
# allows for pre-determined or random ranking

# This function runs deferred acceptance on the instance where men are proposing
def weaklyStableMatch2(n):
    data = IndividualGenerator(n)

    '''for m in data.maleSet:
        print(m.index)
        print(m.preference.ranking)
        print()
    for m in data.femaleSet:
        print(m.index)
        print(m.preference.ranking)
        print()
    print("-----------------------------")'''

    while not data.emptyMaleList():
        for man in data.maleSet:
            if data.emptyMaleList():
                return None
            if man.isFree():
                woman = data.findWoman(man.getHead()[0])
                data.propose(man, woman)
                wEngagementCopy = woman.engagedWith[:-1].copy()
                for i in wEngagementCopy:
                    data.removeEngagement(data.findMan(i), woman)
                for i in range(woman.getRank(man.index), len(woman.preference.ranking)):
                    tempPref = woman.preference.getRankOccupants(i).copy()
                    for mpref in tempPref:  # MIGHT CAUSE ISSUE
                        if mpref == -1 or mpref == man.index:
                            continue
                        data.deletePair(data.findMan(mpref), woman)
        if data.allEngaged():
            '''for m in data.maleSet:
                print(m.index)
                print(m.preference.ranking)
                print()
            for m in data.femaleSet:
                print(m.index)
                print(m.preference.ranking)
                print()'''
            return data

# This function runs deferred acceptance on the instance where women are proposing
def weaklyStableMatchWomen(n):
    data = IndividualGenerator(n)

    '''for m in data.maleSet:
        print(m.index)
        print(m.preference.ranking)
        print()
    for m in data.femaleSet:
        print(m.index)
        print(m.preference.ranking)
        print()'''

    while not data.emptyFemaleList():
        for woman in data.femaleSet:
            if data.emptyFemaleList():
                return None
            if woman.isFree():
                man = data.findMan(woman.getHead()[0])
                data.propose(woman, man)
                mEngagementCopy = man.engagedWith[:-1].copy()
                for i in mEngagementCopy:
                    data.removeEngagement(man, data.findWoman(i))

                for i in range(man.getRank(woman.index), len(man.preference.ranking)):
                    #print(f"woman index and engaged with: {woman.index} {woman.engagedWith}")
                    tempPref = man.preference.getRankOccupants(i).copy()
                    for wpref in tempPref:  # MIGHT CAUSE ISSUE
                        if wpref == -1 or wpref == woman.index:
                            #print("if loop continue")
                            continue
                        data.deletePair(man, data.findWoman(wpref))
        if data.allEngaged():
            '''for m in data.maleSet:
                print(m.index)
                print(m.preference.ranking)
                print()
            for m in data.femaleSet:
                print(m.index)
                print(m.preference.ranking)
                print()'''
            return data

# This function runs Gusfield's break marriage algorithm
def breakMarriage(n):
    manOptGS = weaklyStableMatch2(n)
    womanOptMatch = [-1] * n
    womanOptGS = weaklyStableMatchWomen(n)
    print(manOptGS)
    print(womanOptGS)
    for i in womanOptGS.maleSet:
        womanOptMatch[i.index] = i.engagedWith[0]

    print("------------------THIS IS WHERE BM STARTS------------------")

    M = copy.deepcopy(manOptGS)
    currentMatch = [-1]*n
    markedWomen = []
    allRotations = []
    initW = -1

    while True:
        #print("NEW ROUND")
        markedWomen = []
        step1 = False
        for i in M.maleSet:
            currentMatch[i.index] = i.engagedWith[0]
        if currentMatch == womanOptMatch:
            #print(len(allRotations))
            return allRotations

        for i in range(len(currentMatch)):
            if currentMatch[i] != womanOptMatch[i]:
                markedWomen.append(currentMatch[i])
                M.removeEngagement(M.findMan(i), M.findWoman(currentMatch[i]))
                M.deletePair(M.findMan(i), M.findWoman(currentMatch[i]))
                initW = currentMatch[i]
                break

        while not step1:
            for man in M.maleSet:
                #print(f"INDEX INIT {man.index}")
                if M.emptyMaleList():  # LOOK AT THIS
                    return None
                if man.isFree():
                    #print(f"MAN INDEX: {man.index}, {man.preference.ranking}")
                    for i in man.preference.ranking:
                        if i[0] == -1 or i[0] == currentMatch[man.index]:
                            continue
                        woman = M.findWoman(i[0])
                        '''print("MATCHING SO FAR")
                        print(M)
                        print(allRotations)
                        print(f"WOMAN INDEX {woman.index}")'''
                        if woman.index in markedWomen:
                            '''print("WOMAN MARKED")
                            print(f"INDICES: {man.index, woman.index}")
                            print(f"ENGAGEMENTS: {man.engagedWith}")
                            print(markedWomen)'''
                            if woman.getRank(man.index) < woman.getRank(currentMatch.index(woman.index)):
                                rotation = []
                                for j in markedWomen[markedWomen.index(woman.index):]:
                                    rotation.append((currentMatch.index(j), j))
                                # NEW STUFF
                                for count, j in enumerate(rotation):
                                    #print(M.findMan(j[0]).engagedWith)
                                    currentMatch[j[0]] = rotation[(count+1) % len(rotation)][1]
                                    markedWomen.remove(j[1])
                                allRotations.append(rotation)
                            else:
                                continue
                            if woman.index == initW:
                                #print("DONE WITH ONE ROUND BABY")
                                #M.removeEngagement(M.findMan(woman.engagedWith[0]), woman)
                                M.propose(man, woman)
                                step1 = True
                                break
                                # add more here maybe
                            else:
                                #print("W' NOT W")
                                if len(woman.engagedWith) == 0:
                                    M.propose(man, woman)
                                    # markedWomen.remove(woman.index)
                                    break
                                if woman.getRank(man.index) < woman.getRank(woman.engagedWith[0]):
                                    M.removeEngagement(M.findMan(woman.engagedWith[0]), woman)
                                    M.propose(man, woman)
                                    # markedWomen.remove(woman.index)
                                    break
                                else:
                                    # markedWomen.remove(woman.index)
                                    markedWomen.append(woman.index)
                                    continue
                        else:
                            #print("UNMARKED W")
                            if len(woman.engagedWith) == 0:
                                #print("UNMARKED W EMPTY")
                                M.propose(man, woman)
                                markedWomen.append(woman.index)
                                break
                            elif woman.getRank(man.index) < woman.getRank(woman.engagedWith[0]):
                                #print("UNMARKED W BETTER")
                                M.removeEngagement(M.findMan(woman.engagedWith[0]), woman)
                                M.propose(man, woman)
                                markedWomen.append(woman.index)
                                break
                            continue
                    if step1:
                        break
            if step1:
                break

# This function runs Irving's egalitarian stable marriage algorithm (using the previous 3 functions)
def egalitarianStableMatch(n, mpref, wpref, gale_shapley):
    initialPrefs = IndividualGenerator(n, mpref, wpref)
    GS = gale_shapley
    posets = breakMarriage(n)
    print(posets)
    print("-----------EGAL--------------------------")
    rotationPairs = np.empty([n,n], dtype=int)
    elimPairs = np.empty([n,n], dtype=int)
    rotationPairs.fill(-1)
    elimPairs.fill(-1)


    for woman in GS.femaleSet:
        #print(woman.index, woman.engagedWith[0])
        elimPairs[woman.engagedWith[0]][woman.index] = -2
        for j in range(woman.preference.getRank(woman.engagedWith[0]), len(woman.preference.ranking)):
            w = initialPrefs.findWoman(woman.index)
            man = w.preference.getRankOccupants(j)[0]
            if man == -1:
                continue
            #print(man, woman.index)
            elimPairs[man][woman.index] = -2

    # DO IT FOR WOMEN LIKE ABOVE
    posetWeight = []
    for count, i in enumerate(posets):
        sum = 0
        for pairCount, j in enumerate(i):
            print(f"PAIR: {j[0]+1, j[1]+1}")
            #print(initialPrefs.findMan(j[0]).getRank(j[1]), i[(pairCount+1)%len(i)])
            sum += initialPrefs.findMan(j[0]).getRank(j[1]) - initialPrefs.findMan(j[0]).getRank(i[(pairCount+1)%len(i)][1])
            sum += initialPrefs.findWoman(j[1]).getRank(j[0]) - initialPrefs.findWoman(j[1]).getRank(i[pairCount-1][0])
            elimPairs[j[0]][j[1]] = count
            rotationPairs[j[0]][j[1]] = count
            woman = initialPrefs.findWoman(j[1])
            #currentPartner = j[0]
            newPartner = i[pairCount-1][0]
            #for k in range(woman.preference.getRank(newPartner))
            #print(elimPairs)
            for k in range(woman.preference.getRank(newPartner)+1, len(woman.preference.ranking)):
                man = woman.preference.getRankOccupants(k)[0]
                if elimPairs[man][j[1]] == -1:
                    print(f"ELIM PAIR: {man+1, woman.index+1}")
                    elimPairs[man][j[1]] = count
        #print(f"SUM {sum}")
        posetWeight.append(sum)
    print(f"WEIGHT: {posetWeight}")
    print()
    print(elimPairs)
    print()
    print(rotationPairs)

    G = nx.DiGraph()
    G.add_nodes_from([*range(len(posets))])

    #orderedRot = []

    for man in initialPrefs.maleSet:
        rotList = []

        for count, i in enumerate(man.preference.ranking):
            currentRot = rotationPairs[man.index][i[0]]
            rotList.append(currentRot)
            if currentRot >= 0 and count == (len(man.preference.ranking)-1):
                continue
            elif currentRot < 0 and count == 0:
                continue
            if currentRot >= 0:
                nextRot = -1
                #nextIndex = -1
                for nextCount, j in enumerate(man.preference.ranking[count+1:]):
                    nextRot = rotationPairs[man.index][j[0]]
                    if nextRot < 0:
                        continue
                    if currentRot >= nextRot:
                        break
                    print(f"ADD EDGE: {currentRot, nextRot}")
                    G.add_edge(currentRot, nextRot)
                    break
            elif currentRot < 0:
                if elimPairs[man.index][i[0]] < 0:
                    continue
                prevRot = -1
                '''print(man.preference.ranking)
                print()
                print(np.flip(man.preference.ranking[:count]))'''
                for prevCount, j in enumerate(np.flip(man.preference.ranking[:count])):
                    prevRot = rotationPairs[man.index][j[0]]
                    #print(elimPairs[man.index][i[0]], prevRot)
                    #print(prevRot)
                    if prevRot < 0:
                        continue
                    if elimPairs[man.index][i[0]] >= prevRot:
                        break
                    print(f"ELIF ADD EDGE: {elimPairs[man.index][i[0]], prevRot}")
                    G.add_edge(elimPairs[man.index][i[0]], prevRot)
                    break
        '''for count, i in enumerate(man.preference.ranking[:-1]):
            #print(i)
            currentRot = rotationPairs[man.index][i[0]]
            rotList.append(currentRot)
            if currentRot < 0:
                continue
            nextRot = -1
            nextIndex = -1
            for nextCount, j in enumerate(man.preference.ranking[count+1:]):
                #print(j, elimPairs[man.index][j[0]])
                if elimPairs[man.index][j[0]] >= 0:
                    #print(f"ELIM PAIR: {elimPairs[man.index][j[0]]}")
                    nextRot = rotationPairs[man.index][j[0]]
                    nextIndex = j[0]
                    break
            #print(f"NEXT ROT: {currentRot, nextRot}")
            if currentRot == nextRot:
                continue
            #nextRot = rotationPairs[man.index][man.preference.ranking[count+1][0]]
            #print(man.preference.ranking[count+1])
            if nextRot >= 0:
                if currentRot > nextRot:
                    continue
                print(f"ADD EDGE: {currentRot, nextRot}")
                G.add_edge(currentRot, nextRot)
                continue
            #print(f"NOT VALID {elimPairs[man.index][nextIndex]}")
            if elimPairs[man.index][nextIndex] >= 0 and nextIndex != -1:
                #print(man.index, nextIndex)
                #LOOK AT THIS POTENTIALLY
                #if elimPairs[man.index][nextIndex] > currentRot:
                    #continue
                print(f"ELIF ADD EDGE: {elimPairs[man.index][nextIndex], currentRot}")
                G.add_edge(elimPairs[man.index][nextIndex], currentRot)
        #orderedRot.append(rotList)'''
    G.add_nodes_from(["s", "t"])
    for count, i in enumerate(posetWeight):
        if i < 0:
            G.add_edge("s", count, capacity=abs(i))
        elif i > 0:
            G.add_edge(count, "t", capacity=abs(i))

    print(nx.to_numpy_array(G))

    cut_value, partition = nx.minimum_cut(G, "s", "t")
    reachable, non_reachable = partition
    cutset = set()
    for u, nbrs in ((n, G[n]) for n in reachable):
        cutset.update((u, v) for v in nbrs if v in non_reachable)
    print(reachable, non_reachable)
    print(cutset)

    egalitarianRotations = []
    for count, i in enumerate(posetWeight):
        if i > 0 and ((count, "t") not in cutset):
            print("YES")
            for pred in list(nx.edge_dfs(G, count, orientation='reverse')):
                print(pred)
                if type(pred[0]) != str and pred[0] not in egalitarianRotations:
                    egalitarianRotations.append(pred[0])
            if count not in egalitarianRotations:
                egalitarianRotations.append(count)
    egalitarianRotations.sort()
    print(egalitarianRotations)
    for i in egalitarianRotations:
        for count, j in enumerate(posets[i]):
            # print(j, posets[i][(count+1) % len(posets[i])])
            man = GS.findMan(j[0])
            woman = GS.findWoman(j[1])
            GS.removeEngagement(man, woman)
            GS.propose(man, GS.findWoman(posets[i][(count+1) % len(posets[i])][1]))
    print(GS)
    return GS

#Tests all permutations of an agent's preferences
def testCases(n):
    mPreferences = []
    wPreferences = []
    for i in range(n):
        x = [j for j in range(1, n + 1)]
        y = [j for j in range(1, n + 1)]
        shuffle(x)
        shuffle(y)
        mPreferences.append(x)
        wPreferences.append(y)

    #mPreferences = [[5, 7, 1, 2, 6, 8, 4, 3],[2, 3, 7, 5, 4, 1, 8, 6],[8, 5, 1, 4, 6, 2, 3, 7],[3, 2, 7, 4, 1, 6, 8, 5],[7, 2, 5, 1, 3, 6, 8, 4],[1, 6, 7, 5, 8, 4, 2, 3],[2, 5, 7, 6, 3, 4, 8, 1],[3, 8, 4, 5, 7, 2, 6, 1]]
    #wPreferences = [[5, 3, 7, 6, 1, 2, 8, 4],[8, 6, 3, 5, 7, 2, 1, 4],[1, 5, 6, 2, 4, 8, 7, 3],[8, 7, 3, 2, 4, 1, 5, 6],[6, 4, 7, 3, 8, 1, 2, 5],[2, 8, 5, 4, 6, 3, 7, 1],[7, 5, 2, 1, 8, 6, 4, 3],[7, 4, 1, 5, 2, 3, 6, 8]]

    mPrefStr = ""
    for count, i in enumerate(mPreferences):
        for j in i:
            mPrefStr += f"{j}"
            if j != i[-1]:
                mPrefStr += ","
        if count != len(mPreferences)-1:
            mPrefStr += "\n"
    print(mPrefStr)
    print()

    wPrefStr = ""
    for count, i in enumerate(wPreferences):
        for j in i:
            wPrefStr += f"{j}"
            if j != i[-1]:
                wPrefStr += ","
        if count != len(wPreferences)-1:
            wPrefStr += "\n"
    print(wPrefStr)

    global malePref
    malePref = mPrefStr

    global femalePref
    femalePref = wPrefStr

    manOpt = weaklyStableMatch2(n)
    womanOpt = weaklyStableMatchWomen(n)
    egalitarian = egalitarianStableMatch(n)
    initialPrefs = IndividualGenerator(n)

    examples = 0
    correct = 0

    for m in initialPrefs.maleSet:
        print(f"---HERE HERE HERE {egalitarian.findMan(m.index).engagedWith[0], womanOpt.findMan(m.index).engagedWith[0]}")
        if m.getRank(egalitarian.findMan(m.index).engagedWith[0]) == m.getRank(womanOpt.findMan(m.index).engagedWith[0]):
            examples += 1
            modmPref = mPreferences.copy()
            modmPref[m.index].append(modmPref[m.index].pop(modmPref[m.index].index(egalitarian.findMan(m.index).engagedWith[0]+1)))
            mPrefStrTemp = ""
            for count, i in enumerate(mPreferences):
                for j in i:
                    mPrefStrTemp += f"{j}"
                    if j != i[-1]:
                        mPrefStrTemp += ","
                if count != len(mPreferences) - 1:
                    mPrefStrTemp += "\n"
            #global malePref
            malePref = mPrefStrTemp
            newEgal = egalitarianStableMatch(n)
            if m.getRank(egalitarian.findMan(m.index).engagedWith[0]) > m.getRank(newEgal.findMan(m.index).engagedWith[0]):
                correct += 1
            #global malePref
            malePref = mPrefStr

    for w in initialPrefs.femaleSet:
        print(f"---HERE HERE HERE {egalitarian.findWoman(w.index).engagedWith[0], manOpt.findWoman(w.index).engagedWith[0]}")
        if w.getRank(egalitarian.findWoman(w.index).engagedWith[0]) == w.getRank(manOpt.findWoman(w.index).engagedWith[0]):
            examples += 1
            modwPref = wPreferences.copy()
            modwPref[w.index].append(modwPref[w.index].pop(modwPref[w.index].index(egalitarian.findWoman(w.index).engagedWith[0]+1)))
            wPrefStrTemp = ""
            for count, i in enumerate(wPreferences):
                for j in i:
                    wPrefStrTemp += f"{j}"
                    if j != i[-1]:
                        wPrefStrTemp += ","
                if count != len(wPreferences) - 1:
                    wPrefStrTemp += "\n"
            #global malePref
            femalePref = wPrefStrTemp
            newEgal = egalitarianStableMatch(n)
            if w.getRank(egalitarian.findWoman(w.index).engagedWith[0]) > w.getRank(newEgal.findWoman(w.index).engagedWith[0]):
                correct += 1
            #global malePref
            femalePref = wPrefStr
    print(correct, examples)

# calculate weight for each edge
# establish s and t nodes
# add weights and edges properly


'''d = weaklyStableMatch2(f)
w = weaklyStableMatchWomen(f)
print(d)
print(w)'''

def permutation(n):
    list = [*range(1, n+1)]
    p = permutations(list)
    EXAMPLES = []
    count = 1
    global femalePref
    for i in p:
        prefs = ""
        for j in i:
            prefs = prefs + str(j) + ","
        prefs = prefs[:-1]

        femalePref = f"\
        5,3,7,6,1,2,8,4\n\
        8,6,3,5,7,2,1,4\n\
        1,5,6,2,4,8,7,3\n\
        8,7,3,2,4,1,5,6\n\
        {prefs}\n\
        2,8,5,4,6,3,7,1\n\
        7,5,2,1,8,6,4,3\n\
        7,4,1,5,2,3,6,8"

        egal = egalitarianStableMatch(n)
        print(f"COUNT: {count}")
        count += 1
        if egal.findWoman(4).engagedWith[0] not in [0, 5]:
            break
            prefs = prefs + f", PARTNER {egal.findWoman(4).engagedWith[0]}"
            EXAMPLES.append(prefs)
    print(f"EXAMPLES: {EXAMPLES}")
    return EXAMPLES


#p = permutation(f)
bm = egalitarianStableMatch(f)
#tc = testCases(f)
#print(bm)

print(resource.getrusage(RUSAGE_SELF))
