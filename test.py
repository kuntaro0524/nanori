# socket通信を行う

import socket

# サーバーのIPアドレスとポート番号
server_ip = '10.10.122.178'
server_port = 7777

# ソケットの作成
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((server_ip, server_port))

# VERSIONの取得
sock.send(b'ABS0+10000')
# データの受信
# print(sock.recv(1024))

# print(data.decode('utf-8'))