#! /usr/bin/python
'''
Created on May 14, 2011

@author: baro
'''

import random
best_usage = 0

file = open("boxes.txt")
rawboxes_source = file.readlines()
file.close()
length_of_file = len(rawboxes_source)

def initialize():
    
    rawboxes = rawboxes_source

    result = []
    for index in xrange(0,len(rawboxes)):
        result.append(rawboxes[index].translate(None, '\n').split("\t"))                # split on tabs, remove trailing newline
                                                                                        # unplaced_boxes is now a list, with lists inside
        for index2 in xrange(0,len(result[index])):
            result[index][index2] = int(result[index][index2])                          # convert to integer
    return result
    
def rotate(list,number):
    result = [0,0,0,0,0]
    
    if number == 0:                     # X+Y
        for each in xrange(0,len(list)):
            result[each] = list [each]
    elif number == 1:
        result[0] = list[0]             # X+Z
        result[1] = list[1]
        result[2] = list[3]
        result[3] = list[2]
        result[4] = list[4]
    elif number == 2:                   # X+Y Alt
        result[0] = list[0]
        result[1] = list[2] # X
        result[2] = list[1] # Y
        result[3] = list[3] # Z
        result[4] = list[4]
    elif number == 3:
        result[0] = list[0]             # Y+Z ALT
        result[1] = list[2]
        result[2] = list[3]
        result[3] = list[1]
        result[4] = list[4]
    elif number == 4:
        result[0] = list[0]             # X+Z ALT
        result[1] = list[3]
        result[2] = list[1]
        result[3] = list[2]
        result[4] = list[4]
    elif number == 5:
        result[0] = list[0]             # Y+Z
        result[1] = list[3]
        result[2] = list[2]
        result[3] = list[1]
        result[4] = list[4]

    else:
        print("Error occured: rotation value not valid")
        quit()
            
    return result

def place(box):
    best_index = 2**50                                                              # start with high index
    
    current_height = get_convex_hull(placed_boxes)[2]                           # get the heigth of the convex hull until now
    if len(extreme_points) == 0:
        extreme_points.append((0,0,current_height))
    
    for rotation in xrange(0,6):                                                 #check every rotation
        box = rotate(box,rotation)
        for point_index in xrange(0,len(extreme_points)):                             # run over every extreme point 
            if best_index > get_index(box,extreme_points[point_index]):            # to check if the placement of the box in this point has a lower index
                if box[1] + extreme_points[point_index][0] < 1000 and box[2] + extreme_points[point_index][1] < 600: #within shelf?
                    if not check_collisions(box,extreme_points[point_index]):         #Does it collide with other boxes?
                        best_index = get_index(box,extreme_points[point_index])        # if it doesn't, update the index (lower it)
                        best_point_index = point_index                                    # and save the best point
    if best_index == 2**50:                                                           #failsafe: if no new best index is discovered over every rotation and point that does not collide
        extreme_points.append((0,0,current_height))                                    #place the box on top at origin
        best_point_index = -1
                        
    #covert point index to point (coordinates)
    best_point = extreme_points[best_point_index]
    
    #  add new extreme points
    extreme_points.append((extreme_points[best_point_index][0]+box[1] , extreme_points[best_point_index][1] , extreme_points[best_point_index][2]))
    extreme_points.append((extreme_points[best_point_index][0] , extreme_points[best_point_index][1]+box[2] , extreme_points[best_point_index][2]))
    extreme_points.append((extreme_points[best_point_index][0] , extreme_points[best_point_index][1] , extreme_points[best_point_index][2]+box[3]))
    
    # remove used extreme point from the list
    del extreme_points[best_point_index]
    
    # return box placement
    return [box,best_point]

def get_weight(placedset):
    sum = 0
    if len(placedset) == 0:
        pass
    else:
        for box in placedset:
            sum += box[0][4]    # add the weight of the box to the sum
    return sum

def check_collisions(box,point):
    collision = False
    for index in xrange(0,len(placed_boxes)):
        boundx = [placed_boxes[index][1][0],placed_boxes[index][1][0] + placed_boxes[index][0][1]]
        boundy = [placed_boxes[index][1][1],placed_boxes[index][1][1] + placed_boxes[index][0][2]]
        boundz = [placed_boxes[index][1][2],placed_boxes[index][1][2] + placed_boxes[index][0][3]]
    
        if (point[0] < boundx[1] and point[0]+box[1] > boundx[0]) and (point[1] < boundy[1] and point[1]+box[2] > boundy[0]) and (point[2] < boundz[1] and point[2]+box[3] > boundz[0]):
            collision = True
        
        if (point[0] < boundx[0] and point[0]+box[1] < boundx[1]) and (point[1] < boundy[0] and point[1]+box[2] < boundy[1]) and (point[2] < boundz[0] and point[2]+box[3] < boundz[1]):
            collision = True
                
    return collision
    
def get_convex_hull(placed_boxes):
    convex_L = 0
    convex_W = 0
    convex_H = 0
    
    for box in placed_boxes:
        if box[0][1]+box[1][0] > convex_L:                  # if placement+value of LENGTH does exceed current convex hull
            convex_L = box[0][1]+box[1][0]                  # coordinate+value is new convex hull-point
        else:                                               # if it does not exceed
            pass                                            # do nothing
        if box[0][2]+box[1][1] > convex_W:                  # if placement+value of WIDTH does exceed current convex hull
            convex_W = box[0][2]+box[1][1]                  # coordinate+value is new convex hull-point
        else:                                               # if it does not exceed
            pass                                            # do nothing
        if box[0][3]+box[1][2] > convex_H:                  # if placement+value of HEIGTH does exceed current convex hull
            convex_H = box[0][3]+box[1][2]                  # coordinate+value is new convex hull-point
        else:                                               # if it does not exceed
            pass                                            # do nothing
    return (convex_L,convex_W, convex_H)

def get_index(box,point):
    convex_hull = get_convex_hull(placed_boxes)
    
    index = max(convex_hull[0],box[1]+point[0]) * max(convex_hull[1],box[2]+point[1]) * max(convex_hull[2],box[3]+point[2])**3

    volume = box[1] * box[2] * box[3]
    for placed_box in placed_boxes:
        volume += (placed_box[0][1] * placed_box[0][2] * placed_box[0][3])
    index = float(index) / float(volume)

    return index
    
iter = 0

for trial in xrange(0,10000):                                                           # 10000 random interations
    placed_boxes = []
    extreme_points = [(0,0,0)]
    unplaced_boxes = initialize()
    iter += 1
    
    for each in xrange(0,length_of_file):
        index = random.randint(0,length_of_file-each-1)
        if get_weight(placed_boxes) + unplaced_boxes[index][4] < 50000:
            placed_boxes.append(place(unplaced_boxes[index]))
            del unplaced_boxes[index]
        else:
            continue

    convex_hull = get_convex_hull(placed_boxes)
    usedvolume = convex_hull[0]*convex_hull[1]*convex_hull[2]
    actualvolume = 0

    for box in placed_boxes:
        actualvolume += box[0][1]*box[0][2]*box[0][3]
    
    usage = (actualvolume*100)/usedvolume
    if usage > best_usage:
        best_usage = usage
        best_set = placed_boxes
    print("iteration %d" % (iter))
    print('boxes: %r \n' % (placed_boxes))
    print("usage: %d" % (usage))
    print("best usage: %d \n" % (best_usage))
    print("\n")
    
print("FINAL RESULT")
print(best_usage)
print(iter)
print('boxes: %r \n' % (best_set))
raw_input()
        
