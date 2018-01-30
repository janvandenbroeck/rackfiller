'''
Created on May 29, 2011

@author: baro
'''

import population
import time


if __name__ == '__main__':
    starttime = time.clock()
    pop = population.Population(20)
    
    for generation in range(250):
        report = pop.getReport()
        #print "best:%f, average:%f" % (report["best"],report["average"])
        '''
        print "best:{0},\n average:{1},\n bbO:{2},\n bbR:{3}\n\n".format(
                                                report["best"],
                                                report["average"],
                                                report["bestBoxOrder"],
                                                report["bestBoxRotation"])
        '''
        print "best:{0}, average:{1}".format(
                                                report["best"],
                                                report["average"])
        currenttime = time.clock()
        print "generation {0} took {1} seconds".format(generation+1,
                                                       currenttime-starttime)
        pop.evolve()
        print "mutated after {0}\n".format(time.clock()-currenttime)
        
    print "this took {0} seconds".format(time.clock()-starttime)