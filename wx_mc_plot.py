#! /usr/bin/env python3
import sys
import numpy as np
from collections import defaultdict

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.gridspec as gridspec

from zmq_sub import zmq_sub_option, ZMQ_sub_buffered

"""
('NoNe@Motor_id_123',
 {'aux': 0.0,
  'board_temp': 41.0,
  'fault': 0,
  'link_pos': -0.12549510598182678,
  'link_vel': 0.0,
  'motor_pos': -0.1254965364933014,
  'motor_temp': 33.0,
  'motor_vel': 0.0,
  'op_idx_ack': 0,
  'rtt': 990,
  'temperature': 8489,
  'torque': -4.564897060394287})
"""


#lin10, = ax6.plot([], [], lw=2, label='p_err')
#lin11, = ax6.plot([], [], lw=2, label='v_err')


class LivePlot(object):

    def __init__(self, opt):

        dict_opt = zmq_sub_option(opt)
        self.th = ZMQ_sub_buffered(**dict_opt)

        self.plot_data = defaultdict(list)  # type: defaultdict[Any, list]
        self.lines = dict()
        self.axes = dict()

        fig = plt.figure()
        gs = gridspec.GridSpec(5, 3)

        self.x_dim = 10000

        self.axes["pos"] = fig.add_subplot(gs[0, :], xlim=(0, self.x_dim), ylim=(-1.5, 1.5))
        self.axes["vel"] = fig.add_subplot(gs[1, :], xlim=(0, self.x_dim), ylim=(-0.5, 0.5))
        self.axes["tor"] = fig.add_subplot(gs[3, :], xlim=(0, self.x_dim), ylim=(-5, 5))
        self.axes["rtt"] = fig.add_subplot(gs[4, 0], xlim=(0, self.x_dim), ylim=(900, 1100))
        self.axes["tmp"] = fig.add_subplot(gs[4, 1], xlim=(0, self.x_dim), ylim=(20, 90))
        self.axes["aux"] = fig.add_subplot(gs[2, :], xlim=(0, self.x_dim), ylim=(-15, 15))

        self.lines['_motor_pos'],  = self.axes["pos"].plot([], [], lw=1, label='motor_pos')
        self.lines['_link_pos'],   = self.axes["pos"].plot([], [], lw=1, label='link_pos')
        self.lines['_motor_vel'],  = self.axes["vel"].plot([], [], lw=1, label='motor_vel')
        self.lines['_link_vel'],   = self.axes["vel"].plot([], [], lw=1, label='link_vel')
        self.lines['_torque'],     = self.axes["tor"].plot([], [], lw=1, label='torque')
        self.lines['_rtt'],        = self.axes["rtt"].plot([], [], lw=1, label='rtt')
        self.lines['_motor_temp'], = self.axes["tmp"].plot([], [], lw=1, label='mT')
        self.lines['_board_temp'], = self.axes["tmp"].plot([], [], lw=1, label='bT')
        self.lines['_aux'],        = self.axes["aux"].plot([], [], lw=1, label='aux')

        for ax in self.axes.values():
            ax.legend()
            ax.grid()

        self.ani = animation.FuncAnimation(fig, self.animate, interval=50, blit=True)
        self.th.start()
        self.show()

    def animate(self, i):
        new_data = self.th.next()
        #for k in self.plot_data.keys():
        for k in new_data.keys():
            self.plot_data[k].extend(new_data[k])
            self.plot_data[k] = self.plot_data[k][-self.x_dim:]
        #print(self.plot_data.keys())
        #print(len(self.plot_data[self.th.key_prefix+'_force_x']))
        #x = np.arange(len(self.plot_data[self.th.key_prefix+'_motor_pos']))

        for name, lin in self.lines.items():
            x = np.arange(len(self.plot_data[self.th.key_prefix+name]))
            y = np.array(self.plot_data[self.th.key_prefix + name])
            #print(f"{len(x)} {len(y)} {name}")
            lin.set_data(x, y)
            min_ = max_ = 0
            if len(y):
                ax = None
                if name in ('_motor_vel', '_link_vel'):
                    ax = self.axes["vel"]
                if name in ('_motor_pos', '_link_pos'):
                    ax = self.axes["pos"]
                if name in ('_torque',):
                    ax = self.axes["tor"]
                if name in ('_aux',):
                    ax = self.axes["aux"]
                if ax:
                    min_ = y.min() if min_ > y.min() else min_
                    max_ = y.max() if max_ < y.max() else max_
                    ax.set_ylim(min_ - 0.15 * (max_ - min_), max_ + 0.15 * (max_ - min_))        

        return self.lines.values()

    @staticmethod
    def show():
        plt.show()

    def stop(self):
        self.th.stop()


if __name__ == '__main__':

    #arg = "--zmq-pub-gen-host=com-exp.local --zmq-pub-gen-port=9014  --key=NoNe@Motor_id_14"
    #p = LivePlot(arg.split())
    p = LivePlot(sys.argv[1:])
    p.show()
    print("Set thread event ....")
    p.stop()
