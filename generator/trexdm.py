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


LEFT_CALIBRATION_OPEN = True
RIGHT_CALIBRATION_OPEN = True
LEFT_GEM = True
RIGHT_GEM = False
GAS = "Neon2%Isobutane1.1bar"
CATHODE_TYPE = "wired"  # "wired" or "plain"
SIMPLIFY_MM_GEOMETRY = False



reg = g4.Registry()

galactic = g4.nist_material_2geant4Material("G4_Galactic")
# world solid and logical
ws   = g4.solid.Box("ws",5,5,5,reg, "m")
world  = g4.LogicalVolume(ws, galactic,"world",reg)

# Generate the assemblies
shielding.generate_shielding_assembly_by_parts(registry=reg)
vessel.generate_vessel_assembly(registry=reg, left_calibration_is_open=LEFT_CALIBRATION_OPEN, right_calibration_is_open=RIGHT_CALIBRATION_OPEN, gas=GAS)
micromegas.generate_micromegas_assembly(registry=reg, is_right_side=True, simple_geometry=SIMPLIFY_MM_GEOMETRY)
if LEFT_GEM or RIGHT_GEM:
    gem.generate_gem_assembly(registry=reg, is_right_side=True)
fieldcage.generate_fieldcage_assembly(registry=reg, cathode_type=CATHODE_TYPE)

shielding_assembly = utils.get_logical_volume_by_name("shielding_assembly", reg)
vessel_assembly = utils.get_logical_volume_by_name("vessel_assembly", reg)
micromegas_assembly = utils.get_logical_volume_by_name("micromegas_assembly", reg)
gem_assembly = utils.get_logical_volume_by_name("gem_assembly", reg)
fieldcage_assembly = utils.get_logical_volume_by_name("fieldcage_assembly", reg)

# Find the logical volumes needed for mounting the assemblies together
outerGas_LV = utils.get_logical_volume_by_name("outerGas_LV", reg)
innerGas_LV = utils.get_logical_volume_by_name("gas_LV", reg)

gem_position_z = vessel.vesselLength/2 - micromegas.capSupportFinalHeight - micromegas.mMBaseThickness  - micromegas.mMBoardThickness - gem.gemmMSeparatorThickness - gem.gemKaptonFoilThickness/2
mM_position_z = vessel.vesselLength/2 - micromegas.capSupportFinalHeight - 0.5*micromegas.mMBaseThickness

# === CREATE THE SENSITIVE GAS VOLUME ===
sensitiveGasWidth = micromegas.mMLength
if CATHODE_TYPE == "plain":
    cathodeSideThickness = fieldcage.cathodeKaptonThickness + fieldcage.cathodeCuThickness*2
else:  # wired cathode
    cathodeSideThickness = 0 #fieldcage.cathodeWireRadius*2

driftLeftGasGap = (gem_position_z - gem.gemKaptonFoilThickness/2 - gem.gemCopperFoilThickness) - cathodeSideThickness #(fieldcage.cathodeKaptonThickness/2 + fieldcage.cathodeCuThickness)
transferGasGap = gem.gemmMSeparatorThickness - gem.gemCopperFoilThickness
driftLeftGas0 = g4.solid.Box(
    name="driftLeftGas0",
    pX=sensitiveGasWidth, # 206 mm because cathode frame is inside active gas volume so I need to avoid that overlap
    pY=sensitiveGasWidth,
    pZ=driftLeftGasGap,
    registry=reg,
    lunit="mm"
)
cathodeFrameSolid = utils.get_solid_by_name("cathodeFrame", reg)
sideSeparatorSolid = utils.get_solid_by_name("sideSeparator", reg)
cathodeFeedThroughSolid = utils.get_solid_by_name("cathodeFeedthrough", reg)
cathodeWired = utils.get_solid_by_name("cathodeWiredFull", reg)
driftLeftGas1 = g4.solid.Subtraction(
    name="driftLeftGas1",
    obj1=driftLeftGas0,
    obj2=cathodeFrameSolid,
    tra2=[[0, 0, 0], [0, 0, -driftLeftGasGap/2]],
    registry=reg
)
driftLeftGas2 = g4.solid.Subtraction(
    name="driftLeftGas2",
    obj1=driftLeftGas1,
    obj2=sideSeparatorSolid,
    tra2=[[0, 0, 0], [0, 0, -driftLeftGasGap/2]],
    registry=reg
)

cathodeFeedThroughPosition = utils.get_position_of_physical_volume("cathodeFeedthrough", reg)
cathodeFeedThroughPosition[2] -= driftLeftGasGap/2 # relative to driftLeftGas1 center
cathodeFeedThroughRotation = utils.get_rotation_of_physical_volume("cathodeFeedthrough", reg)
driftLeftGas3 = g4.solid.Subtraction(
    name="driftLeftGas3",
    obj1=driftLeftGas2,
    obj2=cathodeFeedThroughSolid,
    tra2=[cathodeFeedThroughRotation, cathodeFeedThroughPosition],
    registry=reg
) 
#rotation=[90*np.pi/180, 0, 0],
#position=[-cathodeWireLength/2+first_wire_distance_to_frame, 0, cathodeWireRadius],
cathodeWiredPosition = utils.get_position_of_physical_volume("cathodeWired", reg)
cathodeWiredPosition[2] -= driftLeftGasGap/2 # relative to driftLeftGas2 center
cathodeWiredRotation = utils.get_rotation_of_physical_volume("cathodeWired", reg)
driftLeftGas = g4.solid.Subtraction(
    name="driftLeftGas",
    obj1=driftLeftGas3,
    obj2=cathodeWired,
    tra2=[cathodeWiredRotation, cathodeWiredPosition],
    registry=reg
)
transferGasSolid = g4.solid.Box(
    name="transferGasSolid",
    pX=sensitiveGasWidth,
    pY=sensitiveGasWidth,
    pZ=transferGasGap,
    registry=reg,
    lunit="mm"
)

sensitiveGasLeft = g4.solid.Union(
    name="sensitiveGasLeft",
    obj1=driftLeftGas,
    obj2=transferGasSolid,
    tra2=[[0, 0, 0], [0, 0, driftLeftGasGap/2 + gem.gemCopperFoilThickness*2 + gem.gemKaptonFoilThickness + transferGasGap/2]],
    registry=reg
)

driftRightGasGap = mM_position_z - micromegas.mMBaseThickness/2 - micromegas.mMBoardThickness 
driftRightGas0 = g4.solid.Box(
    name="driftRightGas0",
    pX=sensitiveGasWidth,
    pY=sensitiveGasWidth,
    pZ=driftRightGasGap,
    registry=reg,
    lunit="mm"
)

driftRightGas1 = g4.solid.Subtraction(
    name="driftRightGas1",
    obj1=driftRightGas0,
    obj2=cathodeFrameSolid,
    tra2=[[0, 0, 0], [0, 0, driftRightGasGap/2]],
    registry=reg
)

driftRightGas2 = g4.solid.Subtraction(
    name="driftRightGas2",
    obj1=driftRightGas1,
    obj2=sideSeparatorSolid,
    tra2=[[0, 0, 0], [0, 0, driftRightGasGap/2]],
    registry=reg
)

cathodeFeedThroughPosition = utils.get_position_of_physical_volume("cathodeFeedthrough", reg)
cathodeFeedThroughPosition[2] += driftRightGasGap/2 # relative to driftRightGas1 center
cathodeFeedThroughRotation = utils.get_rotation_of_physical_volume("cathodeFeedthrough", reg)
driftRightGas3 = g4.solid.Subtraction(
    name="driftRightGas3",
    obj1=driftRightGas2,
    obj2=cathodeFeedThroughSolid,
    tra2=[cathodeFeedThroughRotation, cathodeFeedThroughPosition],
    registry=reg
)

cathodeWiredPosition = utils.get_position_of_physical_volume("cathodeWired", reg)
cathodeWiredPosition[2] += driftRightGasGap/2 # relative to driftRightGas2 center
cathodeWiredRotation = utils.get_rotation_of_physical_volume("cathodeWired", reg)
driftRightGas = g4.solid.Subtraction(
    name="driftRightGas",
    obj1=driftRightGas3,
    obj2=cathodeWired,
    tra2=[cathodeWiredRotation, cathodeWiredPosition],
    registry=reg
)

sensitiveGasRight = driftRightGas # no transfer gap on right side (no gem)

sensitiveGasBothSides = g4.solid.Union(
    name="sensitiveGasBothSides",
    obj1=sensitiveGasLeft,
    obj2=sensitiveGasRight,
    tra2=[[0, np.pi, 0], [0, 0, -(driftLeftGasGap/2 + cathodeSideThickness)]],
    registry=reg
)

gas_material = innerGas_LV.material
sensitiveGasLeft_LV = g4.LogicalVolume(
    name="sensitiveGasLeft_LV",
    solid=sensitiveGasLeft,
    material=gas_material,
    registry=reg
)

sensitiveGasRight_LV = g4.LogicalVolume(
    name="sensitiveGasRight_LV",
    solid=sensitiveGasRight,
    material=gas_material,
    registry=reg
)

sensitiveGasLeft_PV = g4.PhysicalVolume(
    name="sensitiveGasLeft",
    logicalVolume=sensitiveGasLeft_LV,
    motherVolume=innerGas_LV,
    rotation=[0, 0, 0],
    position=[0, 0, driftLeftGasGap/2 + cathodeSideThickness],
    registry=reg
)

sensitiveGasRight_PV = g4.PhysicalVolume(
    name="sensitiveGasRight",
    logicalVolume=sensitiveGasRight_LV,
    motherVolume=innerGas_LV,
    rotation=[0, 0, 0],
    position=[0, 0, -(driftRightGasGap/2 + cathodeSideThickness)],
    registry=reg
)

# Create the physical volumes

if RIGHT_GEM:
    gemRight_PV = g4.PhysicalVolume(
        name="gemRight",
        logicalVolume=gem_assembly,
        motherVolume=innerGas_LV,
        rotation=[0, 0, 0],
        position=[0, 0, -gem_position_z],
        registry=reg
    )

micromegasRight_PV = g4.PhysicalVolume(
    name="micromegasRight",
    logicalVolume=micromegas_assembly,
    motherVolume=innerGas_LV,
    rotation=[0, 0, 0],
    position=[0, 0, -mM_position_z],
    registry=reg
)

if LEFT_GEM:
    gemLeft_PV = g4.PhysicalVolume(
        name="gemLeft",
        logicalVolume=gem_assembly,
        motherVolume=innerGas_LV,
        rotation=[np.pi, 0, 0],
        position=[0, 0, gem_position_z],
        registry=reg
    )

micromegasLeft_PV = g4.PhysicalVolume(
    name="micromegasLeft",
    logicalVolume=micromegas_assembly,
    motherVolume=innerGas_LV,
    rotation=[np.pi, 0, 0],
    position=[0, 0, mM_position_z],
    registry=reg
)

vesselassembly_PV = g4.PhysicalVolume(
    name="vesselassembly",
    logicalVolume=vessel_assembly,
    motherVolume=outerGas_LV,
    rotation=[0, 0, 0],
    position=[0, 0, 0],
    registry=reg
)

shielding_PV = g4.PhysicalVolume(
    name="shielding",
    logicalVolume=shielding_assembly,
    motherVolume=world,
    rotation=[0, 0, 0],
    position=[0, 0, 0],
    registry=reg
)

fieldcage_PV = g4.PhysicalVolume(
    name="fieldcage",
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
defaultName = f"trexdm_{GAS}_cathode-{CATHODE_TYPE}_GEM-{'left' if LEFT_GEM else ''}{'-right' if RIGHT_GEM else ''}_leftCalib-{'open' if LEFT_CALIBRATION_OPEN else 'closed'}_rightCalib-{'open' if RIGHT_CALIBRATION_OPEN else 'closed'}{'_simplifiedMM' if SIMPLIFY_MM_GEOMETRY else ''}.gdml"
parser.add_argument("-f", "--file", type=str, default=defaultName, help="Output GDML file name")

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
