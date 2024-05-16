import sys
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QProgressBar

class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.progressBar = QProgressBar(self)
        self.progressBar.setMaximum(100)
        self.startBtn = QPushButton('Start', self)
        self.startBtn.clicked.connect(self.startProcess)

        layout = QVBoxLayout(self)
        layout.addWidget(self.progressBar)
        layout.addWidget(self.startBtn)

        self.setGeometry(300, 300, 280, 170)
        self.setWindowTitle('Process Events Example')

    def startProcess(self):
        for i in range(1, 101):
            time.sleep(0.1)  # ここで重い処理を想定
            self.progressBar.setValue(i)
            QApplication.processEvents()  # UIの更新を維持

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec_())

