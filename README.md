# 基于CT扫描的砾石图像三维重建

**主界面**：

<img src="README.assets/image-20220118171145158.png" alt="image-20220118171145158" style="zoom: 50%;" />

**效果：**

<img src="README.assets/display.gif" alt="display" style="zoom: 50%;" />

## 使用方法

#### 配置环境

requirement.txt

```
scipy==1.5.4
torch==1.6.0+cpu
pyqtgraph==0.11.1
numpy==1.19.5
mayavi==4.7.4
tqdm==4.42.1
pandas==1.1.5
opencv_python_headless==4.5.3.56
torchvision==0.7.0+cpu
matplotlib==3.1.2
Pillow==9.0.0
PyQt5==5.15.6
```

主目录下：

```bash
pip install -r requirement.txt
```

#### 下载预训练权重



#### 导入CT影像

#### 选择神经网络模型

目前只支持UNet

#### 载入权重

#### 进行图像分割

可选择使用GPU加速

#### 结果优化

可使用画笔将粘结的砾石通过人工分开，右侧可调整画笔粗细和颜色。

<img src="README.assets/image-20220118192928686.png" alt="image-20220118192928686" style="zoom:80%;" />

<img src="README.assets/image-20220118193013517.png" alt="image-20220118193013517" style="zoom:80%;" />

<img src="README.assets/image-20220118193517921.png" alt="image-20220118193517921" style="zoom: 50%;" />
