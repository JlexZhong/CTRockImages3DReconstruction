import vtk

reader = vtk.vtkPolyDataReader()
# reader.SetDataScalarTypeToFloat()
reader.SetFileName(r'E:/My Projects/rocks_view/my2.vtk')
reader.Update()

points = vtk.vtkPolyData()
points.SetPoints(reader.GetOutput().GetPoints())  # 获得网格模型中的几何数据：点集

surf = vtk.vtkSurfaceReconstructionFilter()
'''
隐式曲面重建，将曲面看作一个符号距离函数的等值面，曲面内外的距离值的符号相反，而零等值面即为所求的曲面
该方法需要对点云数据进行网格划分，然后估算每个点的切平面和方向，并以每个点与最近的切平面距离来近似表面距离
这样可以得到一个符号距离的体数据
'''
surf.SetInputData(points)
surf.SetNeighborhoodSize(20)
'''
SetNeighborhoodSize设置邻域点的个数，这些邻域点则用于估计每个点的局部切平面，默认为20
能够处理大多数重建问题，个数设置越大，计算消耗时间越长，当点的分部不均匀时，可以适当增加该值
'''
surf.SetSampleSpacing(0.005) # 用于设置划分网格的网格间距，间距越小网格越密集，一般采用默认值
surf.Update()

contour = vtk.vtkContourFilter()  # 提取零等值面即可得到相应的网格
contour.SetInputConnection(surf.GetOutputPort())
contour.SetValue(0, 0.0)
contour.Update()

leftViewport = [0.0, 0.0, 0.5, 1.0]
rightViewport = [0.5, 0.0, 1.0, 1.0]

vertexGlyphFilter = vtk.vtkVertexGlyphFilter()
vertexGlyphFilter.AddInputData(points)
vertexGlyphFilter.Update()
vertexMapper = vtk.vtkPolyDataMapper()
vertexMapper.SetInputData(vertexGlyphFilter.GetOutput())
vertexMapper.ScalarVisibilityOff()

vertexActor = vtk.vtkActor()
vertexActor.SetMapper(vertexMapper)
vertexActor.GetProperty().SetColor(1.0, 0.0, 0.0)

vertexRenderer = vtk.vtkRenderer()
vertexRenderer.AddActor(vertexActor)
vertexRenderer.SetViewport(leftViewport)
vertexRenderer.SetBackground(1.0, 1.0, 1.0)

surfMapper = vtk.vtkPolyDataMapper()
surfMapper.SetInputData(contour.GetOutput())
surfMapper.ScalarVisibilityOff()

surfActor = vtk.vtkActor()
surfActor.SetMapper(surfMapper)
surfActor.GetProperty().SetColor(1.0, 0.0, 0.0)

surfRenderer = vtk.vtkRenderer()
surfRenderer.AddActor(surfActor)
surfRenderer.SetViewport(rightViewport)
surfRenderer.SetBackground(1.0, 1.0, 1.0)

renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(vertexRenderer)
renderWindow.AddRenderer(surfRenderer)
renderWindow.SetSize(640, 320)
renderWindow.Render()
renderWindow.SetWindowName('PolyDataSurfaceReconstruction')

renderWindowInteractor = vtk.vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)
renderWindowInteractor.Initialize()
renderWindowInteractor.Start()

