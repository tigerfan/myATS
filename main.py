# main.py

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QSizePolicy, QPushButton
from ui_main import Ui_MainWindow
from logic import Logic

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 创建逻辑处理对象
        self.logic = Logic(self.ui)
        self.logic.setup()

        # 设置窗口大小策略
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # 设置按钮连接
        self.setup_buttons()

    def setup_buttons(self):
        # 设置设备按钮 (12台设备)
        for i in range(1, 13):
            button = self.ui.groupBox_2.findChild(QPushButton, f"pushButton_{i}")
            if button:
                button.clicked.connect(self.device_button_clicked)

        # 设置通道按钮 (18个通道)
        for i in range(1, 19):
            button = self.ui.groupBox.findChild(QPushButton, f"pushButton_{i}")
            if button:
                button.clicked.connect(self.channel_button_clicked)

        # 设置ALL按钮
        self.ui.pushButton_13.clicked.connect(self.logic.device_all_clicked)  # 设备ALL按钮
        self.ui.pushButton_19.clicked.connect(self.logic.channel_all_clicked)  # 通道ALL按钮

        # 设置START, STOP, RST按钮
        self.ui.pushButton_33.clicked.connect(self.logic.start_action)
        self.ui.pushButton_34.clicked.connect(self.logic.pause_resume_action)
        self.ui.pushButton_35.clicked.connect(self.logic.reset_action)

    def device_button_clicked(self):
        button = self.sender()
        self.logic.device_button_clicked(int(button.text()))

    def channel_button_clicked(self):
        button = self.sender()
        self.logic.channel_button_clicked(int(button.text()))

    def on_matrix_cell_clicked(self, row, column):
        print(f"Matrix cell clicked: row {row}, column {column}")  # 调试信息
        self.logic.display_channel_data(row + 1, column + 1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())