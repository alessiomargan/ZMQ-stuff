#! /usr/bin/env python
import sys
sys.path.append('/home/amargan/work/code/ecat_dev/ecat_master_advr/build/protobuf')
import ecat_pdo_pb2


import asyncio
import zmq
import zmq.asyncio
import argparse
import pprint
import json
from protobuf_to_dict import protobuf_to_dict
from contextlib import suppress

ctx = zmq.asyncio.Context()

# Define a global variable to store the last received data
last_received_data = None,None

def process_data(msg_id, data):
    rx_pdo = ecat_pdo_pb2.Ec_slave_pdo()
    rx_pdo.ParseFromString(data)
    pb_dict = protobuf_to_dict(rx_pdo)
    return msg_id,pb_dict

async def zsub(args):
    global last_recv_data
    subscriber = ctx.socket(zmq.SUB)
    uri = f"{args.protocol}://{args.address}:{args.port}"
    print("connect to", uri)
    subscriber.connect(uri)
    subscriber.subscribe(b"")
    with suppress(asyncio.CancelledError):
        while True:
            #data = await subscriber.recv_json()
            msg_id, data = await subscriber.recv_multipart()
            # store the last received data
            last_recv_data = process_data(msg_id, data)
            pprint.pprint(last_recv_data)
    subscriber.close()
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-P', '--protocol', type=str,
                        choices=['tcp', 'udp', 'inproc'], default='tcp')
    parser.add_argument('-a', '--address',  type=str, default='127.0.0.1')
    parser.add_argument('-p', '--port',     type=int)
    args = parser.parse_args()
    print(args)
    try:
        asyncio.run(zsub(args))
    except KeyboadInterrupt:
        print('Exiting ...')
        ctx.term()
