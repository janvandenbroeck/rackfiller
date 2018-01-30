#! /usr/bin/python
'''
Created on May 14, 2011

@author: baro
'''

class Box:
    '''
    classdocs
    '''
    def __init__(self, id, length, width, height, weight):
        '''
        Set the initial variables
        '''
        self.id = id
        self.originalLength = length
        self.originalWidth = width
        self.originalHeight = height
        self.length = length
        self.width = width
        self.height = height
        self.weight = weight
        self.fixed_position = False
        self.volume = length * height * width
        
    def __str__(self):
        '''
        What to print
        '''
        return("id:{0}, l:{1}, w:{2}, h:{3}, wt:{4}".format(self.id, self.length, self.width, self.height, self.weight))

    def setRotation(self, number):
        if number == 0:
            pass
        elif number == 1:
            self.width, self.height = self.originalHeight, self.originalWidth
        elif number == 2:
            self.length, self.width = self.originalWidth, self.originalLength
        elif number == 3:
            self.length, self.width, self.height = self.originalWidth, self.originalHeight, self.originalLength
        elif number == 4:
            self.length, self.width, self.height = self.originalHeight, self.originalLength, self.originalWidth
        elif number == 5:
            self.length, self.height = self.originalHeight, self.originalLength
        else:
            print("Error occurred: rotation value not valid")
            quit()
    
    def place(self, coordinates):
        '''
        Function that places a box at a certain coordinate
        '''
        if self.fixed_position == False:
            self.left = coordinates[0]
            self.right = self.left + self.length
            self.back = coordinates[1]
            self.front = self.back + self.width
            self.bottom = coordinates[2]
            self.top = self.bottom + self.height
        else:
            print("error, tried to place box %d, already fixed" % (self.id))
            quit()
            
    def fixPosition(self):
        '''
        make the position permanent
        '''
        self.fixed_position = True
        
    def reset(self):
        self.fixed_position = False
        # print "reset %d" % self.id
        self.setRotation(0)

if __name__ == '__main__':
    file = open("boxes.txt")
    rawboxes = file.readlines()
    file.close()
    
    boxes = []     
    
    for index in range(0,len(rawboxes)):
        boxes.append(rawboxes[index].translate(None, '\n').split("\t"))
        for index2 in range(0,len(boxes[index])):
            boxes[index][index2] = int(boxes[index][index2])  
        
    objectBoxes = []
    for data in boxes:
        objectBoxes.append(Box(data[0], data[1], data[2], data[3], data[4]))
        
    for box in objectBoxes:
        print(box)