import sys
import socket
import threading
import time
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QLineEdit, QApplication)
from PyQt5.QtCore import pyqtSignal, QObject

class CommunicationThread(QObject):
    pulse_updated = pyqtSignal(str)
    
    def __init__(self, ip, port):
        super().__init__()
        self.ip = ip
        self.port = port
        self.running = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.ip, self.port))
        
    def send_command(self, command):
        print("Sending command:", command)
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
        self.send_command(command)
        recv = self.receive_response()
        print("Received:", recv)
    
    def run(self):
        while self.running:
            print("RUNRUNRUNRUNRUNRUNRUR")
            command = "STS0?" + '\r\n'
            self.send_command(command)
            response = self.receive_response()
            self.pulse_updated.emit(response)
            time.sleep(1)

class MotorControl(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.comm_thread = CommunicationThread("10.10.122.178", 7777)
        self.comm_thread.pulse_updated.connect(self.update_pulse_display)
        self.thread = threading.Thread(target=self.comm_thread.run)
        self.thread.start()

    def initUI(self):
        self.move_amount = QLineEdit(self)
        self.move_amount.setPlaceholderText('Enter pulse amount')

        self.move_button = QPushButton('Move', self)
        self.move_button.clicked.connect(self.start_moving)

        self.stop_button = QPushButton('Stop', self)
        self.stop_button.clicked.connect(self.stop_moving)

        # self.pulse_label = QLabel('Current Pulse: 0', self)

        # パルスを表示する窓
        self.pulse_display = QLabel('Current Pulse: 0', self)

        hbox = QHBoxLayout()
        hbox.addWidget(self.move_button)
        hbox.addWidget(self.stop_button)

        vbox = QVBoxLayout()
        vbox.addWidget(self.move_amount)
        vbox.addLayout(hbox)
        vbox.addWidget(self.pulse_display)

        self.setLayout(vbox)
        self.setWindowTitle('Motor Control')
        self.show()

    def start_moving(self):
        amount = self.move_amount.text()
        if not amount.isdigit():
            self.pulse_display.setText('Invalid pulse amount')
            return

        command = f"ABS0{amount}"+'\r\n'
        print(command)
        self.comm_thread.send_command(command)

    def stop_moving(self):
        self.comm_thread.stop()

    def update_pulse_display(self, pulse_value):
        self.pulse_display.setText(f'Current Pulse: {pulse_value}')

    def closeEvent(self, event):
        self.comm_thread.stop()
        self.thread.join()
        self.comm_thread.socket.close()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MotorControl()
    sys.exit(app.exec_())

