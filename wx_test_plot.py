#! /usr/bin/env python3

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
gs = gridspec.GridSpec(2, 1)

buff_size = 5000

ax1 = fig.add_subplot(gs[0, :], xlim=(0, buff_size), ylim=(-0.5, 3))
ax2 = fig.add_subplot(gs[1, :], xlim=(0, buff_size), ylim=(-100, 3000))

lin1, = ax1.plot([], [], lw=1, label='fx')
lin2, = ax1.plot([], [], lw=1, label='fy')
lin3, = ax1.plot([], [], lw=1, label='fz')
lin4, = ax1.plot([], [], lw=1, label='tx')
lin5, = ax1.plot([], [], lw=1, label='ty')
lin6, = ax1.plot([], [], lw=1, label='tz')
lin7, = ax2.plot([], [], lw=1, label='rtt')

ax1.legend()

ati_lines = (
    #
    lin1, lin2, lin3, lin4, lin5, lin6, lin7
)

names = (
    '_force_x',
    '_force_y',
    '_force_z',
    '_torque_x',
    '_torque_y',
    '_torque_z',
    '_rtt',
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
        gPlot_data[k] = gPlot_data[k][-buff_size:]

    x = np.arange(len(gPlot_data[th.key_prefix+'_force_x']))

    for name, lin in zip(var_names, lines):
        y = np.array(gPlot_data[th.key_prefix + name])
        lin.set_data(x, y)

    return lines


if __name__ == '__main__':

    dict_opt = zmq_sub_option(sys.argv[1:])
    th = ZMQ_sub_buffered(**dict_opt)
    th.start()

    ani = animation.FuncAnimation(fig, animate, init_func=init, interval=100, blit=True)
    plt.show()
    
    print("Set thread event ....")
    th.stop()
