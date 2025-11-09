import vtk
import pyg4ometry
from pyg4ometry import geant4 as g4
import numpy as np

import vessel
import shielding
import gem
import micromegas
import fieldcage
import utils

reg = g4.Registry()

galactic = g4.MaterialPredefined("G4_Galactic")
# world solid and logical
ws   = g4.solid.Box("ws",5,5,5,reg, "m")
world  = g4.LogicalVolume(ws, galactic,"world",reg)

# Generate the assemblies
shielding.generate_shielding_assembly_by_parts(registry=reg)
vessel.generate_vessel_assembly(registry=reg)
micromegas.generate_micromegas_assembly(registry=reg, is_right_side=True)
gem.generate_gem_assembly(registry=reg, is_right_side=True)
fieldcage.generate_fieldcage_assembly(registry=reg)

shielding_assembly = utils.get_logical_volume_by_name("shielding_assembly", reg)
vessel_assembly = utils.get_logical_volume_by_name("vessel_assembly", reg)
micromegas_assembly = utils.get_logical_volume_by_name("micromegas_assembly", reg)
gem_assembly = utils.get_logical_volume_by_name("gem_assembly", reg)
fieldcage_assembly = utils.get_logical_volume_by_name("fieldcage_assembly", reg)

# Find the logical volumes needed for mounting the assemblies together
outerGas_LV = utils.get_logical_volume_by_name("outerGas_LV", reg)
innerGas_LV = utils.get_logical_volume_by_name("gas_LV", reg)

gem_position_z = vessel.vesselLength/2 - micromegas.capSupportFinalHeight - micromegas.mMBaseThickness  - micromegas.mMBoardThickness - gem.gemmMSeparatorThickness - gem.gemKaptonFoilThickness/2

driftGasGap = (gem_position_z - gem.gemKaptonFoilThickness/2 - gem.gemCopperFoilThickness) - (fieldcage.cathodeKaptonThickness/2 + fieldcage.cathodeCuThickness)
transferGasGap = gem.gemmMSeparatorThickness - gem.gemCopperFoilThickness
driftGasSolid = g4.solid.Box(
    name="driftGasSolid",
    pX=206, # 206 mm because cathode frame is inside active gas volume so I need to avoid that overlap
    pY=206,
    pZ=driftGasGap,
    registry=reg,
    lunit="mm"
)
transferGasSolid = g4.solid.Box(
    name="transferGasSolid",
    pX=206,
    pY=206,
    pZ=transferGasGap,
    registry=reg,
    lunit="mm"
)

sensitiveGasOneSide = g4.solid.Union(
    name="sensitiveGasOneSide",
    obj1=driftGasSolid,
    obj2=transferGasSolid,
    tra2=[[0, 0, 0], [0, 0, driftGasGap/2 + gem.gemCopperFoilThickness*2 + gem.gemKaptonFoilThickness + transferGasGap/2]],
    registry=reg
)

sensitiveGasBothSides = g4.solid.Union(
    name="sensitiveGasBothSides",
    obj1=sensitiveGasOneSide,
    obj2=sensitiveGasOneSide,
    tra2=[[0, np.pi, 0], [0, 0, -(driftGasGap/2 + fieldcage.cathodeKaptonThickness/2 + fieldcage.cathodeCuThickness)]],
    registry=reg
)

gas_material = innerGas_LV.material
sensitiveGasOneSide_LV = g4.LogicalVolume(
    name="sensitiveGasOneSide_LV",
    solid=sensitiveGasOneSide,
    material=gas_material,
    registry=reg
)

sensitiveGasLeft_PV = g4.PhysicalVolume(
    name="sensitiveGasLeft_PV",
    logicalVolume=sensitiveGasOneSide_LV,
    motherVolume=innerGas_LV,
    rotation=[0, 0, 0],
    position=[0, 0, driftGasGap/2 + fieldcage.cathodeKaptonThickness/2 + fieldcage.cathodeCuThickness],
    registry=reg
)

# Create the physical volumes
"""
gemRight_PV = g4.PhysicalVolume(
    name="gemRight_PV",
    logicalVolume=gem_assembly,
    motherVolume=innerGas_LV,
    rotation=[0, 0, 0],
    position=[0, 0, -(vessel.vesselLength/2 - micromegas.capSupportFinalHeight - micromegas.mMBaseThickness - micromegas.mMBoardThickness - gem.gemmMSeparatorThickness - gem.gemKaptonFoilThickness/2)],
    registry=reg
)
"""
micromegasRight_PV = g4.PhysicalVolume(
    name="micromegasRight_PV",
    logicalVolume=micromegas_assembly,
    motherVolume=innerGas_LV,
    rotation=[0, 0, 0],
    position=[0, 0, -(vessel.vesselLength/2 - micromegas.capSupportFinalHeight - 0.5*micromegas.mMBaseThickness)],
    registry=reg
)

gemLeft_PV = g4.PhysicalVolume(
    name="gemLeft_PV",
    logicalVolume=gem_assembly,
    motherVolume=innerGas_LV,
    rotation=[np.pi, 0, 0],
    position=[0, 0, vessel.vesselLength/2 - micromegas.capSupportFinalHeight - micromegas.mMBaseThickness - micromegas.mMBoardThickness - gem.gemmMSeparatorThickness - gem.gemKaptonFoilThickness/2 ],
    registry=reg
)

micromegasLeft_PV = g4.PhysicalVolume(
    name="micromegasLeft_PV",
    logicalVolume=micromegas_assembly,
    motherVolume=innerGas_LV,
    rotation=[np.pi, 0, 0],
    position=[0, 0, vessel.vesselLength/2 - micromegas.capSupportFinalHeight - 0.5*micromegas.mMBaseThickness],
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
    motherVolume=world,
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


reg.setWorld(world.name)


import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--childless", action="store_true", default=False)
parser.add_argument("-f", "--file", type=str, default="trexdm.gdml")

args = parser.parse_args()

w = pyg4ometry.gdml.Writer()
w.addDetector(reg)
w.write(args.file)

if args.childless:
    print("ORIGINAL WL DAUGHTERS LIST:")
    for daughter in world.daughterVolumes:
        print(f"{daughter.name}")
    print("END OF ORIGINAL WL DAUGHTERS LIST")

    """
    reg_noDaughters = g4.Registry()

    # Create a new registry without daughters
    for name, solid in reg.solidDict.items():
        reg_noDaughters.transferSolid(solid)
    for name, material in reg.materialDict.items():
        reg_noDaughters.transferMaterial(material)
    world_noDaughters = g4.LogicalVolume(ws, galactic,"world",reg_noDaughters)
    utils.get_childless_volume(world, world_volume=world_noDaughters, registry=reg_noDaughters)

    reg_noDaughters.setWorld(world_noDaughters.name)
    """

    reg_noDaughters = utils.transfer_childless_world(reg)
    world_noDaughters = reg_noDaughters.getWorldVolume()
    w = pyg4ometry.gdml.Writer()
    w.addDetector(reg_noDaughters)
    name = args.file.split(".gdml")[0] + "_noDaughters.gdml"
    w.write(name)

    """
    gas_wo_daughters = utils.get_solid_by_name("gasSolid-0-17", reg_noDaughters)
    v = pyg4ometry.visualisation.VtkViewerColouredMaterial()
    v.addSolid(gas_wo_daughters)
    v.addAxes(1000)
    v.view()
    """
