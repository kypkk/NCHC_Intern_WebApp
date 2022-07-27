import os

from trame.app import get_server
from trame.ui.vuetify import SinglePageWithDrawerLayout
from trame.widgets import vtk, vuetify, trame

from vtkmodules.vtkCommonDataModel import vtkDataObject
from vtkmodules.vtkFiltersCore import vtkContourFilter
from vtkmodules.vtkFiltersGeneral import vtkWarpVector
from vtkmodules.vtkCommonTransforms import vtkTransform
from vtkmodules.vtkIOXML import vtkXMLUnstructuredGridReader
from vtkmodules.vtkRenderingAnnotation import vtkCubeAxesActor, vtkScalarBarActor
from vtkmodules.vtkInteractionWidgets import vtkScalarBarWidget


from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
)

# Required for interactor initialization
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleSwitch  # noqa

# Required for rendering initialization, not necessary for
# local rendering, but doesn't hurt to include it
import vtkmodules.vtkRenderingOpenGL2  # noqa

CURRENT_DIRECTORY = os.path.abspath(os.path.dirname(__file__))

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

class Representation:
    Points = 0
    Wireframe = 1
    Surface = 2
    SurfaceWithEdges = 3

class LookupTable:
    Rainbow = 0
    Inverted_Rainbow = 1
    Greyscale = 2
    Inverted_Greyscale = 3

# -----------------------------------------------------------------------------
# VTK pipeline
# -----------------------------------------------------------------------------

renderer = vtkRenderer()
renderWindow = vtkRenderWindow()
renderWindow.AddRenderer(renderer)

renderWindowInteractor = vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)
renderWindowInteractor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

# Read Data
reader = vtkXMLUnstructuredGridReader()
reader.SetFileName(os.path.join(CURRENT_DIRECTORY, "./data/1-full_model.vtu"))
reader.Update()

# Extract Array/Field information
dataset_arrays = []
fields = [
    (reader.GetOutput().GetPointData(), vtkDataObject.FIELD_ASSOCIATION_POINTS),
    (reader.GetOutput().GetCellData(), vtkDataObject.FIELD_ASSOCIATION_CELLS),
]
for field in fields:
    field_arrays, association = field
    for i in range(field_arrays.GetNumberOfArrays()):
        array = field_arrays.GetArray(i)
        array_range = array.GetRange()
        dataset_arrays.append(
            {
                "text": array.GetName(),
                "value": i,
                "range": list(array_range),
                "type": association,
            }
        )
default_array = dataset_arrays[0]
default_min, default_max = default_array.get("range")

# Mesh
mesh_mapper = vtkDataSetMapper()
mesh_mapper.SetInputConnection(reader.GetOutputPort())
mesh_actor = vtkActor()
mesh_actor.SetMapper(mesh_mapper)
renderer.AddActor(mesh_actor)

# Mesh: Setup default representation to surface
mesh_actor.GetProperty().SetRepresentationToSurface()
mesh_actor.GetProperty().SetPointSize(1)
mesh_actor.GetProperty().EdgeVisibilityOff()

# Mesh: Apply rainbow color map
mesh_lut = mesh_mapper.GetLookupTable()
mesh_lut.SetHueRange(0.666, 0.0)
mesh_lut.SetSaturationRange(1.0, 1.0)
mesh_lut.SetValueRange(1.0, 1.0)
mesh_lut.Build()

# Mesh: Color by default array
mesh_mapper.SelectColorArray(default_array.get("text"))
mesh_mapper.GetLookupTable().SetRange(default_min, default_max)
if default_array.get("type") == vtkDataObject.FIELD_ASSOCIATION_POINTS:
    mesh_mapper.SetScalarModeToUsePointFieldData()
else:
    mesh_mapper.SetScalarModeToUseCellFieldData()
mesh_mapper.SetScalarVisibility(True)
mesh_mapper.SetUseLookupTableScalarRange(True)

# Contour
contour = vtkContourFilter()
contour.SetInputConnection(reader.GetOutputPort())
contour_mapper = vtkDataSetMapper()
contour_mapper.SetInputConnection(contour.GetOutputPort())
contour_actor = vtkActor()
contour_actor.SetMapper(contour_mapper)
renderer.AddActor(contour_actor)
contour_actor.SetVisibility(0)

# Contour: ContourBy default array
contour_value = 0.5 * (default_max + default_min)
contour.SetInputArrayToProcess(
    0, 0, 0, default_array.get("type"), default_array.get("text")
)
contour.SetValue(0, contour_value)

# Contour: Setup default representation to surface
contour_actor.GetProperty().SetRepresentationToSurface()
contour_actor.GetProperty().SetPointSize(1)
contour_actor.GetProperty().EdgeVisibilityOff()

# Contour: Apply rainbow color map
contour_lut = contour_mapper.GetLookupTable()
contour_lut.SetHueRange(0.666, 0.0)
contour_lut.SetSaturationRange(1.0, 1.0)
contour_lut.SetValueRange(1.0, 1.0)
contour_lut.Build()

# Contour: Color by default array
contour_mapper.SelectColorArray(default_array.get("text"))
contour_mapper.GetLookupTable().SetRange(default_min, default_max)
if default_array.get("type") == vtkDataObject.FIELD_ASSOCIATION_POINTS:
    contour_mapper.SetScalarModeToUsePointFieldData()
else:
    contour_mapper.SetScalarModeToUseCellFieldData()
contour_mapper.SetScalarVisibility(True)
contour_mapper.SetUseLookupTableScalarRange(True)

# WarpVector
warpVector = vtkWarpVector()
warpVector.SetInputConnection(reader.GetOutputPort())
warpVector_mapper = vtkDataSetMapper()
warpVector_mapper.SetInputConnection(warpVector.GetOutputPort())
warpVector_actor = vtkActor()
warpVector_actor.SetMapper(warpVector_mapper)
renderer.AddActor(warpVector_actor)
warpVector_actor.SetVisibility(0)

# warpVector: warpVector By default array
scale_factor = 1
warpVector.SetInputArrayToProcess(
    0, 0, 0, default_array.get("type"), "vector_006"
)
warpVector.SetScaleFactor(scale_factor)


# warpVector: Setup default representation to surface
warpVector_actor.GetProperty().SetRepresentationToSurface()
warpVector_actor.GetProperty().SetPointSize(1)
warpVector_actor.GetProperty().EdgeVisibilityOff()

# warpVector: Apply rainbow color map
warpVector_lut = warpVector_mapper.GetLookupTable()
warpVector_lut.SetHueRange(0.666, 0.0)
warpVector_lut.SetSaturationRange(1.0, 1.0)
warpVector_lut.SetValueRange(1.0, 1.0)
warpVector_lut.Build()

# warpVector: Color by default array
warpVector_mapper.SelectColorArray(default_array.get("text"))
warpVector_mapper.GetLookupTable().SetRange(default_min, default_max)
if default_array.get("type") == vtkDataObject.FIELD_ASSOCIATION_POINTS:
    warpVector_mapper.SetScalarModeToUsePointFieldData()
else:
    warpVector_mapper.SetScalarModeToUseCellFieldData()
warpVector_mapper.SetScalarVisibility(True)
warpVector_mapper.SetUseLookupTableScalarRange(True)

# Cube Axes
transform = vtkTransform()
transform.Translate(1.0, 0.0, 0.0)
cube_axes = vtkCubeAxesActor()
cube_axes.SetUserTransform(transform)
renderer.AddActor(cube_axes)

# Cube Axes: Boundaries, camera, and styling
cube_axes.SetBounds(warpVector_actor.GetBounds())
cube_axes.SetCamera(renderer.GetActiveCamera())
cube_axes.SetFlyModeToOuterEdges()

renderer.ResetCamera()

# create the scalar_bar
scalar_bar = vtkScalarBarActor()
scalar_bar.SetOrientationToHorizontal()
scalar_bar.SetLookupTable(mesh_lut)

renderer.AddActor(scalar_bar)

# -----------------------------------------------------------------------------
# Trame setup
# -----------------------------------------------------------------------------

server = get_server()
state, ctrl = server.state, server.controller

state.setdefault("active_ui", None)

# -----------------------------------------------------------------------------
# Callbacks
# -----------------------------------------------------------------------------

# Cube_Axes_Callback
@state.change("cube_axes_visibility")
def update_cube_axes_visibility(cube_axes_visibility, **kwargs):
    cube_axes.SetVisibility(cube_axes_visibility)
    ctrl.view_update()

# -----------------------------------------------------------------------------
# GUI elements
# -----------------------------------------------------------------------------

def standard_buttons():
    vuetify.VCheckbox(
        v_model=("cube_axes_visibility", True),
        on_icon="mdi-cube-outline",
        off_icon="mdi-cube-off-outline",
        classes="mx-1",
        hide_details=True,
        dense=True,
    )
    vuetify.VCheckbox(
        v_model="$vuetify.theme.dark",
        on_icon="mdi-lightbulb-off-outline",
        off_icon="mdi-lightbulb-outline",
        classes="mx-1",
        hide_details=True,
        dense=True,
    )
    vuetify.VCheckbox(
        v_model=("viewMode", "local"), # VtkRemoteLocalView => {namespace}Mode=['local', 'remote']
        on_icon="mdi-lan-disconnect",
        off_icon="mdi-lan-connect",
        true_value="local",
        false_value="remote",
        classes="mx-1",
        hide_details=True,
        dense=True,
    )
    with vuetify.VBtn(icon=True, click="$refs.view.resetCamera()"):
        vuetify.VIcon("mdi-crop-free")

def pipeline_widget():
    trame.GitTree(
        sources=(
            "pipeline",
            [
                {"id": "1", "parent": "0", "visible": 1, "name": "Mesh"},
                {"id": "2", "parent": "1", "visible": 0, "name": "Contour"},
                {"id": "3", "parent": "1", "visible": 0, "name": "WarpbyVector"},
            ],
        ),
        actives_change=(actives_change, "[$event]"),
        visibility_change=(visibility_change, "[$event]"),
    )

def ui_card(title, ui_name):
    with vuetify.VCard(v_show=f"active_ui == '{ui_name}'"):
        vuetify.VCardTitle(
            title,
            classes="grey lighten-1 py-1 grey--text text--darken-3",
            style="user-select: none; cursor: pointer",
            hide_details=True,
            dense=True,
        )
        content = vuetify.VCardText(classes="py-2")
    return content

def mesh_card():
    with ui_card(title="Mesh", ui_name="mesh"):
        vuetify.VSelect(
            # Representation
            v_model=("mesh_representation", Representation.Surface),
            items=(
                "representations",
                [
                    {"text": "Points", "value": 0},
                    {"text": "Wireframe", "value": 1},
                    {"text": "Surface", "value": 2},
                    {"text": "SurfaceWithEdges", "value": 3},
                ],
            ),
            label="Representation",
            hide_details=True,
            dense=True,
            outlined=True,
            classes="pt-1",
        )
        with vuetify.VRow(classes="pt-2", dense=True):
            with vuetify.VCol(cols="6"):
                vuetify.VSelect(
                    # Color By
                    label="Color by",
                    v_model=("mesh_color_array_idx", 0),
                    items=("array_list", dataset_arrays),
                    hide_details=True,
                    dense=True,
                    outlined=True,
                    classes="pt-1",
                )
            with vuetify.VCol(cols="6"):
                vuetify.VSelect(
                    # Color Map
                    label="Colormap",
                    v_model=("mesh_color_preset", LookupTable.Rainbow),
                    items=(
                        "colormaps",
                        [
                            {"text": "Rainbow", "value": 0},
                            {"text": "Inv Rainbow", "value": 1},
                            {"text": "Greyscale", "value": 2},
                            {"text": "Inv Greyscale", "value": 3},
                        ],
                    ),
                    hide_details=True,
                    dense=True,
                    outlined=True,
                    classes="pt-1",
                )
        vuetify.VSlider(
            # Opacity
            v_model=("mesh_opacity", 1.0),
            min=0,
            max=1,
            step=0.1,
            label="Opacity",
            classes="mt-1",
            hide_details=True,
            dense=True,
        )

def contour_card():
    with ui_card(title="Contour", ui_name="contour"):
        vuetify.VSelect(
            # Contour By
            label="Contour by",
            v_model=("contour_by_array_idx", 0),
            items=("array_list", dataset_arrays),
            hide_details=True,
            dense=True,
            outlined=True,
            classes="pt-1",
        )
        vuetify.VSlider(
            # Contour Value
            v_model=("contour_value", contour_value),
            min=("contour_min", default_min),
            max=("contour_max", default_max),
            step=("contour_step", 0.01 * (default_max - default_min)),
            label="Value",
            classes="my-1",
            hide_details=True,
            dense=True,
        )
        vuetify.VSelect(
            # Representation
            v_model=("contour_representation", Representation.Surface),
            items=(
                "representations",
                [
                    {"text": "Points", "value": 0},
                    {"text": "Wireframe", "value": 1},
                    {"text": "Surface", "value": 2},
                    {"text": "SurfaceWithEdges", "value": 3},
                ],
            ),
            label="Representation",
            hide_details=True,
            dense=True,
            outlined=True,
            classes="pt-1",
        )
        with vuetify.VRow(classes="pt-2", dense=True):
            with vuetify.VCol(cols="6"):
                vuetify.VSelect(
                    # Color By
                    label="Color by",
                    v_model=("contour_color_array_idx", 0),
                    items=("array_list", dataset_arrays),
                    hide_details=True,
                    dense=True,
                    outlined=True,
                    classes="pt-1",
                )
            with vuetify.VCol(cols="6"):
                vuetify.VSelect(
                    # Color Map
                    label="Colormap",
                    v_model=("contour_color_preset", LookupTable.Rainbow),
                    items=(
                        "colormaps",
                        [
                            {"text": "Rainbow", "value": 0},
                            {"text": "Inv Rainbow", "value": 1},
                            {"text": "Greyscale", "value": 2},
                            {"text": "Inv Greyscale", "value": 3},
                        ],
                    ),
                    hide_details=True,
                    dense=True,
                    outlined=True,
                    classes="pt-1",
                )
        vuetify.VSlider(
            # Opacity
            v_model=("contour_opacity", 1.0),
            min=0,
            max=1,
            step=0.1,
            label="Opacity",
            classes="mt-1",
            hide_details=True,
            dense=True,
        )

def warpVector_card():
    with ui_card(title="WarpbyVector", ui_name="WarpbyVector"):
        vuetify.VSelect(
            # Vectors
            label="Vectors",
            v_model=("warp_vectors", 0),
            items=("array_list", dataset_arrays),
            hide_details=True,
            dense=True,
            outlined=True,
            classes="pt-1",
        )
        vuetify.VSlider(
            # Scale factor
            v_model=("scale_factor", scale_factor),
            min=("factor_min", 1),
            max=("factor_max", 100),
            step=("scale_step",  0.0001 * (100 - 1)),
            label="Scale Factor",
            classes="my-1",
            hide_details=True,
            dense=True,
        )
        vuetify.VSelect(
            # Representation
            v_model=("warpVector_representation", Representation.Surface),
            items=(
                "representations",
                [
                    {"text": "Points", "value": 0},
                    {"text": "Wireframe", "value": 1},
                    {"text": "Surface", "value": 2},
                    {"text": "SurfaceWithEdges", "value": 3},
                ],
            ),
            label="Representation",
            hide_details=True,
            dense=True,
            outlined=True,
            classes="pt-1",
        )
        with vuetify.VRow(classes="pt-2", dense=True):
            with vuetify.VCol(cols="6"):
                vuetify.VSelect(
                    # Color By
                    label="Color by",
                    v_model=("warpVector_color_array_idx", 0),
                    items=("array_list", dataset_arrays),
                    hide_details=True,
                    dense=True,
                    outlined=True,
                    classes="pt-1",
                )
            with vuetify.VCol(cols="6"):
                vuetify.VSelect(
                    # Color Map
                    label="Colormap",
                    v_model=("warpVector_color_preset", LookupTable.Rainbow),
                    items=(
                        "colormaps",
                        [
                            {"text": "Rainbow", "value": 0},
                            {"text": "Inv Rainbow", "value": 1},
                            {"text": "Greyscale", "value": 2},
                            {"text": "Inv Greyscale", "value": 3},
                        ],
                    ),
                    hide_details=True,
                    dense=True,
                    outlined=True,
                    classes="pt-1",
                )
        vuetify.VSlider(
            # Opacity
            v_model=("warpVector_opacity", 1.0),
            min=0,
            max=1,
            step=0.1,
            label="Opacity",
            classes="mt-1",
            hide_details=True,
            dense=True,
        )

# -----------------------------------------------------------------------------
# GUI
# -----------------------------------------------------------------------------

with SinglePageWithDrawerLayout(server) as layout:
    layout.title.set_text("App")

    with layout.toolbar:
        # toolbar components
        vuetify.VSpacer()
        vuetify.VDivider(vertical=True, classes="mx-2")
        standard_buttons()

    with layout.drawer as drawer:
        #drawer components
        drawer.width = 325
        pipeline_widget()
        vuetify.VDivider(classes="mb-2")
        mesh_card()
        contour_card()
        warpVector_card()

    with layout.content:
        # content components
        with vuetify.VContainer(
            fluid=True,
            classes="pa-0 fill-height",
        ):
            local_view = vtk.VtkLocalView(renderWindow)
            remote_view = vtk.VtkRemoteView(renderWindow)
            view = local_view
            ctrl.view_update = view.update
            ctrl.view_reset_camera = view.reset_camera
            ctrl.on_server_ready.add(view.update)

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    server.start()
