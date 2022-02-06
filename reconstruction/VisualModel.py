import math
import random
import cv2
import numpy as np
import pyqtgraph.opengl as gl
from PIL import ImageQt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from palette import ReviseForm
from PyQt5.QtCore import Qt
from matplotlib.path import Path
import os
from output_vtk_file import VtkPointCloud
import vtk


class VisualModelWidget(QDialog):
    """三维重建窗口类"""
    def __init__(self, parent, MainUi):
        super(VisualModelWidget, self).__init__(parent)
        self.parent = parent
        self.MainUi = MainUi
        self.setWindowTitle("三维砾石重建")
        self.resize(1000, 800)
        # 显示点云的组件
        
        self.w = gl.GLViewWidget(self)
        self.w.opts['distance'] = 130  # 视图距离
        
        
        # 右侧ID框
        self.Widget_ID = QWidget(self)
        self.Widget_ID.setMaximumWidth(200)
        # 布局
        self.HLayout = QHBoxLayout(self)
        self.HLayout.addWidget(self.w)
        self.HLayout.addWidget(self.Widget_ID)
        # 设置窗口布局
        self.setLayout(self.HLayout)
        # ID框的布局
        self.Layout_ID = QVBoxLayout(self.Widget_ID)
        self.View_ID = QTableView(self.Widget_ID)
        self.pushbutton_all_select = QPushButton(self.Widget_ID)
        self.pushbutton_all_select.setText("全选")
        self.pushbutton_all_unselect = QPushButton(self.Widget_ID)
        self.pushbutton_all_unselect.setText("全不选")
        self.pushbutton_3D_Modeling = QPushButton(self.Widget_ID)
        self.pushbutton_3D_Modeling.setText("三维重建")
        self.pushbutton_save_to_txt = QPushButton(self.Widget_ID)
        self.pushbutton_save_to_txt.setText("输出为txt文件")
        self.pushbutton_save_to_vtk = QPushButton(self.Widget_ID)
        self.pushbutton_save_to_vtk.setText("输出为vtk文件")
        self.Layout_ID.addWidget(self.View_ID)
        self.Layout_ID.addWidget(self.pushbutton_all_select)
        self.Layout_ID.addWidget(self.pushbutton_all_unselect)
        self.Layout_ID.addWidget(self.pushbutton_3D_Modeling)
        self.Layout_ID.addWidget(self.pushbutton_save_to_txt)
        self.Layout_ID.addWidget(self.pushbutton_save_to_vtk)
        # View_ID
        self.View_ID.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # add action
        self.pushbutton_all_select.clicked.connect(self.Action_all_select)
        self.pushbutton_all_unselect.clicked.connect(self.Action_all_unselect)
        self.pushbutton_3D_Modeling.clicked.connect(self.Action_Visual_in_Dialog)
        self.pushbutton_save_to_txt.clicked.connect(self.Action_save_coordinates_to_txt)
        self.pushbutton_save_to_vtk.clicked.connect(self.Action_output_to_vtk)

    def createModel(self, parent):
        """

        创建模型
        :param parent:
        :return:
        """
        model = QStandardItemModel(0, 3, parent)
        model.setHorizontalHeaderLabels(['', 'ID', '切片数'])
        return model

    def CreateViewID(self):
        """关键Id选择框"""
        model = self.createModel(self.View_ID)
        row = 0  # 行数，等于文件数
        self.lst_id_checkBox = []  # 存放复选框变量
        for id in range(len(ALL_ROCKS_LIST)):  # 初始化模型model数据，插入文件名
            model.insertRow(row)
            model.setData(model.index(row, 1), id + 1)
            model.setData(model.index(row, 2),len(ALL_ROCKS_LIST[id]['z_coordinates']))
            row = row + 1
        for i in range(row):
            item_checked = QStandardItem()
            item_checked.setCheckState(Qt.Checked)
            item_checked.setCheckable(True)
            model.setItem(i, 0, item_checked)
            self.lst_id_checkBox.append(item_checked)  # 添加到列表中
        self.View_ID.setModel(model)
        self.View_ID.setColumnWidth(0, 20)
        self.View_ID.setColumnWidth(1, 50)
        self.View_ID.setColumnWidth(2, 50)
        
        
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
        PRE_IMG_ROCK_ID = []
        NOW_IMG_ROCK_ID = []
        # !使用for循环创建字典，必须在循环内先构造一个空字典，否则每次循环都是对同一个对象字典进行操作，用同一块内存空间
        for i in range(K):
            rock_dict = {}
            rock_dict['id'] = i + 1
            rock_dict['contours'] = []  # 边界矩阵
            rock_dict['contours'].append(self.contours_list[0][i])
            rock_dict['z_coordinates'] = []  # 砾石的Z轴坐标
            rock_dict['z_coordinates'].append(0)  # 第一张图像的Z = 0
            ALL_ROCKS_LIST.append(rock_dict)
            PRE_IMG_ROCK_ID.append(i + 1)

        # isAddRock = False
        while(now_img_id <= total_img_num):
            M = len(self.contours_list[now_img_id - 1])  # now_img_id张图片中的边界矩阵数
            N = len(self.contours_list[now_img_id - 2])  # now_img_id - 1张图片中的边界矩阵数
            m = 1  # 计数
            n = 1
            
            while(m <= M):
                n = 1
                while(n <= N):
                    flag = IsSameRock(m,n,now_img_id,self.contours_list,central_points_list)  # 两边界是否为同一个砾石
                    if flag:  # 属于同一砾石
                        # TODO：属于同一砾石，重组
                        # FIXME:找到第now_img_id - 1 张中第n个砾石在ALL_ROCKS_LIST中的位置
                        # !BUG:
                        pre_id = PRE_IMG_ROCK_ID[n-1]
                        ALL_ROCKS_LIST[pre_id - 1]['contours'].append(self.contours_list[now_img_id - 1][m - 1])
                        ALL_ROCKS_LIST[pre_id - 1]['z_coordinates'].append(now_img_id - 1)
                        NOW_IMG_ROCK_ID.append(pre_id)   # 当前图像的第m个边界属于的砾石id
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
                    NOW_IMG_ROCK_ID.append(K)  # 
                m+=1  # 处理当前图像的下一个边界
                #
            now_img_id+=1  # while(m <= M)  #  当前图像的砾石已经找完，处理下一张
            PRE_IMG_ROCK_ID = NOW_IMG_ROCK_ID
            NOW_IMG_ROCK_ID = []
            
        print("Successful!")  # while(now_img_id <= total_img_num):
        global ALL_ROCKS_COORDINATES
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
        self.scatter_plot()
        
    def Action_save_coordinates_to_txt(self):
        """保存坐标为txt"""
        folderDir_save = None
        folderDir_save = QFileDialog.getExistingDirectory(
            self, '选取文件夹', "./")  # 打开文件夹选择对话框
        if folderDir_save == "":
            pass  # 防止未选择文件或者关闭对话框程序闪退
        else:
            list_selected_ID = self.Get_select_ids()
            x = []
            y = []
            z = []
            colors = []
            for id in list_selected_ID:
                i = id -1
                color = get_random_color()
                for j in range(len(ALL_ROCKS_COORDINATES[i][0])):
                    x.append(ALL_ROCKS_COORDINATES[i][0][j])
                    y.append(ALL_ROCKS_COORDINATES[i][1][j])
                    z.append(ALL_ROCKS_COORDINATES[i][2][j])
                    colors.append(color)
                
                pos = np.empty((len(x), 3))
                for i in range(len(x)):
                    pos[i] = (x[i], y[i], z[i])
                pos = np.array(pos)
                np.savetxt(folderDir_save + '/' + 'rock_' + str(id) + '.txt',pos,'%.2d')  # 保存为txt，'%.2d'为精度
        
    def Action_output_to_vtk(self):
        """输出为VTK"""
        vtkFileSavePath = None
        vtkFileSavePath = QFileDialog.getSaveFileName(self, '保存vtk文件', "./",'.vtk')  # 打开文件夹选择对话框
        if vtkFileSavePath == "":
            pass  # 防止未选择文件或者关闭对话框程序闪退
        else:
            list_selected_ID = self.Get_select_ids()
            pointCloud = VtkPointCloud(list_selected_ID[0],list_selected_ID[len(list_selected_ID) - 1])
            x = []
            y = []
            z = []
            for id in list_selected_ID:
                i = id -1
                for j in range(len(ALL_ROCKS_COORDINATES[i][0])):
                    x.append(ALL_ROCKS_COORDINATES[i][0][j])
                    y.append(ALL_ROCKS_COORDINATES[i][1][j])
                    z.append(ALL_ROCKS_COORDINATES[i][2][j])
                
                self.MainUi.statusbar.showMessage("输出vtk:" + str(id) + "/" + str(len(list_selected_ID)))
                for k in range(len(x)):
                    pos = (x[k], y[k], z[k])
                    pointCloud.addPoint(pos,id)
            # ++++++++++++++++++  writer保存文件 +++++++++++++++++++
            writer = vtk.vtkPolyDataWriter()
            
            # !若在保存文件对话框中没写.vtk后缀，则加上vtk后缀（即vtkFileSavePath[1]）
            if vtkFileSavePath[0][-4:] != '.vtk':
                writer.SetFileName(os.path.join((vtkFileSavePath[0] + vtkFileSavePath[1])))
            else:
                writer.SetFileName(os.path.join(vtkFileSavePath[0]))
            writer.SetInputData(pointCloud.vtkPolyData)
            writer.Write()
            writer.Update()    
            
            """
            # !加上这一段即可显示出vtk窗口
            # Renderer
            renderer = vtk.vtkRenderer()
            renderer.AddActor(pointCloud.vtkActor)
            renderer.SetBackground(.2, .3, .4)
            renderer.ResetCamera()

            # Render Window
            renderWindow = vtk.vtkRenderWindow()
            renderWindow.AddRenderer(renderer)

            # Interactor
            renderWindowInteractor = vtk.vtkRenderWindowInteractor()
            renderWindowInteractor.SetRenderWindow(renderWindow)

            # Begin Interaction
            renderWindow.Render()
            renderWindowInteractor.Start()"""
                
        
    def scatter_plot(self):
        """利用Pyqtgraph画出三维点云图"""
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
        self.sp1 = gl.GLScatterPlotItem(pos=self.pos, color=colors, size=0.4, pxMode=True)
        self.w.addItem(self.sp1)
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
        self.CreateViewID()

    def Action_all_select(self):
        """全选"""
        for i in range(len(self.lst_id_checkBox)):
            self.lst_id_checkBox[i].setCheckState(Qt.Checked)

    def Action_all_unselect(self):
        """全不选"""
        for i in range(len(self.lst_id_checkBox)):
            self.lst_id_checkBox[i].setCheckState(Qt.Unchecked)


    def Get_select_ids(self):
        """获取选择的id"""
        list_selected_ID = []
        for i in range(len(self.lst_id_checkBox)):
            if (self.lst_id_checkBox[i].checkState() == Qt.Checked):
                list_selected_ID.append(i + 1)
        return list_selected_ID


    def Action_Visual_in_Dialog(self):
        """三维重建按钮的触发事件"""
        list_selected_ID = self.Get_select_ids()
        x = []
        y = []
        z = []
        colors = []
        for id in list_selected_ID:
            i = id -1
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
        self.w.removeItem(self.sp1)
        self.sp1 = gl.GLScatterPlotItem(pos=self.pos, color=colors, size=0.4, pxMode=False)
        self.w.addItem(self.sp1)
        

        self.w.show()


def get_random_color():
    """获取一个随机的颜色"""
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
    if flag_point1 >= 0:
        return True
    elif flag_point2 >= 0:
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


def IsSameRock_2(m,n,now_img_id,contours_list,central_points_list):
    """
    两边界矩阵属于同一个砾石，给予相同的砾石编号
    """
    max_id      = compare_area(contours_list,m,n,now_img_id)
    if max_id   == "m":
        xq = [central_points_list[now_img_id - 2][n - 1][0][0],
              central_points_list[now_img_id - 2][n - 1][0][1]]
        yq = [central_points_list[now_img_id - 2][n - 1][1][0],
              central_points_list[now_img_id - 2][n - 1][1][1]]
        xv = []
        yv = []
        for i in range(len(contours_list[now_img_id - 1][m - 1])):
            xv.append(contours_list[now_img_id - 1][m - 1][i][0][0])
            yv.append(contours_list[now_img_id - 1][m - 1][i][0][1])
        xq = np.array(xq)
        yq = np.array(yq)
        xv = np.array(xv)
        yv = np.array(yv)
        flag,_     = inpolygon(xq,yq,xv,yv)
    else:
        xq = [central_points_list[now_img_id - 1][m - 1][0][0],
              central_points_list[now_img_id - 1][m - 1][0][1]]
        yq = [central_points_list[now_img_id - 1][m - 1][1][0],
              central_points_list[now_img_id - 1][m - 1][1][1]]
        xv = []
        yv = []
        for i in range(len(contours_list[now_img_id - 2][n - 1])):
            xv.append(contours_list[now_img_id - 2][n - 1][i][0][0])
            yv.append(contours_list[now_img_id - 2][n - 1][i][0][1])
        xq = np.array(xq)
        yq = np.array(yq)
        xv = np.array(xv)
        yv = np.array(yv)
        flag,_    = inpolygon(xq,yq,xv,yv)
    if (flag[0] or flag[1]) == True:
        return True
    else:
        return False


def inpolygon(xq, yq, xv, yv):
    """
    reimplement inpolygon in matlab
    :type xq: np.ndarray
    :type yq: np.ndarray
    :type xv: np.ndarray
    :type yv: np.ndarray
    """
    # 合并xv和yv为顶点数组
    vertices = np.vstack((xv, yv)).T
    # 定义Path对象
    path = Path(vertices)
    # 把xq和yq合并为test_points
    test_points = np.hstack([xq.reshape(xq.size, -1), yq.reshape(yq.size, -1)])
    # 得到一个test_points是否严格在path内的mask，是bool值数组
    _in = path.contains_points(test_points)
    # 得到一个test_points是否在path内部或者在路径上的mask
    _in_on = path.contains_points(test_points, radius=10)
    # 得到一个test_points是否在path路径上的mask
    _on = _in ^ _in_on
    
    return _in_on, _on
