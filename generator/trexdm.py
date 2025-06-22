import vtk
import pyg4ometry
from pyg4ometry import geant4 as g4
import numpy as np

import vessel
import shielding
import gem
import micromegas
import fieldcage

reg = g4.Registry()

galactic = g4.MaterialPredefined("G4_Galactic")
# world solid and logical
ws   = g4.solid.Box("ws",5,5,5,reg, "m")
wl   = g4.LogicalVolume(ws, galactic,"wl",reg)

# Generate the assemblies
shielding.generate_shielding_assembly(registry=reg)
vessel.generate_vessel_assembly(registry=reg)
micromegas.generate_micromegas_assembly(registry=reg, is_right_side=True)
gem.generate_gem_assembly(registry=reg, is_right_side=True)
fieldcage.generate_fieldcage_assembly(registry=reg)

shielding_assembly = reg.findLogicalVolumeByName("shielding_assembly")[0]
vessel_assembly = reg.findLogicalVolumeByName("vessel_assembly")[0]
micromegas_assembly = reg.findLogicalVolumeByName("micromegas_assembly")[0]
gem_assembly = reg.findLogicalVolumeByName("gem_assembly")[0]
fieldcage_assembly = reg.findLogicalVolumeByName("fieldcage_assembly")[0]

# Find the logical volumes needed for mounting the assemblies together
outerGas_LV = reg.findLogicalVolumeByName("outerGasVolume")[0]
innerGas_LV = reg.findLogicalVolumeByName("gas_LV")[0]


# Create the physical volumes
gemRight_PV = g4.PhysicalVolume(
    name="gemRight_PV",
    logicalVolume=gem_assembly,
    motherVolume=innerGas_LV,
    rotation=[0, 0, 0],
    position=[0, 0, -(vessel.vesselLength/2 - micromegas.mMTapSeparatorFinalHeight - micromegas.mMBaseThickness - gem.gemmMSeparatorThickness - gem.gemKaptonFoilThickness)],
    registry=reg
)
micromegasRight_PV = g4.PhysicalVolume(
    name="micromegasRight_PV",
    logicalVolume=micromegas_assembly,
    motherVolume=innerGas_LV,
    rotation=[0, 0, 0],
    position=[0, 0, -(vessel.vesselLength/2 - micromegas.mMTapSeparatorFinalHeight - 0.5*micromegas.mMBaseThickness)],
    registry=reg
)
gemLeft_PV = g4.PhysicalVolume(
    name="gemLeft_PV",
    logicalVolume=gem_assembly,
    motherVolume=innerGas_LV,
    rotation=[np.pi, 0, 0],
    position=[0, 0, vessel.vesselLength/2 - micromegas.mMTapSeparatorFinalHeight - micromegas.mMBaseThickness - gem.gemmMSeparatorThickness - gem.gemKaptonFoilThickness],
    registry=reg
)

micromegasLeft_PV = g4.PhysicalVolume(
    name="micromegasLeft_PV",
    logicalVolume=micromegas_assembly,
    motherVolume=innerGas_LV,
    rotation=[np.pi, 0, 0],
    position=[0, 0, vessel.vesselLength/2 - micromegas.mMTapSeparatorFinalHeight - 0.5*micromegas.mMBaseThickness],
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

fieldcage_PV = g4.PhysicalVolume(
    name="fieldcage_PV",
    logicalVolume=fieldcage_assembly,
    motherVolume=innerGas_LV,
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
