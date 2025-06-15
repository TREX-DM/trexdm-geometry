import vtk
import pyg4ometry
from pyg4ometry import geant4 as g4

import pyg4ometry.geant4 as g4
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

copperVesselSolid = g4.solid.Tubs(
    name = "copperVesselSolid",
    pRMin=0,
    pRMax=vesselRadius + vesselThickness,
    pDz=vesselLength + 2*vesselThickness,
    pSPhi=0,
    pDPhi=360,
    aunit="deg",
    lunit="mm",
    registry=reg
)

_calibrationHoleTube = g4.solid.Tubs(
    name = "calibrationHoleTube",
    pRMin=0,
    pRMax=calibrationHoleRadius,
    pDz=vesselThickness*2, # TODO: check this
    pSPhi=0,
    pDPhi=360,
    aunit="deg",
    lunit="mm",
    registry=reg
)

calibrationHoleSolid = g4.solid.Intersection(
    "calibrationHoleSolid",
    g4.solid.Tubs(
        name="copperVesselRing",
        pRMin=vesselRadius,
        pRMax=vesselRadius + vesselThickness,
        pDz=vesselLength + 2*vesselThickness,
        pSPhi=0,
        pDPhi=360,
        aunit="deg",
        lunit="mm",
        registry=reg
    ),
    _calibrationHoleTube,
    [[0,90*3.1416/180,0], calibrationHolePos1], # rotate it to be perpendicular to the vessel wall and move it to the vessel wall. set zpos to the final location???
    reg
) # TODO??: hacer la interseccion al revés para obtener el calibrationHoleSolid con referencia en el centro del solido resultante

gasTube = g4.solid.Tubs(
    name = "gasTube",
    pRMin=0,
    pRMax=vesselRadius,
    pDz=vesselLength,
    pSPhi=0,
    pDPhi=360,
    aunit="deg",
    lunit="mm",
    registry=reg
)

Zero3vector = [0,0,0]
gasSolid_1 = g4.solid.Union(
    "gasSolid_1",
    gasTube,
    calibrationHoleSolid,
    [Zero3vector, Zero3vector], # calibrationHoleSolid is positioned at calibrationHolePos1 at creation
    reg
)

gasSolid = g4.solid.Union(
    name="gasSolid",
    obj1=gasSolid_1,
    obj2=calibrationHoleSolid,
    tra2=[Zero3vector, [0,0,-160]], # calibrationHoleSolid is positioned at calibrationHolePos1 at creation, so we need to move it to calibrationHolePos2
    registry=reg
)

copperVesselVolume = g4.LogicalVolume(copperVesselSolid, copper, "copperVesselVolume", reg)
gasVolume = g4.LogicalVolume(gasSolid, air, "gasVolume", reg)

gasPhysical = g4.PhysicalVolume(
    rotation=[0,0,0],
    position=[0,0,0],
    name="gasPV",
    logicalVolume=gasVolume,
    motherVolume=copperVesselVolume,
    registry=reg
)

copperCalShieldingTube = g4.solid.Tubs(
    name = "copperCalShieldingTube",
    pRMin=0,
    pRMax=calibrationShieldingRadius,
    pDz=calibrationShieldingLength,
    pSPhi=0,
    pDPhi=360,
    aunit="deg",
    lunit="mm",
    registry=reg
)
copperCalShieldingCutBox = g4.solid.Box(
    name = "copperCalShieldingCutBox",
    pX=calibrationShieldingCutLength,
    pY=calibrationShieldingCutHeight,
    pZ=calibrationShieldingCutThickness,
    lunit="mm",
    registry=reg
)

copperCalShieldingSolid = g4.solid.Subtraction(
    name = "copperCalShieldingSolid",
    obj1=copperCalShieldingTube,
    obj2=copperCalShieldingCutBox,
    tra2=[[0,90*3.1416/180,0], [calibrationShieldingCutSeparation+0.5*calibrationShieldingCutThickness,0,0]],
    registry=reg
)

copperCalShieldingVolume = g4.LogicalVolume(copperCalShieldingSolid, copper, "copperCalShieldingVolume", reg)


calibrationShieldingRealPos1 = [calibrationShieldingPosX, -calibrationShieldingShift, calibrationShieldingPosZ]
calibrationShieldingRealPos2 = [calibrationShieldingPosX, -calibrationShieldingShift, -calibrationShieldingPosZ]
calibrationShieldingParkingPos1 = [calibrationShieldingPosX, 0, calibrationShieldingPosZ]
calibrationShieldingParkingPos2 = [calibrationShieldingPosX, 0, -calibrationShieldingPosZ]
copperCalShieldingPhysical1 = g4.PhysicalVolume(
    rotation=[120*3.1416/180,90*3.1416/180,0],
    position=calibrationShieldingParkingPos1,
    name="copperCalShieldingPV1",
    logicalVolume=copperCalShieldingVolume,
    motherVolume=gasVolume,
    registry=reg
)
copperCalShieldingPhysical2 = g4.PhysicalVolume(
    rotation=[120*3.1416/180,90*3.1416/180,0],
    position=calibrationShieldingParkingPos2,
    name="copperCalShieldingPV2",
    logicalVolume=copperCalShieldingVolume,
    motherVolume=gasVolume,
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
    #v.addSolid(copperVesselSolid)
    v.addLogicalVolumeRecursive(gasVolume)
    
    
    v.addAxes(200)
    v.view()

