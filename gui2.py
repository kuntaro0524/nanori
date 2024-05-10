import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QFrame
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox

class AxisControlWidget(QWidget):
    def __init__(self, axis_number):
        super().__init__()
        self.axis_number = axis_number
        self.initUI()

    def initUI(self):
        self.main_layout = QHBoxLayout()

        # 現在のパルス値を表示
        self.current_pulse_label = QLabel('1000 pls')
        self.main_layout.addWidget(self.current_pulse_label)

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

        self.setLayout(self.main_layout)

    def move_absolute(self):
        # 絶対値移動の処理
        self.update_status('moving')
        # 実際の移動処理はここに実装
        try:
            # もしも目標パルス値が入力されていない場合はエラーを表示
            if self.target_pulse_input.text() == '':
                self.status_display.setStyleSheet("background-color: red")
                return
            # 目標パルス値を取得
            target_pulse = int(self.target_pulse_input.text())
            print(target_pulse)
        except:
            # もしも目標パルス値が数値でないポップアップウインドウを表示
            # "数値を入力してください"というメッセージと OK ぼたんがある
            popup = QMessageBox()
            popup.setWindowTitle('Error')
            popup.setText('Please input a number')
            popup.exec_()
            return

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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_widget = QWidget()
    layout = QVBoxLayout(main_widget)
    # 複数の軸に対するウィジェットを作成
    for i in range(1, 9):  # 例として4軸まで示す
        axis_widget = AxisControlWidget(i)
        layout.addWidget(axis_widget)
    main_widget.setWindowTitle('Axis Control Interface')
    main_widget.show()
    sys.exit(app.exec_())
