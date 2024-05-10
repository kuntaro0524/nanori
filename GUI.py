import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit

class AxisControlWidget(QWidget):
    def __init__(self, axis_number):
        super().__init__()
        self.axis_number = axis_number
        self.initUI()

    def initUI(self):
        # メインレイアウト
        self.main_layout = QVBoxLayout()

        # 軸の番号
        self.axis_label = QLabel(f'Axis {self.axis_number}')
        self.main_layout.addWidget(self.axis_label)

        # 増減ステップを設定する入力ボックス
        self.step_input = QLineEdit('1')
        self.main_layout.addWidget(self.step_input)

        # パルス制御レイアウト
        self.control_layout = QHBoxLayout()

        # 現在のパルス値を表示するラベル
        self.current_pulse_label = QLabel('Current Pulse: 0')
        self.control_layout.addWidget(self.current_pulse_label)

        # パルス値の減少ボタン
        self.decrease_button = QPushButton('-')
        self.decrease_button.clicked.connect(self.decrease_pulse)
        self.control_layout.addWidget(self.decrease_button)

        # パルス値を表示・設定するための入力ボックス
        self.pulse_input = QLineEdit('0')
        self.control_layout.addWidget(self.pulse_input)

        # パルス値の増加ボタン
        self.increase_button = QPushButton('+')
        self.increase_button.clicked.connect(self.increase_pulse)
        self.control_layout.addWidget(self.increase_button)

        # コントロールレイアウトをメインレイアウトに追加
        self.main_layout.addLayout(self.control_layout)
        self.setLayout(self.main_layout)

    def decrease_pulse(self):
        current_value = int(self.pulse_input.text())
        step_value = int(self.step_input.text())
        current_value -= step_value  # ステップ値に基づいてパルス値を減少
        self.pulse_input.setText(str(current_value))

    def increase_pulse(self):
        current_value = int(self.pulse_input.text())
        step_value = int(self.step_input.text())
        current_value += step_value  # ステップ値に基づいてパルス値を増加
        self.pulse_input.setText(str(current_value))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_widget = QWidget()
    layout = QVBoxLayout(main_widget)
    # 12軸すべてに対するウィジェットを作成
    for i in range(1, 13):
        axis_widget = AxisControlWidget(i)
        layout.addWidget(axis_widget)
    main_widget.setWindowTitle('Multi-Axis Pulse Control')
    main_widget.show()
    sys.exit(app.exec_())

