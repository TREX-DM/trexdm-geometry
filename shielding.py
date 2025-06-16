import vtk
import pyg4ometry
from pyg4ometry import geant4 as g4


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
        
    copperTopThickness = 50

    copperCageThickness = 50.0
    copperCageOutSizeX = 700.0
    copperCageOutSizeY = 750.0
    copperCageOutSizeZ = 900.0

    outerGasSizeX  = copperCageOutSizeX - 2 * copperCageThickness
    outerGasSizeY  = copperCageOutSizeY - copperCageThickness
    outerGasSizeZ  = copperCageOutSizeZ - 2 * copperCageThickness

    leadSizeX = 200 + copperCageOutSizeX + 200
    leadSizeY = 200 + copperCageOutSizeY + copperTopThickness + 200
    leadSizeZ = 200 + copperCageOutSizeZ + 200

    copperTopSizeX  = leadSizeX
    copperTopSizeY  = copperCageThickness
    copperTopSizeZ  = leadSizeZ




    copperCageOutSolid = g4.solid.Box(
            "copperCageOutSolid",
            copperCageOutSizeX,
            copperCageOutSizeY,
            copperCageOutSizeZ,
            reg,
            "mm"
        )
    outerGasSolid = g4.solid.Box(
            "outerGasSolid",
            outerGasSizeX,
            outerGasSizeY,
            outerGasSizeZ,
            reg,
            "mm"
        )

    copperTopSolid = g4.solid.Box(
        "copperTopSolid",
        copperTopSizeX,
        copperTopSizeY,
        copperTopSizeZ,
        reg,
        "mm"
    )
    leadBoxSolid = g4.solid.Box(
        "leadBoxSolid",
        leadSizeX,
        leadSizeY,
        leadSizeZ,
        reg,
        "mm"
    )
    
    shielding_assembly = g4.AssemblyVolume(
        name=name,
        registry=reg,
        addRegistry=True
    )
    outerGasVolume = g4.LogicalVolume(outerGasSolid, air, "outerGasVolume", reg)
    copperCageVolume = g4.LogicalVolume(copperCageOutSolid, copper, "copperCageVolume", reg)
    copperTopVolume = g4.LogicalVolume(copperTopSolid, copper, "copperTopVolume", reg)
    leadShieldingVolume = g4.LogicalVolume(leadBoxSolid, lead, "leadShieldingVolume", reg) 
    
    copperCagePhysical = g4.PhysicalVolume(
        rotation=[0,0,0],
        position=[0, copperCageThickness / 2, 0],
        name="copperCagePV",
        logicalVolume=copperCageVolume,
        motherVolume=leadShieldingVolume,
        registry=reg
    )
    copperTopPhysical = g4.PhysicalVolume(
        rotation=[0,0,0],
        position=[0, copperCageOutSizeY / 2 + copperCageThickness / 2 + copperTopThickness / 2, 0],
        name="copperTopPV",
        logicalVolume=copperTopVolume,
        motherVolume=leadShieldingVolume,
        registry=reg
    )
    outerGasPhysical = g4.PhysicalVolume(
        rotation=[0,0,0],
        position=[0, copperCageThickness / 2, 0],
        name="outerGasPV",
        logicalVolume=outerGasVolume,
        motherVolume=copperCageVolume,
        registry=reg
    )

    leadShieldingPV = g4.PhysicalVolume(
        rotation=[0,0,0],
        position=[0,0,0],
        name="shielding",
        logicalVolume=leadShieldingVolume,
        motherVolume=shielding_assembly,
        registry=reg
    )

    return reg



import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--vis", action="store_true")
parser.add_argument("--gdml", action="store_true")
args = parser.parse_args()

if args.gdml:
    w = pyg4ometry.gdml.Writer()
    w.addDetector(reg)
    w.write('shielding.gdml')

if args.vis:
    v = pyg4ometry.visualisation.VtkViewerColouredMaterial()
    #v.addLogicalVolume(g4.LogicalVolume(gasSolid, air, "gasLogical", reg))
    #v.addSolid(gasSolid)
    #v.addSolid(copperVesselSolid)
    v.addLogicalVolumeRecursive(wl)
    
    v.addAxes(200)
    v.view()