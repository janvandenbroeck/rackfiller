'''
Created on May 14, 2011

@author: baro
'''

import random
import boxset
import box

class Individual:
    '''
    @change: 24/05/2011: implemented boxOrder and boxRotation dictionaries
    '''
    def __init__(self, mode, boxes, order={}, rotation={}):
        
        self.boxes = boxes
        self.alleleLength = len(self.boxes)
        
        
        if mode == "normal":
            if order == {} or rotation == {}: 
                print "order or rotation not set"
                quit()
            self.boxOrder = order
            self.boxRotation = rotation
            
        elif mode == "random":
            self.boxOrder = {}
            self.boxRotation = {}
            order = range(self.alleleLength)
            random.shuffle(order)
            for box in range(self.alleleLength):
                self.boxOrder[box+1] = order[box]+1
            
            for box in range(self.alleleLength):
                self.boxRotation[box+1] = random.randint(0,5)
            
        else:
            print("Individual.mode was set invalidly")
            quit()
        
        self.getFitness()
        
    def __str__(self):
        string = "".join([str(box) + '\n' for box in self.boxes])
        return string
        
    def __add__(self, other):
        """
        self.boxOrder is dictionary (step, box)
        """
        if len(self.boxOrder) != len(other.boxOrder):
            print "trying to add boxes with different lengths"
            quit()
        
        offspring = self.singlePointCrossover(other)
        
        return offspring

    def greedySubTourCrossover(self, other):
        baseBoxID = random.randint(1,len(other.boxOrder))
        
        for pair in self.boxOrder.viewitems():
            if pair[1] == baseBoxID:
                baseBoxNr = pair[0]
        
        placed = [baseBoxID]
        fromFirstParent = []
        fromSecondParent = []
        fBroken = False
        sBroken = False
        
        for offset in range(1,len(self.boxOrder)):
            if baseBoxNr <= offset or baseBoxNr+offset > len(self.boxOrder):
                break
            
            if (self.boxOrder[baseBoxNr-offset] not in placed) and not fBroken:
                fromFirstParent.append(self.boxOrder[baseBoxNr-offset])
                placed.append(self.boxOrder[baseBoxNr-offset])
            else:
                fBroken = True
                
            if (other.boxOrder[baseBoxNr+offset] not in placed) and not sBroken:
                fromSecondParent.append(other.boxOrder[baseBoxNr+offset])
                placed.append(other.boxOrder[baseBoxNr+offset])
            else:
                sBroken = True
            
            if fBroken and sBroken:
                break

        # find remaining boxes
        unp1 = [it for it in self.boxOrder.viewvalues() if it not in placed]
        placed.extend(unp1)
        unp2 = [it for it in other.boxOrder.viewvalues() if it not in placed]
        unp1.extend(unp2)
        random.shuffle(unp1)
        
        fromFirstParent.reverse()
        
        # create a list with the correct order 
        returnList = []
        returnList.extend(fromFirstParent)
        returnList.append(baseBoxID)
        returnList.extend(fromSecondParent)
        returnList.extend(unp1)
    
        retOrder = {}
        for item in range(1, len(self.boxOrder)+1):
            retOrder[item] = returnList[item-1]
        
        returnRotations = {}
        for id in range(1,len(self.boxOrder)+1):
            if retOrder[id] in fromFirstParent:
                returnRotations[id] = self.boxRotation[id]
            elif retOrder[id] in fromSecondParent:
                returnRotations[id] = other.boxRotation[id]
            else:
                z = random.random()
                if z > 0.5:
                    returnRotations[id] = self.boxRotation[id]
                else:
                    returnRotations[id] = other.boxRotation[id]
        
        offspring = Individual("normal",self.boxes,retOrder, returnRotations)
        return offspring
    
    def singlePointCrossover(self, other):
        crossPoint = random.randint(1, len(self.boxOrder))
        
        fromFirstParent = []
        fromSecondParent = []
        
        for place in range(1,crossPoint+1):
            fromFirstParent.append(self.boxOrder[place])
        
        for place in range(crossPoint+1,len(self.boxOrder)+1):
            if other.boxOrder[place] not in fromFirstParent:
                fromSecondParent.append(other.boxOrder[place])
            else:
                continue
        
        rest = []
        for place in range(1,len(other.boxOrder)+1):
            if((other.boxOrder[place] not in fromFirstParent) and 
               (other.boxOrder[place] not in fromSecondParent)):
                rest.append(other.boxOrder[place])
        
        random.shuffle(rest)
        returnList = []
        returnList.extend(fromFirstParent)
        returnList.extend(fromSecondParent)
        returnList.extend(rest)
        
        retOrder = {}
        for item in range(1, len(self.boxOrder)+1):
            retOrder[item] = returnList[item-1]
        
        returnRotations = {}
        for item in range(1,len(self.boxOrder)+1):
            if retOrder[item] in fromFirstParent:
                returnRotations[item] = self.boxRotation[item]
            elif retOrder[item] in fromSecondParent:
                returnRotations[item] = other.boxRotation[item]
            else:
                z = random.random()
                if z > 0.5:
                    returnRotations[item] = self.boxRotation[item]
                else:
                    returnRotations[item] = other.boxRotation[item]
        
        offspring = Individual("normal", self.boxes, retOrder, returnRotations) 
        return offspring
    
    def mutate(self, probMutation, maxMutation):
        pass
                
    def getFitness(self):
        #print "creating Boxset"
        #print [(box.id, box.fixed_position) for box in self.boxes]
        placement = boxset.Boxset(self.boxes, self.boxOrder, self.boxRotation)
        #print "Boxset created, getting fitnes"
        self.fitness = placement.getFitness()
        #print "fitnet got, resetting"
        placement.reset()
        #print "reset, deleting"
        del placement
        return self.fitness
        
if __name__ == '__main__':    
    file = open("boxes.txt")
    fileinput = file.readlines()
    file.close()
        
    rawboxes = []
    for index in range(len(fileinput)):
        rawboxes.append(fileinput[index].replace("\n", "").split("\t"))                
        for index2 in range(len(rawboxes[index])):
            rawboxes[index][index2] = int(rawboxes[index][index2])

    objectboxes = []
    for item in rawboxes:
        placing_box = box.Box(item[0],item[1],item[2],item[3],item[4])
        objectboxes.append(placing_box)
    
    size = 10
    
    population = []
    for step in range(size):
        individual = Individual("random", objectboxes)
        population.append(individual)
    print "population complete"
    
    scores = []
    step = 1
    for ind in population:
        scores.append(ind.fitness)
        if step%5 == 0:
            print "%d/%d" % (step, size)
        step += 1
        
    maximum = max(scores)
    print maximum
    