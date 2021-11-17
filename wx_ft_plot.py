#! /usr/bin/env python

import sys
import numpy as np
from collections import defaultdict

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.gridspec as gridspec

from zmq_sub import zmq_sub_option, ZMQ_sub_buffered

"""
('NoNe@Ft_id_696',
 {'fault': 1,
  'force_x': 0.8883124589920044,
  'force_y': 2.3079349994659424,
  'force_z': 0.01067500002682209,
  'rtt': 992,
  'torque_x': 1.3453549146652222,
  'torque_y': 1.1281949281692505,
  'torque_z': 1.000095009803772}
)
  
('ATI@Ft_id_255',
 {'aforce_x': 0.05375099927186966,
  'aforce_y': -0.06818100064992905,
  'aforce_z': -0.04397200047969818,
  'atorque_x': 0.0014440000522881746,
  'atorque_y': 2.700000004551839e-05,
  'atorque_z': -0.0006000000284984708,
  'force_x': 1.2506524324417114,
  'force_y': 1.2450100183486938,
  'force_z': 1.2424174547195435,
  'torque_x': 1.250195026397705,
  'torque_y': 1.2393674850463867,
  'torque_z': 1.2389099597930908}
)
"""

class LivePlot(object):

    def __init__(self, opt):

        dict_opt = zmq_sub_option(opt)
        self.th = ZMQ_sub_buffered(**dict_opt)

        self.ati = False
        self.num_axes = 3
        if "ATI" in dict_opt["key_prefix"]:
            self.ati = True
            self.num_axes = 5

        self.plot_data = defaultdict(list)  # type: defaultdict[Any, list]
        self.lines = dict()
        self.axes = dict()

        fig = plt.figure()
        gs = gridspec.GridSpec(self.num_axes, 1)

        self.x_dim = 10000

        self.axes["force"]  = fig.add_subplot(gs[0, :], xlim=(0, self.x_dim), ylim=(-1.3, 1.3))
        self.axes["torque"] = fig.add_subplot(gs[1, :], xlim=(0, self.x_dim), ylim=(-1.3, 1.3))
        if self.ati:
            self.axes["aforce"] = fig.add_subplot(gs[2, :], xlim=(0, self.x_dim), ylim=(-300, 300))
            self.axes["atorque"] = fig.add_subplot(gs[3, :], xlim=(0, self.x_dim), ylim=(-15, 15))
        else:
            self.axes["rtt"]    = fig.add_subplot(gs[2, :], xlim=(0, self.x_dim), ylim=(900, 2100))

        self.lines['_force_x'],  = self.axes["force"].plot([], [], lw=1, label='Fx')
        self.lines['_force_y'],  = self.axes["force"].plot([], [], lw=1, label='Fy')
        self.lines['_force_z'],  = self.axes["force"].plot([], [], lw=1, label='Fz')
        self.lines['_torque_x'], = self.axes["torque"].plot([], [], lw=1, label='Tx')
        self.lines['_torque_y'], = self.axes["torque"].plot([], [], lw=1, label='Ty')
        self.lines['_torque_z'], = self.axes["torque"].plot([], [], lw=1, label='Tz')
        if self.ati:
            self.lines['_aforce_x'],  = self.axes["aforce"].plot([], [], lw=1, label='Fx')
            self.lines['_aforce_y'],  = self.axes["aforce"].plot([], [], lw=1, label='Fy')
            self.lines['_aforce_z'],  = self.axes["aforce"].plot([], [], lw=1, label='Fz')
            self.lines['_atorque_x'], = self.axes["atorque"].plot([], [], lw=1, label='Tx')
            self.lines['_atorque_y'], = self.axes["atorque"].plot([], [], lw=1, label='Ty')
            self.lines['_atorque_z'], = self.axes["atorque"].plot([], [], lw=1, label='Tz')
        else:
            self.lines['_rtt'],      = self.axes["rtt"].plot([], [], lw=1, label='rtt')

        for ax in self.axes.values():
            ax.legend()
            ax.grid()

        self.ani = animation.FuncAnimation(fig, self.animate, interval=50, blit=True)
        self.th.start()
        self.show()

    def animate(self, i):
        new_data = self.th.next()

        for k in self.plot_data.keys():
            self.plot_data[k].extend(new_data[k])
            self.plot_data[k] = self.plot_data[k][-self.x_dim:]

        x = np.arange(len(self.plot_data[self.th.key_prefix+'_force_x']))

        for name, lin in self.lines.items():
            y = np.array(self.plot_data[self.th.key_prefix + name])
            lin.set_data(x, y)

            if len(y):
                ax = None
                if name in ('_force_x', '_force_y', '_force_z'):
                    ax = self.axes["force"]
                elif name in ('_torque_x', '_torque_y', '_torque_z'):
                    ax = self.axes["torque"]

                if 0 and ax:
                    mi, ma = ax.get_ylim()
                    ymin = y.min()
                    ymax = y.max()
                    #print(ymin, ymax, mi, ma)
                    ax.set_ylim(ymin - 0.1 * (ymax - ymin), ymax + 0.1 * (ymax - ymin))


        return self.lines.values()

    @staticmethod
    def show():
        plt.show()

    def stop(self):
        self.th.stop()


if __name__ == '__main__':

    #arg = "--zmq-pub-gen-host=com-exp.local --zmq-pub-gen-port=9696  --key=NoNe@Ft_id_696"
    #p = LivePlot(arg.split())
    p = LivePlot(sys.argv[1:])
    p.show()
    print("Set thread event ....")
    p.stop()
