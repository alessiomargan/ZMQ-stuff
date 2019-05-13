#! /usr/bin/env python

import sys, os
import zmq
import json
import datetime
import time
import threading
import pprint
import numpy
import math
import itertools
from collections import defaultdict

#DEFAULT_ZMQ_PUB = 'tcp://localhost:5555'
#DEFAULT_ZMQ_PUB = 'tcp://carm-deb.local:6666'
#DEFAULT_ZMQ_PUB = 'tcp://10.255.32.203:6666'
#DEFAULT_ZMQ_PUB = 'tcp://ccub-deb-test.local:6666'
DEFAULT_ZMQ_PUB = 'tcp://localhost:6666'


# ##############################################################
#
try: 
    import glcube
    
    def vect_norm(v):
        return numpy.array(v) / numpy.linalg.norm(v)
    
    def draw_gl_init(*args):
        global th
        glcube.init_scene()
        th.callback = draw_gl_cube
        
    def draw_gl_cube(*args):
    
        id, data = args
    
        if id == 'uStrain':
            for k,v in data.items() :
                hiris_vars[k].append(v)
            
                
        elif id == 'hiris':
            for var_as_dict in data['_payload']['_vars'] :
                # !!! 
                hiris_vars[var_as_dict['name']].append(var_as_dict['_value']/1000.0)
    
            
        try :
            imu_quat = [hiris_vars[var_name][-1] for var_name in "quat_0 quat_1 quat_2 quat_3".split()]
            glcube.draw_scene_quat(imu_quat)
        except IndexError :
            # not enought data ....
            print '... retry'
    
        try :
            imu_mag =  [hiris_vars[var_name][-1] for var_name in "mag_x mag_y mag_z".split()]
            imu_gyr =  [hiris_vars[var_name][-1] for var_name in "gyr_x gyr_y gyr_z".split()]
            imu_acc =  [hiris_vars[var_name][-1] for var_name in "acc_x acc_y acc_z".split()]
        except IndexError :
            # not enought data ....
            print '... retry'
            return
        
        print "M:", vect_norm(imu_mag)
        print "G:", vect_norm(imu_gyr)
        print "A:", vect_norm(imu_acc)
        print "Q:", imu_quat
    
        
        #glcube.draw_scene_vect([(vect_norm(imu_mag),(1,0,1)),
        #                        (vect_norm(imu_gyr),(0,1,1)),
        #                        (vect_norm(imu_acc),(1,1,0))])
        
        #print datetime.datetime.now()

except ImportError, e : print e

# ##############################################################
    
hiris_vars = defaultdict(list)
    
def hiris_var_cb(*args):
    
    id, data = args
    #values = [var_as_dict['_value'] for var_as_dict in data['_payload']['_vars']]
    #print values
    #print numpy.linalg.norm(values)
    for var_as_dict in data['_payload']['_vars'] :
        hiris_vars[var_as_dict['name']].append(var_as_dict['_value'])
        
    [hiris_vars[var_name][:-1] for var_name in "quat_0 quat_1 quat_2 quat_3".split()]
   

    
if __name__ == '__main__' :
    
    import sys
    import csv
    from zmq_sub import ZMQ_sub, zmq_sub_option, cb_map

    cb_map['hiris_var_cb'] = hiris_var_cb
    
    dict_opt = zmq_sub_option()

    # one ctx for each process
    dict_opt['zmq_context'] = zmq.Context()
    
    th = ZMQ_sub(**dict_opt)
    th.start()
    try : sys.__stdin__.readline()
    except KeyboardInterrupt : pass
    print "Set thread event ...."
    th.stop()
        
    w = csv.writer(open('M.csv', 'w'),delimiter=' ')
    w.writerows(itertools.izip(hiris_vars['mag_x'],hiris_vars['mag_y'],hiris_vars['mag_z']))    
    w = csv.writer(open('G.csv', 'w'),delimiter=' ')
    w.writerows(itertools.izip(hiris_vars['gyr_x'],hiris_vars['gyr_y'],hiris_vars['gyr_z']))    
    w = csv.writer(open('A.csv', 'w'),delimiter=' ')
    w.writerows(itertools.izip(hiris_vars['acc_x'],hiris_vars['acc_y'],hiris_vars['acc_z']))    
        
