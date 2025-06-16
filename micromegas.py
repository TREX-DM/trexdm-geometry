import vtk
import pyg4ometry
from pyg4ometry import geant4 as g4
import numpy as np

def generate_micromegas_assembly(registry=None):
    """
    Generates the micromegas assembly with all its components.
    Returns the assembly volume.
    """

    mMBaseSquareLength = 324.0 # 324 mm is the full length, so half is 162 mm
    mMBBaseCornerRadius = 187.0 # 187 mm is the radius of the corners
    mMBaseThickness = 4.0 # 4 mm is the thickness of the base
    mMBaseRecessSquareLength = 180.0 # mm
    mMBaseRecessThickness = 2.5 # mm

    mMBaseBracketLength = 210 # mm 
    mMBaseBracketWidth = 37 # mm
    mMBaseBracketThickness = 7.8 # mm
    mMBaseEndToBracketDistance = 15.6 # mm, this is the distance from the end of the base to the bracket

    mMTeflonSpacerPadLength = 202 # mm
    mMTeflonSpacerPadWidth = 18 # mm
    mMTeflonSpacerPadThickness = 4.2 *2 # mm. In the CAD it is 4.2 mm, but in the real one there are two pads, so we double the thickness

    mMTriangularSupportThickness = 15 # mm
    mMTriangularSupportSquareLength = 40 # mm

    mMTapSeparatorBaseLength = 90 # mm
    mMTapSeparatorBaseHeight = 37 # mm
    mMTapSeparatorBaseThickness = 10 # mm

    mMTapSeparatorBaseCutLength = 28 # mm
    mMTapSeparatorBaseCutHeight = 15 # mm


    mMTapSeparatorColumnHeightA = 45# mm
    mMTapSeparatorColumnHeightB = 57.2 # mm
    mMTapSeparatorColumnHeightC = 3 # mm

    mMTapSeparatorColumnLengthA = 34 # mm
    mMTapSeparatorColumnLengthB = 18 # mm
    mMTapSeparatorColumnLengthC = 12 # mm. this is a diameter in reality

    mMTapSeparatorColumnThicknessA = 15 # mm
    mMTapSeparatorColumnThicknessB = 12
    mMTapSeparatorColumnThicknessC = mMTapSeparatorColumnLengthC # mm. this is a diameter in reality

    mMTapSeparatorColumnProtrusionAtoB = 2.5 # mm
    mMTapSeparatorColumnBtoBase = -1 # mm. In the CAD it is -1 mm, but it is adjustable in real life. Negative means that the column B starts below the base, positive means that it starts above the base.

    mMTapSeparatorColumnCtoTriangularSupport = 5.45 + 5.05 # mm. 5.05mm should be the columnCradius (6mm) but the hole of the triangular support is smaller (5.05mm radius) in the CAD

    rollerCylinderRadius = 5.0 # mm
    rollerCylinderLength = 164.0 # mm
    rollerCutShift = 1.0 # mm, this is the shift of the cut to avoid the cylinder to be cut in the middle


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
    galactic = g4.nist_material_2geant4Material("G4_Galactic")
    """

    ### Micromegas base
    mMBaseBracket = g4.solid.Box(
        name="mMBaseBracket",
        pX=mMBaseBracketLength,
        pY=mMBaseBracketWidth,
        pZ=mMBaseBracketThickness,
        lunit="mm",
        registry=reg
    )

    mMBaseSquare0 = g4.solid.Box(
        name="mMBaseSquare0",
        pX=mMBaseSquareLength,
        pY=mMBaseSquareLength,
        pZ=mMBaseThickness,
        lunit="mm",
        registry=reg
    )

    mMBaseCornersCut = g4.solid.Tubs(
        name="mMBaseCornersCut",
        pRMin=0,
        pRMax=mMBBaseCornerRadius,
        pDz=mMBaseThickness,
        pSPhi=0,
        pDPhi=360,
        aunit="deg",
        lunit="mm",
        registry=reg
    )

    mMBaseSquareCutted = g4.solid.Intersection(
        name="mMBase",
        obj1=mMBaseSquare0,
        obj2=mMBaseCornersCut,
        tra2=[[0, 0, 0], [0, 0, 0]],
        registry=reg
    )

    mMBaseSquare1 = g4.solid.Union(
        name="mMBaseSquare1",
        obj1=mMBaseSquareCutted,
        obj2=mMBaseBracket,
        tra2=[[0, 0, 0], [0, mMBaseSquareLength/2 - mMBaseBracketWidth/2 - mMBaseEndToBracketDistance, -(mMBaseThickness/2 + mMBaseBracketThickness/2)]],
        registry=reg
    )
    mMBaseSquare2 = g4.solid.Union(
        name="mMBaseSquare2",
        obj1=mMBaseSquare1,
        obj2=mMBaseBracket,
        tra2=[[0, 0, 0], [0, -(mMBaseSquareLength/2 - mMBaseBracketWidth/2 - mMBaseEndToBracketDistance), -(mMBaseThickness/2 + mMBaseBracketThickness/2)]],
        registry=reg
    )
    mMBaseSquare3 = g4.solid.Union(
        name="mMBaseSquare3",
        obj1=mMBaseSquare2,
        obj2=mMBaseBracket,
        tra2=[[0, 0, 90*3.1416/180], [mMBaseSquareLength/2 - mMBaseBracketWidth/2 - mMBaseEndToBracketDistance, 0, -(mMBaseThickness/2 + mMBaseBracketThickness/2)]],
        registry=reg
    )
    mMBaseSquare = g4.solid.Union(
        name="mMBaseSquare",
        obj1=mMBaseSquare3,
        obj2=mMBaseBracket,
        tra2=[[0, 0, 90*3.1416/180], [-(mMBaseSquareLength/2 - mMBaseBracketWidth/2 - mMBaseEndToBracketDistance), 0, -(mMBaseThickness/2 + mMBaseBracketThickness/2)]],
        registry=reg
    )

    mMBaseRecessSquare = g4.solid.Box(
        name="mMBaseRecessSquare",
        pX=mMBaseRecessSquareLength,
        pY=mMBaseRecessSquareLength,
        pZ=mMBaseRecessThickness,
        lunit="mm",
        registry=reg
    )

    mMBase = g4.solid.Subtraction(
        name="mMBaseSquareCutted",
        obj1=mMBaseSquare,
        obj2=mMBaseRecessSquare,
        tra2=[[0, 0, 0], [0, 0, -mMBaseThickness/2 + mMBaseRecessThickness/2]],
        registry=reg
    )

    ### Spacers

    mMTeflonSpacerPad = g4.solid.Box(
        name="mMTeflonSpacerPad",
        pX=mMTeflonSpacerPadLength,
        pY=mMTeflonSpacerPadWidth,
        pZ=mMTeflonSpacerPadThickness,
        lunit="mm",
        registry=reg
    )

    ### Micromegas to tap separator (and support)
    mMTriangularSupportSquare = g4.solid.Box(
        name="mMTriangularSupportSquare",
        pX=mMTriangularSupportSquareLength,
        pY=mMTriangularSupportSquareLength,
        pZ=mMTriangularSupportThickness,
        lunit="mm",
        registry=reg
    )
    mMTriangularSupportSquareCut = g4.solid.Box(
        name="mMTriangularSupportSquareCut",
        pX=mMTriangularSupportSquareLength*1.414,  # sqrt(2) * length
        pY=mMTriangularSupportSquareLength*1.414,  # sqrt(2) * length
        pZ=mMTriangularSupportThickness,
        lunit="mm",
        registry=reg
    )
    mMTriangularSupport = g4.solid.Subtraction(
        name="mMTriangularSupport",
        obj1=mMTriangularSupportSquare,
        obj2=mMTriangularSupportSquareCut,
        tra2=[[0, 0, 45*3.1416/180], [mMTriangularSupportSquareLength/2, mMTriangularSupportSquareLength/2, 0]],
        registry=reg
    )

    mMTapSeparatorBase0 = g4.solid.Box(
        name="mMTapSeparatorBase0",
        pX=mMTapSeparatorBaseLength,
        pY=mMTapSeparatorBaseHeight,
        pZ=mMTapSeparatorBaseThickness,
        lunit="mm",
        registry=reg
    )
    mMTapSeparatorBaseCut = g4.solid.Box(
        name="mMTapSeparatorBaseCut",
        pX=mMTapSeparatorBaseCutLength,
        pY=mMTapSeparatorBaseCutHeight,
        pZ=mMTapSeparatorBaseThickness,
        lunit="mm",
        registry=reg
    )

    mMTapSeparatorBase = g4.solid.Subtraction(
        name="mMTapSeparatorBase",
        obj1=mMTapSeparatorBase0,
        obj2=mMTapSeparatorBaseCut,
        tra2=[[0, 0, 0], [0, mMTapSeparatorBaseHeight/2 - mMTapSeparatorBaseCutHeight/2, 0]],
        registry=reg
    )

    mMTapSeparatorColumnA = g4.solid.Box(
        name="mMTapSeparatorColumnA",
        pX=mMTapSeparatorColumnLengthA,
        pY=mMTapSeparatorColumnThicknessA,
        pZ=mMTapSeparatorColumnHeightA,
        lunit="mm",
        registry=reg
    )
    mMTapSeparatorColumnB = g4.solid.Box(
        name="mMTapSeparatorColumnB",
        pX=mMTapSeparatorColumnLengthB,
        pY=mMTapSeparatorColumnThicknessB,
        pZ=mMTapSeparatorColumnHeightB,
        lunit="mm",
        registry=reg
    )
    mMTapSeparatorColumnC = g4.solid.Tubs(
        name="mMTapSeparatorColumnC",
        pRMin=0,
        pRMax=mMTapSeparatorColumnThicknessC/2,
        pDz=mMTapSeparatorColumnHeightC,
        pSPhi=0,
        pDPhi=360,
        aunit="deg",
        lunit="mm",
        registry=reg
    )

    mMTapSeparatorBaseA = g4.solid.Union(
        name="mMTapSeparatorBaseA",
        obj1=mMTapSeparatorBase,
        obj2=mMTapSeparatorColumnA,
        tra2=[[0, 0, 0], [0, -mMTapSeparatorBaseHeight/2 + mMTapSeparatorColumnThicknessA/2, mMTapSeparatorBaseThickness/2 +mMTapSeparatorColumnHeightA/2]],
        registry=reg
    )

    mMTapSeparatorBaseACutted = g4.solid.Subtraction(
        name="mMTapSeparatorBaseACutted",
        obj1=mMTapSeparatorBaseA,
        obj2=mMTapSeparatorColumnB,
        tra2=[[0, 0, 0], [0, -mMTapSeparatorBaseHeight/2 + mMTapSeparatorColumnThicknessB/2 -mMTapSeparatorColumnProtrusionAtoB, -mMTapSeparatorBaseThickness/2 + mMTapSeparatorColumnHeightB/2]],
        registry=reg
    )
    mMTapSeparatorColumnBC = g4.solid.Union(
        name="mMTapSeparatorColumnBC",
        obj1=mMTapSeparatorColumnB,
        obj2=mMTapSeparatorColumnC,
        tra2=[[0, 0, 0], [0, 0, mMTapSeparatorColumnHeightB/2 + mMTapSeparatorColumnHeightC/2]],
        registry=reg
    )

    mMTapSeparatorBaseColumn = g4.solid.Union(
        name="mMTapSeparatorBaseColumn",
        obj1=mMTapSeparatorBaseACutted,
        obj2=mMTapSeparatorColumnBC,
        tra2=[[0, 0, 0], [0, -mMTapSeparatorBaseHeight/2 + mMTapSeparatorColumnThicknessB/2 - mMTapSeparatorColumnProtrusionAtoB, mMTapSeparatorBaseThickness/2 + mMTapSeparatorColumnHeightB/2 + mMTapSeparatorColumnBtoBase]],
        registry=reg
    )

    mMSupport = g4.solid.Union(
        name="mMSupport",
        obj1=mMTapSeparatorBaseColumn,
        obj2=mMTriangularSupport,
        tra2=[[0, 0, -135*3.1416/180], [0, - mMTapSeparatorColumnCtoTriangularSupport - mMTapSeparatorBaseHeight/2 + mMTapSeparatorColumnThicknessB/2-mMTapSeparatorColumnProtrusionAtoB, mMTapSeparatorBaseThickness/2 + mMTapSeparatorColumnHeightB + mMTapSeparatorColumnHeightC + mMTapSeparatorColumnBtoBase + mMTriangularSupportThickness/2 ]],
        registry=reg
    )

    ### Roller
    rollerCylinder = g4.solid.Tubs(
        name="rollerCylinder",
        pRMin=0,
        pRMax=rollerCylinderRadius,
        pDz=rollerCylinderLength,
        pSPhi=0,
        pDPhi=360,
        aunit="deg",
        lunit="mm",
        registry=reg
    )

    rollerCut = g4.solid.Box(
        name="rollerCut",
        pX=rollerCylinderRadius,
        pY=rollerCylinderRadius,
        pZ=rollerCylinderLength,
        lunit="mm",
        registry=reg
    )

    roller = g4.solid.Subtraction(
        name="roller",
        obj1=rollerCylinder,
        obj2=rollerCut,
        tra2=[[0, 0, 0], [rollerCylinderRadius/2, -(rollerCylinderRadius/2+rollerCutShift),0]],
        registry=reg
    )

    ### JOIN THE SOLIDS INTO THE ASSEMBLY
    micromegas_assembly = g4.AssemblyVolume(
        name="micromegas_assembly",
        registry=reg,
        addRegistry=True
    )

    mMBase_LV = g4.LogicalVolume(
        solid=mMBase,
        material=copper,
        name="mMBase_LV",
        registry=reg
    )
    mMBaseClosingBracket_LV = g4.LogicalVolume(
        solid=mMBaseBracket,
        material=copper,
        name="mMBaseClosingBracket_LV",
        registry=reg
    )

    mMTeflonSpacerPad_LV = g4.LogicalVolume(
        solid=mMTeflonSpacerPad,
        material=teflon,
        name="mMTeflonSpacerPad_LV",
        registry=reg
    )
    mMSupport_LV = g4.LogicalVolume(
        solid=mMSupport,
        material=copper,
        name="mMSupport_LV",
        registry=reg
    )
    roller_LV = g4.LogicalVolume(
        solid=roller,
        material=teflon,
        name="roller_LV",
        registry=reg
    )

    # Create the physical volumes and add them to the assembly
    mMBase_PV = g4.PhysicalVolume(
        rotation=[0, 0, 0],
        position=[0, 0, 0],
        name="mMBase_PV",
        logicalVolume=mMBase_LV,
        motherVolume=micromegas_assembly,
        registry=reg
    )

    teflonspacerpad_pos_xory = mMBaseSquareLength/2 - mMBaseBracketWidth/2 - mMBaseEndToBracketDistance
    teflonspacerpad_pos_z = mMBaseThickness/2 + mMBaseBracketThickness + mMTeflonSpacerPadThickness/2
    mMTeflonSpacerPad1_PV = g4.PhysicalVolume(
        rotation=[0, 0, 0],
        position=[0, teflonspacerpad_pos_xory, -teflonspacerpad_pos_z],
        name="mMTeflonSpacerPad1_PV",
        logicalVolume=mMTeflonSpacerPad_LV,
        motherVolume=micromegas_assembly,
        registry=reg
    )
    mMTeflonSpacerPad2_PV = g4.PhysicalVolume(
        rotation=[0, 0, 0],
        position=[0, -teflonspacerpad_pos_xory, -teflonspacerpad_pos_z],
        name="mMTeflonSpacerPad2_PV",
        logicalVolume=mMTeflonSpacerPad_LV,
        motherVolume=micromegas_assembly,
        registry=reg
    )
    mMTeflonSpacerPad3_PV = g4.PhysicalVolume(
        rotation=[0, 0, 90*np.pi/180],
        position=[teflonspacerpad_pos_xory, 0, -teflonspacerpad_pos_z],
        name="mMTeflonSpacerPad3_PV",
        logicalVolume=mMTeflonSpacerPad_LV,
        motherVolume=micromegas_assembly,
        registry=reg
    )
    mMTeflonSpacerPad4_PV = g4.PhysicalVolume(
        rotation=[0, 0, 90*np.pi/180],
        position=[-teflonspacerpad_pos_xory, 0, -teflonspacerpad_pos_z],
        name="mMTeflonSpacerPad4_PV",
        logicalVolume=mMTeflonSpacerPad_LV,
        motherVolume=micromegas_assembly,
        registry=reg
    )

    closingbracket_pos_xory = teflonspacerpad_pos_xory
    closingbracket_pos_z = teflonspacerpad_pos_z + mMTeflonSpacerPadThickness/2 + mMBaseBracketThickness/2 + 0 # that 0 should be the thickness of the (double) limandes

    mMBaseClosingBracket1_PV = g4.PhysicalVolume(
        rotation=[0, 0, 0],
        position=[0, closingbracket_pos_xory, -closingbracket_pos_z],
        name="mMBaseClosingBracket1_PV",
        logicalVolume=mMBaseClosingBracket_LV,
        motherVolume=micromegas_assembly,
        registry=reg
    )
    mMBaseClosingBracket2_PV = g4.PhysicalVolume(
        rotation=[0, 0, 0],
        position=[0, -closingbracket_pos_xory, -closingbracket_pos_z],
        name="mMBaseClosingBracket2_PV",
        logicalVolume=mMBaseClosingBracket_LV,
        motherVolume=micromegas_assembly,
        registry=reg
    )
    mMBaseClosingBracket_3_PV = g4.PhysicalVolume(
        rotation=[0, 0, 90*np.pi/180],
        position=[closingbracket_pos_xory, 0, -closingbracket_pos_z],
        name="mMBaseClosingBracket3_PV",
        logicalVolume=mMBaseClosingBracket_LV,
        motherVolume=micromegas_assembly,
        registry=reg
    )
    mMBaseClosingBracket_4_PV = g4.PhysicalVolume(
        rotation=[0, 0, 90*np.pi/180],
        position=[-closingbracket_pos_xory, 0, -closingbracket_pos_z],
        name="mMBaseClosingBracket4_PV",
        logicalVolume=mMBaseClosingBracket_LV,
        motherVolume=micromegas_assembly,
        registry=reg
    )
    ### Rollers. In the CAD design there are 4 (one on each side), but in the real life there are only 2
    mMBaseTeflonRoller1_PV = g4.PhysicalVolume(
        rotation=[90*3.1416/180, 0, 0],
        position=[-mMBaseSquareLength/2, 0, -(mMBaseThickness/2 + rollerCutShift)],
        name="mMBaseTeflonRoller1_PV",
        logicalVolume=roller_LV,
        motherVolume=micromegas_assembly,
        registry=reg
    )
    mMBaseTeflonRoller2_PV = g4.PhysicalVolume(
        rotation=[-90*3.1416/180, 0, np.pi],
        position=[mMBaseSquareLength/2, 0, -(mMBaseThickness/2 + rollerCutShift)],
        name="mMBaseTeflonRoller2_PV",
        logicalVolume=roller_LV,
        motherVolume=micromegas_assembly,
        registry=reg
    )


    ### Micromegas support
    mMSupportDistanceToCenter_XorY = 220.79/2 #mm
    mMSupport_pos_z = mMBaseThickness/2 + mMTapSeparatorBaseThickness/2 + mMTapSeparatorColumnHeightB + mMTapSeparatorColumnHeightC + mMTapSeparatorColumnBtoBase + mMTriangularSupportThickness
    mMSupport1_PV = g4.PhysicalVolume(
        rotation=[0, 0, -45*np.pi/180],  # 45 degrees rotation
        position=[mMSupportDistanceToCenter_XorY, -mMSupportDistanceToCenter_XorY, -mMSupport_pos_z],
        name="mMSupport1_PV",
        logicalVolume=mMSupport_LV,
        motherVolume=micromegas_assembly,
        registry=reg
    )
    mMSupport2_PV = g4.PhysicalVolume(
        rotation=[0, 0, 135*np.pi/180],  # 45 degrees rotation
        position=[-mMSupportDistanceToCenter_XorY, mMSupportDistanceToCenter_XorY, -mMSupport_pos_z],
        name="mMSupport2_PV",
        logicalVolume=mMSupport_LV,
        motherVolume=micromegas_assembly,
        registry=reg
    )

    return reg

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--vis", action="store_true")
    parser.add_argument("--gdml", action="store_true")
    args = parser.parse_args()
    
    reg = generate_micromegas_assembly()
    micromegas_assembly = reg.findLogicalVolumeByName("micromegas_assembly")[0]
    print(micromegas_assembly)

    if args.gdml:
        assembly_LV = micromegas_assembly.logicalVolume(material=galactic)
        reg.setWorld(assembly_LV.name)
        w = pyg4ometry.gdml.Writer()
        w.addDetector(reg)
        w.write('micromegas.gdml')

    if args.vis:
        v = pyg4ometry.visualisation.VtkViewerColouredMaterial()

        v.addLogicalVolume(micromegas_assembly.logicalVolume())

        v.addAxes(300)
        v.view()
