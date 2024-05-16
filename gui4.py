import sys
import time
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QFrame
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox
import Nanori

class AxisControlWidget(QWidget):
    def __init__(self, nanori, axis_number):
        super().__init__()
        self.nanori = nanori
        self.axis_number = axis_number
        self.initUI()

    def initUI(self):
        self.main_layout = QHBoxLayout()

        # 現在のパルス値を表示
        value = nanori.getPosition(self.axis_number)
        self.current_pulse_label = QLabel(str(value))
        self.main_layout.addWidget(self.current_pulse_label)
        # 幅を固定する
        self.current_pulse_label.setFixedWidth(200)

        # 目標パルス値の入力
        self.target_pulse_input = QLineEdit()
        self.main_layout.addWidget(self.target_pulse_input)

        # ABSボタン（絶対値移動）
        self.abs_button = QPushButton('ABS')
        self.abs_button.clicked.connect(self.move_absolute)
        self.main_layout.addWidget(self.abs_button)

        # RELボタン（相対値移動）
        self.rel_button = QPushButton('REL')
        self.rel_button.clicked.connect(self.move_relative)
        self.main_layout.addWidget(self.rel_button)

        # STOPボタン（緊急停止）
        self.stop_button = QPushButton('STOP')
        self.stop_button.clicked.connect(self.stop_movement)
        self.main_layout.addWidget(self.stop_button)

        # 状態表示窓
        self.status_display = QFrame()
        self.status_display.setFrameShape(QFrame.StyledPanel)
        self.status_display.setFixedWidth(100)
        self.main_layout.addWidget(self.status_display)

        # トグルボタンを作成
        # High, Middle, Low の３つのスピードを切り替える
        # ボタンを１回押すと High になり、もう一度押すと Middle になり、さらに押すと Low になる
        # この繰り返し
        self.speed_button = QPushButton('Speed')
        self.i_speed_push = 0
        self.speed_button.clicked.connect(self.toggle_speed)
        # ボタンの幅は変更しない
        self.speed_button.setFixedWidth(100)
        self.main_layout.addWidget(self.speed_button)

        # トグルボタンを追加
        # Hold on/off をトグルするボタン
        self.hold_button = QPushButton('Hold')
        self.i_hold_push = 0
        self.hold_button.clicked.connect(self.toggle_hold)
        self.hold_button.setFixedWidth(100)
        self.main_layout.addWidget(self.hold_button)
        

        self.setLayout(self.main_layout)

    def checkValue(self):
        # boxの数値を取得
        value = self.target_pulse_input.text()
        print("VALUE:",value,":")
        # valueが空の場合
        if value == '':
            # popupを表示
            self.popup = QMessageBox()
            self.popup.setWindowTitle('Error')
            self.popup.setText('Please input a number')
            self.popup.exec_()
            return None
        # 数値かどうかを判定
        elif value.isdecimal():
            return int(value)
        else:
            # popupを表示
            self.popup = QMessageBox()
            self.popup.setWindowTitle('Error')
            self.popup.setText('Please input a number')
            self.popup.exec_()
            return None

    def toggle_speed(self):
        # ボタンを押した回数を数える
        self.i_speed_push += 1
        # 3種類のスピードを切り替える (High, Middle, Low)
        if self.i_speed_push % 3 == 1:
            self.speed_button.setText('High')
            self.nanori.switchSpeed(self.axis_number, 'H')
        elif self.i_speed_push % 3 == 2:
            self.speed_button.setText('Middle')
            self.nanori.switchSpeed(self.axis_number, 'M')
        else:
            self.speed_button.setText('Low')
            self.nanori.switchSpeed(self.axis_number, 'L')

        # 実際のスピード切り替え処理はここに実装

    def move_absolute(self):
        # もしも返り値がNoneであれば、処理を終了
        if self.checkValue() == None:
            return
        # 絶対値移動の処理
        self.update_status('moving')
        time.sleep(1.0)
        # 実際の移動処理はここに実装
        # 目標パルス値を取得
        target_pulse = int(self.target_pulse_input.text())
        self.nanori.moveAbs(self.axis_number, target_pulse)

    def move_relative(self):
        # 相対値移動の処理
        self.update_status('moving')
        # 実際の移動処理はここに実装

    def stop_movement(self):
        # 緊急停止の処理
        self.update_status('stopped')
        # 実際の停止処理はここに実装

    def update_status(self, status):
        # 状態に応じて色を変更
        if status == 'moving':
            self.status_display.setStyleSheet("background-color: orange")
        else:
            self.status_display.setStyleSheet("background-color: none")

    def toggle_hold(self):
        # ボタンを押した回数を数える
        self.i_hold_push += 1
        # 2種類のHoldを切り替える (Hold on, Hold off)
        if self.i_hold_push % 2 == 1:
            self.hold_button.setText('Hold on')
            self.nanori.setHoldStatus(self.axis_number, 'on')
        else:
            self.hold_button.setText('Hold off')
            self.nanori.setHoldStatus(self.axis_number, 'off')

class ValveControlWidget(QWidget):
    def __init__(self, nanori, valve_number):
        super().__init__()
        self.nanori = nanori
        # valve_number (1-5)
        self.valve_number = valve_number
        self.initUI()
        self.i_valve_push = 0

        # valve_number 1-5 に対応した軸のチャンネルは以下の通り
        # {1: 0, 2: 2, 3: 4, 4: 6, 5: 8}
        self.dic_valve_channel = {1: 0, 2: 2, 3: 4, 4: 6, 5: 8}

    def initUI(self):
        self.main_layout = QHBoxLayout()

        # ラベルを作成し、表示する
        self.valve_label = QLabel('valve'+str(self.valve_number))
        self.main_layout.addWidget(self.valve_label)

        # トグルボタンを作成
        self.toggle_button = QPushButton('open')
        self.toggle_button.clicked.connect(self.toggle_valve)
        self.main_layout.addWidget(self.toggle_button)

        self.setLayout(self.main_layout)

    def toggle_valve(self):
        # ボタンを押した回数を数える
        self.i_valve_push += 1
        # 2種類のスピードを切り替える (open, close)
        if self.i_valve_push % 2 == 1:
            self.toggle_button.setText('open')
            # channel は valve_number に対応するものを取得する
            channel = self.dic_valve_channel[self.valve_number]
            print("Channel:",channel)
            # バルブを開く
            self.nanori.setHoldStatus(channel, 'on')
            print("Switching valve open")
        else:
            self.toggle_button.setText('off')
            channel = self.dic_valve_channel[self.valve_number]
            print("Switching valve close")
            print("Channel:",channel)
            # バルブを閉じる
            self.nanori.setHoldStatus(channel, 'off')

# GUI全体を作成するクラス 
class NanoriControlWidget(QWidget):
    def __init__(self,nanori_instance):
        super().__init__()
        self.initUI()
        self.nanori = nanori_instance

    def initUI(self):
        self.main_layout = QVBoxLayout()

        # 複数の軸に対するウィジェットを作成
        for i in range(0, 4):  # 例として4軸まで示す
            axis_widget = AxisControlWidget(nanori,i)
            # current_pulse_labelに value を表示する
            self.main_layout.addWidget(axis_widget)

        # 新しいボタンを追加する
        # ボタンは全部で５つある
        # valve1-valve5 とする
        # Labelに valve1と表示し、横に open/close のトグルボタンを配置する
        # トグルボタンを押すと、open/close が切り替わる
        # この状態を保持する
        valve_number = [1,2,3,4,5]
        for i in valve_number:
            valve_widget = ValveControlWidget(nanori,i)
            self.main_layout.addWidget(valve_widget)

        self.setLayout(self.main_layout)

if __name__ == '__main__':
    nanori = Nanori.Nanori()
    app = QApplication(sys.argv)
    main_widget = NanoriControlWidget(nanori)
    main_widget.show()
    sys.exit(app.exec_())