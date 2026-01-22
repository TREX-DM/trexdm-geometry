import vtk
import pyg4ometry
import numpy as np
from pyg4ometry import geant4 as g4
import utils

copperTopThickness = 50

copperCageThickness = 50.0
copperCageOutSizeX = 700.0
copperCageOutSizeY = 750.0
copperCageOutSizeZ = 900.0
calibrationHoleRadius = 25 # diameter match the thickness of a lead block (50 mm)
calibrationHoleZpos = 80 # it should be the same as vessel.calibrationHoleZpos

leadBlockThickness = 50
leadBlockLength = 200
leadBlockWidth = 100

outerGasSizeX  = copperCageOutSizeX - 2 * copperCageThickness
outerGasSizeY  = copperCageOutSizeY - copperCageThickness
outerGasSizeZ  = copperCageOutSizeZ - 2 * copperCageThickness

leadThickness = 200
leadSizeX = leadThickness*2 + copperCageOutSizeX
leadSizeY = leadThickness + copperCageOutSizeY
leadSizeZ = leadThickness*2 + copperCageOutSizeZ

castleSizeX = leadSizeX
castleSizeY = leadSizeY + copperTopThickness + leadThickness
castleSizeZ = leadSizeZ

copperTopSizeX  = leadSizeX
copperTopSizeY  = copperCageThickness
copperTopSizeZ  = leadSizeZ

peFloorThickness = 400
peRoofThickness = 400
peTankWidth = 750 # the tank in front of the calibration ports is made from polyethylene blocks instead of water

waterTankThickness = 400
waterTankHeight = 1700
waterTanksWheelsHeight = 100
waterTankDistanceToCastleX1 = 400 # distance to the lead castle at the calibration ports part
waterTankDistanceToCastleX2 = 150 # distance to the lead castle at the opposite part
waterTankDistanceToCastleZ = 500 # space needed for the electronics


def generate_shielding_assembly_by_parts(name="shielding_assembly", open_calibration_lead_block=False, registry=None):
    # Registry
    if registry is None:
        reg = g4.Registry()
    else:
        reg = registry  

    # Materials
    
    copper = g4.nist_material_2geant4Material("G4_Cu")
    lead = g4.nist_material_2geant4Material("G4_Pb")
    air = g4.nist_material_2geant4Material("G4_AIR")
    """
    copper = g4.MaterialPredefined("G4_Cu", reg)
    lead = g4.MaterialPredefined("G4_Pb", reg)
    air = g4.MaterialPredefined("G4_AIR", reg)
    """

    copperCageYpos = -castleSizeY/2 + leadThickness + copperCageOutSizeY/2
    leadCageYpos = -castleSizeY/2 + leadSizeY/2

    leadCage0 = g4.solid.Box(
        name="leadCage0",
        pX=leadSizeX,
        pY=leadSizeY,
        pZ=leadSizeZ,
        lunit="mm",
        registry=reg
    )

    leadBlock = g4.solid.Box(
        name="leadBlock",
        pX=leadBlockLength + 0.01, # to ensure complete subtraction
        pY=leadBlockWidth,
        pZ=leadBlockThickness,
        lunit="mm",
        registry=reg
    )

    if open_calibration_lead_block:
        leadCage1 = g4.solid.Subtraction(
            name="leadCage1",
            obj1=leadCage0,
            obj2=leadBlock,
            tra2 =[[0, 0, 0], [leadSizeX/2 - leadBlockLength/2, -leadCageYpos, calibrationHoleZpos]],
            registry=reg
        )

        leadCage2 = g4.solid.Subtraction(
            name="leadCage2",
            obj1=leadCage1,
            obj2=leadBlock,
            tra2 =[[0, 0, 0], [leadSizeX/2 - leadBlockLength/2, -leadCageYpos, -calibrationHoleZpos]],
            registry=reg
        )

    copperCage0 = g4.solid.Box(
        name="copperCage0",
        pX=copperCageOutSizeX,
        pY=copperCageOutSizeY,
        pZ=copperCageOutSizeZ,
        lunit="mm",
        registry=reg
    )

    calibrationHole = g4.solid.Tubs(
        name="calibrationHole",
        pRMin=0,
        pRMax=calibrationHoleRadius,
        pDz=copperCageThickness + 0.01,
        pSPhi=0,
        pDPhi=360,
        aunit="deg",
        lunit="mm",
        registry=reg
    )

    copperCage1 = g4.solid.Subtraction(
        name="copperCage1",
        obj1=copperCage0,
        obj2=calibrationHole,
        tra2 =[[0, 90*np.pi/180, 0], [copperCageOutSizeX/2 - copperCageThickness/2, -copperCageYpos, +calibrationHoleZpos]],
        registry=reg
    )

    copperCage2 = g4.solid.Subtraction(
        name="copperCage2",
        obj1=copperCage1,
        obj2=calibrationHole,
        tra2 =[[0, 90*np.pi/180, 0], [copperCageOutSizeX/2 - copperCageThickness/2, -copperCageYpos, -calibrationHoleZpos]],
        registry=reg
    )

    outerGasBox = g4.solid.Box(
        name="outerGasBox",
        pX=outerGasSizeX,
        pY=outerGasSizeY,
        pZ=outerGasSizeZ,
        lunit="mm",
        registry=reg
    )

    leadCage = g4.solid.Subtraction(
        name="leadCage",
        obj1=leadCage2 if open_calibration_lead_block else leadCage0,
        obj2=copperCage0,
        tra2=[[0, 0, 0], [0, -leadSizeY/2 + leadThickness + copperCageOutSizeY/2, 0]],
        registry=reg
    )
    
    copperCage = g4.solid.Subtraction(
        name="copperCage",
        obj1=copperCage2,
        obj2=outerGasBox,
        tra2=[[0, 0, 0], [0, copperCageOutSizeY/2 - outerGasSizeY/2, 0]],
        registry=reg
    )
    
    copperTop = g4.solid.Box(
        name="copperTop",
        pX=copperTopSizeX,
        pY=copperTopSizeY,
        pZ=copperTopSizeZ,
        lunit="mm",
        registry=reg
    )
    
    leadTop = g4.solid.Box(
        name="leadTop",
        pX=leadSizeX,
        pY=leadThickness,
        pZ=leadSizeZ,
        lunit="mm",
        registry=reg
    )
    
    shielding_assembly = g4.AssemblyVolume(
        name=name,
        registry=reg,
        addRegistry=True
    )
    
    leadCage_LV = g4.LogicalVolume(
        name="leadCage_LV",
        solid=leadCage,
        material=lead,
        registry=reg
    )
    
    copperCage_LV = g4.LogicalVolume(
        name="copperCage_LV",
        solid=copperCage,
        material=copper,
        registry=reg
    )
    
    outerGas_LV = g4.LogicalVolume(
        name="outerGas_LV",
        solid=outerGasBox,
        material=air,
        registry=reg
    )
    
    copperTop_LV = g4.LogicalVolume(
        name="copperTop_LV",
        solid=copperTop,
        material=copper,
        registry=reg
    )
    
    leadTop_LV = g4.LogicalVolume(
        name="leadTop_LV",
        solid=leadTop,
        material=lead,
        registry=reg
    )
    
    # physical volumes
    leadCage_PV = g4.PhysicalVolume(
        name="leadCage",
        rotation=[0, 0, 0],
        position=[0, leadCageYpos, 0],
        logicalVolume=leadCage_LV,
        motherVolume=shielding_assembly,
        registry=reg
    )
    
    copperCage_PV = g4.PhysicalVolume(
        name="copperCage",
        rotation=[0, 0, 0],
        position=[0, copperCageYpos, 0],
        logicalVolume=copperCage_LV,
        motherVolume=shielding_assembly,
        registry=reg
    )
    
    outerGas_PV = g4.PhysicalVolume(
        name="outerGas",
        rotation=[0, 0, 0],
        position=[0, castleSizeY/2 - leadThickness - copperTopThickness - outerGasSizeY/2, 0],
        logicalVolume=outerGas_LV,
        motherVolume=shielding_assembly,
        registry=reg
    )

    copperTop_PV = g4.PhysicalVolume(
        name="copperTop",
        rotation=[0, 0, 0],
        position=[0, -castleSizeY/2 + leadThickness + copperCageOutSizeY + copperTopThickness/2, 0],
        logicalVolume=copperTop_LV,
        motherVolume=shielding_assembly,
        registry=reg
    )
    
    leadTop_PV = g4.PhysicalVolume(
        name="leadTop",
        rotation=[0, 0, 0],
        position=[0, castleSizeY/2 - leadThickness/2, 0],
        logicalVolume=leadTop_LV,
        motherVolume=shielding_assembly,
        registry=reg
    )

    return reg

def generate_shielding_volume(name="shielding_LV", open_calibration_lead_block=False, registry=None):
    """
    Generates the shielding geometry for the TREX-DM detector.
    Returns a Geant4 Registry containing the shielding geometry.
    """
    # Registry
    if registry is None:
        reg = g4.Registry()
    else:
        reg = registry  

    copper = g4.nist_material_2geant4Material("G4_Cu")
    lead = g4.nist_material_2geant4Material("G4_Pb")
    air = g4.nist_material_2geant4Material("G4_AIR")
    """
    copper = g4.MaterialPredefined("G4_Cu", reg)
    lead = g4.MaterialPredefined("G4_Pb", reg)
    air = g4.MaterialPredefined("G4_AIR", reg)
    """

    copperCage = g4.solid.Box(
        name="copperCage",
        pX=copperCageOutSizeX,
        pY=copperCageOutSizeY,
        pZ=copperCageOutSizeZ,
        registry=reg,
        lunit="mm"
    )

    calibrationHole = g4.solid.Tubs(
        name="calibrationHole",
        pRMin=0,
        pRMax=calibrationHoleRadius,
        pDz=copperCageThickness,
        pSPhi=0,
        pDPhi=360,
        aunit="deg",
        lunit="mm",
        registry=reg
    )

    outerGas0 = g4.solid.Box(
        name="outerGas0",
        pX=outerGasSizeX,
        pY=outerGasSizeY,
        pZ=outerGasSizeZ,
        registry=reg,
        lunit="mm"
    )

    outerGas1 = g4.solid.Union(
        name="outerGas1",
        obj1=outerGas0,
        obj2=calibrationHole,
        tra2 =[[0, 90*np.pi/180, 0], [outerGasSizeX/2 + copperCageThickness/2, 0, +calibrationHoleZpos]],
        registry=reg
    )

    outerGas = g4.solid.Union(
        name="outerGas",
        obj1=outerGas1,
        obj2=calibrationHole,
        tra2 =[[0, 90*np.pi/180, 0], [outerGasSizeX/2 + copperCageThickness/2, 0, -calibrationHoleZpos]],
        registry=reg
    )

    copperTop = g4.solid.Box(
        name="copperTop",
        pX=copperTopSizeX,
        pY=copperTopSizeY,
        pZ=copperTopSizeZ,
        registry=reg,
        lunit="mm"
    )

    castleBox = g4.solid.Box(
        name="castleBox0" if open_calibration_lead_block else "castleBox",
        pX=castleSizeX,
        pY=castleSizeY,
        pZ=castleSizeZ,
        registry=reg,
        lunit="mm"
    )

    if open_calibration_lead_block:
        leadBlock = g4.solid.Box(
            name="leadBlock",
            pX=leadBlockLength, # to ensure complete subtraction
            pY=leadBlockWidth,
            pZ=leadBlockThickness,
            lunit="mm",
            registry=reg
        )
        castleBox1 = g4.solid.Subtraction(
            name="castleBox1",
            obj1=castleBox,
            obj2=leadBlock,
            tra2 =[[0, 0, 0], [castleSizeX/2 - leadBlockLength/2, copperCageThickness, calibrationHoleZpos]],
            registry=reg
        )

        castleBox = g4.solid.Subtraction(
            name="castleBox",
            obj1=castleBox1,
            obj2=leadBlock,
            tra2 =[[0, 0, 0], [castleSizeX/2 - leadBlockLength/2, copperCageThickness, -calibrationHoleZpos]],
            registry=reg
        )

    outerGas_LV = g4.LogicalVolume(
        name="outerGas_LV",
        solid=outerGas,
        material=air,
        registry=reg
    )
    copperCage_LV = g4.LogicalVolume(
        name="copperCage_LV",
        solid=copperCage,
        material=copper,
        registry=reg
    )
    copperTop_LV = g4.LogicalVolume(
        name="copperTop_LV",
        solid=copperTop,
        material=copper,
        registry=reg
    )
    leadShielding_LV = g4.LogicalVolume(
        name=name,
        solid=castleBox,
        material=lead,
        registry=reg
    )

    copperCage_PV = g4.PhysicalVolume(
        rotation=[0,0,0],
        position=[0, copperCageThickness / 2, 0],
        name="copperCage",
        logicalVolume=copperCage_LV,
        motherVolume=leadShielding_LV,
        registry=reg
    )
    copperTop_PV = g4.PhysicalVolume(
        rotation=[0,0,0],
        position=[0, copperCageOutSizeY / 2 + copperCageThickness / 2 + copperTopThickness / 2, 0],
        name="copperTop",
        logicalVolume=copperTop_LV,
        motherVolume=leadShielding_LV,
        registry=reg
    )
    outerGas_PV = g4.PhysicalVolume(
        rotation=[0,0,0],
        position=[0, copperCageThickness / 2, 0],
        name="outerGas",
        logicalVolume=outerGas_LV,
        motherVolume=copperCage_LV,
        registry=reg
    )


    return reg


def generate_neutron_shielding_assembly(name="neutron_shielding_assembly", registry=None):
    # Registry
    if registry is None:
        reg = g4.Registry()
    else:
        reg = registry  

    # Materials
    polyethylene = g4.nist_material_2geant4Material("G4_POLYETHYLENE")
    water = g4.nist_material_2geant4Material("G4_WATER")

    peBase = g4.solid.Box(
        name="peBase",
        pX=castleSizeX,
        pY=peFloorThickness,
        pZ=castleSizeZ,
        lunit="mm",
        registry=reg
    )

    waterTanksHV = g4.solid.Box(
        name="waterTanksHV",
        pX=waterTankThickness,
        pY=waterTankHeight,
        pZ=castleSizeZ + 2*waterTankDistanceToCastleZ + 2*waterTankThickness,
        lunit="mm",
        registry=reg
    )
    waterTanksElectronics = g4.solid.Box(
        name="waterTanksElectronics",
        pX=waterTankDistanceToCastleX1 + castleSizeX + waterTankDistanceToCastleX2,
        pY=waterTankHeight,
        pZ=waterTankThickness,
        lunit="mm",
        registry=reg
    )

    waterTankCalibrationSizeZ = (castleSizeZ + 2*waterTankDistanceToCastleZ + 2*waterTankThickness - peTankWidth)/2
    waterTanksCalibration = g4.solid.Box(
        name="waterTanksCalibration",
        pX=waterTankThickness,
        pY=waterTankHeight,
        pZ=waterTankCalibrationSizeZ,
        lunit="mm",
        registry=reg
    )
    peTankCalibration = g4.solid.Box(
        name="peTankCalibration",
        pX=waterTankThickness, # same as water tank thickness
        pY=waterTankHeight, # same as water tank height
        pZ=peTankWidth,
        lunit="mm",
        registry=reg
    )

    neutron_shielding_assembly = g4.AssemblyVolume(
        name=name,
        registry=reg,
        addRegistry=True
    )

    peBase_LV = g4.LogicalVolume(
        name="peBase_LV",
        solid=peBase,
        material=polyethylene,
        registry=reg
    )

    waterTanksHV_LV = g4.LogicalVolume(
        name="waterTanksHV_LV",
        solid=waterTanksHV,
        material=water,
        registry=reg
    )

    waterTanksElectronics_LV = g4.LogicalVolume(
        name="waterTanksElectronics_LV",
        solid=waterTanksElectronics,
        material=water,
        registry=reg
    )

    waterTanksCalibration_LV = g4.LogicalVolume(
        name="waterTanksCalibration_LV",
        solid=waterTanksCalibration,
        material=water,
        registry=reg
    )

    peTankCalibration_LV = g4.LogicalVolume(
        name="peTankCalibration_LV",
        solid=peTankCalibration,
        material=polyethylene,
        registry=reg
    )

    # physical volumes
    yPos = -castleSizeY/2 - peFloorThickness + waterTanksWheelsHeight + waterTankHeight/2
    peFloor_PV = g4.PhysicalVolume(
        name="peFloor",
        rotation=[0, 0, 0],
        position=[0, -castleSizeY/2 - peFloorThickness/2, 0],
        logicalVolume=peBase_LV,
        motherVolume=neutron_shielding_assembly,
        registry=reg
    )

    peRoof_PV = g4.PhysicalVolume(
        name="peRoof",
        rotation=[0, 0, 0],
        position=[0, castleSizeY/2 + peRoofThickness/2, 0],
        logicalVolume=peBase_LV,
        motherVolume=neutron_shielding_assembly,
        registry=reg
    )

    waterTanksHV_PV = g4.PhysicalVolume(
        name="waterTanksHV",
        rotation=[0, 0, 0],
        position=[-castleSizeX/2 - waterTankDistanceToCastleX2 - waterTankThickness/2, yPos, 0],
        logicalVolume=waterTanksHV_LV,
        motherVolume=neutron_shielding_assembly,
        registry=reg
    )

    waterTanksElectronics_PV = g4.PhysicalVolume(
        name="waterTanksElectronicsLeft",
        rotation=[0, 0, 0],
        position=[(waterTankDistanceToCastleX1 - waterTankDistanceToCastleX2)/2, yPos, castleSizeZ/2 + waterTankDistanceToCastleZ + waterTankThickness/2],
        logicalVolume=waterTanksElectronics_LV,
        motherVolume=neutron_shielding_assembly,
        registry=reg
    )

    waterTanksElectronicsRight_PV = g4.PhysicalVolume(
        name="waterTanksElectronicsRight",
        rotation=[0, 0, 0],
        position=[(waterTankDistanceToCastleX1 - waterTankDistanceToCastleX2)/2, yPos, - (castleSizeZ/2 + waterTankDistanceToCastleZ + waterTankThickness/2)],
        logicalVolume=waterTanksElectronics_LV,
        motherVolume=neutron_shielding_assembly,
        registry=reg
    )

    waterTanksCalibrationLeft_PV = g4.PhysicalVolume(
        name="waterTanksCalibrationLeft",
        rotation=[0, 0, 0],
        position=[castleSizeX/2 + waterTankDistanceToCastleX1 + waterTankThickness/2, yPos, castleSizeZ/2 + waterTankDistanceToCastleZ + waterTankThickness - waterTankCalibrationSizeZ/2],
        logicalVolume=waterTanksCalibration_LV,
        motherVolume=neutron_shielding_assembly,
        registry=reg
    )

    waterTanksCalibrationRight_PV = g4.PhysicalVolume(
        name="waterTanksCalibrationRight",
        rotation=[0, 0, 0],
        position=[castleSizeX/2 + waterTankDistanceToCastleX1 + waterTankThickness/2, yPos, - (castleSizeZ/2 + waterTankDistanceToCastleZ + waterTankThickness - waterTankCalibrationSizeZ/2)],
        logicalVolume=waterTanksCalibration_LV,
        motherVolume=neutron_shielding_assembly,
        registry=reg
    )

    peTankCalibration_PV = g4.PhysicalVolume(
        name="peTankCalibration",
        rotation=[0, 0, 0],
        position=[castleSizeX/2 + waterTankDistanceToCastleX1 + waterTankThickness/2, yPos, 0],
        logicalVolume=peTankCalibration_LV,
        motherVolume=neutron_shielding_assembly,
        registry=reg
    )

    return reg

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--vis", action="store_true")
    parser.add_argument("--gdml", action="store_true")
    args = parser.parse_args()

    #reg = generate_shielding_assembly_by_parts("shielding_assembly", True)
    #shielding = utils.get_logical_volume_by_name("shielding_assembly", reg)

    reg = generate_shielding_volume("shielding_LV", open_calibration_lead_block=True)
    shielding = utils.get_logical_volume_by_name("shielding_LV", reg)


    if args.gdml:
        galactic = g4.nist_material_2geant4Material("G4_Galactic")
        assembly_LV = shielding.logicalVolume(material=galactic)
        reg.setWorld(assembly_LV.name)
        w = pyg4ometry.gdml.Writer()
        w.addDetector(reg)
        w.write('shielding.gdml')

    if args.vis:
        v = pyg4ometry.visualisation.VtkViewerColouredMaterial()
        v.addLogicalVolume(shielding)
        v.addAxes(200)
        v.view()