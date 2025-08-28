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
        self.rel_button = QPushButton('R+')
        self.rel_button.clicked.connect(self.move_relative_plus)
        self.main_layout.addWidget(self.rel_button)
        self.rel_button = QPushButton('R-')
        self.rel_button.clicked.connect(self.move_relative_minus)
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

    def move_relative_plus(self):
        # 相対値移動の処理
        self.update_status('moving')
        # パルス値を取得
        target_pulse = int(self.target_pulse_input.text())
        print(f"Moving axis {self.axis_number} by {target_pulse} pulses")
        # current position
        current_position = self.nanori.getPosition(self.axis_number)
        # target position
        target_position = current_position + target_pulse
        print(f"Current position: {current_position}, Target position: {target_position}")
        print(f"Moving axis {self.axis_number} to {target_position}")
        self.nanori.moveAbs(self.axis_number, target_position)

    def move_relative_minus(self):
        # 相対値移動の処理
        self.update_status('moving')
        # パルス値を取得
        target_pulse = int(self.target_pulse_input.text())
        print(f"Moving axis {self.axis_number} by {target_pulse} pulses")
        # current position
        current_position = self.nanori.getPosition(self.axis_number)
        # target position
        target_position = current_position - target_pulse
        print(f"Current position: {current_position}, Target position: {target_position}")
        print(f"Moving axis {self.axis_number} to {target_position}")
        self.nanori.moveAbs(self.axis_number, target_position)

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

        # Update button と Cut button を横並びにする
        row = QHBoxLayout()
        row.setSpacing(8)  # ボタン間の余白（お好みで）

        # Update button 
        self.update_button = QPushButton('Update')
        self.update_button.clicked.connect(self.update_all)
        row.addWidget(self.update_button)
        self.update_button.setFixedWidth(100)

        # Cut button
        self.cut_button = QPushButton('Cut')
        self.cut_button.clicked.connect(self.cut_all)
        row.addWidget(self.cut_button)
        self.cut_button.setFixedWidth(100)

        # Cut timer box
        # このボックスに何秒間でカットするか入力する
        # ボタンのラベルを書く
        # default: 3 sec
        self.cut_timer_label = QLabel('Cut Timer')
        self.cut_timer_input = QLineEdit()
        self.cut_timer_input.setFixedWidth(200)
        self.cut_timer_input.setText('3')
        self.cut_timer_input.setFixedWidth(50)

        row.addWidget(self.cut_timer_label)
        row.addWidget(self.cut_timer_input)
        self.setLayout(self.main_layout)

        #self.main_layout.addWidget(self.cut_timer_input)

        # 右側を余白で押しのけたい場合（左寄せしたいとき）
        row.addStretch()

        # 縦並びレイアウトに「横一列」を追加
        self.main_layout.addLayout(row)
        # 画面が縦に広がったときでも上に張り付けたいなら、最後にストレッチ
        self.main_layout.addStretch()

        # --- ボタン行（横並び）を作る ---
        row = QHBoxLayout()
        row.setSpacing(8)  # ボタン間の余白（お好みで）
        
        # 左のボタン
        self.prep_film_chack_button = QPushButton('Prep Film Chack Upper')
        self.prep_film_chack_button.clicked.connect(self.prepFilmChackUpper)
        self.prep_film_chack_button.setFixedWidth(200)
        row.addWidget(self.prep_film_chack_button)
        
        # 右のボタン（コメントどおり「左ボタンの右」に並べる）
        self.self_prep_film_chack_hole1_button = QPushButton('Prep Film Chack Hole1')
        self.self_prep_film_chack_hole1_button.clicked.connect(self.prepHole1)
        self.self_prep_film_chack_hole1_button.setFixedWidth(200)
        row.addWidget(self.self_prep_film_chack_hole1_button)

        # prep cut button
        self.prep_cut_button = QPushButton('Prep Cut')
        self.prep_cut_button.clicked.connect(self.prepCut)
        self.prep_cut_button.setFixedWidth(200)
        row.addWidget(self.prep_cut_button)

        # down & release
        self.prep_cut_button = QPushButton('Down and release')
        self.prep_cut_button.clicked.connect(self.downAndRelease)
        self.prep_cut_button.setFixedWidth(200)
        row.addWidget(self.prep_cut_button)
        
        # 右側を余白で押しのけたい場合（左寄せしたいとき）
        row.addStretch()

        # 縦並びレイアウトに「横一列」を追加
        self.main_layout.addLayout(row)
        # 画面が縦に広がったときでも上に張り付けたいなら、最後にストレッチ
        self.main_layout.addStretch()

        ###############################3
        # Last line
        ###############################3
        # --- ボタン行（横並び）を作る ---
        row = QHBoxLayout()
        row.setSpacing(8)  # ボタン間の余白（お好みで）
        
        # plate setting position
        self.prep_cut_button = QPushButton('Plate setting position')
        self.prep_cut_button.clicked.connect(self.movePlatePosition)
        self.prep_cut_button.setFixedWidth(200)
        row.addWidget(self.prep_cut_button)

        # plate upper position
        self.prep_upper_position_button = QPushButton('Grab plate')
        self.prep_upper_position_button.clicked.connect(self.grabPlate)
        self.prep_upper_position_button.setFixedWidth(200)
        row.addWidget(self.prep_upper_position_button)

        # Cut & Release
        self.cut_and_release_button = QPushButton('Cut & Release')
        self.cut_and_release_button.clicked.connect(self.cut_and_release)
        self.cut_and_release_button.setFixedWidth(200)
        row.addWidget(self.cut_and_release_button)
        
        # 右側を余白で押しのけたい場合（左寄せしたいとき）
        row.addStretch()

        # 縦並びレイアウトに「横一列」を追加
        self.main_layout.addLayout(row)
        # 画面が縦に広がったときでも上に張り付けたいなら、最後にストレッチ
        self.main_layout.addStretch()

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

    def prepFilmChackUpper(self):
        # self.axi_dic = { 0: 'S-X', 1: 'S-Y1', 2: 'S-Y2', 3: 'S-Z1', 4: 'S-Z2', 5: 'F-X', 6: 'F-Y', 7: 'F-Z'}
        # F-X: 2800
        # F-Y: 23800
        # F-Z: 22000 (a bit gap between the film) <-> 10000)
        # Set the speed to High
        self.nanori_axis.switchSpeed(5, 'H')
        self.nanori_axis.switchSpeed(6, 'H')
        self.nanori_axis.switchSpeed(7, 'H')
        # move to the position
        self.nanori_axis.moveAbs(5, 2800)
        self.nanori_axis.moveAbs(6, 23800)
        self.nanori_axis.moveAbs(7, 10000)

    def prepHole1(self):
        # self.axi_dic = { 0: 'S-X', 1: 'S-Y1', 2: 'S-Y2', 3: 'S-Z1', 4: 'S-Z2', 5: 'F-X', 6: 'F-Y', 7: 'F-Z'}
        # F-X: 35600
        # F-Y: 24000
        # F-Z: 19200
        # Set the speed to High
        self.nanori_axis.switchSpeed(5, 'H')
        self.nanori_axis.switchSpeed(6, 'H')
        self.nanori_axis.switchSpeed(7, 'H')
        # move to the position
        self.nanori_axis.moveAbs(5, 35400)
        self.nanori_axis.moveAbs(6, 24160)
        self.nanori_axis.moveAbs(7, 18000)

    def downAndRelease(self):
        self.nanori_axis.moveAbs(7, 19000)
        time.sleep(3.0)
        # self.axi_dic = { 0: 'S-X', 1: 'S-Y1', 2: 'S-Y2', 3: 'S-Z1', 4: 'S-Z2', 5: 'F-X', 6: 'F-Y', 7: 'F-Z'}
        self.nanori_axis.moveAbs(7, 19700)
        # valve 1 'close'
        self.definitely_grub_release(grub_flag = False)
        # 5 sec wait
        time.sleep(3)
        self.nanori_axis.moveAbs(7, 10000)

    def prepCut(self):
        # self.axi_dic = { 0: 'S-X', 1: 'S-Y1', 2: 'S-Y2', 3: 'S-Z1', 4: 'S-Z2', 5: 'F-X', 6: 'F-Y', 7: 'F-Z'}
        # F-X: 2800
        # F-Y: 23800
        # F-Z: 22000
        # Set the speed to Middle
        self.nanori_axis.switchSpeed(5, 'H')
        self.nanori_axis.switchSpeed(6, 'H')
        self.nanori_axis.switchSpeed(7, 'H')
        # move to the position
        self.nanori_axis.moveAbs(5, 2800)
        self.nanori_axis.moveAbs(6, 23800)
        self.nanori_axis.moveAbs(7, 22000)
        # valve 1 'on'
        self.definitely_grub_release(grub_flag=True)

    def movePlatePosition(self):
        # self.axi_dic = { 0: 'S-X', 1: 'S-Y1', 2: 'S-Y2', 3: 'S-Z1', 4: 'S-Z2', 5: 'F-X', 6: 'F-Y', 7: 'F-Z'}
        # S-X: 5500
        # S-Y1: 19800
        # S-Z1: 24600
        # Set the speed to High
        self.nanori_axis.switchSpeed(0, 'H')
        self.nanori_axis.switchSpeed(1, 'H')
        self.nanori_axis.switchSpeed(3, 'H')
        # move to the position
        self.nanori_axis.moveAbs(0, 5500)
        self.nanori_axis.moveAbs(1, 19800)
        self.nanori_axis.moveAbs(3, 24000) # 1-2 mm  upper from the stage

    def grabPlate(self):
        # self.axi_dic = { 0: 'S-X', 1: 'S-Y1', 2: 'S-Y2', 3: 'S-Z1', 4: 'S-Z2', 5: 'F-X', 6: 'F-Y', 7: 'F-Z'}
        # S-X: 5500
        # S-Y1: 19800
        # S-Z1: 24600
        # Set the speed to High
        self.nanori_axis.switchSpeed(0, 'M')
        self.nanori_axis.switchSpeed(1, 'M')
        self.nanori_axis.switchSpeed(3, 'M')
        # move to the position
        self.nanori_axis.moveAbs(0, 5500)
        self.nanori_axis.moveAbs(1, 19800)
        self.nanori_axis.moveAbs(3, 24600) # 1-2 mm  upper from the stage
        # Balve 2,3 open
        self.nanori_valve.setHoldStatus(2, 'off')
        self.nanori_valve.setHoldStatus(4, 'off')
        # time sleep
        time.sleep(2)
        # S-Z1: 24000
        self.nanori_axis.moveAbs(3, 24000)

    # Grub the film and check the status
    # grub_flag == True -> Grub the film
    # grub_flag == False -> Release
    def definitely_grub_release(self, grub_flag):
        # n time out 
        n_time_out = 5
        # grub
        if grub_flag == True:
            for i in range(n_time_out):
                self.nanori_valve.setHoldStatus(0, 'off')
                time.sleep(0.5)
                is_hold = self.nanori_valve.getHoldStatus(0)
                if is_hold == False:
                    print("Grub is successful")
                    return True
                else:
                    print("Grub is not successful, try again")
                    time.sleep(1)
        else:
            for i in range(n_time_out):
                self.nanori_valve.setHoldStatus(0, 'on')
                time.sleep(0.5)
                is_hold = self.nanori_valve.getHoldStatus(0)
                if is_hold == True:
                    print("Release is successful")
                    return True
                else:
                    print("Release is not successful, try again")
                    time.sleep(1)

    def cut_and_release(self):
        self.prepFilmChackUpper()
        print(f"Cut & Release will be started.")
        time.sleep(10.0)
        self.prepCut()
        print("Prep cut is done.")
        time.sleep(10.0)
        print("Cutting will be started.")
        self.cut_all()
        print("Cutting is done.")
        time.sleep(5.0)
        print("Down & Release will be started.")
        self.prepFilmChackUpper()
        print("Prep film check upper is done.")
        time.sleep(5.0)
        print("Move to hole 1 position.")
        self.prepHole1()
        time.sleep(15.0)
        print("Prep hole 1 is done.")
        print("Down & Release will be started.")
        self.downAndRelease()

if __name__ == '__main__':
    nanori_axis = Nanori.Nanori('192.168.111.102',7777)
    nanori_valve = Nanori.Nanori('192.168.111.101',7777)
    app = QApplication(sys.argv)
    main_widget = NanoriControlWidget(nanori_axis, nanori_valve)
    main_widget.show()
    sys.exit(app.exec_())