#! /usr/bin/env python
import sys
sys.path.append('/home/amargan/work/code/ecat_dev/ecat_master_advr/build/protobuf')
import ecat_pdo_pb2


import asyncio
import zmq
import zmq.asyncio
import pprint
import json
from protobuf_to_dict import protobuf_to_dict

# Define a global variable to store the last received data
last_received_data = None,None

def process_data(msg_id, data):
    rx_pdo = ecat_pdo_pb2.Ec_slave_pdo()
    rx_pdo.ParseFromString(data)
    pb_dict = protobuf_to_dict(rx_pdo)
    last_received_data = msg_id,pb_dict
    return msg_id,pb_dict

#from utils import get_address
def get_address():
    protocol = "tcp"
    address = "127.0.0.1"
    port = 9601
    return f"{protocol}://{address}:{port}"

async def zsub():
    subscriber = zmq.asyncio.Context().socket(zmq.SUB)
    subscriber.connect(get_address())
    subscriber.subscribe(b"")

    while True:
        #data = await subscriber.recv_json()
        msg_id, data = await subscriber.recv_multipart()
        # Process data as needed
        msg_id, pb_dict = process_data(msg_id, data)
        pprint.pprint((msg_id, pb_dict))

        
if __name__ == '__main__':
    asyncio.run(zsub())