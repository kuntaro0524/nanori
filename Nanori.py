# socket通信を行う
import sys,time
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

    def getStatus(self,ch):
        command = 'STS'+ch +'?' + self.crlf
        self.s.send(command.encode('utf-8'))
        recv=self.s.recv(1024).decode('utf-8')
        # "+"もしくは"-"でスプリットし、最後のカラムの値をintegerに変換する
        import re
        cols=re.split('[+-]',recv)
        former_buf=cols[-2]
        pulse = int(cols[-1])

        # former_buf は非常に複雑
        # 1文字目が　Rであらば 'remote', Lであれば 'local'
        if former_buf[0] == 'R':
            r_or_l = 'remote'
        elif former_buf[0] == 'L':
            r_or_l = 'local'
        # 3文字目が 'S' であれば 停止中、'P'であれば 'CW'方向に動いている
        # 'N' であれば 'CCW'方向に動いている
        if former_buf[2] == 'S':
            s_p_n = 'stop'
        elif former_buf[2] == 'P':
            s_p_n = 'cw'
        elif former_buf[2] == 'N':
            s_p_n = 'ccw'

        return r_or_l,s_p_n,pulse
    
    def getPosition(self, ch):
        r_or_l, s_p_n, pulse = self.getStatus(ch)
        return int(pulse)

    def switchSpeed(self, ch, speed):
        # speed が 'L', 'M', 'H' のいずれかであることを確認
        if speed not in ['L', 'M', 'H']:
            print('speed should be L, M, or H')
            return
        # ch　は　0-15 の整数であるがここでは１６進数に変換している
        # これは文字列として扱うためである
        # 1文字の16進数に変換する
        hex_char = format(int(ch), 'x')
        command = 'SPD'+ speed + hex_char + self.crlf
        print(command)
        self.s.send(command.encode('utf-8'))
        recv=self.s.recv(1024)
        print(recv)
    # end of setSpeed

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
        # これを入れておかないと最初の状態が「停止」になる
        # 多分、加速度の設定によっては時間は変わると思われるが今のところハードコードしておく
        time.sleep(0.1)
        # while 文で動いている間はLoopを回す
        i_count = 0
        # 軸の移動速度が遅すぎるとこのループで'stop'を検出することが至難
        # 1000pps以上であればモンダイは無かった
        while True:
            r_or_l, s_p_n, curr_pulse = self.getStatus(channel)
            print(s_p_n)
            if s_p_n == 'stop' and i_count != 0:
                print('stop')
                break
            time.sleep(0.1)
            i_count += 1
    # end of moveAbs

    def stopAxis(self, channel,option="rapid"):
        # optionは 'rapid' or 'smooth' のいずれかである
        if option not in ['rapid', 'smooth']:
            print('option should be rapid or smooth')
            return

        if option == 'rapid':
            command = 'ESTP' + channel + self.crlf
        else:
            command = 'SSTP' + channel + self.crlf
        
        self.s.send(command.encode('utf-8'))
        rec_mes = self.s.recv(1024) 
        print(rec_mes)
    # end of stopAxis

    def checkLS(self, channel):
        # hardware limit switch の状態を確認する
        # LS_16?H でハードウェアリミット
        command = 'LS_16?H' + self.crlf
        self.s.send(command.encode('utf-8'))
        recv=self.s.recv(1024)
        rec_mes = recv.decode('utf-8')
        print(rec_mes)
        # channel は intにして recvの前から channel文字目を解析する
        i_channnel = int(channel)
        status = int(rec_mes[i_channnel])
        print(type(status))
        if status == 1:
            print('CW limit!')
        elif status == 2:
            print('CCW limit!')
        elif status == 0:
            print('normal position')
        # 8 の意味がわかっていない
        # 軸を動かした直後に停止している状態であれば、0が返ってくる
        # 軸を動かす以前にリミットがついているかどうかを確認して踏んでいなければ 8 が返るらしい
        elif status == 8:
            print("not moved.")
        return status

    def setSpeed(self, ch, lmh, speed_value):
        # lmh が 'L', 'M', 'H' のいずれかであることを確認
        if lmh not in ['L', 'M', 'H']:
            print('speed should be L, M, or H')
            return
        # ch　は　0-15 の整数だが　１桁の16進数に変換する
        hex_char = format(int(ch), 'x')
        command = 'SPD'+ lmh + str(ch) + str(speed_value) + self.crlf
        print(command)
        self.s.send(command.encode('utf-8'))
        recv_mes = self.s.recv(1024).decode('utf-8')
        print(recv_mes)

    def getSpeed(self, ch, lmh):
        # lmh が 'L', 'M', 'H' のいずれかであることを確認
        if lmh not in ['L', 'M', 'H']:
            print('speed should be L, M, or H')
            return
        # ch　は　0-15 の整数だが　１桁の16進数に変換する
        hex_char = format(int(ch), 'x')
        command = 'SPD'+ lmh + '?' + str(ch) + self.crlf
        print("getSpeed")
        self.s.send(command.encode('utf-8'))
        recv_mes = self.s.recv(1024).decode('utf-8')
        speed = int(recv_mes)
        return speed

    def test(self):
        # nanori.get_version()
        target_pos=int(sys.argv[1])

        # target channel
        channel = '0'
        curr_pos = nanori.getPosition(channel)

        if curr_pos == target_pos:
            print('already in the target position')
        else:
            # current position
            nanori.moveAbs(channel,target_pos)
            for i in range(0,10):
                r_or_l, s_p_n, curr_pulse=nanori.getStatus(channel)
                print(curr_pulse)
                if s_p_n == 'stop':
                    print('stop')
                    break
                time.sleep(0.5)

nanori=Nanori()
# nanori.test()
#nanori.stopAxis('0')
# nanori.setSpeed('0','H')
# nanori.moveAbs('0',int(sys.argv[1]))
# print(nanori.checkLS('0'))
nanori.setSpeed('0','M',int(sys.argv[1]))
nanori.switchSpeed('0', 'M')
speed = nanori.getSpeed('0','L')
print(speed)
nanori.moveAbs('0',int(sys.argv[2]))