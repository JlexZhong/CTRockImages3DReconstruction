
import cv2
import numpy as np
from PIL import Image
from scipy.ndimage.measurements import label,find_objects,center_of_mass
import math
import os
from tqdm import tqdm,trange
# sys.setrecursionlimit(5000) #例如这里设置为十万




contours_list = []

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
    if flag_point1 and flag_point2 == 1.:      
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
        return 0
    else:
        return 1

def func_1(now_img_id,K):
    if now_img_id > total_img_num:
        print("#=========================================================#")
        print("                   A L L   C O M P L E T E D !             ")
        print("#=========================================================#")
    else:
        # now_img_id : 1,2,3,4,5,6...
        M = len(contours_list[now_img_id - 1])
        N = len(contours_list[now_img_id - 2])
        m = 1
        n = 1
        func_2(M,N,m,n,now_img_id,K)
    
def func_2(M,N,m,n,now_img_id,K):
    if m > M:
        now_img_id = now_img_id + 1
        func_1(now_img_id,K)
    else:
        func_3(M,N,m,n,now_img_id,K) 
    
def func_3(M,N,m,n,now_img_id,K):
    if n > N:
        K           = K + 1
        # 找到新砾石，新建一个字典
        rock_dict = {}
        rock_dict['id'] = K
        rock_dict['contours'] = []
        # FIXME:  m? n ?
        rock_dict['contours'].append(contours_list[now_img_id - 1][m - 1])
        rock_dict['z_coordinates'] = []
        rock_dict['z_coordinates'].append(now_img_id - 1)
        ALL_ROCKS_LIST.append(rock_dict)
        
        m           = m + 1
        func_2(M,N,m,n,now_img_id,K)
    else:
        func_4(M,N,m,n,now_img_id,K)
    
def func_4(M,N,m,n,now_img_id,K):
    """
    两边界矩阵属于同一个砾石，给予相同的砾石编号
    """
    max_id      = compare_area(contours_list,m,n,now_img_id)
    if max_id   == 0:
        flag    = is_central_points_on_polygons(contours_list[now_img_id - 1][m - 1],
                                                central_points_list[now_img_id - 2][n - 1])
    else:
        flag    = is_central_points_on_polygons(contours_list[now_img_id - 2][n - 1],
                                                central_points_list[now_img_id - 1][m - 1])
    if flag     == False:
        n       = n + 1
        func_3(M,N,m,n,now_img_id,K)
    else:
        # 
        ALL_ROCKS_LIST[n - 1]['contours'].append(contours_list[now_img_id - 1][m - 1])
        ALL_ROCKS_LIST[n - 1]['z_coordinates'].append(now_img_id - 1)
        m       = m + 1
        func_2(M,N,m,n,now_img_id,K)   
    
    

if __name__ == "__main__":
    
    # 砾石CT切片图像的存放路径
    rocks_img_path = r"E:\My Projects\rocks_view\test_modeling_final"# 
    rocks_images_name = os.listdir(rocks_img_path) 
    
    # print(rocks_images_name)
    #  加载保存的结果图，保存在r_imgs
    r_imgs = []
    for i in trange(len(rocks_images_name)):
        rock_img = Image.open(os.path.join(rocks_img_path,rocks_images_name[i])) 
        r_imgs.append(rock_img)

    
    # 计算每个图像的所有mask的边界矩阵
    for i in range(len(r_imgs)):
        contours = extract_contour(r_imgs[i])
        contours = np.array(contours)
        contours_list.append(contours)
    # contours_list = np.array(contours_list)
    
    
    x = []
    y = []
    z = []
    
    for i in range(len(contours_list)):
        for j in range(len(contours_list[i])):
            for k in range(len(contours_list[i][j])):
                x.append(contours_list[i][j][k][0][0] * 0.25)
                y.append(contours_list[i][j][k][0][1] * 0.25)
                z.append(i * 0.70)
    print(str(len(x)))
    print(str(len(y)))
    print(str(len(z)))

    
    # 计算每个图像中的所有mask的假中心点
    central_points_list = []
    for i in range(len(r_imgs)):
        central_points = calculate_central_points(contours_list[i])
        central_points_list.append(central_points)
    central_points_list = np.array(central_points_list)
    
    
    
    global total_img_num
    total_img_num   = len(rocks_images_name)
    now_img_id      = 2
    K               = len(contours_list[0])  # 第一张图像的砾石数量，后面图像在此基础上增加

    global ALL_ROCKS_LIST
    ALL_ROCKS_LIST = []
    # !使用for循环创建字典，必须在循环内先构造一个空字典，否则每次循环都是对同一个对象字典进行操作，用同一块内存空间
    for i in range(K):
        rock_dict = {}
        rock_dict['id'] = i + 1
        rock_dict['contours'] = []  # 边界矩阵
        rock_dict['contours'].append(contours_list[0][i])
        rock_dict['z_coordinates'] = []  # 砾石的Z轴坐标
        rock_dict['z_coordinates'].append(0)  # 第一张图像的Z = 0
        ALL_ROCKS_LIST.append(rock_dict)
        
    func_1(now_img_id,K)