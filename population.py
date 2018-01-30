#!/usr/bin/env python

import individual
import box
import random

'''
Created on May 24, 2011

@author: baro
'''

class Population:
    def __init__(self, 
                 population_size, 
                 elitism=True, 
                 elitismFraction=0.10,
                 deathFraction=0.10,
                 mutationProb=0.001):
        
        self.population_size = population_size
        self.elitism = elitism
        self.mutationProb = mutationProb
        self.elistismFraction = elitismFraction
        self.infantMortality = deathFraction
        
        file = open("boxes.txt")
        fileinput = file.readlines()
        file.close()
            
        rawboxes = []
        for index in range(len(fileinput)):
            rawboxes.append(fileinput[index].replace("\n", "").split("\t"))                
            for index2 in range(len(rawboxes[index])):
                rawboxes[index][index2] = int(rawboxes[index][index2])
    
        objectBoxes = []
        for item in rawboxes:
            placing_box = box.Box(item[0],item[1],item[2],item[3],item[4])
            objectBoxes.append(placing_box)
        
        self.population = []
        for iteration in range(self.population_size):
            self.population.append(individual.Individual("random", objectBoxes))
            
    def evolve(self):
        populationToMate = len(self.population)
        workingPopulation = self.population[:]
        workingPopulation.sort(key=lambda obj: obj.fitness, reverse=True)
        
        newPopulation = []
        if self.elitism == True:
            numberOfElites = int(round(len(workingPopulation) * 
                                       self.elistismFraction))
            populationToMate -= numberOfElites
            for ind in range(numberOfElites):
                newPopulation.append(workingPopulation[ind])
        
        numberOfDeadInfants = int(round(len(workingPopulation) * 
                                        self.infantMortality))
        del workingPopulation[-numberOfDeadInfants:-1]

        total = int(round(sum([ind.fitness for ind in workingPopulation])))
        
        for ind in range(populationToMate):
            sel1 = random.randint(1, total-2)
            sel2 = random.randint(sel1, total-1)
            
            count = 0
            firstParentPlaced = False
            for individual in workingPopulation:
                count += individual.fitness
                if count > sel1 and not firstParentPlaced:
                    firstParent = individual
                    firstParentPlaced = True
                if count > sel2:
                    secondParent = individual
                    count = 0
                    firstParentPlaced = False
                    break
            offspring = firstParent + secondParent    
            self.mutate(offspring)
            newPopulation.append(offspring)        
            
        self.population = newPopulation
        
        #TODO: reporting of results to txtfile with actual rotations/boxorders
        #TODO: mutation
        
    def mutate(self, ind):
        chance = random.random()
        if chance < self.mutationProb * ind.alleleLength:
            pick = random.randint(1,3)
            al1 = random.randint(1,ind.alleleLength)
            al2 = random.randint(1,ind.alleleLength)
            
            if pick == 1:
                (ind.boxOrder[al1], ind.boxOrder[al2]) = (ind.boxOrder[al2], 
                                                        ind.boxOrder[al1])
            if pick == 2:
                ind.boxRotation[al1] = random.randint(0,5)
                ind.boxRotation[al2] = random.randint(0,5)
            else:
                (ind.boxOrder[al1], ind.boxOrder[al2]) = (ind.boxOrder[al2], 
                                                          ind.boxOrder[al1])
                (ind.boxRotation[al1], 
                 ind.boxRotation[al2]) = (ind.boxRotation[al2], 
                                          ind.boxRotation[al1])

    def getReport(self):
        total = sum([individual.fitness for individual in self.population])
        average = total/len(self.population)
        best = max([individual.fitness for individual in self.population])
        
        bOrd = [ind.boxOrder for ind in self.population if ind.fitness == best][0]
        bRot = [ind.boxRotation for ind in self.population if ind.fitness == best ][0]
        
        return {"average": average, "best": best, "bestBoxRotation": bRot, "bestBoxOrder": bOrd}
        

