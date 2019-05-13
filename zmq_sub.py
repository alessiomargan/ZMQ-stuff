#! /usr/bin/python3

import threading
import datetime
import pprint
import zmq
import json
from collections import defaultdict
from optparse import OptionParser
from protobuf_to_dict import protobuf_to_dict

import sys
sys.path.append('/home/amargan/work/code/ecat_dev/ecat_master_advr/build/protobuf')
import ecat_pdo_pb2


def zmq_pub_gen(hostname, port_range):
    def gen():
        for e in port_range:
            yield 'tcp://%s:%d,' % (hostname, e)
    return "".join(gen())[:-1]


# DEFAULT_ZMQ_PUB = 'tcp://carm-deb.local:6666'
# DEFAULT_ZMQ_PUB = 'tcp://ccub-deb-test.local:6666'
# DEFAULT_ZMQ_PUB = 'tcp://localhost:%d'%CSTRUCT_PUB_PORT
# DEFAULT_ZMQ_PUB = 'tcp://wheezy-i386-test.local:%d'%CSTRUCT_PUB_PORT
# DEFAULT_ZMQ_PUB = 'tcp://localhost:5555'
# DEFAULT_ZMQ_PUB = 'ipc:///tmp/6969'
# DEFAULT_ZMQ_PUB = 'tcp://coman-linux.local:%d'%CSTRUCT_PUB_PORT
# DEFAULT_ZMQ_PUB = 'tcp://amargan-desktop.local:9601'
# DEFAULT_ZMQ_PUB = 'tcp://coman-disney.local:9001,tcp://coman-disney.local:9002,tcp://coman-disney.local:9003'
# DEFAULT_ZMQ_PUB = zmq_pub_gen('coman-disney.local', [9008])
# DEFAULT_ZMQ_PUB = zmq_pub_gen('coman-disney.local', range(9001,9038))
# DEFAULT_ZMQ_PUB = zmq_pub_gen('coman-disney.local', [9034,9035,9036,9037])
# DEFAULT_ZMQ_PUB = zmq_pub_gen('coman-disney.local', [9037])
DEFAULT_ZMQ_PUB = zmq_pub_gen('localhost', range(9000, 9100))
# DEFAULT_ZMQ_PUB = zmq_pub_gen('localhost', range(9801,9804))
# DEFAULT_ZMQ_PUB = zmq_pub_gen('com-exp.local', range(9500,9600))
# DEFAULT_ZMQ_PUB = zmq_pub_gen('com-exp.local', [9501,10103,10104])
# DEFAULT_ZMQ_PUB = zmq_pub_gen('com-exp.local', range(9671,9674))

POLLER_TIMEOUT = 1000


def default_cb(msg_id, data, signals):
    
    if len(signals):
        raise BaseException("signals filter NOT supported")
    pprint.pprint(msg_id, data)
    return msg_id, data


def json_cb(msg_id, data, signals):
    
    json_dict = json.loads(data)
    if len(signals):
        try:
            json_dict = {key: json_dict[key] for key in signals if key in json_dict.keys()}
        except KeyError:
            json_dict = {}
    pprint.pprint((msg_id, json_dict))
    return msg_id, json_dict


def protobuf_cb(msg_id, data, signals):
    
    def filter_dict(key, dict_to_filter):
        # type: (string, dict) -> dict
        if len(signals):
            _filter_dict = dict_to_filter[key]
            try:
                _filter_dict = {key: _filter_dict[key] for key in signals if key in _filter_dict.keys()}
            except KeyError:
                _filter_dict = {}
            return _filter_dict
        else:
            return pb_dict[key]

    rx_pdo = ecat_pdo_pb2.Ec_slave_pdo()
    rx_pdo.ParseFromString(data)
    pb_dict = protobuf_to_dict(rx_pdo)
    #print pb_dict
    
    if rx_pdo.type == rx_pdo.RX_XT_MOTOR:
        # motor pdo56 byte
        pb_dict = filter_dict('motor_xt_rx_pdo', pb_dict)

    elif rx_pdo.type == rx_pdo.RX_MOTOR:
        pb_dict = filter_dict('motor_rx_pdo', pb_dict)

    elif rx_pdo.type == rx_pdo.RX_FT6:
        pb_dict = filter_dict('ft6_rx_pdo', pb_dict)
        try:
            ati_dict = pb_dict['ft_ati_rx']
            pb_dict.update(ati_dict)
            pb_dict.pop('ft_ati_rx')
        except KeyError:
            pass

    elif rx_pdo.type == rx_pdo.RX_FOOT_SENS:
        pb_dict = filter_dict('footWalkman_rx_pdo', pb_dict)

    elif rx_pdo.type == rx_pdo.RX_SKIN_SENS:
        pb_dict = filter_dict('skin_rx_pdo', pb_dict)
        # a = np.array(pb_dict['forceXY'])
        # a = np.array([1 if z > 5 else 0 for z in pb_dict['forceXY']] )
        # b = np.reshape(a, (8, 3))
        # c = b.transpose()
        # print (c)
        
    elif rx_pdo.type == rx_pdo.RX_MC_HAND:
        pb_dict = filter_dict('mcHand_rx_pdo', pb_dict)

    elif rx_pdo.type == rx_pdo.RX_HERI_HAND:
        pb_dict = filter_dict('heriHand_rx_pdo', pb_dict)

    elif rx_pdo.type == rx_pdo.RX_POW_F28M36:
        pb_dict = filter_dict('powF28M36_rx_pdo', pb_dict)

    pprint.pprint((msg_id, pb_dict))
    return msg_id, pb_dict


def cstruct_cb(msg_id, data, signals):
    pass

'''    
def cstruct_cb(id,data):

    policy = 'Position|Velocity|Torque|PID_out|PID_err|Link_pos|Target_pos|TempTarget_pos'
    bcast_data = board_data_type.data_factory(policy, policy_maps.mc_policy_map) # bigLeg_policy_map)
    bcast_data.decode(data) 
    # do some scaling
    bcast_data.Position /= 1e2
    bcast_data.Target_pos /= 1e2
    bcast_data.TempTarget_pos /= 1e2
    
    data_dict = bcast_data.toDict(all_fields=False)
    #pprint.pprint((id, data_dict))
    return id, data_dict
'''

cb_map = {'default_cb': default_cb,
          'json_cb':    json_cb,
          'cstruct_cb': cstruct_cb,
          'protobuf_cb': protobuf_cb,
          }


class ZMQ_sub(threading.Thread):
    # read data from a zmq publisher '''
    
    def __init__(self, **kwargs):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()
        self.stop_event.clear()
        self.msg_id_ts = defaultdict(list)
        self.msg_loop = 0
        self.zmq_context = kwargs.get('zmq_context')
        self.zmq_pub = kwargs.get('zmq_pub')
        self.zmq_msg_sub = kwargs.get('zmq_msg_sub')
        self.signals = kwargs.get('signals')        
        self.callback = cb_map[kwargs.get('cb', 'default_cb')]
        
        assert self.zmq_context
        self.subscriber = self.zmq_context.socket(zmq.SUB)
        for msg in self.zmq_msg_sub:
            self.subscriber.setsockopt_string(zmq.SUBSCRIBE, msg)
            #self.subscriber.setsockopt_string(zmq.SUBSCRIBE, unicode(msg))
        for pub in self.zmq_pub:
            self.subscriber.connect(pub)
        print('Connect to Data publisher %s' % self.zmq_pub)

        # Initialize poll set
        self.poller = zmq.Poller()
        self.poller.register(self.subscriber, zmq.POLLIN)
        
        # start thread activity .... start by user !!!!
        # self.start()

    def run(self):
        # poll on sockets
        print("...start thread activity")
        start_time = datetime.datetime.now()
        previous = datetime.datetime.now()
        self.msg_loop = datetime.timedelta()
        
        while not self.stop_event.is_set():
            
            socks = dict(self.poller.poll(POLLER_TIMEOUT))

            if self.subscriber in socks and socks[self.subscriber] == zmq.POLLIN:
                now = datetime.datetime.now()
                self.msg_loop = now - previous
                previous = now
                try:
                    msg_id, data = self.subscriber.recv_multipart()
                    msg_id = msg_id.decode('utf-8')
                    self.msg_id_ts[id].append((self.msg_loop, now-start_time))
                except Exception as e:
                    print(e)
                    continue
                
                self.callback(msg_id, data, self.signals)
                
            else:
                print(datetime.datetime.now(), socks, ("poller timeout"))

        print("thread Exit ...")

    def stop(self):
        self.stop_event.set()


class ZMQ_sub_buffered(ZMQ_sub):

    def __init__(self, **kwargs):
        self.elapsed = datetime.timedelta()
        self.buffered = defaultdict(list)
        self.lock_buff = threading.RLock()
        ZMQ_sub.__init__(self, **kwargs)
        self.callback = self.on_rx
        self.key_prefix = kwargs.get('key_prefix')

    def on_rx(self, msg_id, data, signals):
        with self.lock_buff:
            # msg_id, data_dict = json_cb(msg_id, data, signals)
            msg_id, data_dict = protobuf_cb(msg_id, data, signals)
            self.buffered[msg_id].append(data_dict)
        self.elapsed += self.msg_loop
        return msg_id, data_dict

    def next(self):
        data = defaultdict(list)
        with self.lock_buff:
            for msg_id in self.buffered.keys():
                print(msg_id, len(self.buffered[msg_id]))
                for d in self.buffered[msg_id]:
                    for key, v in d.items():
                        data[msg_id+'_'+key].append(v)
            # clean buffered data
            self.buffered = defaultdict(list)
        return data


def zmq_sub_option(args):
    
    parser = OptionParser()
    parser.add_option("--zmq-pub", action="store", type="string", dest="zmq_pub", default=DEFAULT_ZMQ_PUB)
    parser.add_option("--zmq-msg-sub", action="store", type="string", dest="zmq_msg_sub", default="")
    parser.add_option("--zmq-pub-gen-host", action="store", type="string", dest="zmq_pub_gen_host", default="")
    parser.add_option("--zmq-pub-gen-port", action="store", type="string", dest="zmq_pub_gen_port", default="")
    parser.add_option("--signals", action="store", type="string", dest="signals", default="")
    parser.add_option("--cb", action="store", type="string", dest="cb", default="protobuf_cb")
    # used in wx_animation
    parser.add_option("--key", action="store", type="string", dest="key_prefix", default="")
    (options, args) = parser.parse_args(args=args)
    dict_opt = vars(options)

    # one ctx for each process
    dict_opt['zmq_context'] = zmq.Context()
    gen_pub_zmq = zmq_pub_gen(dict_opt['zmq_pub_gen_host'],
                              [int(x) for x in dict_opt['zmq_pub_gen_port'].split(',')
                               if len(dict_opt['zmq_pub_gen_port'])])
    print(gen_pub_zmq)
    if len(gen_pub_zmq):
        dict_opt['zmq_pub'] = gen_pub_zmq
    dict_opt['zmq_pub'] = dict_opt['zmq_pub'].split(',')
    dict_opt['zmq_msg_sub'] = dict_opt['zmq_msg_sub'].split(',')
    dict_opt['signals'] = dict_opt['signals'].split(',') if len(dict_opt['signals']) else []   
    
    return dict_opt
    
    
if __name__ == '__main__' :
    
    import sys
    import csv 
    import operator
    
    opts = zmq_sub_option(sys.argv[1:])
    
    th = ZMQ_sub(**opts)
    th.start()
    try:
        sys.__stdin__.readline()
    except KeyboardInterrupt:
        pass
    print("Set thread event ....")
    th.stop()
    th.join(1.0)

    for k in th.msg_id_ts.keys():
        pprint.pprint((k, th.msg_id_ts[k][:10]))
        # print reduce(operator.add ,(ts for ts in th.msg_id_ts[k]))
