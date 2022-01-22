import vtk
class VtkPointCloud:

    def __init__(self, id_Min=-10.0, id_Max=10.0):
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
        pointId = self.vtkPoints.InsertNextPoint(point[:])
        self.vtkPointsId.InsertNextValue(id)
        
        self.vtkCells.InsertNextCell(1)
        self.vtkCells.InsertCellPoint(pointId)
        self.vtkCells.Modified()
        self.vtkPoints.Modified()
        self.vtkPointsId.Modified()

    def clearPoints(self):
        self.vtkPoints = vtk.vtkPoints()   # 点
        self.vtkCells = vtk.vtkCellArray() # 单元
        self.vtkPointsId = vtk.vtkDoubleArray()  # 存放砾石Id的数组
        self.vtkPointsId.SetName('RockIdArray')  # 名字
        # 数据集设置属性
        self.vtkPolyData.SetPoints(self.vtkPoints)
        self.vtkPolyData.SetVerts(self.vtkCells)
        self.vtkPolyData.GetPointData().SetScalars(self.vtkPointsId)  # 设置标量，即id
        self.vtkPolyData.GetPointData().SetActiveScalars('RockIdArray')
