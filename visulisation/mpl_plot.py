import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure(figsize=(20,20))
ax = Axes3D(fig)

# x
x = np.load(r"E:\\My Projects\\rocks_view\\x.npy")
# y
y = np.load(r"E:\\My Projects\\rocks_view\\y.npy")
# z
z = np.load(r"E:\\My Projects\\rocks_view\\z.npy")

#ax.plot3D(x,y,z)
ax.scatter3D(x,y,z,s=100)
plt.show()