# -*- coding: utf-8 -*-

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(550, 602)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")

        self.textEdit = QTextEdit(self.centralwidget)
        self.textEdit.setObjectName(u"textEdit")
        self.textEdit.setGeometry(QRect(170, 30, 321, 41))

        self.gridLayoutWidget = QWidget(self.centralwidget)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QRect(70, 170, 421, 321))
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)

        self.pushButton_4 = QPushButton(self.gridLayoutWidget)
        self.pushButton_4.setObjectName(u"pushButton_4")
        self.gridLayout.addWidget(self.pushButton_4, 1, 0, 1, 1)

        self.pushButton_3 = QPushButton(self.gridLayoutWidget)
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.gridLayout.addWidget(self.pushButton_3, 0, 2, 1, 1)

        self.pushButton_6 = QPushButton(self.gridLayoutWidget)
        self.pushButton_6.setObjectName(u"pushButton_6")
        self.gridLayout.addWidget(self.pushButton_6, 1, 2, 1, 1)

        self.pushButton_5 = QPushButton(self.gridLayoutWidget)
        self.pushButton_5.setObjectName(u"pushButton_5")
        self.gridLayout.addWidget(self.pushButton_5, 1, 1, 1, 1)

        self.pushButton = QPushButton(self.gridLayoutWidget)
        self.pushButton.setObjectName(u"pushButton")
        self.gridLayout.addWidget(self.pushButton, 0, 1, 1, 1)

        self.pushButton_2 = QPushButton(self.gridLayoutWidget)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 0, 0, 1, 1)

        self.plainTextEdit = QPlainTextEdit(self.centralwidget)
        self.plainTextEdit.setObjectName(u"plainTextEdit")
        self.plainTextEdit.setGeometry(QRect(170, 90, 171, 41))
        self.plainTextEdit.setReadOnly(True)

        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(100, 100, 67, 17))
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(90, 40, 67, 17))

        self.pushButton_7 = QPushButton(self.centralwidget)
        self.pushButton_7.setObjectName(u"pushButton_7")
        self.pushButton_7.setGeometry(QRect(370, 100, 89, 25))

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 550, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.connect_buttons()

        QMetaObject.connectSlotsByName(MainWindow)

    def connect_buttons(self):
        self.pushButton_2.clicked.connect(lambda: self.add_operation("+"))
        self.pushButton.clicked.connect(lambda: self.add_operation("-"))
        self.pushButton_4.clicked.connect(lambda: self.add_operation("*"))
        self.pushButton_3.clicked.connect(lambda: self.add_operation("//"))
        self.pushButton_6.clicked.connect(lambda: self.add_operation("**"))
        self.pushButton_5.clicked.connect(lambda: self.add_operation("%"))

        self.pushButton_7.clicked.connect(self.clear_all)

    def add_operation(self, operation):
        current_text = self.textEdit.toPlainText().strip()

        if not current_text:
            current_text = "0"

        new_text = current_text + operation
        self.textEdit.setPlainText(new_text)

        result = self.calculate_expression(new_text)
        self.plainTextEdit.setPlainText(str(result))

    def calculate_expression(self, expression):
        local_vars = {}
        exec(f"result = {expression}", {"__builtins__": {}}, local_vars)

        return local_vars.get('result', 'Ошибка')

    def clear_all(self):
        self.textEdit.clear()
        self.plainTextEdit.clear()

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Калькулятор", None))
        self.pushButton_4.setText(QCoreApplication.translate("MainWindow", u"*", None))
        self.pushButton_3.setText(QCoreApplication.translate("MainWindow", u"//", None))
        self.pushButton_6.setText(QCoreApplication.translate("MainWindow", u"**", None))
        self.pushButton_5.setText(QCoreApplication.translate("MainWindow", u"%", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"-", None))
        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", u"+", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Ответ", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Задача", None))
        self.pushButton_7.setText(QCoreApplication.translate("MainWindow", u"очистить", None))


class CalculatorWindow(QMainWindow):
    def __init__(self):
        super(CalculatorWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = CalculatorWindow()
    window.show()
    sys.exit(app.exec_())