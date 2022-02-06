import cgitb
from PyQt5 import QtCore, QtGui, QtWidgets
from Ui_MainW import Ui_MainWindow

# 这句放在所有程序开始前，这样就可以正常打印异常了
cgitb.enable(format="text")

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("fusion")
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.setWindowTitle("基于深度学习的CT扫描砾石图像三维重建")
    MainWindow.show()
    sys.exit(app.exec_())
