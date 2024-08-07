# -*- coding: utf-8 -*-

# ui_main.py

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect,
                            QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
                           QFont, QFontDatabase, QGradient, QIcon,
                           QImage, QKeySequence, QLinearGradient, QPainter,
                           QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCalendarWidget, QGridLayout,
                               QGroupBox, QHBoxLayout, QMainWindow, QMenuBar,
                               QProgressBar, QPushButton, QSizePolicy, QStatusBar,
                               QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QTextEdit)
from PySide6.QtCharts import QChartView


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1631, 889)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")

        self.groupBox_3 = QGroupBox(self.centralwidget)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.groupBox_3.setGeometry(QRect(20, 40, 621, 371))

        self.groupBox = QGroupBox(self.groupBox_3)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(20, 150, 581, 91))
        self.layoutWidget = QWidget(self.groupBox)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(10, 20, 565, 56))
        self.gridLayout_2 = QGridLayout(self.layoutWidget)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")

        # 创建18个通道按钮
        for i in range(1, 19):
            button = QPushButton(self.layoutWidget)
            button.setObjectName(f"pushButton_{i}")
            button.setText(str(i))
            row = (i - 1) // 6
            col = (i - 1) % 6
            self.gridLayout.addWidget(button, row, col, 1, 1)

        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.pushButton_19 = QPushButton(self.layoutWidget)
        self.pushButton_19.setObjectName(u"pushButton_19")
        self.gridLayout_2.addWidget(self.pushButton_19, 0, 1, 1, 1)

        self.groupBox_2 = QGroupBox(self.groupBox_3)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setGeometry(QRect(20, 20, 581, 111))
        self.layoutWidget1 = QWidget(self.groupBox_2)
        self.layoutWidget1.setObjectName(u"layoutWidget1")
        self.layoutWidget1.setGeometry(QRect(10, 20, 565, 85))
        self.horizontalLayout = QHBoxLayout(self.layoutWidget1)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName(u"gridLayout_3")

        # 创建12个设备按钮
        for i in range(1, 13):
            button = QPushButton(self.layoutWidget1)
            button.setObjectName(f"pushButton_{i}")
            button.setText(str(i))
            row = (i - 1) // 4
            col = (i - 1) % 4
            self.gridLayout_3.addWidget(button, row, col, 1, 1)

        self.horizontalLayout.addLayout(self.gridLayout_3)

        self.pushButton_13 = QPushButton(self.layoutWidget1)
        self.pushButton_13.setObjectName(u"pushButton_13")
        self.horizontalLayout.addWidget(self.pushButton_13)

        self.progressBar = QProgressBar(self.groupBox_3)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setGeometry(QRect(20, 330, 591, 23))
        self.progressBar.setValue(24)
        self.layoutWidget2 = QWidget(self.groupBox_3)
        self.layoutWidget2.setObjectName(u"layoutWidget2")
        self.layoutWidget2.setGeometry(QRect(20, 260, 239, 25))
        self.horizontalLayout_2 = QHBoxLayout(self.layoutWidget2)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.pushButton_33 = QPushButton(self.layoutWidget2)
        self.pushButton_33.setObjectName(u"pushButton_33")
        self.horizontalLayout_2.addWidget(self.pushButton_33)
        self.pushButton_34 = QPushButton(self.layoutWidget2)
        self.pushButton_34.setObjectName(u"pushButton_34")
        self.horizontalLayout_2.addWidget(self.pushButton_34)
        self.pushButton_35 = QPushButton(self.layoutWidget2)
        self.pushButton_35.setObjectName(u"pushButton_35")
        self.horizontalLayout_2.addWidget(self.pushButton_35)

        self.chartView = QChartView(self.centralwidget)
        self.chartView.setObjectName(u"chartView")
        self.chartView.setGeometry(QRect(760, 460, 751, 261))
        self.chartView.setRenderHint(QPainter.Antialiasing)  # 添加这行以提高渲染质量
        self.calendarWidget = QCalendarWidget(self.centralwidget)
        self.calendarWidget.setObjectName(u"calendarWidget")
        self.calendarWidget.setGeometry(QRect(110, 440, 391, 301))

        self.statusTextEdit = QTextEdit(self.centralwidget)
        self.statusTextEdit.setObjectName(u"statusTextEdit")
        self.statusTextEdit.setGeometry(QRect(110, 760, 391, 100))  # 调整位置和大小
        self.statusTextEdit.setReadOnly(True)  # 设置为只读

        self.colorMatrix = QTableWidget(self.centralwidget)
        self.colorMatrix.setObjectName(u"colorMatrix")
        self.colorMatrix.setGeometry(QRect(710, 70, 751, 281))
        self.colorMatrix.setRowCount(12)
        self.colorMatrix.setColumnCount(18)
        self.colorMatrix.horizontalHeader().setVisible(False)
        self.colorMatrix.verticalHeader().setVisible(False)
        self.colorMatrix.setShowGrid(True)
        self.colorMatrix.setStyleSheet("QTableWidget { border: none; }")

        # 初始化矩阵颜色并设置项目为可选择
        for row in range(12):
            for col in range(18):
                item = QTableWidgetItem()
                item.setBackground(QColor(200, 200, 200))  # 设置为灰色
                item.setFlags(item.flags() | Qt.ItemIsSelectable)  # 使项目可选择
                self.colorMatrix.setItem(row, col, item)

        # 连接单元格点击信号到槽函数
        self.colorMatrix.cellClicked.connect(MainWindow.on_matrix_cell_clicked)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1631, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("MainWindow", u"\u9009\u62e9", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"\u901a\u9053", None))

        # 设置18个通道按钮的文本
        for i in range(1, 19):
            button = self.groupBox.findChild(QPushButton, f"pushButton_{i}")
            if button:
                button.setText(QCoreApplication.translate("MainWindow", str(i), None))

        self.pushButton_19.setText(QCoreApplication.translate("MainWindow", u"ALL", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"\u8bbe\u5907", None))

        # 设置12个设备按钮的文本
        for i in range(1, 13):
            button = self.groupBox_2.findChild(QPushButton, f"pushButton_{i}")
            if button:
                button.setText(QCoreApplication.translate("MainWindow", str(i), None))

        self.pushButton_13.setText(QCoreApplication.translate("MainWindow", u"ALL", None))
        self.pushButton_33.setText(QCoreApplication.translate("MainWindow", u"START", None))
        self.pushButton_34.setText(QCoreApplication.translate("MainWindow", u"PAUSE", None))
        self.pushButton_35.setText(QCoreApplication.translate("MainWindow", u"RESET", None))

        # 为 QTableWidget 添加行列标签
        self.colorMatrix.setHorizontalHeaderLabels([str(i + 1) for i in range(18)])
        self.colorMatrix.setVerticalHeaderLabels([str(i + 1) for i in range(12)])

        self.statusTextEdit.setPlaceholderText("Measurement status will be displayed here...")