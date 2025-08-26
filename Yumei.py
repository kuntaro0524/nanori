import sys
import time
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QFrame
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox
import Nanori

class AxisControlWidget(QWidget):
    def __init__(self, nanori_axis, axis_number):
        super().__init__()
        self.nanori = nanori_axis
        self.axis_number = axis_number

        # 軸情報について定義を辞書として
        self.axi_dic = { 0: 'S-X', 1: 'S-Y1', 2: 'S-Y2', 3: 'S-Z1', 4: 'S-Z2', 5: 'F-X', 6: 'F-Y', 7: 'F-Z'}
        # extract axis_name from self.axi_dic
        self.axis_name = self.axi_dic[self.axis_number]

        self.initUI()

    def initUI(self):
        self.main_layout = QHBoxLayout()
        # 軸名を表示する
        self.axis_label = QLabel(self.axis_name)
        # Font size is 32pts
        self.axis_label.setStyleSheet("font-size: 18pt")
        # set a fixed width to 150
        self.axis_label.setFixedWidth(50)
        self.main_layout.addWidget(self.axis_label)

        # 現在のパルス値を表示
        value = self.nanori.getPosition(self.axis_number)
        self.current_pulse_label = QLabel(str(value))
        # QLabel: light blue background
        # width is fixed to 300
        # text position is 'centered'
        self.current_pulse_label.setStyleSheet("background-color: lightblue")
        self.current_pulse_label.setAlignment(Qt.AlignCenter)
        self.current_pulse_label.setFixedWidth(300)
        self.main_layout.addWidget(self.current_pulse_label)
         
        # 幅を固定する
        self.current_pulse_label.setFixedWidth(200)

        # 目標パルス値の入力
        self.target_pulse_input = QLineEdit()
        # Fixed width to 200
        self.target_pulse_input.setFixedWidth(200)
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
        self.nanori.stopAxis(self.axis_number)
        # 停止後のパルス数を self.current_pulse_label に表示
        value = self.nanori.getPosition(self.axis_number)
        self.current_pulse_label.setText(str(value))

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
        # valve_number 1-5 に対応した軸のチャンネルは以下の通り
        # {1: 0, 2: 2, 3: 4, 4: 6, 5: 8}
        self.dic_valve_channel = {1: 0, 2: 2, 3: 4, 4: 6, 5: 8}
        # valve_number (1-5)
        self.valve_number = valve_number
        self.initUI()
        self.i_valve_push = 0

    def initUI(self):
        self.main_layout = QHBoxLayout()

        # ラベルを作成し、表示する
        self.valve_label = QLabel('valve'+str(self.valve_number))
        self.main_layout.addWidget(self.valve_label)

        # トグルボタンを作成
        self.toggle_button = QPushButton('open')
        # text size を 32pts に設定
        self.toggle_button.setStyleSheet("font-size: 16pt")
        self.toggle_button.clicked.connect(self.toggle_valve)
        self.main_layout.addWidget(self.toggle_button)
        self.toggle_button.setFixedWidth(100)
        self.toggle_button.setFixedHeight(25)

        # 吸着しているかどうかのステータスを表示するランプを追加
        # 吸着している場合は緑、吸着していない場合は赤
        # 吸着しているかどうかは、nanori.getHoldStatus(channel)で取得できる
        # channelはvalve_numberに対応するものを取得する
        channel = self.dic_valve_channel[self.valve_number]
        print("Channel:",channel)
        is_hold = self.nanori.getHoldStatus(channel)
        print("Is hold:",is_hold)

        self.lamp = QLabel()
        self.lamp.setFixedWidth(100)
        self.lamp.setFixedHeight(25)
        self.lamp.setAlignment(Qt.AlignCenter)

        if is_hold:
            self.lamp.setStyleSheet("background-color: green")
        else:
            self.lamp.setStyleSheet("background-color: red")

        self.main_layout.addWidget(self.lamp)
        self.setLayout(self.main_layout)

    def toggle_valve(self):
        # ボタンを押した回数を数える
        self.i_valve_push += 1
        # 2種類のスピードを切り替える (open, close)
        if self.i_valve_push % 2 == 1:
            self.toggle_button.setText('open')
            # 色も変更する
            self.toggle_button.setStyleSheet("background-color: red")
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
            self.toggle_button.setStyleSheet("background-color: green")

# GUI全体を作成するクラス 
class NanoriControlWidget(QWidget):
    def __init__(self,nanori_axis, nanori_valve):
        super().__init__()
        self.initUI()
        self.nanori_axis = nanori_axis
        self.nanori_valve = nanori_valve

    def initUI(self):
        self.main_layout = QVBoxLayout()

        # タブを追加する
        # self.tab_widget = QTabWidget()
        # self.main_layout.addWidget(self.tab_widget)

        # 複数の軸に対するウィジェットを作成
        for i in range(0, 8):  
            axis_widget = AxisControlWidget(nanori_axis,i)
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
            valve_widget = ValveControlWidget(nanori_valve,i)
            self.main_layout.addWidget(valve_widget)

        # Update button 
        self.update_button = QPushButton('Update')
        self.update_button.clicked.connect(self.update_all)
        self.main_layout.addWidget(self.update_button)

        # Cut button
        self.cut_button = QPushButton('Cut')
        self.cut_button.clicked.connect(self.cut_all)
        self.main_layout.addWidget(self.cut_button)
        
        # Cut timer box
        # このボックスに何秒間でカットするか入力する
        # ボタンのラベルを書く
        self.cut_timer_label = QLabel('Cut Timer')
        self.cut_timer_input = QLineEdit()
        self.cut_timer_input.setFixedWidth(200)
        self.main_layout.addWidget(self.cut_timer_input)
        self.setLayout(self.main_layout)

    def cut_all(self):
        # cut timer から秒数を取得
        cut_timer = float(self.cut_timer_input.text())
        print("Cut timer:",cut_timer)
        print("Cut button was pushed.")
        # reset ch11
        self.nanori_valve.setHoldStatus(11, 'on')
        time.sleep(0.5)
        self.nanori_valve.setHoldStatus(10, 'off')
        time.sleep(0.5)
        self.nanori_valve.setHoldStatus(10, 'on')

        time.sleep(cut_timer)
        print(self.nanori_valve.isLSon("CWLS",10))
        time.sleep(0.1)
        print(self.nanori_valve.isLSon("CCWLS",10))

        self.nanori_valve.setHoldStatus(11, 'off')
        time.sleep(0.5)
        self.nanori_valve.setHoldStatus(11, 'on')
        print(self.nanori_valve.isLSon("CCWLS",10))

    def update_all(self):
        # 全ての軸の現在のパルス値を更新する
        for i in range(0, 8):
            axis_widget = self.main_layout.itemAt(i).widget()
            value = self.nanori_axis.getPosition(i)
            axis_widget.current_pulse_label.setText(str(value))

        # 全てのバルブのステータスを更新する
        for i in range(8, 13):
            valve_widget = self.main_layout.itemAt(i).widget()
            channel = valve_widget.dic_valve_channel[valve_widget.valve_number]
            is_hold = self.nanori_valve.getHoldStatus(channel)
            if is_hold:
                valve_widget.lamp.setStyleSheet("background-color: green")
            else:
                valve_widget.lamp.setStyleSheet("background-color: red")

if __name__ == '__main__':
    nanori_axis = Nanori.Nanori('10.178.163.102',7777)
    nanori_valve = Nanori.Nanori('10.178.163.101',7777)
    app = QApplication(sys.argv)
    main_widget = NanoriControlWidget(nanori_axis, nanori_valve)
    main_widget.show()
    sys.exit(app.exec_())
