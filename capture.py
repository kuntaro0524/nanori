import zmq
import sys

context = zmq.Context()
socket = context.socket(zmq.REQ)
<<<<<<< HEAD
socket.connect("tcp://192.168.163.103:5555")
=======
socket.connect("tcp://10.178.163.104:5555")
>>>>>>> reflesh codes

# JSON
data = {
    "filename": sys.argv[1]
}

socket.send_json(data)
message = socket.recv_string()
<<<<<<< HEAD
print(message)
=======
print(message)
>>>>>>> reflesh codes
