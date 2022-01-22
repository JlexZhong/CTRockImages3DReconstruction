# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPixmap, QPen, QColor
from PyQt5.QtCore import Qt, QPoint

class ReviseForm(QWidget):
    """用于展示模型分割的结果和用画笔完善结果的类"""

    def __init__(self, parent, MainUi):
        super(ReviseForm, self).__init__(parent)
        self.parent = parent
        self.MainUi = MainUi
        self.pix = QPixmap()  # 实例化一个 QPixmap 对象
        self.lastPoint = QPoint()  # 起始点
        self.endPoint = QPoint()  # 终点
        self.r = 0
        self.g = 0
        self.b = 0
        self.a = 255
        self.penSize = 2  # 笔粗细

    def mousePressEvent(self, event):
        """鼠标按压事件"""
        # 鼠标左键按下
        try:
            if event.button() == Qt.LeftButton:
                # pixmap -> Image
                image = self.pix.toImage()
                position = QPoint(event.x(), event.y())
                color = QColor.fromRgb(image.pixel(position))
                # 获取当前点击位置的RGB值
                if color.isValid():
                    self.r, self.g, self.b = color.red(), color.green(), color.blue()
                print("RGB：", color.red(), color.green(),
                      color.blue(), "坐标：", (event.x(), event.y()))
                # 修改界面中的颜色下拉框
                if self.r == 0 and self.g == 0 and self.b == 0:
                    self.MainUi.comboBox_color.setCurrentIndex(0)
                else:
                    self.MainUi.comboBox_color.setCurrentIndex(1)
                self.lastPoint = event.pos()
                self.endPoint = self.lastPoint
        except:
            print("获取颜色失败！")

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        # 鼠标左键按下的同时移动鼠标
        try:

            if event.buttons() and Qt.LeftButton:
                # print("移动坐标", event.pos())
                self.endPoint = event.pos()
                # 进行重新绘制
                self.update()
        except:
            print("3")

    # 鼠标释放事件
    def mouseReleaseEvent(self, event):
        # 鼠标左键释放
        try:
            if event.button() == Qt.LeftButton:
                self.endPoint = event.pos()
                # print("释放坐标", event.pos())
                # 进行重新绘制
                self.update()
        except:
            print("4")

    def paintEvent(self, event):
        try:
            # print("绘画")
            pp = QPainter(self.pix)
            pen = QPen(QColor(self.r, self.g, self.b))  # 定义笔格式对象
            pen.setWidth(self.penSize)  # 设置笔的宽度
            pp.setPen(pen)  # 将笔格式赋值给 画笔
            # 根据鼠标指针前后两个位置绘制直线
            pp.drawLine(self.lastPoint, self.endPoint)
            # 让前一个坐标值等于后一个坐标值，
            # 这样就能实现画出连续的线
            self.lastPoint = self.endPoint
            painter = QPainter(self)
            painter.drawPixmap(0, 0, self.pix)  # 在画布上画出
            # self.pix.save(save_path)
        except:
            print("5")
