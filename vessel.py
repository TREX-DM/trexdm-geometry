import vtk
import pyg4ometry
from pyg4ometry import geant4 as g4
from pyg4ometry import transformation as tf
import pyg4ometry.geant4 as g4
import numpy as np
reg  = g4.Registry()

copper = g4.nist_material_2geant4Material("G4_Cu", reg)
lead = g4.nist_material_2geant4Material("G4_Pb", reg)
air = g4.nist_material_2geant4Material("G4_AIR", reg)

vesselRadius = 192.5
vesselLength = 530
vesselThickness = 60

calibrationHoleRadius = 20

calibrationHolePos1 = [vesselRadius+0.5*vesselThickness, 0, 80]
calibrationHolePos2 = [vesselRadius+0.5*vesselThickness, 0, -80] # x = vesselRadius+0.5*vesselThickness, why not ???

calibrationShieldingRadius = 25
calibrationShieldingLength = 60

calibrationShieldingCutLength = 60.1 # extra 0.1 mm to avoid precision errors in subtraction
calibrationShieldingCutHeight = 24
calibrationShieldingCutThickness = 3
calibrationShieldingCutSeparation = 22

calibrationShieldingPosX = 158.5
calibrationShieldingShift = 7.3
calibrationShieldingPosZ = 95.5

copperVesselTubeSolid = g4.solid.Tubs(
    name = "copperVesselTubeSolid",
    pRMin=vesselRadius,
    pRMax=vesselRadius + vesselThickness,
    pDz=vesselLength,
    pSPhi=0,
    pDPhi=360,
    aunit="deg",
    lunit="mm",
    registry=reg
)

copperVesselEndCapSolid = g4.solid.Tubs(
    name = "copperVesselEndCapSolid",
    pRMin=0,
    pRMax=vesselRadius + vesselThickness,
    pDz=vesselThickness,
    pSPhi=0,
    pDPhi=360,
    aunit="deg",
    lunit="mm",
    registry=reg
)

copperVesselSolid0 = g4.solid.Union(
    name = "copperVesselSolid0",
    obj1 = copperVesselTubeSolid,
    obj2 = copperVesselEndCapSolid,
    tra2 = [[0, 0, 0], [0, 0, -(vesselLength/2 + 0.5*vesselThickness)]],
    registry=reg
)
copperVesselSolid = g4.solid.Union(
    name = "copperVesselSolid",
    obj1 = copperVesselSolid0,
    obj2 = copperVesselEndCapSolid,
    tra2 = [[0, 0, 0], [0, 0, vesselLength/2 + 0.5*vesselThickness]],
    registry=reg
)

calibrationExternalTapLength = 10
calibrationExternalTapRadius = 40
calibrationExternalTap = g4.solid.Tubs(
    name = "calibrationExternalTap",
    pRMin=0,
    pRMax=calibrationExternalTapRadius,
    pDz=calibrationExternalTapLength,
    pSPhi=0,
    pDPhi=360,
    aunit="deg",
    lunit="mm",
    registry=reg
)

calibrationInternalTapLength = 5
calibrationInternalTapRadius = 25
calibrationInternalTap = g4.solid.Tubs(
    name = "calibrationInternalTap",
    pRMin=0,
    pRMax=calibrationInternalTapRadius,
    pDz=calibrationInternalTapLength,
    pSPhi=0,
    pDPhi=360,
    aunit="deg",
    lunit="mm",
    registry=reg
)

copperVesselSolid_LE = g4.solid.Union(
    name = "copperVesselSolid_LE",
    obj1 = copperVesselSolid,
    obj2 = calibrationExternalTap,
    tra2 =[[0, 90*3.1416/180, 0], [vesselRadius + vesselThickness + 0.5*calibrationExternalTapLength - 2, 0, +80]],
    registry=reg
)
copperVesselSolid_LERE = g4.solid.Union(
    name = "copperVesselSolid_LERE",
    obj1 = copperVesselSolid_LE,
    obj2 = calibrationExternalTap,
    tra2 = [[0, 90*3.1416/180, 0], [vesselRadius + vesselThickness + 0.5*calibrationExternalTapLength - 2, 0, -80]],
    registry=reg
)
copperVesselSolid_LERE_LI = g4.solid.Union(
    name = "copperVesselSolid_LERE_LI",
    obj1 = copperVesselSolid_LERE,
    obj2 = calibrationInternalTap,
    tra2 = [[0, 90*3.1416/180, 0], [vesselRadius - 0.5*calibrationInternalTapLength, 0, +80]],
    registry=reg
)
copperVesselSolid_LERE_LIRI = g4.solid.Union(
    name = "copperVesselSolid_LERE_LIRI",
    obj1 = copperVesselSolid_LERE_LI,
    obj2 = calibrationInternalTap,
    tra2 = [[0, 90*3.1416/180, 0], [vesselRadius - 0.5*calibrationInternalTapLength, 0, -80]],
    registry=reg
)


sourceContainer = g4.solid.Tubs(
    name = "sourceContainer",
    pRMin=0.5,
    pRMax=1.5,
    pDz=5,
    pSPhi=0,
    pDPhi=360,
    aunit="deg",
    lunit="mm",
    registry=reg
)

calibrationShielding_base = g4.solid.Tubs(
    name = "calibrationShielding_base",
    pRMin=0,
    pRMax=calibrationShieldingRadius,
    pDz=calibrationShieldingLength,
    pSPhi=0,
    pDPhi=360,
    aunit="deg",
    lunit="mm",
    registry=reg
)
calibrationShieldingCutBox = g4.solid.Box(
    name = "calibrationShieldingCutBox",
    pX=calibrationShieldingCutThickness,
    pY=calibrationShieldingCutHeight,
    pZ=calibrationShieldingCutLength,
    lunit="mm",
    registry=reg
)


# create the two solids for the calibration shielding (even if they are the same) because I cannot rotate them with two different angles correctly afterwards...
rot_close = [0, 0, -66.6*3.1416/180]
rot_open = [0, 0, 6.59*3.1416/180]
cutbox_relpos_unrotated = [calibrationShieldingCutSeparation+0.5*calibrationShieldingCutThickness,0, -0.5*calibrationShieldingLength] #-0.5*calibrationShieldingLength is to cut only half of the cilinder
calibrationShieldingCloseSolid = g4.solid.Subtraction(
    name = "calibrationShieldingCloseSolid",
    obj1=calibrationShielding_base,
    obj2=calibrationShieldingCutBox,
    tra2=[rot_close, list(np.sum(tf.tbxyz2matrix(rot_close)*cutbox_relpos_unrotated, axis=1))],
    registry=reg
)
calibrationShieldingOpenSolid = g4.solid.Subtraction(
    name = "calibrationShieldingOpenSolid",
    obj1=calibrationShielding_base,
    obj2=calibrationShieldingCutBox,
    tra2=[rot_open, list(np.sum(tf.tbxyz2matrix(rot_open)*cutbox_relpos_unrotated, axis=1))],
    registry=reg
)



vesselSolid_2 = g4.solid.Union(
    name = "vesselSolid_2",
    obj1 = copperVesselSolid_LERE_LIRI,
    obj2 = calibrationShieldingOpenSolid,
    tra2 = [[0,-90*3.1416/180,0], [vesselRadius-5-0.5*calibrationShieldingCutLength, -9.15, 80-15.68] ],
    registry=reg
)
vesselSolid = g4.solid.Union(
    name = "vesselSolid",
    obj1 = vesselSolid_2,
    obj2 = calibrationShieldingCloseSolid,
    tra2 = [[0,-90*3.1416/180,0], [vesselRadius-5-0.5*calibrationShieldingCutLength, 0, -80]],
    registry=reg
)


gasTube = g4.solid.Tubs(
    name = "gasTube",
    pRMin=0,
    pRMax=vesselRadius, # +0.01 ?
    pDz=vesselLength, # +0.01 ?
    pSPhi=0,
    pDPhi=360,
    aunit="deg",
    lunit="mm",
    registry=reg
)

gasSolid = g4.solid.Subtraction(
    name = "gasSolid",
    obj1=gasTube,
    obj2=vesselSolid,
    tra2=[[0, 0, 0], [0, 0, 0]],
    registry=reg
)

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--vis", action="store_true")
parser.add_argument("--gdml", action="store_true")
args = parser.parse_args()

if args.gdml:
    reg.setWorld(copperVesselVolume.name)
    w = pyg4ometry.gdml.Writer()
    w.addDetector(reg)
    w.write('vessel.gdml')

if args.vis:
    v = pyg4ometry.visualisation.VtkViewer()
    #v.addLogicalVolume(g4.LogicalVolume(gasSolid, air, "gasLogical", reg))
    #v.addSolid(gasSolid)
    """
    v.addSolid(copperVesselSolid_LERE_LIRI)
    v.addSolid(calibrationShieldingSolid,
               rotation=[0, 90*3.1416/180,-6.59*3.1416/180],
               position=[vesselRadius-5-0.5*calibrationShieldingCutLength, -9.15, 80-15.68] # -5 in x to avoid the internal tap
            )
    v.addSolid(calibrationShieldingSolid,
            rotation=[0, 90*3.1416/180, 66.6*3.1416/180],
            position=[vesselRadius-5-0.5*calibrationShieldingCutLength, 0, -80]
    )
    """
    #v.addSolid(vesselSolid)
    #v.addSolid(calibrationShieldingSolid)
    v.addSolid(gasSolid)
    
    v.addAxes(200)
    v.view()

