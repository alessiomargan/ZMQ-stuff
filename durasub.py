#! /usr/bin/env python
# encoding: utf-8
#
#   Durable subscriber
#
#   Author: Jeremy Avnet (brainsik) <spork(dash)zmq(at)theory(dot)org>
#

import zmq
import datetime
import json
import pprint

context = zmq.Context()

# Connect our subscriber socket
subscriber = context.socket(zmq.SUB)
subscriber.setsockopt(zmq.IDENTITY, "Hello")
subscriber.setsockopt(zmq.SUBSCRIBE, "")
#subscriber.connect("tcp://10.255.32.48:5555")
#subscriber.connect("tcp://pc104-alessio.local:5555")
#subscriber.connect("tcp://amargan-desktop.local:5555")
#subscriber.connect("tcp://10.255.32.77:11224")
#subscriber.connect("tcp://10.255.32.77:5555")
subscriber.connect("tcp://nuc.local:9001")

print 'connected ...'
prev = datetime.datetime.now()

ids = dict()

try :
    # Get updates, expect random Ctrl-C death
    while True:

        #data = subscriber.recv()
        try : id,data = subscriber.recv_multipart()
        except ValueError : continue 

        try : ids[id]
        except KeyError : ids[id] = 0
        ids[id] += 1
        
        now = datetime.datetime.now()
        elap = now - prev
        prev = now

        print elap
        print id
        pprint.pprint(json.loads(data))
        #for c in data : print hex(ord(c)),
        print


except KeyboardInterrupt :
    pass

pprint.pprint(ids)
