from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QLineEdit, QApplication)
from PyQt5.QtCore import QThread, pyqtSignal, QObject
import sys
import socket
import threading
import time

class CommunicationThread(QObject):
    pulse_updated = pyqtSignal(int, str)  # 軸番号とパルス値を送信するシグナル
    
    def __init__(self, ip, port):
        super().__init__()
        self.ip = ip
        self.port = port
        self.running = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.ip, self.port))
        self.crlf="\r\n"

    def getStatus(self,ch):
        command = 'STS'+str(ch) +'?' + self.crlf
        self.socket.sendall(command.encode('utf-8'))
        recv=self.socket.recv(1024).decode('utf-8')
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

        # 4文字目を取得する（limit switchの状態を示す16進数）
        ch_limit_switch = former_buf[3]

        return r_or_l,s_p_n,pulse, ch_limit_switch
    # end of getStatus
        
    def send_command(self, command):
        try:
            self.socket.sendall(command.encode())
        except Exception as e:
            print(f"Error sending command: {e}")
    
    def receive_response(self):
        try:
            return self.socket.recv(1024).decode()
        except Exception as e:
            print(f"Error receiving response: {e}")
            return ""
    
    def stop(self):
        self.running = False
        command = "SSTP0" + '\r\n'
        print("PUSSSSSSSSSSSSSSSSSSDF")
        self.send_command("SSTP")
    
    def run(self):
        while self.running:
            for axis in range(4):  # ここで軸の数を指定
                response = self.receive_response()
                r_or_l, s_p_n, pulse, ch_limit_switch = self.getStatus(axis)
                pulse_char = str(pulse)
                print("RUN:",axis,pulse)
                self.pulse_updated.emit(axis, pulse_char)
                time.sleep(0.1)

class MotorControl(QWidget):
    def __init__(self):
        super().__init__()
        self.previous_pulse_values = {}  # 各軸の前回のパルス値を保存する辞書を初期化
        self.initUI()
        self.comm_thread = CommunicationThread("10.10.122.178", 7777)
        self.comm_thread.pulse_updated.connect(self.update_pulse_display)
        self.thread = threading.Thread(target=self.comm_thread.run)
        self.thread.start()

    def initUI(self):
        self.axis_controls = {}

        layout = QVBoxLayout()

        for axis in range(4):  # ここで軸の数を指定
            axis_layout = QVBoxLayout()
            axis_label = QLabel(f'Axis {axis}', self)
            move_amount = QLineEdit(self)
            move_amount.setPlaceholderText('Enter pulse amount')

            move_button = QPushButton('Move', self)
            move_button.clicked.connect(lambda _, a=axis: self.start_moving(a))

            stop_button = QPushButton('Stop', self)
            stop_button.clicked.connect(lambda _, a=axis: self.stop_moving(a))

            pulse_label = QLabel('Current Pulse: 0', self)

            hbox = QHBoxLayout()
            hbox.addWidget(move_button)
            hbox.addWidget(stop_button)

            axis_layout.addWidget(axis_label)
            axis_layout.addWidget(move_amount)
            axis_layout.addLayout(hbox)
            axis_layout.addWidget(pulse_label)

            layout.addLayout(axis_layout)

            self.axis_controls[axis] = {
                'move_amount': move_amount,
                'pulse_label': pulse_label
            }

            self.previous_pulse_values[axis] = None  # 初期値はNone

        self.setLayout(layout)
        self.setWindowTitle('Motor Control')
        self.show()

    def start_moving(self, axis):
        amount = self.axis_controls[axis]['move_amount'].text()
        if not amount.isdigit():
            self.axis_controls[axis]['pulse_label'].setText('Invalid pulse amount')
            return

        command = f"ABS{axis}+{amount}" + '\r\n'
        self.comm_thread.send_command(command)

    def stop_moving(self, axis):
        command = f"ESTP{axis}" + '\r\n'
        self.comm_thread.send_command(command)

    def update_pulse_display(self, axis, pulse_value):
        print("updated", axis, pulse_value)
        if self.previous_pulse_values[axis] != pulse_value:
            print("Motor moved:", axis, pulse_value)
            self.axis_controls[axis]['pulse_label'].setText(f'Current Pulse: {pulse_value}')
            self.previous_pulse_values[axis] = pulse_value

    def closeEvent(self, event):
        self.comm_thread.stop()
        self.thread.join()
        self.comm_thread.socket.close()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MotorControl()
    sys.exit(app.exec_())