#! /usr/bin/env python

import sys
import numpy as np
from collections import defaultdict

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.gridspec as gridspec
import seaborn as sns

sns.set()

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
        plt.tight_layout()
        gs = gridspec.GridSpec(self.num_axes, 1)

        self.x_dim = 10000

        ati_force_scale = (-200, 200)
        ati_torque_scale = (-15, 15)
        volt_scale = (-0.05, 0.05)
        use_volt = dict_opt["use_volt"]
        iit_force_scale = volt_scale if use_volt else ati_force_scale
        iit_torque_scale = volt_scale if use_volt else ati_torque_scale
        
        if self.ati:
            self.axes["force"]   = fig.add_subplot(gs[0, :], xlim=(0, self.x_dim), ylim=iit_force_scale)
            self.axes["torque"]  = fig.add_subplot(gs[2, :], xlim=(0, self.x_dim), ylim=iit_torque_scale)
            self.axes["aforce"]  = fig.add_subplot(gs[1, :], xlim=(0, self.x_dim), ylim=ati_force_scale)
            self.axes["atorque"] = fig.add_subplot(gs[3, :], xlim=(0, self.x_dim), ylim=ati_torque_scale)
        else:
            self.axes["force"]  = fig.add_subplot(gs[0, :], xlim=(0, self.x_dim), ylim=iit_force_scale)
            self.axes["torque"] = fig.add_subplot(gs[1, :], xlim=(0, self.x_dim), ylim=iit_torque_scale)
            self.axes["rtt"]    = fig.add_subplot(gs[2, :], xlim=(0, self.x_dim), ylim=(900, 2100))

        self.lines['_force_x'],  = self.axes["force"].plot([], [], lw=1, label='Fx')
        self.lines['_force_y'],  = self.axes["force"].plot([], [], lw=1, label='Fy')
        self.lines['_force_z'],  = self.axes["force"].plot([], [], lw=1, label='Fz')
        self.lines['_torque_x'], = self.axes["torque"].plot([], [], lw=1, label='Tx')
        self.lines['_torque_y'], = self.axes["torque"].plot([], [], lw=1, label='Ty')
        self.lines['_torque_z'], = self.axes["torque"].plot([], [], lw=1, label='Tz')
        if self.ati:
            self.lines['_aforce_x'],  = self.axes["aforce"].plot([], [], lw=1, label='Fx_a')
            self.lines['_aforce_y'],  = self.axes["aforce"].plot([], [], lw=1, label='Fy_a')
            self.lines['_aforce_z'],  = self.axes["aforce"].plot([], [], lw=1, label='Fz_a')
            self.lines['_atorque_x'], = self.axes["atorque"].plot([], [], lw=1, label='Tx_a')
            self.lines['_atorque_y'], = self.axes["atorque"].plot([], [], lw=1, label='Ty_a')
            self.lines['_atorque_z'], = self.axes["atorque"].plot([], [], lw=1, label='Tz_a')
        else:
            self.lines['_rtt'],      = self.axes["rtt"].plot([], [], lw=1, label='rtt')

        for ax in self.axes.values():
            ax.legend()
            ax.grid()
        # NOTE matplotlib animated plot wont update labels on axis using blit 
        self.ani = animation.FuncAnimation(fig, self.animate, interval=50, blit=False)
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
        #x = np.arange(len(self.plot_data[self.th.key_prefix+'_force_x']))
        
        min_F = max_F = min_T = max_T = 0
            
        for name, lin in self.lines.items():
            x = np.arange(len(self.plot_data[self.th.key_prefix+name]))
            y = np.array(self.plot_data[self.th.key_prefix + name])
            #print(f"{len(x)} {len(y)} {name}")
            lin.set_data(x, y)
            
            if len(y) :
                if name in ('_force_x', '_force_y', '_force_z'):
                    ax = self.axes["force"]
                    min_F = y.min() if min_F > y.min() else min_F
                    max_F = y.max() if max_F < y.max() else max_F
                elif name in ('_torque_x', '_torque_y', '_torque_z'):
                    ax = self.axes["torque"]
                    min_T = y.min() if min_T > y.min() else min_T
                    max_T = y.max() if max_T < y.max() else max_T
        
        self.axes["force"].set_ylim(min_F - 0.15 * (max_F - min_F), max_F + 0.15 * (max_F - min_F))
        self.axes["torque"].set_ylim(min_T - 0.15 * (max_T - min_T), max_T + 0.15 * (max_T - min_T))
        
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
