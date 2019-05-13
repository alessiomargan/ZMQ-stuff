#! /usr/bin/env python

import zmq
import datetime
import threading
from collections import defaultdict

import numpy as np
from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import cm
import numpy as np

from zmq_sub import zmq_sub_option, ZMQ_sub, protobuf_cb

#SENS_ROWS = 16
#SENS_COLS =  8

SENS_ROWS = 3
SENS_COLS = 8


global running
running = True

def handle_close(evt) :
    global running
    running = False

fig = plt.figure()
fig.canvas.mpl_connect('close_event', handle_close)
ax = fig.add_subplot(111, projection='3d')
ax.set_aspect(0.5,'datalim')
#ax.auto_scale_xyz([0,16],[0,8],[0,255])
    
xs = np.linspace(0, SENS_ROWS, SENS_COLS)
ys = np.linspace(0, 20, SENS_ROWS)
X, Y = np.meshgrid(xs, ys)
Z = np.zeros(SENS_ROWS* SENS_COLS).reshape(SENS_ROWS, SENS_COLS)
#Z = np.zeros(128).reshape(16,8)
#Z = np.arange(0,255,2).reshape(SENS_ROWS,SENS_COLS)

wframe = ax.plot_surface(X, Y, Z, cmap=cm.coolwarm,
                         rstride=1, cstride=1,
                         linewidth=1,
                         antialiased=False)

#fig.colorbar(wframe, ax=ax, shrink=0.9) # aspect=10)




class ZMQ_sub_buffered(ZMQ_sub) :

    def __init__(self, **kwargs):

        self.elapsed = datetime.timedelta()
        self.buffered = defaultdict(list)
        self.forceXY = np.zeros(SENS_ROWS*SENS_COLS)
        self.lock_buff = threading.RLock()
        ZMQ_sub.__init__(self, **kwargs)
        self.callback = self.on_rx

    def on_rx(self, id, data, signals):
        ''' '''
        with self.lock_buff :
            id, data_dict = protobuf_cb(id, data, signals)
            # ('Foot_id_48',{'forceXY': [0,...,0])
            try : self.forceXY = data_dict['forceXY']
            except KeyError, e :
                print e
                running = False
                
        self.elapsed += self.msg_loop
        return id,data_dict

    def next(self):
        '''  '''
        data = []
        with self.lock_buff :
            data = self.forceXY
        return data


    

if __name__ == '__main__' :
    
    dict_opt = zmq_sub_option()
    th = ZMQ_sub_buffered(**dict_opt)
    
    while running :
    
        try :
            oldcol = wframe
        
            a = np.array([z if z > 5 else 0 for z in th.next()]).reshape(SENS_ROWS,SENS_COLS)
            Z = a.transpose()
            wframe = ax.plot_surface(X, Y, Z, cmap=cm.coolwarm,
                                     rstride=1, cstride=1, linewidth=0.2,
                                     antialiased=False)
            wframe = ax.plot_wireframe(X, Y, Z, rstride=1, cstride=1, linewidth=0.1)
            
            # Remove old line collection before drawing
            if oldcol is not None:
                ax.collections.remove(oldcol)
        
            plt.pause(.01)
        
        except Exception, e :
            print e
            running = False
    
    print "Set thread event ...."
    th.stop()
