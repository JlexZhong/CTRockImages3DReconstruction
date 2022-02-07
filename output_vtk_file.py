import vtk
class VtkPointCloud:
    """使用VTK处理点云的类"""
    def __init__(self, id_Min=-10.0, id_Max=10.0):
        """构造函数"""
        self.vtkPolyData = vtk.vtkPolyData()
        self.clearPoints()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(self.vtkPolyData)
        mapper.SetColorModeToDefault()
        mapper.SetScalarRange(id_Min, id_Max)
        mapper.SetScalarVisibility(1)
        self.vtkActor = vtk.vtkActor()
        self.vtkActor.SetMapper(mapper)

    def addPoint(self, point,id):
        """添加vtkPoints对象，添加标量值

        Args:
            point (numpy.ndarray): 点三维坐标
            id (int): 所属砾石的id,根据id给予标量值
        """
        pointId = self.vtkPoints.InsertNextPoint(point[:])
        self.vtkPointsId.InsertNextValue(id)
        
        self.vtkCells.InsertNextCell(1)
        self.vtkCells.InsertCellPoint(pointId)
        self.vtkCells.Modified()
        self.vtkPoints.Modified()
        self.vtkPointsId.Modified()

    def clearPoints(self):
        """清除点云"""
        self.vtkPoints = vtk.vtkPoints()   # 点
        self.vtkCells = vtk.vtkCellArray() # 单元
        self.vtkPointsId = vtk.vtkDoubleArray()  # 存放砾石Id的数组
        self.vtkPointsId.SetName('RockIdArray')  # 名字
        # 数据集设置属性
        self.vtkPolyData.SetPoints(self.vtkPoints)
        self.vtkPolyData.SetVerts(self.vtkCells)
        self.vtkPolyData.GetPointData().SetScalars(self.vtkPointsId)  # 设置标量，即id
        self.vtkPolyData.GetPointData().SetActiveScalars('RockIdArray')
