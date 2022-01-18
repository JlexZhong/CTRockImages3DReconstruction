# -*- coding: utf-8 -*-
"""
Demonstrates use of GLScatterPlotItem with rapidly-updating plots.

"""

## Add path to library (just for examples; you do not need this)

from pandas import array
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import numpy as np

app = QtGui.QApplication([])

w = gl.GLViewWidget()
w.opts['distance'] = 100
w.setWindowTitle('pyqtgraph example: GLScatterPlotItem')
w.resizeGL(1200,1000)
#

# x
x = np.load(r"E:\\My Projects\\rocks_view\\x.npy")
# y
y = np.load(r"E:\\My Projects\\rocks_view\\y.npy")
# z
z = np.load(r"E:\\My Projects\\rocks_view\\z.npy")
x = x - 256 * 0.25
y = y - 256 * 0.25

pos = np.empty((len(x),3))
for i in range(len(x)):
    pos[i] = (x[i],y[i],z[i])

pos = np.array(pos)
sp1 = gl.GLScatterPlotItem(pos=pos,color = (1,1,1,1),size=0.3, pxMode=False)
w.addItem(sp1)

w.setCameraPosition()


# 显示坐标轴
axex_x = gl.GLLinePlotItem(pos=np.asarray([[0, 0, 0], [80, 0, 0]]), color=(1, 0, 0, 1), width=0.01)
axex_y = gl.GLLinePlotItem(pos=np.asarray([[0, 0, 0], [0, 80, 0]]), color=(0, 1, 0, 1), width=0.01)
axex_z = gl.GLLinePlotItem(pos=np.asarray([[0, 0, 0], [0, 0, 180]]), color=(0, 0, 1, 1), width=0.01)
w.addItem(axex_x)
w.addItem(axex_y)
w.addItem(axex_z)



w.show()


## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
