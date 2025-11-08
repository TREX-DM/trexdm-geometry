import vtk
import pyg4ometry
from pyg4ometry import geant4 as g4
from pyg4ometry import transformation as tf
import pyg4ometry.geant4 as g4
import numpy as np
import utils

vesselRadius = 192.5
vesselLength = 530
vesselThickness = 60

calibrationHoleRadius = 20
calibrationHoleZpos = 80 # z position of the calibration holes, positive and negative
calibrationHolePos1 = [vesselRadius+0.5*vesselThickness, 0, calibrationHoleZpos]
calibrationHolePos2 = [vesselRadius+0.5*vesselThickness, 0, -calibrationHoleZpos] # x = vesselRadius+0.5*vesselThickness, why not ???

calibrationShieldingRadius = 25
calibrationShieldingLength = 30

calibrationShieldingCutLength = calibrationShieldingLength + 0.1 # extra 0.1 mm to avoid precision errors in subtraction
calibrationShieldingCutHeight = 24
calibrationShieldingCutThickness = 3
calibrationShieldingCutSeparation = 22

calibrationShieldingOpenShiftY = -9.15 # shift in y direction of the open shielding, to avoid the calibration hole
calibrationShieldingOpenShiftZ = 15.68 # shift in z direction of the open shielding, to avoid the calibration hole

calibrationExternalTapLength = 10
calibrationExternalTapRadius = 40
calibrationExternalTapPosToVesselDistance = -2

calibrationInternalTapLength = 5
calibrationInternalTapRadius = 25

def generate_vessel_assembly(name="vessel_assembly", registry=None, left_calibration_is_open=True, right_calibration_is_open=False):
    """
    Generates the vessel geometry for the TREX-DM detector.
    Returns a Geant4 Registry containing the vessel geometry.
    """
    # Registry
    if registry is None:
        reg = g4.Registry()
    else:
        reg = registry 
    """  
    copper = g4.MaterialPredefined("G4_Cu")
    air = g4.MaterialPredefined("G4_AIR") 
    """
    copper = g4.nist_material_2geant4Material("G4_Cu")
    air = g4.nist_material_2geant4Material("G4_AIR")
    
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
        tra2 =[[0, 90*np.pi/180, 0], [vesselRadius + vesselThickness + 0.5*calibrationExternalTapLength + calibrationExternalTapPosToVesselDistance, 0, +calibrationHoleZpos]],
        registry=reg
    )
    copperVesselSolid_LERE = g4.solid.Union(
        name = "copperVesselSolid_LERE",
        obj1 = copperVesselSolid_LE,
        obj2 = calibrationExternalTap,
        tra2 = [[0, 90*np.pi/180, 0], [vesselRadius + vesselThickness + 0.5*calibrationExternalTapLength + calibrationExternalTapPosToVesselDistance, 0, -calibrationHoleZpos]],
        registry=reg
    )
    copperVesselSolid_LERE_LI = g4.solid.Union(
        name = "copperVesselSolid_LERE_LI",
        obj1 = copperVesselSolid_LERE,
        obj2 = calibrationInternalTap,
        tra2 = [[0, 90*np.pi/180, 0], [vesselRadius - 0.5*calibrationInternalTapLength, 0, +calibrationHoleZpos]],
        registry=reg
    )
    copperVesselSolid_LERE_LIRI = g4.solid.Union(
        name = "copperVesselSolid_LERE_LIRI",
        obj1 = copperVesselSolid_LERE_LI,
        obj2 = calibrationInternalTap,
        tra2 = [[0, 90*np.pi/180, 0], [vesselRadius - 0.5*calibrationInternalTapLength, 0, -calibrationHoleZpos]],
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
    rot_close = [0, 0, -66.6*np.pi/180]
    rot_open = [0, 0, 6.59*np.pi/180]
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


    shiftY = 0
    shiftZ = 0
    if left_calibration_is_open:
        shiftY = calibrationShieldingOpenShiftY
        shiftZ = -calibrationShieldingOpenShiftZ
    vesselSolid_2 = g4.solid.Union(
        name = "vesselSolid_2",
        obj1 = copperVesselSolid_LERE_LIRI,
        obj2 = calibrationShieldingOpenSolid,
        tra2 = [[0,-90*np.pi/180,0], [vesselRadius-calibrationInternalTapLength - 0.5*calibrationShieldingCutLength, shiftY, calibrationHoleZpos + shiftZ] ],
        registry=reg
    )
    
    if right_calibration_is_open:
        shiftY = calibrationShieldingOpenShiftY
        shiftZ = calibrationShieldingOpenShiftZ
    else:
        shiftY = 0
        shiftZ = 0  
    vesselSolid = g4.solid.Union(
        name = "vesselSolid",
        obj1 = vesselSolid_2,
        obj2 = calibrationShieldingCloseSolid,
        tra2 = [[0,-90*np.pi/180,0], [vesselRadius-calibrationInternalTapLength - 0.5*calibrationShieldingCutLength, shiftY, -calibrationHoleZpos + shiftZ] ],
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
    
    # assembly
    vessel_assembly = g4.AssemblyVolume(
        name=name,
        registry=reg,
        addRegistry=True
    )
    
    
    vessel_LV = g4.LogicalVolume(
        name="vessel_LV",
        solid=vesselSolid,
        material=copper,
        registry=reg
    )

    gas_LV = g4.LogicalVolume(
        name="gas_LV",
        solid=gasSolid,
        material=air,
        registry=reg
    )
        
    vessel_PV = g4.PhysicalVolume(
        name="vessel_PV",
        logicalVolume=vessel_LV,
        motherVolume=vessel_assembly,
        position=[0, 0, 0],
        rotation=[0, 0, 0],
        registry=reg
    )
    gas_PV = g4.PhysicalVolume(
        name="gas_PV",
        logicalVolume=gas_LV,
        motherVolume=vessel_assembly,
        position=[0, 0, 0],
        rotation=[0, 0, 0],
        registry=reg
    )

    return reg

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--vis", action="store_true")
    parser.add_argument("--gdml", action="store_true")
    args = parser.parse_args()

    reg = generate_vessel_assembly("vessel_assembly")
    vessel_assembly = utils.get_logical_volume_by_name("vessel_assembly", reg)

    if args.gdml:
        galactic = g4.nist_material_2geant4Material("G4_Galactic")
        assembly_LV = vessel_assembly.logicalVolume(material=galactic)
        reg.setWorld(assembly_LV.name)
        w = pyg4ometry.gdml.Writer()
        w.addDetector(reg)
        w.write('vessel.gdml')

    if args.vis:
        v = pyg4ometry.visualisation.VtkViewer()
        v.addLogicalVolume(vessel_assembly)
        v.addAxes(200)
        v.view()

