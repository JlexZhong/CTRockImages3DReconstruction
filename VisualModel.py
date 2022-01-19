import math
import sys
import random
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

    def Visual_(self):
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


    def Visual(self):
         # 计算每个图像的所有mask的边界矩阵
        self.GetAllImages()
        self.contours_list = []
        for i in range(self.MainUi.stackedWidget.count()):
            contours = extract_contour(self.imgs[i])
            contours = np.array(contours)
            self.contours_list.append(contours)
            # 计算每个图像中的所有mask的假中心点
        central_points_list = []
        for i in range(len(self.contours_list)):
            central_points = calculate_central_points(self.contours_list[i])
            central_points_list.append(central_points)
        central_points_list = np.array(central_points_list)
        # 初始化
        global total_img_num
        total_img_num   = len(self.imgs)
        now_img_id      = 2
        K               = len(self.contours_list[0])  # 第一张图像的砾石数量，后面图像在此基础上增加

        global ALL_ROCKS_LIST
        ALL_ROCKS_LIST = []
        #  用一个列表记录前一张图片中各个边界矩阵在ALL_ROCKS_LIST中的位置
        global PRE_IMG_ROCK_ID
        PRE_IMG_ROCK_ID = np.empty((3000,),int)

        # !使用for循环创建字典，必须在循环内先构造一个空字典，否则每次循环都是对同一个对象字典进行操作，用同一块内存空间
        for i in range(K):
            rock_dict = {}
            rock_dict['id'] = i + 1
            rock_dict['contours'] = []  # 边界矩阵
            rock_dict['contours'].append(self.contours_list[0][i])
            rock_dict['z_coordinates'] = []  # 砾石的Z轴坐标
            rock_dict['z_coordinates'].append(0)  # 第一张图像的Z = 0
            ALL_ROCKS_LIST.append(rock_dict)
            PRE_IMG_ROCK_ID[i] = i + 1

        # isAddRock = False
        while(now_img_id <= total_img_num):
            M = len(self.contours_list[now_img_id - 1])  # now_img_id张图片中的边界矩阵数
            N = len(self.contours_list[now_img_id - 2])  # now_img_id - 1张图片中的边界矩阵数
            m = 1  # 计数
            n = 1
            
            while(m <= M):
                while(n <= N):
                    flag = IsSameRock(m,n,now_img_id,self.contours_list,central_points_list)  # 两边界是否为同一个砾石
                    if flag:  # 属于同一砾石
                        # TODO：属于同一砾石，重组
                        # FIXME:找到第now_img_id - 1 张中第n个砾石在ALL_ROCKS_LIST中的位置
                        pre_index = PRE_IMG_ROCK_ID[n-1]
                        ALL_ROCKS_LIST[pre_index - 1]['contours'].append(self.contours_list[now_img_id - 1][m - 1])
                        ALL_ROCKS_LIST[pre_index - 1]['z_coordinates'].append(now_img_id - 1)
                        PRE_IMG_ROCK_ID[m - 1] = pre_index   # 当前图像的第m个边界属于的砾石id
                        #K-=1  # 属于同一砾石不需要K+1，但是为了避免后续K+=1时特殊处理，在这里先K-1
                        #isAddRock = False
                        break
                    else:  # 两边界不属于同一砾石
                        n+=1  # 继续遍历前一张图像的下一个边界
                # while(n <= N)上一张图像的所有砾石已经找完，说明当前这张图像的剩余边界矩阵（若有）均为新砾石
                if n > N:   # 用于解决是因为n>N还是因为找到两个边界属于同一个砾石而结束循环
                    # isAddRock = True
                
                    K+=1  # 找到新砾石
                    # TODO:添加新砾石K
                    rock_dict = {}
                    rock_dict['id'] = K
                    rock_dict['contours'] = []
                    rock_dict['contours'].append(self.contours_list[now_img_id - 1][m - 1])
                    rock_dict['z_coordinates'] = []
                    rock_dict['z_coordinates'].append(now_img_id - 1)
                    ALL_ROCKS_LIST.append(rock_dict)
                    PRE_IMG_ROCK_ID[m - 1] = K  # 
                m+=1  # 处理当前图像的下一个边界
                #
            now_img_id+=1  # while(m <= M)  #  当前图像的砾石已经找完，处理下一张

        print("Successful!")  # while(now_img_id <= total_img_num):
        ALL_ROCKS_COORDINATES = []
        for i in range(K):  # 每个砾石
            x = []
            y = []
            z = []
            for j in range(len(ALL_ROCKS_LIST[i]['contours'])):
                for k in range(len(ALL_ROCKS_LIST[i]['contours'][j])):
                    x.append((ALL_ROCKS_LIST[i]['contours'][j][k][0][0] - 256) * 0.3)  # x
                    y.append((ALL_ROCKS_LIST[i]['contours'][j][k][0][1] - 256) * 0.3)  # y
                    z.append((ALL_ROCKS_LIST[i]['z_coordinates'][j] * 0.60))   # z
            contours = np.array([np.array(x),np.array(y),np.array(z)])
            ALL_ROCKS_COORDINATES.append(contours)

        
        x = []
        y = []
        z = []
        colors = []
        for i in range(len(ALL_ROCKS_COORDINATES)):
            color = get_random_color()
            for j in range(len(ALL_ROCKS_COORDINATES[i][0])):
                x.append(ALL_ROCKS_COORDINATES[i][0][j])
                y.append(ALL_ROCKS_COORDINATES[i][1][j])
                z.append(ALL_ROCKS_COORDINATES[i][2][j])
                colors.append(color)
                
        self.pos = np.empty((len(x), 3))
        for i in range(len(x)):
            self.pos[i] = (x[i], y[i], z[i])
        self.pos = np.array(self.pos)
        colors = np.array(colors)
        sp1 = gl.GLScatterPlotItem(pos=self.pos, color=colors, size=0.4, pxMode=False)
        self.w.addItem(sp1)
        # 显示坐标轴
        axex_x = gl.GLLinePlotItem(pos=np.asarray(
            [[0, 0, 0], [80, 0, 0]]), color=(1, 0, 0, 1), width=0.1)
        axex_y = gl.GLLinePlotItem(pos=np.asarray(
            [[0, 0, 0], [0, 80, 0]]), color=(0, 1, 0, 1), width=0.1)
        axex_z = gl.GLLinePlotItem(pos=np.asarray(
            [[0, 0, 0], [0, 0, 120]]), color=(0, 0, 1, 1), width=0.1)
        self.w.addItem(axex_x)
        self.w.addItem(axex_y)
        self.w.addItem(axex_z)

        self.w.show()



def get_random_color():
    #random.uniform(0, 100)
    r = lambda: random.uniform(0,1)
    return [r(),r(),r(),1]

def extract_contour(r_img):
    """传入一个图像，返回该图像的所有mask的边界轮廓矩阵
    """
    img = cv2.cvtColor(np.asarray(r_img),cv2.COLOR_RGB2BGR)
    
    gray        = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # 彩色图变灰度图
    _,binary    = cv2.threshold(gray,127,255,cv2.THRESH_BINARY) # 灰度图变二值图
    contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) # 根据二值图找轮廓
    # cv2.drawContours(img,contours,-1,(0,0,255),1) # 把轮廓画在原图上（0,0,255） 表示 RGB 三通道，红色
    return contours

def calculate_two_central_points(contour_pixel_xy_list):
    """计算两个假中心点

    Args:
        contour_pixel_xy_list (np.array): 一个目标的所有边界像素点坐标
    """ 
    num_pixel           = len(contour_pixel_xy_list)
    # 获取四个点的坐标
    first_xy            = contour_pixel_xy_list[0]
    half_xy             = contour_pixel_xy_list[int(num_pixel/2)]
    quarter_xy          = contour_pixel_xy_list[int(num_pixel/4)]
    three_quarters_xy   = contour_pixel_xy_list[(int(num_pixel/4)) + int((num_pixel/2)) ]
    # 计算第一个假中心点
    central_point_1_x   = ((math.fabs(first_xy[0][0] - half_xy[0][0])) / 2) + min(first_xy[0][0],half_xy[0][0])
    central_point_1_y   = ((math.fabs(first_xy[0][1] - half_xy[0][1])) / 2) + min(first_xy[0][1],half_xy[0][1])
    central_points_1_xy = [central_point_1_x,central_point_1_y]
    # 计算第二个假中心点
    central_point_2_x   = ((math.fabs(quarter_xy[0][0] - three_quarters_xy[0][0])) / 2) + min(quarter_xy[0][0],three_quarters_xy[0][0])
    central_point_2_y   = ((math.fabs(quarter_xy[0][1] - three_quarters_xy[0][1])) / 2) + min(quarter_xy[0][1],three_quarters_xy[0][1])
    central_points_2_xy = [central_point_2_x,central_point_2_y]
    # 
    central_points      = []
    central_points.append(central_points_1_xy)
    central_points.append(central_points_2_xy)
    central_points      = np.array(central_points)
    central_points.reshape((2,2))
    
    return central_points

def calculate_central_points(contours):
    """传入一张图像的所有边界矩阵，，依次遍历目标然后调用calculate_central_points，返回该图像的所有假中心点的矩阵
    """
    central_points          = []
    for i in range(len(contours)):
        two_central_points  = calculate_two_central_points(contours[i])
        central_points.append(two_central_points)
    central_points          = np.array(central_points)
    # print(central_points_list)
    return central_points


def is_central_points_on_polygons(contour,central_points):
    """
    判断两个假中心点是否在轮廓内
    """
    # cv2.pointPolygonTest只接受元组
    central_points_1_xy     = (central_points[0][0],central_points[0][1])
    central_points_2_xy     = (central_points[1][0],central_points[1][1])
    flag_point1             = cv2.pointPolygonTest(contour,
                                                   central_points_1_xy, False)
    flag_point2             = cv2.pointPolygonTest(contour,
                                                   central_points_2_xy, False)
    if (flag_point1 == 1 or flag_point2 == 1) :      
        return True
    else:
        return False

def compare_area(contours_list,m,n,now_img_id):
    """
    计算两个边界矩阵面积的大小,返回较大值index
    """
    area_m      = cv2.contourArea(contours_list[now_img_id - 1][m - 1])
    area_n      = cv2.contourArea(contours_list[now_img_id - 2][n - 1])
    max_contour = max(area_m,area_n)
    # 返回m/n
    if max_contour == area_m:
        return "m"
    else:
        return "n"

           
             
def IsSameRock(m,n,now_img_id,contours_list,central_points_list):
    """
    两边界矩阵属于同一个砾石，给予相同的砾石编号
    """
    max_id      = compare_area(contours_list,m,n,now_img_id)
    if max_id   == "m":
        flag    = is_central_points_on_polygons(contours_list[now_img_id - 1][m - 1],
                                                central_points_list[now_img_id - 2][n - 1])
    else:
        flag    = is_central_points_on_polygons(contours_list[now_img_id - 2][n - 1],
                                                central_points_list[now_img_id - 1][m - 1])
    return flag      
