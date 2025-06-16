import vtk
import pyg4ometry
from pyg4ometry import geant4 as g4
import numpy as np

import vessel
from gem import generate_gem_assembly
from micromegas import generate_micromegas_assembly


worldSolid = g4.solid.Box(
    name="worldSolid",
    pX=5,
    pY=5,
    pZ=5,
    lunit="m",
    registry=vessel.reg
)

world_LV = g4.LogicalVolume(
    name="world_LV",
    solid=worldSolid,
    material=vessel.air,
    registry=vessel.reg
)


vessel_LV = g4.LogicalVolume(
    name="vessel_LV",
    solid=vessel.vesselSolid,
    material=vessel.copper,
    registry=vessel.reg
)

gas_LV = g4.LogicalVolume(
    name="gas_LV",
    solid=vessel.gasSolid,
    material=vessel.air,
    registry=vessel.reg
)

generate_gem_assembly(registry=vessel.reg, is_right_side=True)
generate_micromegas_assembly(registry=vessel.reg, is_right_side=True)
gem_assembly = vessel.reg.findLogicalVolumeByName("gem_assembly")[0]
micromegas_assembly = vessel.reg.findLogicalVolumeByName("micromegas_assembly")[0]

vessel_PV = g4.PhysicalVolume(
    name="vessel_PV",
    logicalVolume=vessel_LV,
    motherVolume=world_LV,
    position=[0, 0, 0],
    rotation=[0, 0, 0],
    registry=vessel.reg
)
gas_PV = g4.PhysicalVolume(
    name="gas_PV",
    logicalVolume=gas_LV,
    motherVolume=world_LV,
    position=[0, 0, 0],
    rotation=[0, 0, 0],
    registry=vessel.reg
)
gemRight_PV = g4.PhysicalVolume(
    name="gemRight_PV",
    logicalVolume=gem_assembly,
    motherVolume=gas_LV,
    rotation=[0, 0, 0],
    position=[0, 0, -(vessel.vesselLength/2 - 84.2 - 4 - 5.5)],
    registry=vessel.reg
)
micromegasRight_PV = g4.PhysicalVolume(
    name="micromegasRight_PV",
    logicalVolume=micromegas_assembly,
    motherVolume=gas_LV,
    rotation=[0, 0, 0],
    position=[0, 0, -(vessel.vesselLength/2 - 84.2 - 0.5*4)],
    registry=vessel.reg
)
gemLeft_PV = g4.PhysicalVolume(
    name="gemLeft_PV",
    logicalVolume=gem_assembly,
    motherVolume=gas_LV,
    rotation=[np.pi, 0, 0],
    position=[0, 0, vessel.vesselLength/2 - 84.2 - 4 - 5.5],
    registry=vessel.reg
)

micromegasLeft_PV = g4.PhysicalVolume(
    name="micromegasLeft_PV",
    logicalVolume=micromegas_assembly,
    motherVolume=gas_LV,
    rotation=[np.pi, 0, 0],
    position=[0, 0, vessel.vesselLength/2 - 84.2 - 0.5*4],
    registry=vessel.reg
)


v = pyg4ometry.visualisation.VtkViewerColouredMaterial()
v.addLogicalVolume(world_LV)
v.addAxes(500)
v.view()
