# socket通信を行う
import socket

class Nanori:
    def __init__(self):
        # サーバーのIPアドレスとポート番号
        server_ip = '10.10.122.178'
        server_port = 7777
        
        # ソケットの作成
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((server_ip, server_port))

        self.crlf="\r\n"

    def check(self):
        self.s.send(b'ABS0+10000')
        self.s.send(b'ABS0+0')

    def get_version(self):
        # VERSIONの取得
        command = 'VER?' + self.crlf
        self.s.send(command.encode('utf-8'))
        recv=self.s.recv(1024)
        print(recv)
        # recv=self.s.recv(1024)
        # print(recv)

    def moveAbs(self, channel, abs_pulse):
        # abs_pulseが負の場合には文字列に'-'を追加
        if abs_pulse < 0:
            command = 'ABS' + str(channel) + str(abs_pulse)
        else: 
            command = 'ABS' + str(channel) + '+' + str(abs_pulse)
        final_command = command + self.crlf
        print(final_command)
        self.s.send(final_command.encode('utf-8'))
        rec_mess=self.s.recv(1024)
        print(rec_mess)
        # print("done")

nanori=Nanori()
# nanori.get_version()
import sys
pulse=int(sys.argv[1])
nanori.moveAbs(0,pulse)