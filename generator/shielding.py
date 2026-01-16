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

def generate_shielding_assembly(name="shielding_assembly", registry=None):
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
            "copperCage",
            copperCageOutSizeX,
            copperCageOutSizeY,
            copperCageOutSizeZ,
            reg,
            "mm"
        )
    outerGas = g4.solid.Box(
            "outerGas",
            outerGasSizeX,
            outerGasSizeY,
            outerGasSizeZ,
            reg,
            "mm"
        )

    copperTop = g4.solid.Box(
        "copperTop",
        copperTopSizeX,
        copperTopSizeY,
        copperTopSizeZ,
        reg,
        "mm"
    )
    castleBox = g4.solid.Box(
        "castleBox",
        castleSizeX,
        castleSizeY,
        castleSizeZ,
        reg,
        "mm"
    )
    
    shielding_assembly = g4.AssemblyVolume(
        name=name,
        registry=reg,
        addRegistry=True
    )
    outerGas_LV = g4.LogicalVolume(outerGas, air, "outerGas_LV", reg)
    copperCage_LV = g4.LogicalVolume(copperCage, copper, "copperCage_LV", reg)
    copperTop_LV = g4.LogicalVolume(copperTop, copper, "copperTop_LV", reg)
    leadShielding_LV = g4.LogicalVolume(castleBox, lead, "leadShielding_LV", reg)

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

    leadShielding_PV = g4.PhysicalVolume(
        rotation=[0,0,0],
        position=[0,0,0],
        name="leadShielding",
        logicalVolume=leadShielding_LV,
        motherVolume=shielding_assembly,
        registry=reg
    )

    return reg


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--vis", action="store_true")
    parser.add_argument("--gdml", action="store_true")
    args = parser.parse_args()

    reg = generate_shielding_assembly_by_parts("shielding_assembly", True)
    shielding_assembly = utils.get_logical_volume_by_name("shielding_assembly", reg)

    if args.gdml:
        galactic = g4.nist_material_2geant4Material("G4_Galactic")
        assembly_LV = shielding_assembly.logicalVolume(material=galactic)
        reg.setWorld(assembly_LV.name)
        w = pyg4ometry.gdml.Writer()
        w.addDetector(reg)
        w.write('shielding.gdml')

    if args.vis:
        v = pyg4ometry.visualisation.VtkViewerColouredMaterial()
        v.addLogicalVolume(shielding_assembly)
        v.addAxes(200)
        v.view()