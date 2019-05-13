#! /usr/bin/env python3

import sys
import zmq
import threading
from multiprocessing import Process

loop = threading.Event() 

ZMQ_REQ_BROKER_PORT = 5559
ZMQ_REP_BROKER_PORT = 5560

zcontext = zmq.Context()
        
def zmq_rep_thread(id):
    zrep_sock = zcontext.socket(zmq.XREQ)
    zrep_sock.setsockopt_string(zmq.IDENTITY, id)
    zrep_sock.connect("tcp://*:5560")
    while not loop.is_set():
        try:
            message = zrep_sock.recv_multipart()
            print(id, "Received request: ", message)
            zrep_sock.send_multipart(["back", "", "World"])
            #zrep_sock.send("World")
        except zmq.ZMQError as e:
            print(e, id)
    zrep_sock.close()
    print('zmq_rep_thread .. exit')
    
    
def zmq_req_rep_queue(req_broker_port=ZMQ_REQ_BROKER_PORT,
                       rep_broker_port=ZMQ_REP_BROKER_PORT):

    # Prepare our context and sockets
    _context = zmq.Context()
    frontend = _context.socket(zmq.XREQ)
    frontend.setsockopt_string(zmq.IDENTITY, 'front')
    backend = _context.socket(zmq.XREQ)
    backend.setsockopt_string(zmq.IDENTITY, 'back')
    frontend.bind("tcp://*:5559")
    backend.bind("tcp://*:5560")
    
    #zmq.device(zmq.QUEUE, frontend, backend)
    
    # Initialize poll set
    poller = zmq.Poller()
    poller.register(frontend, zmq.POLLIN)
    poller.register(backend, zmq.POLLIN)
    
    print("Setup Broker Req:%d --> Rep:%d" % (req_broker_port,rep_broker_port))

    # Switch messages between sockets
    while True:
        try:
            items = dict(poller.poll())
        except:
            break # Interrupted
        
        if frontend in items:
            msg = frontend.recv_multipart()
            print('front2back', msg)
            #msg[0] = 'uno'
            backend.send_multipart(msg)
        if backend in items:
            msg = backend.recv_multipart()
            print('back2front', msg)            #msg[0] = 'culo'
            frontend.send_multipart(msg)
            
            
zbroker = Process(target=zmq_req_rep_queue, args=())
zbroker.start()


threading.Thread(target=zmq_rep_thread, args=('uno',)).start() 
threading.Thread(target=zmq_rep_thread, args=('due',)).start() 

sys.__stdin__.readline()
loop.set()
zcontext.term()
zbroker.terminate()
print('Exit')