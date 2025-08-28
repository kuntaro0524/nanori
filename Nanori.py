# socket通信を行う
import sys,time,datetime
import socket

class Nanori:
    def __init__(self,address, port):
        # サーバーのIPアドレスとポート番号
        server_ip = address
        server_port = port

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

    # checking the LS status and wait for finishing
    def waitLSon(self, channel, which_switch="CW",timestep=0.1, timeout=10):
        # which_switch is either "CW" or "CCW"
        if which_switch not in ["CW", "CCW"]:
            print("which_switch should be CW or CCW")
            return

        def checkIf(flags):
            isHold, isHPLS, isCWLS, isCCWLS = flags
            if which_switch == "CW":
                return isCWLS
            elif which_switch == "CCW":
                return isCCWLS
            elif which_switch == "HOLD":
                return isHold
            elif which_switch == "HPLS":
                return isHPLS

        start_time = datetime.datetime.now()
        while(True):
            print("Checking channel=",channel)
            isIt = checkIf(self.checkLS(channel))
            if isIt:
                break
            curr_time = datetime.datetime.now()
            time.sleep(timestep)
            if (curr_time - start_time).seconds > timeout:
                print("timeout")
                break

    # hold on/off の状態を得る
    def getHoldStatus(self, ch):
        command = "HOLD"+"?"+str(ch)+self.crlf
        print(command)
        self.s.send(command.encode('utf-8'))
        recv=self.s.recv(1024).decode('utf-8')
        print("getHoldStatus [rec]=",recv)
        if "ON" in recv:
            return True
        else:
            return False

    # hold on/off の状態を変更する
    def setHoldStatus(self, ch, on_off):
        # on_off は 小文字に変換したとき 'on' or 'off' であることを確認
        komoji_char = on_off.lower()
        if komoji_char not in ['on', 'off']:
            print('on_off should be on or off')
            return
        else:
            switch = on_off.upper()
        # ch は 0-15 の整数であるが、１桁の16進数に変換する
        hex_char = format(int(ch), 'x').upper()
        command = "HOLD"+str(hex_char)+switch+self.crlf
        print("Execute:", command)
        self.s.send(command.encode('utf-8'))
        print("Sent")
        # スイッチしても、バッファは帰ってこない
        # recv=self.s.recv(1024)
        # print(recv)

    def getStatusCore(self,ch):
        print("getStatusCore!!")
        command = 'STS'+str(ch)+'?'+self.crlf
        print(command)
        self.s.send(command.encode('utf-8'))
        recv=self.s.recv(1024).decode('utf-8')
        print(recv)
        return recv
    
    def getStatus(self, ch):
        # ch は 0-15 の整数であるが、１桁の16進数に変換する
        hex_char = format(int(ch), 'x').upper()
        command = 'STS'+str(hex_char) +'?' + self.crlf
        print("getStatus.command=",command)
        self.s.send(command.encode('utf-8'))
        recv=self.s.recv(1024).decode('utf-8')
        print("getStatus [rec]=",recv)
        # "+"もしくは"-"でスプリットし、最後のカラムの値をintegerに変換する
        import re
        cols=re.split('[+-]',recv)
        # +- のどちらかなので + のときは +1 を、 - のときは -1 をかける
        pulse_input_sign = recv[len(cols[0])]
        print(f"pulse_input_sign={pulse_input_sign}")

        former_buf=cols[-2]
        if pulse_input_sign == '+':
            pulse = int(cols[-1])
        else:
            pulse = -1 * int(cols[-1])

        print("pulse=",pulse)

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

        # 4文字目を取得する（limit switchの状態を示す16進数）
        ch_limit_switch = former_buf[3]

        return r_or_l,s_p_n,pulse, ch_limit_switch 

    def getStatusOBS(self,ch):
        recv = self.getStatusCore(ch)
        print(">>>>>>>>><>>>>>>>>>>")
        print(recv)
        print("<<<<<<<<<<<<<<<<<<<<")
        # ５文字目までとｗをれ以降を分ける
        former_buf = recv[:6]
        latter_buf = recv[6:]

        # １最初の１文字がであればかける数値を -1 にする
        if former_buf[0] == '-':
            seihu = -1
        else:
            seihu = 1
        
        # latter_buf を数字として取り出す
        pulse = int(latter_buf) * seihu
        print("pulse value=",pulse)

        return 

    def isLSon(self, switch_type, ch):
        # ch は 1-15 の整数であるが、１桁の16進数に変換する
        hex_value = format(int(ch), 'x').upper()
        # switch type は
        # HOLD/HPLS/CCWLS/CWLS のいずれかである
        if switch_type not in ['HOLD', 'HPLS', 'CCWLS', 'CWLS']:
            print('switch type should be HOLD, HPLS, CCWLS, or CWLS')
            return

        def is_bit_set(hex_value, bit_position):
            # 16進数の値を10進数に変換
            decimal_value = int(hex_value, 16)
            # 指定されたビットが立っているかを判定
            return (decimal_value & (1 << bit_position)) != 0

        def checkBit(switch, hex_value):
            # bitの情報は
            # 0: holdの状態
            # 1: HPLS
            # 2: CCWLS
            # 3: CWLS 
            switch = switch.upper()
            print(f"switch={switch}")
            bit_dict = {"HOLD": 3, "HPLS": 2, "CCWLS": 1, "CWLS": 0}
            target_bit = bit_dict[switch]
            print(target_bit)
            is_set = is_bit_set(hex_value, target_bit)
            return is_set

        return(checkBit(switch_type, hex_value))
    # end of isLSon
    
    def getPosition(self, ch):
        r_or_l, s_p_n, pulse, ch_info = self.getStatus(ch)
        print(f" r_or_l={r_or_l}, s_p_n={s_p_n}, pulse={pulse}, ch_info={ch_info} ")
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
        print("moveAbs starts")
        # abs_pulseが負の場合には文字列に'-'を追加
        if abs_pulse < 0:
            command = 'ABS' + str(channel) + str(abs_pulse)
        else: 
            command = 'ABS' + str(channel) + '+' + str(abs_pulse)
        final_command = command + self.crlf
        print("moveAbs.Command=",final_command)
        self.s.send(final_command.encode('utf-8'))
        rec_mess=self.s.recv(1024)
        print("moveAbs.received:",rec_mess)
        # これを入れておかないと最初の状態が「停止」になる
        # 多分、加速度の設定によっては時間は変わると思われるが今のところハードコードしておく
        time.sleep(0.1)
        # while 文で動いている間はLoopを回す
        i_count = 0
        # 軸の移動速度が遅すぎるとこのループで'stop'を検出することが至難
        # 1000pps以上であればモンダイは無かった
        # while True:
        #     r_or_l, s_p_n, curr_pulse, chinfo = self.getStatus(channel)
        #     print(s_p_n)
        #     if s_p_n == 'stop' and i_count != 0:
        #         print('stop')
        #         break
        #     time.sleep(0.2)
        #     i_count += 1
    # end of moveAbs

    def stopAxis(self, channel,option="rapid"):
        # optionは 'rapid' or 'smooth' のいずれかである
        if option not in ['rapid', 'smooth']:
            print('option should be rapid or smooth')
            return

        # channelは整数で渡されている可能性があるが、１桁の16進数に変換する
        channel = format(int(channel), 'x')

        if option == 'rapid':
            command = 'ESTP' + channel + self.crlf
        else:
            command = 'SSTP' + channel + self.crlf
        
        self.s.send(command.encode('utf-8'))
        rec_mes = self.s.recv(1024) 
        print(rec_mes)
    # end of stopAxis

    def checkLS(self, channel):
        r_or_l, s_p_n, pulse, ch_limit_switch = self.getStatus(channel)
        print("Limit=",ch_limit_switch)
        isHold = self.isLSon('HOLD', ch_limit_switch)
        isHPLS = self.isLSon('HPLS', ch_limit_switch)
        isCWLS = self.isLSon('CWLS', ch_limit_switch)
        isCCWLS = self.isLSon('CCWLS', ch_limit_switch)

        return  isHold, isHPLS, isCWLS, isCCWLS
    
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
        else: # current position nanori.moveAbs(channel,target_pos)
            for i in range(0,10):
                r_or_l, s_p_n, curr_pulse=nanori.getStatus(channel)
                print(curr_pulse)
                if s_p_n == 'stop':
                    print('stop')
                    break
                time.sleep(0.5)

# mainが関数として存在していなければ以下を実行
if __name__ == '__main__':
    nanori=Nanori('192.168.163.101',7777)
    # nanori.test()
    #nanori.stopAxis('0')
    # nanori.setSpeed('0','H')
    # nanori.moveAbs('0',int(sys.argv[1]))
    # print(nanori.checkLS('0'))
    # nanori.setSpeed('0','M',int(sys.argv[1]))
    # nanori.switchSpeed('0', 'M')
    # speed = nanori.getSpeed('0','L')
    # print(speed)
    # nanori.moveAbs('0',int(sys.argv[2]))
    channel = sys.argv[1]
    curr_flag = nanori.getHoldStatus(channel)
    if curr_flag:
        print("current flag is on")
        nanori.setHoldStatus(channel,'off')
    else:
        nanori.setHoldStatus(channel,'on')
    print(nanori.getHoldStatus(channel))
    # for i in range(0,16):
        # 10進数のi を16進数に変換(1桁)
        # hex_char = format(i, 'x')
        # try:
            # print(nanori.getStatus(hex_char))
            # time.sleep(1)
        # except Exception as e:
            # print(e)
            # continue

    # nanori.checkLS(channel)
    # nanori.waitLSon(channel, which_switch="CW",timeout=10)
    # nanori.waitLSon(channel, which_switch="CCW",timeout=10,timestep=0.1)