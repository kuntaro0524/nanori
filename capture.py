import zmq
import sys

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://192.168.163.103:5555")

# JSON
data = {
    "filename": sys.argv[1]
}

socket.send_json(data)
message = socket.recv_string()
print(message)