import zmq
import sys
import CUI
import time

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://192.168.163.103:5555")

def get_image(filename):
    # JSON
    data = {
        "filename": filename
    }
    
    socket.send_json(data)
    message = socket.recv_string()
    print(message)


if __name__ == "__main__":
    cui = CUI.CUI()

    # capture horizontal
    hori_list=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    vert_list=[1, 2, 3, 4, 5, 6, 7]

    for hori in hori_list:
        for vert in vert_list:
            position_text = f"{hori}{vert}"
            print(f"Move to {position_text}")
            cui.moveto(position_text)
            time.sleep(10)
            filename = f"capture_{position_text}.png"
            get_image(filename)

    #cui.moveto()