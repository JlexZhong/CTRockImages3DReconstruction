import numpy as np
from mayavi import mlab
# x
x = np.load(r"E:\\My Projects\\rocks_view\\x.npy")
# y
y = np.load(r"E:\\My Projects\\rocks_view\\y.npy")
# z
z = np.load(r"E:\\My Projects\\rocks_view\\z.npy")

#对该数据进行三维可视化
s = mlab.points3d(x,y,z)
mlab.show()
