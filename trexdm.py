import vtk
import pyg4ometry
from pyg4ometry import geant4 as g4
import numpy as np

import vessel
from vessel import generate_vessel_assembly
from shielding import generate_shielding_assembly
from gem import generate_gem_assembly
from micromegas import generate_micromegas_assembly

reg = g4.Registry()

galactic = g4.MaterialPredefined("G4_Galactic")
# world solid and logical
ws   = g4.solid.Box("ws",5,5,5,reg, "m")
wl   = g4.LogicalVolume(ws, galactic,"wl",reg)

generate_shielding_assembly(registry=reg)
generate_gem_assembly(registry=reg, is_right_side=True)
generate_micromegas_assembly(registry=reg, is_right_side=True)
generate_vessel_assembly = generate_vessel_assembly(registry=reg)
gem_assembly = reg.findLogicalVolumeByName("gem_assembly")[0]
micromegas_assembly = reg.findLogicalVolumeByName("micromegas_assembly")[0]
vessel_assembly = reg.findLogicalVolumeByName("vessel_assembly")[0]
shielding_assembly = reg.findLogicalVolumeByName("shielding_assembly")[0]
outerGas_LV = reg.findLogicalVolumeByName("outerGasVolume")[0]
innerGas_LV = reg.findLogicalVolumeByName("gas_LV")[0]



gemRight_PV = g4.PhysicalVolume(
    name="gemRight_PV",
    logicalVolume=gem_assembly,
    motherVolume=innerGas_LV,
    rotation=[0, 0, 0],
    position=[0, 0, -(vessel.vesselLength/2 - 84.2 - 4 - 5.5)],
    registry=reg
)
micromegasRight_PV = g4.PhysicalVolume(
    name="micromegasRight_PV",
    logicalVolume=micromegas_assembly,
    motherVolume=innerGas_LV,
    rotation=[0, 0, 0],
    position=[0, 0, -(vessel.vesselLength/2 - 84.2 - 0.5*4)],
    registry=reg
)
gemLeft_PV = g4.PhysicalVolume(
    name="gemLeft_PV",
    logicalVolume=gem_assembly,
    motherVolume=innerGas_LV,
    rotation=[np.pi, 0, 0],
    position=[0, 0, vessel.vesselLength/2 - 84.2 - 4 - 5.5],
    registry=reg
)

micromegasLeft_PV = g4.PhysicalVolume(
    name="micromegasLeft_PV",
    logicalVolume=micromegas_assembly,
    motherVolume=innerGas_LV,
    rotation=[np.pi, 0, 0],
    position=[0, 0, vessel.vesselLength/2 - 84.2 - 0.5*4],
    registry=reg
)

vesselassembly_PV = g4.PhysicalVolume(
    name="vesselassembly_PV",
    logicalVolume=vessel_assembly,
    motherVolume=outerGas_LV,
    rotation=[0, 0, 0],
    position=[0, 0, 0],
    registry=reg
)

shielding_PV = g4.PhysicalVolume(
    name="shielding_PV",
    logicalVolume=shielding_assembly,
    motherVolume=wl,
    rotation=[0, 0, 0],
    position=[0, 0, 0],
    registry=reg
)


reg.setWorld(wl.name)
w = pyg4ometry.gdml.Writer()
w.addDetector(reg)
w.write('trexdm.gdml')

v = pyg4ometry.visualisation.VtkViewerColouredMaterial()
v.addLogicalVolumeRecursive(wl)
v.addAxes(1000)
v.view()
