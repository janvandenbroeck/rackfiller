'''
Created on May 14, 2011

@author: baro
'''

import box
import random

class Boxset:
    '''
    @change: 24/05/2011: made to work with order and rotation dictionaries
    '''
    def __init__(self, boxes, order, rotation):
        # @param boxes: list of box-objects
        # @param order: dictionary with items (step, boxToPlace)
        # @param rotation: dictionary with items (boxID, rotationNr)
        
        self.boxes = boxes
        self.placed_boxes = []
        self.extreme_points = [(0,0,0)]
        self.unplaced_boxes = self.boxes[:]
        self.shelves = [0]
        self.currentShelf = []
        self.order = order
        self.rotation = rotation
        
        
        for step in range(len(self.order)):
            unplacedBoxID = self.order[step+1]
            unplacedBox = self.unplaced_boxes[unplacedBoxID-1]
            unplacedBox.setRotation(self.rotation[unplacedBoxID])
            
            if self.getWeight(self.currentShelf) + unplacedBox.weight > 50000:
                height = self.getConvexHull(self.currentShelf)[2]
                self.shelves.append(height)
                self.extreme_points = [(0,0,height+10)]
                self.currentShelf = []
            unplacedBox.place(self.placeBox(unplacedBox))
            
            if unplacedBox.top > 2200:
                continue
            else:
                unplacedBox.fixPosition()
                self.placed_boxes.append(unplacedBox)
                self.currentShelf.append(unplacedBox)          
                
        
    def __del__(self):
        # Can probably be safely deleted, check individual.py
        for box in self.boxes:
            box.reset()
    
    def reset(self):
        #same as __del__, but in separate callable function
        for box in self.boxes:
            box.reset()
    
    def getFitness(self):
        actualvolume = sum([box.volume for box in self.placed_boxes])
        rack = 2200*1000*600
        usage = (float(actualvolume)*100)/float(rack)
        return usage
        
    def placeBox(self, box):
        '''
        Takes a box and runs over the extreme points to find a suitable
        place to put it. It then returns the coordinates of the best 
        place.
        '''
        best_index = 2**50
        current_height = self.getConvexHull(self.placed_boxes)[2]
        if len(self.extreme_points) == 0:
            self.extreme_points.append((0,0,current_height))
        for point in self.extreme_points:
            if not self.checkCollisions(box, point):                  
                if self.getIndex(box, point) < best_index:
                    if (box.length + point[0] < 1000 and 
                        box.width + point[1] < 600): 
                        best_index = self.getIndex(box,point)
                        best_point_index = self.extreme_points.index(point)
                        
        if best_index == 2**50:
            self.extreme_points.append((0,0,current_height))
            best_point_index = -1
        best_point = self.extreme_points[best_point_index]
        point = best_point
        
        moveable = True
        while moveable:
            dirx, diry, dirz = True, True, True
            while not self.checkCollisions(box, (point[0]-1,point[1],point[2])):
                if point[0] > 0:
                    point = (point[0]-1,point[1],point[2])
                    dirx = False
                else:
                    break
            while not self.checkCollisions(box, (point[0],point[1]-1,point[2])):
                if point[1] > 0:
                    point = (point[0],point[1]-1,point[2])
                    diry = False
                else:
                    break
            while not self.checkCollisions(box, (point[0],point[1],point[2]-1)):
                if point[2] > 0 and point[2] > self.shelves[-1]:
                    point = (point[0],point[1],point[2]-1)
                    dirz = False
                else:
                    break
            if dirx and diry and dirz:
                moveable = False
            
        best_point = point
        
        self.extreme_points.append((best_point[0]+box.length, 
                                    best_point[1], 
                                    best_point[2]))
        self.extreme_points.append((best_point[0], 
                                    best_point[1]+box.width, 
                                    best_point[2]))
        self.extreme_points.append((best_point[0], 
                                    best_point[1], 
                                    best_point[2]+box.height))
        del self.extreme_points[best_point_index]
        
        return best_point

    def getConvexHull(self, placed_boxes):
        convex_L = 0
        convex_W = 0
        convex_H = 0

        for box in placed_boxes:
            if box.right > convex_L:             
                convex_L = box.right                                               
            if box.front > convex_W:             
                convex_W = box.front                                              
            if box.top > convex_H:                 
                convex_H = box.top                 
                                         
        return (convex_L,convex_W, convex_H)

    def checkCollisions(self, box, point):
        '''
        Check if a "box" placed at a "point" intersects with any other
        box that is already placed.
        '''
        collision = False
        box.place(point)
        for pbox in self.placed_boxes:
            if((box.left < pbox.right and box.right > pbox.left) and
               (box.back < pbox.front and box.front > pbox.back) and
               (box.bottom < pbox.top and box.top > pbox.bottom)):
                collision = True
        return collision
    
    def getWeight(self, placedset):
        sum = 0
        for box in placedset:
            sum += box.weight
        return sum

    def getIndex(self, box, point):
        '''
        Lower is better
        not just a ratio, because of the third power
        '''
        convex_hull = self.getConvexHull(self.placed_boxes)
        hullVolume = (max(convex_hull[0],box.length+point[0]) * 
                      max(convex_hull[1],box.width+point[1]) * 
                      max(convex_hull[2],box.height+point[2])**3)

        contentVolume = box.volume
        for placed_box in self.placed_boxes:
            contentVolume += placed_box.volume
        index = float(hullVolume) / float(contentVolume)
        return index
    
    def getReport(self):
        print "%f %% efficiency" % (self.getFitness())
        print "%d boxes used" % (len(self.placed_boxes))
        print self.shelves
        
if __name__ == '__main__':
    ########
    file = open("boxes.txt")
    fileinput = file.readlines()
    file.close()
    rawboxes = []
    for index in range(0,len(fileinput)):
        rawboxes.append(fileinput[index].replace("\n", "").split("\t"))                
        # convert to integer, instead of string
        for index2 in range(0,len(rawboxes[index])):
            rawboxes[index][index2] = int(rawboxes[index][index2])
    
    print("rawboxes loaded")
    objectboxes = []
    for item in rawboxes:
        placing_box = box.Box(item[0],item[1],item[2],item[3],item[4])
        objectboxes.append(placing_box)
    
    allele_length = len(objectboxes)
    order = range(allele_length)
    random.shuffle(order)
    boxOrder = {}
    boxRotation = {}
    
    for box in range(allele_length):
        boxOrder[box+1] = order[box]+1
    
    for box in range(allele_length):
        boxRotation[box+1] = random.randint(0,5)    
    
    print("ready to create boxset")
    best = 0
    for iteration in range(100):
        boxset = Boxset(objectboxes, boxOrder, boxRotation)
        current = boxset.getFitness()
        if best < current: best = current
        #TODO: shuffle