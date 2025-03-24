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

leadSizeX = 200 + copperCageOutSizeX + 200
leadSizeY = 200 + copperCageOutSizeY + copperTopThickness + 200
leadSizeZ = 200 + copperCageOutSizeZ + 200

copperTopSizeX  = leadSizeX
copperTopSizeY  = copperCageThickness
copperTopSizeZ  = leadSizeZ


reg  = g4.Registry()

copper = g4.nist_material_2geant4Material("G4_Cu", reg)
lead = g4.nist_material_2geant4Material("G4_Pb", reg)
air = g4.nist_material_2geant4Material("G4_AIR", reg)


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
outerGasVolume = g4.LogicalVolume(outerGasSolid, air, "outerGasVolume", reg)


copperCageVolume = g4.LogicalVolume(copperCageOutSolid, copper, "copperCageVolume", reg)

outerGasPhysical = g4.PhysicalVolume(
    rotation=[0,0,0],
    position=[0, copperCageThickness / 2, 0],
    name="outerGasPV",
    logicalVolume=outerGasVolume,
    motherVolume=copperCageVolume,
    registry=reg
)

copperTopSolid = g4.solid.Box(
    "copperTopSolid",
    copperTopSizeX,
    copperTopSizeY,
    copperTopSizeZ,
    reg,
    "mm"
)
copperTopVolume = g4.LogicalVolume(copperTopSolid, copper, "copperTopVolume", reg)

leadBoxSolid = g4.solid.Box(
    "leadBoxSolid",
    leadSizeX,
    leadSizeY,
    leadSizeZ,
    reg,
    "mm"
)

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

# world solid and logical
ws   = g4.solid.Box("ws",10,10,10,reg, "m")
wl   = g4.LogicalVolume(ws, air,"wl",reg)

leadShieldingPV = g4.PhysicalVolume(
    rotation=[0,0,0],
    position=[0,0,0],
    name="shielding",
    logicalVolume=leadShieldingVolume,
    motherVolume=wl,
    registry=reg
)

reg.setWorld(wl.name)

w = pyg4ometry.gdml.Writer()
w.addDetector(reg)
w.write('shielding.gdml')