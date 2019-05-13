import zmq

#import ec_boards_base_input_pb2 as repl_cmd
#from protobuf_to_dict import protobuf_to_dict, dict_to_protobuf

#  Prepare our context and sockets
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

#  Do 10 requests, waiting each time for a response
for request in range(0, 100):
    socket.send(b"Hello")
    message = socket.recv()
    print("Received reply %s [%s]" % (request, message))

