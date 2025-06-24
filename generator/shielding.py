import vtk
import pyg4ometry
from pyg4ometry import geant4 as g4


copperTopThickness = 50

copperCageThickness = 50.0
copperCageOutSizeX = 700.0
copperCageOutSizeY = 750.0
copperCageOutSizeZ = 900.0

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

def generate_shielding_assembly_by_parts(name="shielding_assembly", registry=None):
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

    leadCage0 = g4.solid.Box(
        name="leadCage0",
        pX=leadSizeX,
        pY=leadSizeY,
        pZ=leadSizeZ,
        lunit="mm",
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
        obj1=leadCage0,
        obj2=copperCage0,
        tra2=[[0, 0, 0], [0, -leadSizeY/2 + leadThickness + copperCageOutSizeY/2, 0]],
        registry=reg
    )
    
    copperCage = g4.solid.Subtraction(
        name="copperCage",
        obj1=copperCage0,
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
        name="leadCage_PV",
        rotation=[0, 0, 0],
        position=[0, -castleSizeY/2 + leadSizeY/2, 0],
        logicalVolume=leadCage_LV,
        motherVolume=shielding_assembly,
        registry=reg
    )
    
    copperCage_PV = g4.PhysicalVolume(
        name="copperCage_PV",
        rotation=[0, 0, 0],
        position=[0, -castleSizeY/2 + leadThickness + copperCageOutSizeY/2, 0],
        logicalVolume=copperCage_LV,
        motherVolume=shielding_assembly,
        registry=reg
    )
    
    outerGas_PV = g4.PhysicalVolume(
        name="outerGas_PV",
        rotation=[0, 0, 0],
        position=[0, castleSizeY/2 - leadThickness - copperTopThickness - outerGasSizeY/2, 0],
        logicalVolume=outerGas_LV,
        motherVolume=shielding_assembly,
        registry=reg
    )

    copperTop_PV = g4.PhysicalVolume(
        name="copperTop_PV",
        rotation=[0, 0, 0],
        position=[0, -castleSizeY/2 + leadThickness + copperCageOutSizeY + copperTopThickness/2, 0],
        logicalVolume=copperTop_LV,
        motherVolume=shielding_assembly,
        registry=reg
    )
    
    leadTop_PV = g4.PhysicalVolume(
        name="leadTop_PV",
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
        name="copperCage_PV",
        logicalVolume=copperCage_LV,
        motherVolume=leadShielding_LV,
        registry=reg
    )
    copperTop_PV = g4.PhysicalVolume(
        rotation=[0,0,0],
        position=[0, copperCageOutSizeY / 2 + copperCageThickness / 2 + copperTopThickness / 2, 0],
        name="copperTop_PV",
        logicalVolume=copperTop_LV,
        motherVolume=leadShielding_LV,
        registry=reg
    )
    outerGas_PV = g4.PhysicalVolume(
        rotation=[0,0,0],
        position=[0, copperCageThickness / 2, 0],
        name="outerGas_PV",
        logicalVolume=outerGas_LV,
        motherVolume=copperCage_LV,
        registry=reg
    )

    leadShielding_PV = g4.PhysicalVolume(
        rotation=[0,0,0],
        position=[0,0,0],
        name="leadShielding_PV",
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

    reg = generate_shielding_assembly("shielding_assembly")
    shielding_assembly = reg.findLogicalVolumeByName("shielding_assembly")[0]

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