#! /usr/bin/env python

import sys
import numpy as np
from collections import defaultdict

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.gridspec as gridspec
#from typing import Any
from zmq_sub import zmq_sub_option, ZMQ_sub_buffered

print(matplotlib.__version__, matplotlib.__file__)


gPlot_data = defaultdict(list)  # type: defaultdict[Any, list]
global th

fig = plt.figure()
gs = gridspec.GridSpec(6, 1)

f_lim = (-200, 200)
t_lim = (-30, 30)



ax1 = fig.add_subplot(gs[0, :], xlim=(0, 5000), ylim=f_lim)
ax2 = fig.add_subplot(gs[1, :], xlim=(0, 5000), ylim=f_lim)
ax3 = fig.add_subplot(gs[2, :], xlim=(0, 5000), ylim=f_lim)
ax4 = fig.add_subplot(gs[3, :], xlim=(0, 5000), ylim=t_lim)
ax5 = fig.add_subplot(gs[4, :], xlim=(0, 5000), ylim=t_lim)
ax6 = fig.add_subplot(gs[5, :], xlim=(0, 5000), ylim=t_lim)

lin1, = ax1.plot([], [], lw=1, label='ati_fx')
lin11, = ax1.plot([], [], lw=1, label='iit_fx')

lin2, = ax2.plot([], [], lw=1, label='ati_fy')
lin22, = ax2.plot([], [], lw=1, label='iit_fy')

lin3, = ax3.plot([], [], lw=1, label='ati_fz')
lin33, = ax3.plot([], [], lw=1, label='iit_fz')

lin4, = ax4.plot([], [], lw=1, label='ati_tx')
lin44, = ax4.plot([], [], lw=1, label='iit_tx')

lin5, = ax5.plot([], [], lw=1, label='ati_ty')
lin55, = ax5.plot([], [], lw=1, label='iit_ty')

lin6, = ax6.plot([], [], lw=1, label='ati_tz')
lin66, = ax6.plot([], [], lw=1, label='iit_tz')

ax1.legend()
ax2.legend()
ax3.legend()
ax4.legend()
ax5.legend()
ax6.legend()

ati_lines = (
    #
    lin1, lin2, lin3, lin4, lin5, lin6,
    #
    lin11, lin22, lin33, lin44, lin55, lin66,
)
ati_names = (
    '_aforce_x',
    '_aforce_y',
    '_aforce_z',
    '_atorque_x',
    '_atorque_y',
    '_atorque_z',
    '_force_x',
    '_force_y',
    '_force_z',
    '_torque_x',
    '_torque_y',
    '_torque_z',
)

names = (
    '_force_x',
    '_force_y',
    '_force_z',
    '_torque_x',
    '_torque_y',
    '_torque_z',
)

lines = ati_lines
var_names = names

def init():
    
    for l in lines:
        l.set_data([], [])
    return lines


def animate(i):

    new_data = th.next()
    for k in gPlot_data.keys():
        gPlot_data[k].extend(new_data[k])
        gPlot_data[k] = gPlot_data[k][-5000:]

    x = np.arange(len(gPlot_data[th.key_prefix+'_force_x']))

    for name, lin in zip(var_names, lines):
        y = np.array(gPlot_data[th.key_prefix + name])
        lin.set_data(x, y)

    return lines


if __name__ == '__main__' :

    dict_opt = zmq_sub_option(sys.argv[1:])
    th = ZMQ_sub_buffered(**dict_opt)
    th.start()

    ani = animation.FuncAnimation(fig, animate, init_func=init, interval=100, blit=True)
    plt.show()
    
    print ("Set thread event ....")
    th.stop()
