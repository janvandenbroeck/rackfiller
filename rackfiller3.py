import random
import csv
import datetime

class Box(object):
    'Box(id, x, y, z, weight)'

    __slots__ = ('id', 'x', 'y', 'z', 'weight')

    def __init__(self, id, x, y, z, weight):
        self.id = id
        self.x = x
        self.y = y
        self.z = z
        self.weight = weight

    def __iter__(self):
        yield self.id
        yield self.x
        yield self.y
        yield self.z
        yield self.weight

    def __repr__(self):
        return 'Box(id=%r, x=%r, y=%r, z=%r, weight=%r)' % \
            (self.id, self.x, self.y, self.z, self.weight)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and \
            self.x == other.x and self.y == other.y and self.z == other.z and self.weight == other.weight

class Point(object):
    'Point(x, y, z)'

    __slots__ = ('x', 'y', 'z')

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z

    def __repr__(self):
        return 'Point(x=%r, y=%r, z=%r)' % (self.x, self.y, self.z)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and \
            self.x == other.x and self.y == other.y and self.z == other.z

def load_file(filename):
    unplaced = []
    with open(filename) as f:
        for i, x, y, z, weight in csv.reader(f, delimiter="\t"):
            unplaced.append(Box(int(i), int(x), int(y), int(z), int(weight)))
    return unplaced

def rotate(box, rotation):

    if rotation == 0:
        return box
    elif rotation == 1:
        return Box(box.id, box.x, box.z, box.y, box.weight)
    elif rotation == 2:
        return Box(box.id, box.y, box.x, box.z, box.weight)
    elif rotation == 3:
        return Box(box.id, box.y, box.z, box.x, box.weight)
    elif rotation == 4:
        return Box(box.id, box.z, box.x, box.y, box.weight)
    elif rotation == 5:
        return Box(box.id, box.z, box.y, box.x, box.weight)
    else:
        raise AttributeError

def check_collisions(box, point, placed_boxes):
    for placed_box, placed_loc in placed_boxes:
        boundx = (placed_loc.x, placed_loc.x + placed_box.x)
        boundy = (placed_loc.y, placed_loc.y + placed_box.y)
        boundz = (placed_loc.z, placed_loc.z + placed_box.z)

        if (point.x < boundx[1] and point.x + box.x > boundx[0]) and \
           (point.y < boundy[1] and point.y + box.y > boundy[0]) and \
           (point.z < boundz[1] and point.z + box.z > boundz[0]):
            return True

    return False

def get_weight(placed_boxes):
    return sum([box.weight for box, _ in placed_boxes])

def get_convex_hull(placed_boxes):
    convex_X = 0
    convex_Y = 0
    convex_Z = 0

    for box, location in placed_boxes:
        if box.x + location.x > convex_X:
            convex_X = box.x + location.x
        if box.y + location.y > convex_Y:
            convex_Y = box.y + location.y
        if box.z + location.z > convex_Z:
            convex_Z = box.z + location.z

    return Point(convex_X, convex_Y, convex_Z)

def get_fill_rate(*placed_boxes):
    ''' Get fill rate for a list of box-placement tuples'''
    convex_hull = get_convex_hull(placed_boxes)

    hull_volume = convex_hull.x * convex_hull.y * convex_hull.z
    volume = sum([box.x * box.y * box.z for box, _ in placed_boxes])

    return volume / hull_volume

def place(box, placed_boxes, extreme_points, search_with_gravity=True):
    best_score = 0
    original_box = box

    # check every rotation
    for rotation in range(0,6):
        box = rotate(original_box, rotation)

        for point in extreme_points:
            all_points = []
            all_points.append(point)

            if search_with_gravity:
            # check for all points pulled towards origin
                if point.x != 0:
                    all_points.append(Point(0, point.y, point.z))
                    # iterate over ExistingBOXes
                    for ebox, loc in placed_boxes:
                        if ebox.x + loc.x < point.x:
                            all_points.append(Point(loc.x + ebox.x, point.y, point.z))

                if point.y != 0:
                    all_points.append(Point(point.x, 0, point.z))
                    for ebox, loc in placed_boxes:
                        if ebox.y + loc.y < point.y:
                            all_points.append(Point(point.x, loc.y + ebox.y, point.z))

                if point.z != 0:
                    all_points.append(Point(point.x, point.y, 0))
                    for ebox, loc in placed_boxes:
                        if ebox.z + loc.z < point.z:
                            all_points.append(Point(point.x, point.y, loc.z + ebox.z))

            for trial_point in all_points:
                if box.x + trial_point.x < 1000 and \
                   box.y + trial_point.y < 600 and  \
                   not check_collisions(box, trial_point, placed_boxes):
                    fill_rate = get_fill_rate((box, trial_point), *placed_boxes)

                    if best_score < fill_rate:
                        best_score = fill_rate
                        best_box = box
                        best_point = trial_point
                        best_extreme_point = point

    if best_score == 0:
        best_box = original_box
        height = get_convex_hull(placed_boxes).z
        extreme_points.append(Point(0, 0, height))
        best_point = best_extreme_point = Point(0, 0, height)

    #  add new extreme points
    extreme_points.append(Point(best_point.x + best_box.x, best_point.y, best_point.z))
    extreme_points.append(Point(best_point.x, best_point.y + best_box.y, best_point.z))
    extreme_points.append(Point(best_point.x, best_point.y, best_point.z + best_box.z))

    # remove used extreme point from the list
    extreme_points.remove(best_extreme_point)

    # return box placement
    return (best_box, best_point)

def run(sample):
    start = datetime.datetime.now()

    best_usage = 0
    best_set = []
    loaded_boxes = load_file('boxes.txt')

    for trial in range(sample):
        placed_boxes = []
        extreme_points = [Point(0, 0, 0)]
        boxes = loaded_boxes.copy()

        random.shuffle(boxes)

        for idx, box in enumerate(boxes):
            if get_weight(placed_boxes) + box.weight < 50000:
                placed_boxes.append(place(box, placed_boxes, extreme_points))

        usage = get_fill_rate(*placed_boxes)

        if usage > best_usage:
            print("iter {} best usage: {}".format(trial, usage))
            best_usage = usage
            best_set = placed_boxes

    print("best usage: {}".format(best_usage))
    print("nr boxes: {}".format(len(best_set)))
    for box, location in best_set:
        print(box, location)
    print("best dimensions: {}".format(get_convex_hull(best_set)))

    print("time: {}".format(datetime.datetime.now() - start))


if __name__ == '__main__':
    run(100000)
