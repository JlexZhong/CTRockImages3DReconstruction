import sys

import cv2
import numpy as np
import pyqtgraph.opengl as gl
from pandas import array
from PIL import ImageQt
from PyQt5.QtWidgets import *
from pyqtgraph.Qt import QtCore, QtGui

from palette import ReviseForm


class VisualModelWidget(QDialog):
    def __init__(self, parent, MainUi):
        super(VisualModelWidget, self).__init__(parent)
        self.parent = parent
        self.MainUi = MainUi
        self.setWindowTitle("三维砾石重建")
        self.resize(1000, 800)
        # 显示点云的组件
        self.w = gl.GLViewWidget(self)
        self.w.opts['distance'] = 120  # 视图距离
        # 按钮
        self.pushButton_save = QPushButton(self)
        self.pushButton_save.setText("输出vtk文件")
        # self.pushButton.clicked.connect(self.showImage)
        # 布局
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.addWidget(self.w)
        self.verticalLayout.addWidget(self.pushButton_save)
        # 设置窗口布局
        self.setLayout(self.verticalLayout)

    def GetAllImages(self):
        self.imgs = []
        # 将pixmap 转换成Image
        for i in range(self.MainUi.stackedWidget.count()):
            self.imgs.append(ImageQt.fromqpixmap(self.MainUi.stackedWidget.widget(
                i).findChild(ReviseForm, "ReviseForm"+str(i)).pix))

    def Visual(self):
        # 计算每个图像的所有mask的边界矩阵
        self.GetAllImages()
        self.contours_list = []
        for i in range(self.MainUi.stackedWidget.count()):
            contours = extract_contour(self.imgs[i])
            contours = np.array(contours)
            self.contours_list.append(contours)
        x = []
        y = []
        z = []

        for i in range(len(self.contours_list)):
            for j in range(len(self.contours_list[i])):
                for k in range(len(self.contours_list[i][j])):
                    # -256 是因为图片像素坐标是以左上角为原点
                    x.append((self.contours_list[i][j][k][0][0] - 256) * 0.25)
                    y.append((self.contours_list[i][j][k][0][1] - 256) * 0.25)
                    z.append(i * 0.70)

        self.pos = np.empty((len(x), 3))
        for i in range(len(x)):
            self.pos[i] = (x[i], y[i], z[i])
        self.pos = np.array(self.pos)

        sp1 = gl.GLScatterPlotItem(pos=self.pos, color=(
            1, 1, 1, 1), size=0.3, pxMode=False)
        self.w.addItem(sp1)

        # 显示坐标轴
        axex_x = gl.GLLinePlotItem(pos=np.asarray(
            [[0, 0, 0], [80, 0, 0]]), color=(1, 0, 0, 1), width=0.1)
        axex_y = gl.GLLinePlotItem(pos=np.asarray(
            [[0, 0, 0], [0, 80, 0]]), color=(0, 1, 0, 1), width=0.1)
        axex_z = gl.GLLinePlotItem(pos=np.asarray(
            [[0, 0, 0], [0, 0, 130]]), color=(0, 0, 1, 1), width=0.1)
        self.w.addItem(axex_x)
        self.w.addItem(axex_y)
        self.w.addItem(axex_z)

        self.w.show()


def extract_contour(r_img):
    """传入一个图像，返回该图像的所有mask的边界轮廓矩阵
    """
    img = cv2.cvtColor(np.asarray(r_img), cv2.COLOR_RGB2BGR)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 彩色图变灰度图
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)  # 灰度图变二值图
    contours, _ = cv2.findContours(
        binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # 根据二值图找轮廓
    # cv2.drawContours(img,contours,-1,(0,0,255),1) # 把轮廓画在原图上（0,0,255） 表示 RGB 三通道，红色
    return contours
