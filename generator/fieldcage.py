import vtk
import pyg4ometry
from pyg4ometry import geant4 as g4
import numpy as np

cathodeLength = 206 # mm
cathodeCuThickness = 0.002 # 2um
cathodeKaptonThickness = 0.0125 # 12.5um

cathodeFrameLength = 236 # mm
cathodeFrameInnerLength = 206 # mm
cathodeFrameThickness = 10 # 2um

cathodeFeedThroughHeight = 65 # mm
cathodeFeedThroughWidth = 12 # mm
cathodeFeedThroughThickness = 10 # mm
cathodeFeedThroughDistanceToCopperFrame = 2 # mm

cathodeSideFrameLength = 264 # mm
cathodeSideFrameInnerLength = 252 # mm
cathodeSideFrameThickness = 5 # mm

sideSeparatorLength = cathodeSideFrameLength
sideSeparatorInnerLength = 248
sideSeparatorThickness = 15 # mm
sideSeparatorSlotHeight = 65 # mm
sideSeparatorWidth = (sideSeparatorLength - sideSeparatorInnerLength) / 2 # mm

cornersLength = cathodeSideFrameLength
cornersInnerLength = cathodeSideFrameInnerLength
cornersThickness = 144 # mm
cornersWidth = (cornersLength - cornersInnerLength) / 2 # mm
cornersSlotHeight = 184 # mm

closerFrameLength = 266 # mm
closerFrameInnerLength = 248 # mm =sideSeparatorInnerLength
closerFrameThickness = 10 # mm

supportLength = 300 # mm
supportInnerLength = cornersLength
supportCornersThickness = 75 # mm
supportColumnsThickness = 15 # mm

ringsBoardLength = cornersInnerLength
ringsBoardWidth = 0.05 # 50um
ringsBoardInnerLength = cornersInnerLength - 2 * ringsBoardWidth
ringsBoardThickness = cornersThickness # 144 mm

ringLength = ringsBoardInnerLength
ringWidth = 0.1 # 100um
ringInnerLength = ringsBoardInnerLength - 2 * ringWidth
ringThickness = 2 # mm
ringNumber = 21
ringSeparation = 5 #int((ringsBoardThickness - ringNumber * ringThickness) / ringNumber) # mm
if (ringSeparation+ringThickness)*(ringNumber-1)+ringThickness > ringsBoardThickness:
    raise ValueError("The ring separation is too large for the number of rings and the board thickness. Please adjust the parameters.")

resistorShieldingLength = 20 # mm
resistorShieldingWidth = 19 # mm
resistorShieldingThickness = ringsBoardThickness # 144 mm
resistorShieldingSlotLength = 8.43 # mm
resistorShieldingSlotWidth = 1 # mm
resistorShieldingSlotWidthShift = 0.5 # mm, I dont know why it is not centered (then heightShift would be 0)

resistorLength = 3.1 # mm
resistorWidth = 0.6 # mm
resistorThickness = 140 # mm
resistorDistanceToShieldingSlotEdge = 2.5 # mm
if resistorThickness > resistorShieldingThickness:
    raise ValueError("The resistor thickness cannot be larger than its shielding thickness. Please adjust the parameters.")
if resistorDistanceToShieldingSlotEdge + resistorLength > resistorShieldingSlotLength:
    raise ValueError("The resistor does not fit inside the slot with this distance to slot edge. Please adjust the parameters.")

def generate_fieldcage_assembly(name="fieldcage_assembly", registry=None):
    """
    Generate the field cage assembly for the TREX-DM geometry.
    """
    # Registry
    if registry is None:
        reg = g4.Registry()
    else:
        reg = registry

    # Materials
    # Use this for the pyg4ometry coloured material visualisation
    
    copper = g4.MaterialPredefined("G4_Cu")
    teflon = g4.MaterialPredefined("G4_TEFLON")
    kapton = g4.MaterialPredefined("G4_KAPTON")
    """
    # Use this to generate gdmls with NIST materials definitions
    copper = g4.nist_material_2geant4Material("G4_Cu")
    teflon = g4.nist_material_2geant4Material("G4_TEFLON")
    kapton = g4.nist_material_2geant4Material("G4_KAPTON")
    """
    # Creathe the cathode
    cathodeFoilCu = g4.solid.Box(
        name="cathodeFoilCu",
        pX=cathodeLength,
        pY=cathodeLength,
        pZ=cathodeCuThickness,
        lunit="mm",
        registry=reg
    )
    cathodeFoilKapton = g4.solid.Box(
        name="cathodeFoilKapton",
        pX=cathodeLength,
        pY=cathodeLength,
        pZ=cathodeKaptonThickness,
        lunit="mm",
        registry=reg
    )
    """
    cathodeFoil0 = g4.solid.Union(
        name="cathodeFoil",
        obj1=cathodeFoilKapton,
        obj2=cathodeFoilCu,
        tra2=[[0, 0, 0], [0, 0, cathodeKaptonThickness/2]],
        registry=reg
    )
    cathodeFoil = g4.solid.Union(
        name="cathodeFoil",
        obj1=cathodeFoil0,
        obj2=cathodeFoilCu,
        tra2=[[0, 0, 0], [0, 0, -cathodeCuThickness/2]],
        registry=reg
    )
    """
    cathodeFrame0 = g4.solid.Box(
        name="cathodeFrame0",
        pX=cathodeFrameLength,
        pY=cathodeFrameLength,
        pZ=cathodeFrameThickness,
        lunit="mm",
        registry=reg
    )
    cathodeFrameCut = g4.solid.Box(
        name="cathodeFrameCut",
        pX=cathodeFrameInnerLength,
        pY=cathodeFrameInnerLength,
        pZ=cathodeFrameThickness + 0.01,  # Slightly larger to ensure cut
        lunit="mm",
        registry=reg
    )
    cathodeFrame = g4.solid.Subtraction(
        name="cathodeFrame",
        obj1=cathodeFrame0,
        obj2=cathodeFrameCut,
        tra2=[[0, 0, 0], [0, 0, 0]],
        registry=reg
    )
    
    cathodeSideFrame0 = g4.solid.Box(
        name="cathodeSideFrame0",
        pX=cathodeSideFrameLength,
        pY=cathodeSideFrameLength,
        pZ=cathodeSideFrameThickness,
        lunit="mm",
        registry=reg
    )
    cathodeSideFrameCut = g4.solid.Box(
        name="cathodeSideFrameCut",
        pX=cathodeSideFrameInnerLength,
        pY=cathodeSideFrameInnerLength,
        pZ=cathodeSideFrameThickness + 0.01,  # Slightly larger to ensure cut
        lunit="mm",
        registry=reg
    )
    cathodeSideFrame = g4.solid.Subtraction(
        name="cathodeSideFrame",
        obj1=cathodeSideFrame0,
        obj2=cathodeSideFrameCut,
        tra2=[[0, 0, 0], [0, 0, 0]],
        registry=reg
    )
    
    cathodeFeedthrough = g4.solid.Box(
        name="cathodeFeedthrough",
        pX=cathodeFeedThroughWidth,
        pY=cathodeFeedThroughHeight,
        pZ=cathodeFeedThroughThickness,
        lunit="mm",
        registry=reg
    )
    
    sideSeparator0 = g4.solid.Box(
        name="sideSeparator0",
        pX=sideSeparatorLength,
        pY=sideSeparatorLength,
        pZ=sideSeparatorThickness,
        lunit="mm",
        registry=reg
    )
    sideSeparatorCut = g4.solid.Box(
        name="sideSeparatorCut",
        pX=sideSeparatorInnerLength,
        pY=sideSeparatorInnerLength,
        pZ=sideSeparatorThickness + 0.01,  # Slightly larger to ensure cut
        lunit="mm",
        registry=reg
    )
    sideSeparatorNoSlot = g4.solid.Subtraction(
        name="sideSeparatorNoSlot",
        obj1=sideSeparator0,
        obj2=sideSeparatorCut,
        tra2=[[0, 0, 0], [0, 0, 0]],
        registry=reg
    )
    sideSeparatorSlot = g4.solid.Box(
        name="sideSeparatorSlot",
        pX=sideSeparatorWidth,
        pY=sideSeparatorSlotHeight,
        pZ=sideSeparatorThickness + 0.01,  # Slightly larger to ensure cut
        lunit="mm",
        registry=reg
    )
    sideSeparator = g4.solid.Subtraction(
        name="sideSeparator",
        obj1=sideSeparatorNoSlot,
        obj2=sideSeparatorSlot,
        tra2=[[0, 0, 0], [-(sideSeparatorInnerLength/2+sideSeparatorWidth/2), 0, 0]],
        registry=reg
    )
    
    corners0 = g4.solid.Box(
        name="corners0",
        pX=cornersLength,
        pY=cornersLength,
        pZ=cornersThickness,
        lunit="mm",
        registry=reg
    )
    cornersCut = g4.solid.Box(
        name="cornersCut",
        pX=cornersInnerLength,
        pY=cornersInnerLength,
        pZ=cornersThickness,  # Slightly larger to ensure cut
        lunit="mm",
        registry=reg
    )
    cornersBase = g4.solid.Subtraction(
        name="cornersBase",
        obj1=corners0,
        obj2=cornersCut,
        tra2=[[0, 0, 0], [0, 0, 0]],
        registry=reg
    )
    cornersWallCut = g4.solid.Box(
        name="cornersWallCut",
        pX=cornersWidth + 0.001,  # Slightly larger to ensure cut
        pY=cornersSlotHeight,
        pZ=cornersThickness if cornersThickness >= cornersSlotHeight else cornersSlotHeight,  # for simplicity when rotating and moving the wall cut
        lunit="mm",
        registry=reg
    )
    
    corners1 = g4.solid.Subtraction(
        name="corners1",
        obj1=cornersBase,
        obj2=cornersWallCut,
        tra2=[[0, 0, 0], [-(cornersInnerLength/2 + cornersWidth/2), 0, 0]],
        registry=reg
    )
    corners2 = g4.solid.Subtraction(
        name="corners2",
        obj1=corners1,
        obj2=cornersWallCut,
        tra2=[[0, 0, 0], [cornersInnerLength/2 + cornersWidth/2, 0, 0]],
        registry=reg
    )
    corners3 = g4.solid.Subtraction(
        name="corners3",
        obj1=corners2,
        obj2=cornersWallCut,
        tra2=[[0, 0, np.pi/2], [0, -(cornersInnerLength/2 + cornersWidth/2), 0]],
        registry=reg
    )
    corners = g4.solid.Subtraction(
        name="corners4",
        obj1=corners3,
        obj2=cornersWallCut,
        tra2=[[0, 0, 90*np.pi/180], [0, cornersInnerLength/2 + cornersWidth/2, 0]],
        registry=reg
    )
    closerFrame0 = g4.solid.Box(
        name="closerFrame0",
        pX=closerFrameLength,
        pY=closerFrameLength,
        pZ=closerFrameThickness,
        lunit="mm",
        registry=reg
    )
    closerFrameCut = g4.solid.Box(
        name="closerFrameCut",
        pX=closerFrameInnerLength,
        pY=closerFrameInnerLength,
        pZ=closerFrameThickness + 0.01,  # Slightly larger to ensure cut
        lunit="mm",
        registry=reg
    )
    closerFrame = g4.solid.Subtraction(
        name="closerFrame",
        obj1=closerFrame0,
        obj2=closerFrameCut,
        tra2=[[0, 0, 0], [0, 0, 0]],
        registry=reg
    )
    
    ringsBoard0 = g4.solid.Box(
        name="ringsBoard0",
        pX=ringsBoardLength,
        pY=ringsBoardLength,
        pZ=ringsBoardThickness,
        lunit="mm",
        registry=reg
    )
    ringsBoardCut = g4.solid.Box(
        name="ringsBoardCut",
        pX=ringsBoardInnerLength,
        pY=ringsBoardInnerLength,
        pZ=ringsBoardThickness + 0.01,  # Slightly larger to ensure cut
        lunit="mm",
        registry=reg
    )
    ringsBoard = g4.solid.Subtraction(
        name="ringsBoard",
        obj1=ringsBoard0,
        obj2=ringsBoardCut,
        tra2=[[0, 0, 0], [0, 0, 0]],
        registry=reg
    )
    
    ring0 = g4.solid.Box(
        name="ring0",
        pX=ringLength,
        pY=ringLength,
        pZ=ringThickness,
        lunit="mm",
        registry=reg
    )
    ringCut = g4.solid.Box(
        name="ringCut",
        pX=ringInnerLength,
        pY=ringInnerLength,
        pZ=ringThickness + 0.01,  # Slightly larger to ensure cut
        lunit="mm",
        registry=reg
    )
    ring = g4.solid.Subtraction(
        name="ring",
        obj1=ring0,
        obj2=ringCut,
        tra2=[[0, 0, 0], [0, 0, 0]],
        registry=reg
    )
    
    resistorShielding0 = g4.solid.Box(
        name="resistorShielding0",
        pX=resistorShieldingLength,
        pY=resistorShieldingWidth,
        pZ=resistorShieldingThickness,
        lunit="mm",
        registry=reg
    )
    resistorShieldingSlotCut = g4.solid.Box(
        name="resistorShieldingSlotCut",
        pX=resistorShieldingSlotLength,
        pY=resistorShieldingSlotWidth,
        pZ=resistorShieldingThickness,
        lunit="mm",
        registry=reg
    )
    resistorShielding = g4.solid.Subtraction(
        name="resistorShielding",
        obj1=resistorShielding0,
        obj2=resistorShieldingSlotCut,
        tra2=[[0, 0, 0], [-resistorShieldingLength/2 + resistorShieldingSlotLength/2, resistorShieldingSlotWidthShift, 0]],
        registry=reg
    )
    resistor = g4.solid.Box(
        name="resistor",
        pX=resistorLength,
        pY=resistorWidth,
        pZ=resistorThickness,
        lunit="mm",
        registry=reg
    )

    # Create the field cage assembly
    fieldcage_assembly = g4.AssemblyVolume(name=name, registry=reg)
    
    cathodeFoilCu_LV = g4.LogicalVolume(
        name="cathodeFoilCu_LV",
        solid=cathodeFoilCu,
        material=copper,
        registry=reg
    )
    cathodeFoilKapton_LV = g4.LogicalVolume(
        name="cathodeFoilKapton_LV",
        solid=cathodeFoilKapton,
        material=kapton,
        registry=reg
    )
    cathodeFrame_LV = g4.LogicalVolume(
        name="cathodeFrame_LV",
        solid=cathodeFrame,
        material=copper,
        registry=reg
    )
    cathodeFeedthrough_LV = g4.LogicalVolume(
        name="cathodeFeedthrough_LV",
        solid=cathodeFeedthrough,
        material=copper,
        registry=reg
    )
    cathodeSideFrame_LV = g4.LogicalVolume(
        name="cathodeSideFrame_LV",
        solid=cathodeSideFrame,
        material=copper,
        registry=reg
    )
    sideSeparator_LV = g4.LogicalVolume(
        name="sideSeparator_LV",
        solid=sideSeparator,
        material=teflon,
        registry=reg
    )
    corners_LV = g4.LogicalVolume(
        name="corners_LV",
        solid=corners,
        material=teflon,
        registry=reg
    )
    closerFrame_LV = g4.LogicalVolume(
        name="closerFrame_LV",
        solid=closerFrame,
        material=teflon,
        registry=reg
    )
    ringsBoard_LV = g4.LogicalVolume(
        name="ringsBoard_LV",
        solid=ringsBoard,
        material=kapton,
        registry=reg
    )
    ring_LV = g4.LogicalVolume(
        name="ring_LV",
        solid=ring,
        material=copper,
        registry=reg
    )
    
    resistorShielding_LV = g4.LogicalVolume(
        name="resistorShielding_LV",
        solid=resistorShielding,
        material=teflon,
        registry=reg
    )
    resistor_LV = g4.LogicalVolume(
        name="resistor_LV",
        solid=resistor,
        material=copper, # TODO: change to a more appropriate material
        registry=reg
    )
    resistorAssembly = g4.AssemblyVolume(name="resistorAssembly", registry=reg)
    resistorShielding_PV = g4.PhysicalVolume(
        name="resistorShielding_PV",
        rotation=[0, 0, 0],
        position=[0, 0, 0],
        logicalVolume=resistorShielding_LV,
        motherVolume=resistorAssembly,
        registry=reg
    )
    resistor_PV = g4.PhysicalVolume(
        name="resistor_PV",
        rotation=[0, 0, 0],
        position=[-resistorShieldingLength/2 + resistorDistanceToShieldingSlotEdge + resistorLength/2, resistorShieldingSlotWidthShift - resistorShieldingSlotWidth/2 + resistorWidth/2, 0],
        logicalVolume=resistor_LV,
        motherVolume=resistorAssembly,
        registry=reg
    )
    
    
    cathodeFoilKapton_PV = g4.PhysicalVolume(
        name="cathodeFoilKapton_PV",
        rotation=[0, 0, 0],
        position=[0, 0, 0],
        logicalVolume=cathodeFoilKapton_LV,
        motherVolume=fieldcage_assembly,
        registry=reg
    )
        
    cathodeFoilCuLeft_PV = g4.PhysicalVolume(
        name="cathodeFoilCuLeft_PV",
        rotation=[0, 0, 0],
        position=[0, 0, -cathodeKaptonThickness/2],
        logicalVolume=cathodeFoilCu_LV,
        motherVolume=fieldcage_assembly,
        registry=reg
    )
    cathodeFoilCuRight_PV = g4.PhysicalVolume(
        name="cathodeFoilCuRight_PV",
        rotation=[0, 0, 0],
        position=[0, 0, cathodeKaptonThickness/2],
        logicalVolume=cathodeFoilCu_LV,
        motherVolume=fieldcage_assembly,
        registry=reg
    )
    cathodeFrame_PV = g4.PhysicalVolume(
        name="cathodeFrame_PV",
        rotation=[0, 0, 0],
        position=[0, 0, 0],
        logicalVolume=cathodeFrame_LV,
        motherVolume=fieldcage_assembly,
        registry=reg
    )
    
    cathodeSideFrameLeft_PV = g4.PhysicalVolume(
        name="cathodeSideFrameLeft_PV",
        rotation=[0, 0, 0],
        position=[0, 0, -(sideSeparatorThickness/2 + cathodeSideFrameThickness/2)],
        logicalVolume=cathodeSideFrame_LV,
        motherVolume=fieldcage_assembly,
        registry=reg
    )
    cathodeSideFrameRight_PV = g4.PhysicalVolume(
        name="cathodeSideFrameRight_PV",
        rotation=[0, 0, 0],
        position=[0, 0, sideSeparatorThickness/2 + cathodeSideFrameThickness/2],
        logicalVolume=cathodeSideFrame_LV,
        motherVolume=fieldcage_assembly,
        registry=reg
    )
    sideSeparator_PV = g4.PhysicalVolume(
        name="sideSeparator_PV",
        rotation=[0, 0, 0],
        position=[0, 0, 0],
        logicalVolume=sideSeparator_LV,
        motherVolume=fieldcage_assembly,
        registry=reg
    )
    
    cathodeFeedthrough_PV = g4.PhysicalVolume(
        name="cathodeFeedthrough_PV",
        rotation=[0, 0, 0],
        position=[-(cathodeFeedThroughWidth/2 + cathodeFeedThroughDistanceToCopperFrame + cathodeFrameLength/2), 0, 0],
        logicalVolume=cathodeFeedthrough_LV,
        motherVolume=fieldcage_assembly,
        registry=reg
    )
    
    cornersLeft_PV = g4.PhysicalVolume(
        name="cornersLeft_PV",
        rotation=[0, 0, 0],
        position=[0, 0, -(sideSeparatorThickness/2 + cathodeSideFrameThickness + cornersThickness/2)],
        logicalVolume=corners_LV,
        motherVolume=fieldcage_assembly,
        registry=reg
    )
    cornersRight_PV = g4.PhysicalVolume(
        name="cornersRight_PV",
        rotation=[0, 0, 0],
        position=[0, 0, sideSeparatorThickness/2 + cathodeSideFrameThickness + cornersThickness/2],
        logicalVolume=corners_LV,
        motherVolume=fieldcage_assembly,
        registry=reg
    )
    closerFrameLeft_PV = g4.PhysicalVolume(
        name="closerFrameLeft_PV",
        rotation=[0, 0, 0],
        position=[0, 0, -(sideSeparatorThickness/2 + cathodeSideFrameThickness + cornersThickness + closerFrameThickness/2)],
        logicalVolume=closerFrame_LV,
        motherVolume=fieldcage_assembly,
        registry=reg
    )
    closerFrameRight_PV = g4.PhysicalVolume(
        name="closerFrameRight_PV",
        rotation=[0, 0, 0],
        position=[0, 0, sideSeparatorThickness/2 + cathodeSideFrameThickness + cornersThickness + closerFrameThickness/2],
        logicalVolume=closerFrame_LV,
        motherVolume=fieldcage_assembly,
        registry=reg
    )
    
    ringsBoardLeft_PV = g4.PhysicalVolume(
        name="ringsBoardLeft_PV",
        rotation=[0, 0, 0],
        position=[0, 0, -(sideSeparatorThickness/2 + cathodeSideFrameThickness + ringsBoardThickness/2)],
        logicalVolume=ringsBoard_LV,
        motherVolume=fieldcage_assembly,
        registry=reg
    )
    ringsBoardRight_PV = g4.PhysicalVolume(
        name="ringsBoardRight_PV",
        rotation=[0, 0, 0],
        position=[0, 0, sideSeparatorThickness/2 + cathodeSideFrameThickness + ringsBoardThickness/2],
        logicalVolume=ringsBoard_LV,
        motherVolume=fieldcage_assembly,
        registry=reg
    )
    
    for i in range(ringNumber):
        distance = (ringSeparation + ringThickness) * i # to the beginning of the board
        g4.PhysicalVolume(
            name=f"ringLeft{i+1}_PV",
            rotation=[0, 0, 0],
            position=[0, 0, -(sideSeparatorThickness/2 + cathodeSideFrameThickness + ringThickness/2 + distance)],
            logicalVolume=ring_LV,
            motherVolume=fieldcage_assembly,
            registry=reg
        )
        g4.PhysicalVolume(
            name=f"ringRight{i+1}_PV",
            rotation=[0, 0, 0],
            position=[0, 0, sideSeparatorThickness/2 + cathodeSideFrameThickness + ringThickness/2 + distance],
            logicalVolume=ring_LV,
            motherVolume=fieldcage_assembly,
            registry=reg
        )

    resistorAssemblyLeft_PV = g4.PhysicalVolume(
        name="resistorAssemblyLeft_PV",
        rotation=[0, 0, 0],
        position=[(cornersSlotHeight/2-resistorShieldingLength/2), cornersInnerLength/2+resistorShieldingWidth/2, (sideSeparatorThickness/2 + cathodeSideFrameThickness + resistorShieldingThickness/2)],
        logicalVolume=resistorAssembly,
        motherVolume=fieldcage_assembly,
        registry=reg
    )

    resistorAssemblyRight_PV = g4.PhysicalVolume(
        name="resistorAssemblyRight_PV",
        rotation=[0, np.pi, 0],
        position=[-(cornersSlotHeight/2-resistorShieldingLength/2), cornersInnerLength/2+resistorShieldingWidth/2, -(sideSeparatorThickness/2 + cathodeSideFrameThickness + resistorShieldingThickness/2)],
        logicalVolume=resistorAssembly,
        motherVolume=fieldcage_assembly,
        registry=reg
    )

    return reg



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--vis", action="store_true")
    parser.add_argument("--gdml", action="store_true")
    args = parser.parse_args()
    
    reg = generate_fieldcage_assembly()
    fieldcage_assembly = reg.findLogicalVolumeByName("fieldcage_assembly")[0]

    if args.gdml:
        galactic = g4.nist_material_2geant4Material("G4_Galactic")
        assembly_LV = fieldcage_assembly.logicalVolume(material=galactic)
        reg.setWorld(assembly_LV.name)
        w = pyg4ometry.gdml.Writer()
        w.addDetector(reg)
        w.write('fieldcage.gdml')

    if args.vis:
        v = pyg4ometry.visualisation.VtkViewerColouredMaterial()
        v.addLogicalVolume(fieldcage_assembly.logicalVolume())
        v.addAxes(300)
        v.view()