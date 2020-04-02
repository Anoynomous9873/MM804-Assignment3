import vtk
import sys

###############################################################################
# Read the file and calculate the normals
panther = vtk.vtkSTLReader() # to read 3D models
panther.SetFileName("panter.stl")
normals = vtk.vtkPolyDataNormals()
normals.SetInputConnection(panther.GetOutputPort())


###############################################################################
# Create a plane, set the origin, and the normal
plane = vtk.vtkPlane() # create a plane
plane.SetOrigin(0, 0, 0)
plane.SetNormal(0, -1, -1) # normals through which the plane shall pass from the model
print("plane info: ", plane)


###############################################################################
# Create a var that will store the clipped part
clipper = vtk.vtkClipPolyData() # clipped data variable
clipper.SetInputConnection(normals.GetOutputPort()) # define output
clipper.SetClipFunction(plane)
clipper.GenerateClipScalarsOn()
clipper.GenerateClippedOutputOn()
clipper.SetValue(0) # clipper value

clipMapper = vtk.vtkPolyDataMapper() # clip mapper
clipMapper.SetInputConnection(clipper.GetOutputPort())
clipMapper.ScalarVisibilityOff()
clipActor = vtk.vtkActor()
clipActor.SetMapper(clipMapper)
clipActor.GetProperty().SetColor(1,0,0) # color set to red


###############################################################################
# Display the intersection area between plane and the model
cutEdges = vtk.vtkCutter() # used for showing the intersection
cutEdges.SetInputConnection(normals.GetOutputPort())
cutEdges.SetCutFunction(plane)
cutEdges.GenerateCutScalarsOn()
cutEdges.SetValue(0, 0)
cutStrips = vtk.vtkStripper()
cutStrips.SetInputConnection(cutEdges.GetOutputPort())
cutStrips.Update()
cutPoly = vtk.vtkPolyData()
cutPoly.SetPoints(cutStrips.GetOutput().GetPoints())
cutPoly.SetPolys(cutStrips.GetOutput().GetLines())


###############################################################################
# To display the intersection area between interploation and surface
cutTriangles = vtk.vtkTriangleFilter()
cutTriangles.SetInputData(cutPoly)
cutMapper = vtk.vtkPolyDataMapper()
cutMapper.SetInputData(cutPoly)
cutMapper.SetInputConnection(cutTriangles.GetOutputPort())
cutActor = vtk.vtkActor()
cutActor.SetMapper(cutMapper)
cutActor.GetProperty().SetColor(1,1,1)


###############################################################################
# Display interpolated area
restMapper = vtk.vtkPolyDataMapper()
restMapper.SetInputData(clipper.GetClippedOutput())
restMapper.ScalarVisibilityOff()
restActor = vtk.vtkActor()
restActor.SetMapper(restMapper)
restActor.GetProperty().SetRepresentationToWireframe() # display data in wireframe format


###############################################################################
# Displaying the plane of intersection
print('GetBounds: ', clipActor.GetBounds()); 
sample = vtk.vtkSampleFunction()
sample.SetImplicitFunction(plane)
sample.SetModelBounds(clipActor.GetBounds())
sample.SetSampleDimensions(50, 50, 50)
sample.ComputeNormalsOff()

# contour
surface = vtk.vtkContourFilter()
surface.SetInputConnection(sample.GetOutputPort())
surface.SetValue(0, 0.5) # provide the clipping plane more vividly (the default value is 0)

# plane mapper
planemapper = vtk.vtkPolyDataMapper()
planemapper.SetInputConnection(surface.GetOutputPort())
planemapper.ScalarVisibilityOff()
planeActor = vtk.vtkActor()
planeActor.SetMapper(planemapper)
planeActor.GetProperty().EdgeVisibilityOn()
planeActor.GetProperty().SetEdgeColor(0, 1, 0) # set the color to green

###############################################################################
# Set legends using text actor
txtActor = vtk.vtkTextActor()
txtActor.SetInput("Red: Surface    Green: Cutting Plane     White: Intersection     Lines: Wireframe")
txtprop=txtActor.GetTextProperty()
txtprop.SetFontFamilyToArial()
txtprop.SetFontSize(20)
txtprop.SetColor(1,1,0) # set text color to yellow
txtActor.SetDisplayPosition(20,30)


###############################################################################
# Number of vertices 
polydata = panther.GetOutput().GetNumberOfPoints ()
print("No. of vertices of the model: ", polydata)
panther.Update()

rest = cutEdges.GetOutput().GetNumberOfPoints ()
print("No. of vertices of intersection: ", rest)

clippoints = clipper.GetOutput().GetNumberOfPoints ()
print("No. of vertices of model & intersection: ", clippoints)
clipper.Update()

rest = cutEdges.GetOutput().GetNumberOfPoints ()
print("No. of vertices of remaining part: ", rest)


###############################################################################
# Render on the screen
ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
renWin.SetSize(1920, 1080)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

# render the actors
ren.AddActor(clipActor)
ren.AddActor(cutActor)
ren.AddActor(restActor)
ren.AddActor(planeActor)
ren.AddActor(txtActor)

iren.Initialize()
renWin.Render()

# Print the vtk and python version
print(vtk.vtkVersion.GetVTKSourceVersion())
print("Python version:",sys.version)

iren.Start()