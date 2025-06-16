import vtk
import pyg4ometry
from pyg4ometry import geant4 as g4
import numpy as np

def generate_gem_assembly(name="gem_assembly", registry=None, is_right_side=True):
    """
    Generates the GEM assembly with all its components.
    Returns the assembly volume.
    """

    ### ------------------ GEM foil and support frame ------------------ ###
    gemKaptonFoilLength = 280.0 # mm
    gemKaptonFoilThickness = 0.05 # 50um
    gemKaptonFeedthroughLength = 15.81 # mm
    gemKaptonFeedthroughWidth = 12.0 # mm
    gemCopperFoilLength = 245.0 # mm
    gemCopperFoilThickness = 0.005 # 5um

    gemCopperFeedthroughLength = 22.41 # mm
    gemCopperFeedthroughWidth = 2 # mm
    gemCopperFeedthroughInnerRadius = 4.0 # mm
    gemCopperFeedthroughOuterRadius = 5.0 # mm
    gemDistanceBetweenFeedthroughs = 34.0 # mm, this is the distance between the two closer edges of the kaptonfeedthroughs


    gemFrameLength = 280.0 # mm. Length of the outer square of the frame
    gemFrameWidth = 12.5 # mm
    gemFrameThickness = 4.0 # mm

    gemFrameFeedthroughIndentationLength = 14.0 # mm
    gemFrameFeedthroughIndentationDepth = 0.5 # mm

    gemmMSeparatorLength = 242.5 # mm
    gemmMSeparatorWidth = 16.0 # mm
    gemmMSeparatorThickness = 5.5 # mm. There is a protusion to tense the GEM foil that is 2mm more. This is not taken into account...
    gemmMSeparatorExtensionLength = 16.0 # mm
    gemmMSeparatorExtensionWidth = 10.0 # mm
    gemmMSeparatorExtensionDistance = 128.0 # mm, this is the distance from the closer edges of the extensions

    gemmMSeparatorFixerLength = 151.2 # mm
    gemmMSeparatorFixerWidth = 12.25 # mm
    gemmMSeparatorFixerThickness = 3.0 # mm
    gemmMSeparatorFixerToSeparatorDistance = 3.64 # mm, this is the closer edges of the fixer to the separator

    gemmMSeparatorDistance = 248.0 # mm, this is the distance between the two closer edges of the separators

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
    ### Corners Cut to save the vessel radius ###
    mMBBaseCornerRadius = 187.0 # 187 mm is the radius of the corners
    mMBaseThickness = 4.0 # 4 mm is the thickness of the base
    mMBaseCornersCut = g4.solid.Tubs(
        name="mMBaseCornersCutForGem",
        pRMin=0,
        pRMax=mMBBaseCornerRadius,
        pDz=mMBaseThickness,
        pSPhi=0,
        pDPhi=360,
        aunit="deg",
        lunit="mm",
        registry=reg
    )

    ### GEM Kapton Foil Solids ###
    gemKaptonFoilSquare = g4.solid.Box(
        name="gemKaptonFoilSquare",
        pX=gemKaptonFoilLength,
        pY=gemKaptonFoilLength,
        pZ=gemKaptonFoilThickness,
        lunit="mm",
        registry=reg
    )

    gemKaptonFoilSquareCutted = g4.solid.Intersection(
        name="gemKaptonFoilSquareCutted",
        obj1=gemKaptonFoilSquare,
        obj2=mMBaseCornersCut,
        tra2=[[0, 0, 0], [0, 0, 0]],
        registry=reg
    )
    gemKaptonFoilFeedthrough0 = g4.solid.Box(
        name="gemKaptonFoilFeedthrough0",
        pX=gemKaptonFeedthroughLength,
        pY=gemKaptonFeedthroughWidth,
        pZ=gemKaptonFoilThickness,
        lunit="mm",
        registry=reg
    )
    gemKaptonFoilFeedthroughCut = g4.solid.Tubs(
        name="gemKaptonFoilFeedthroughCut",
        pRMin=0,
        pRMax=gemCopperFeedthroughInnerRadius,
        pDz=gemKaptonFoilThickness,
        pSPhi=0,
        pDPhi=360,
        aunit="deg",
        lunit="mm",
        registry=reg
    )

    gemKaptonFoilFeedthrough = g4.solid.Subtraction(
        name="gemKaptonFoilFeedthrough",
        obj1=gemKaptonFoilFeedthrough0,
        obj2=gemKaptonFoilFeedthroughCut,
        tra2=[[0, 0, 0], [gemKaptonFeedthroughLength/2 - gemCopperFeedthroughOuterRadius - 1, 0, 0]],
        registry=reg
    )

    gemKaptonFoil0 = g4.solid.Union(
        name="gemKaptonFoil0",
        obj1=gemKaptonFoilSquareCutted,
        obj2=gemKaptonFoilFeedthrough,
        tra2=[[0, 0, 0], [gemKaptonFoilLength/2 + gemKaptonFeedthroughLength/2, gemDistanceBetweenFeedthroughs/2 + gemKaptonFeedthroughWidth/2, 0]],
        registry=reg
    )

    gemKaptonFoil = g4.solid.Union(
        name="gemKaptonFoil",
        obj1=gemKaptonFoil0,
        obj2=gemKaptonFoilFeedthrough,
        tra2=[[0, 0, 0], [gemKaptonFoilLength/2 + gemKaptonFeedthroughLength/2, -(gemDistanceBetweenFeedthroughs/2 + gemKaptonFeedthroughWidth/2), 0]],
        registry=reg
    )

    ### GEM Copper Foil Solids ###
    gemCopperFeedthroughRing = g4.solid.Tubs(
        name="gemCopperFeedthroughRing",
        pRMin=gemCopperFeedthroughInnerRadius,
        pRMax=gemCopperFeedthroughOuterRadius,
        pDz=gemCopperFoilThickness,
        pSPhi=0,
        pDPhi=360,
        aunit="deg",
        lunit="mm",
        registry=reg
    )
    gemCopperFeedThroughBox = g4.solid.Box(
        name="gemCopperFeedThroughBox",
        pX=gemCopperFeedthroughLength,
        pY=gemCopperFeedthroughWidth,
        pZ=gemCopperFoilThickness,
        lunit="mm",
        registry=reg
    )

    gemCopperFeedThrough = g4.solid.Union(
        name="gemCopperFeedThrough",
        obj1=gemCopperFeedThroughBox,
        obj2=gemCopperFeedthroughRing,
        tra2=[[0, 0, 0], [gemCopperFeedthroughLength/2 + gemCopperFeedthroughOuterRadius, 0, 0]],
        registry=reg
    )

    gemCopperFoil = g4.solid.Box(
        name="gemCopperFoil",
        pX=gemCopperFoilLength,
        pY=gemCopperFoilLength,
        pZ=gemCopperFoilThickness,
        lunit="mm",
        registry=reg
    )

    gemTop = g4.solid.Union(
        name="gemTop",
        obj1=gemCopperFoil,
        obj2=gemCopperFeedThrough,
        tra2=[[0, 0, 0], [gemCopperFoilLength/2 + gemCopperFeedthroughLength/2, -(gemDistanceBetweenFeedthroughs/2 + gemKaptonFeedthroughWidth/2), 0]],
        registry=reg
    )

    gemBottom = g4.solid.Union(
        name="gemBottom",
        obj1=gemCopperFoil,
        obj2=gemCopperFeedThrough,
        tra2=[[0, 0, 0], [gemCopperFoilLength/2 + gemCopperFeedthroughLength/2, gemDistanceBetweenFeedthroughs/2 + gemKaptonFeedthroughWidth/2, 0]],
        registry=reg
    )


    ### GEM Frame Solids ###
    gemFrameOuterSquare = g4.solid.Box(
        name="gemFrameOuterSquare",
        pX=gemFrameLength,
        pY=gemFrameLength,
        pZ=gemFrameThickness,
        lunit="mm",
        registry=reg
    )
    gemFrameInnerSquare = g4.solid.Box(
        name="gemFrameInnerSquare",
        pX=gemFrameLength - 2*gemFrameWidth,
        pY=gemFrameLength - 2*gemFrameWidth,
        pZ=gemFrameThickness,
        lunit="mm",
        registry=reg
    )

    gemFrameOuterWithoutCorners = g4.solid.Intersection(
        name="gemFrameOuterWithoutCorners",
        obj1=gemFrameOuterSquare,
        obj2=mMBaseCornersCut,
        tra2=[[0, 0, 0], [0, 0, 0]],
        registry=reg
    )

    gemFrame0 = g4.solid.Subtraction(
        name="gemFrame0",
        obj1=gemFrameOuterWithoutCorners,
        obj2=gemFrameInnerSquare,
        tra2=[[0, 0, 0], [0, 0, 0]],
        registry=reg
    )

    gemFrameFeedthroughIndentation = g4.solid.Box(
        name="gemFrameFeedthroughIndentation",
        pX=gemFrameWidth,
        pY=gemFrameFeedthroughIndentationLength,
        pZ=gemFrameFeedthroughIndentationDepth,
        lunit="mm",
        registry=reg
    )

    gemFrame1 = g4.solid.Subtraction(
        name="gemFrame1",
        obj1=gemFrame0,
        obj2=gemFrameFeedthroughIndentation,
        tra2=[[0, 0, 0], [gemFrameLength/2 - gemFrameWidth/2, gemDistanceBetweenFeedthroughs/2 + gemKaptonFeedthroughWidth/2, -gemFrameThickness/2 + gemFrameFeedthroughIndentationDepth/2]],
        registry=reg
    )

    gemFrame = g4.solid.Subtraction(
        name="gemFrame",
        obj1=gemFrame1,
        obj2=gemFrameFeedthroughIndentation,
        tra2=[[0, 0, 0], [gemFrameLength/2 - gemFrameWidth/2, -(gemDistanceBetweenFeedthroughs/2 + gemKaptonFeedthroughWidth/2), -gemFrameThickness/2 + gemFrameFeedthroughIndentationDepth/2]],
        registry=reg
    )


    ### GEM - mM separator/support ###

    gemmMSeparatorExtension = g4.solid.Box(
        name="gemmMSeparatorExtension",
        pX=gemmMSeparatorExtensionWidth,
        pY=gemmMSeparatorExtensionLength,
        pZ=gemmMSeparatorThickness,
        lunit="mm",
        registry=reg
    )

    gemmMSeparator0 = g4.solid.Box(
        name="gemmMSeparator0",
        pX=gemmMSeparatorLength,
        pY=gemmMSeparatorWidth,
        pZ=gemmMSeparatorThickness,
        lunit="mm",
        registry=reg
    )

    gemmMSeparator1 = g4.solid.Union(
        name="gemmMSeparator1",
        obj1=gemmMSeparator0,
        obj2=gemmMSeparatorExtension,
        tra2=[[0, 0, 0], [gemmMSeparatorExtensionDistance/2 + gemmMSeparatorExtensionWidth/2, gemmMSeparatorWidth/2 + gemmMSeparatorExtensionLength/2, 0]],
        registry=reg
    )

    gemmMSeparator = g4.solid.Union(
        name="gemmMSeparator",
        obj1=gemmMSeparator1,
        obj2=gemmMSeparatorExtension,
        tra2=[[0, 0, 0], [-(gemmMSeparatorExtensionDistance/2 + gemmMSeparatorExtensionWidth/2), gemmMSeparatorWidth/2 + gemmMSeparatorExtensionLength/2, 0]],
        registry=reg
    )

    gemmMSeparatorFixer = g4.solid.Box(
        name="gemmMSeparatorFixer",
        pX=gemmMSeparatorFixerLength,
        pY=gemmMSeparatorFixerWidth,
        pZ=gemmMSeparatorFixerThickness,
        lunit="mm",
        registry=reg
    )

    ### JOIN THE SOLIDS INTO THE ASSEMBLY ###
    gem_assembly = g4.AssemblyVolume(
        name=name,
        registry=reg,
        addRegistry=True
    )

    gemKaptonFoil_LV = g4.LogicalVolume(
        name="gemKaptonFoil_LV",
        solid=gemKaptonFoil,
        material=kapton,
        registry=reg
    )
    gemTop_LV = g4.LogicalVolume(
        name="gemTop_LV",
        solid=gemTop,
        material=copper,
        registry=reg
    )
    gemBottom_LV = g4.LogicalVolume(
        name="gemBottom_LV",
        solid=gemBottom,
        material=copper,
        registry=reg
    )

    gemFrame_LV = g4.LogicalVolume(
        name="gemFrame_LV",
        solid=gemFrame,
        material=copper,
        registry=reg
    )
    
    gemmMSeparatorFixer_LV = g4.LogicalVolume(
        name="gemmMSeparatorFixer_LV",
        solid=gemmMSeparatorFixer,
        material=copper,
        registry=reg
    )
    
    gemmMSeparator_LV = g4.LogicalVolume(
        name="gemmMSeparator_LV",
        solid=gemmMSeparator,
        material=teflon,
        registry=reg
    )

    # Add the physical volumes to the assembly
    side_z_dir = 1 if is_right_side else -1

    gemKaptonFoil_PV = g4.PhysicalVolume(
        name="gemKaptonFoil_PV",
        rotation=[0, 0, 0],
        position=[0, 0, 0],
        logicalVolume=gemKaptonFoil_LV,
        motherVolume=gem_assembly,
        registry=reg
    )
    gemTop_PV = g4.PhysicalVolume(
        name="gemTop_PV",
        rotation=[0, 0, 0],
        position=[0, 0, side_z_dir*(gemCopperFoilThickness/2 + gemKaptonFoilThickness/2)],
        logicalVolume=gemTop_LV,
        motherVolume=gem_assembly,
        registry=reg
    )
    gemBottom_PV = g4.PhysicalVolume(
        name="gemBottom_PV",
        rotation=[0, 0, 0],
        position=[0, 0, -side_z_dir*(gemCopperFoilThickness/2 + gemKaptonFoilThickness/2)],
        logicalVolume=gemBottom_LV,
        motherVolume=gem_assembly,
        registry=reg
    )
    gemFrame_PV = g4.PhysicalVolume(
        name="gemFrame_PV",
        rotation=[0, 0, 0],
        position=[0, 0, side_z_dir*(gemKaptonFoilThickness + gemFrameThickness/2)],
        logicalVolume=gemFrame_LV,
        motherVolume=gem_assembly,
        registry=reg
    )

    separator1_pos = np.array([ 0, gemmMSeparatorDistance/2 + gemmMSeparatorWidth/2, -side_z_dir*(gemmMSeparatorThickness/2+gemKaptonFoilThickness)])
    fixer_wrt_separator1_pos = np.array([ 0, gemmMSeparatorFixerToSeparatorDistance + gemmMSeparatorWidth/2 + gemmMSeparatorFixerWidth/2, side_z_dir*(gemmMSeparatorThickness/2 + gemmMSeparatorFixerThickness/2)])
    separator2_pos = np.array([ 0, -(gemmMSeparatorDistance/2 + gemmMSeparatorWidth/2), -side_z_dir*(gemmMSeparatorThickness/2+gemKaptonFoilThickness)])
    fixer_wrt_separator2_pos = np.array([ 0, -(gemmMSeparatorFixerToSeparatorDistance + gemmMSeparatorWidth/2 + gemmMSeparatorFixerWidth/2), side_z_dir*(gemmMSeparatorThickness/2 + gemmMSeparatorFixerThickness/2)])
    
    gemmMSeparator1_PV = g4.PhysicalVolume(
        name="gemmMSeparator1_PV",
        rotation=[0, 0, 0],
        position=separator1_pos,
        logicalVolume=gemmMSeparator_LV,
        motherVolume=gem_assembly,
        registry=reg
    )

    gemmMSeparatorFixer1_PV = g4.PhysicalVolume(
        name="gemmMSeparatorFixer1_PV",
        rotation=[0, 0, 0],
        position=separator1_pos + fixer_wrt_separator1_pos,
        logicalVolume=gemmMSeparatorFixer_LV,
        motherVolume=gem_assembly,
        registry=reg
    )

    # Add the second separator and fixer
    gemmMSeparator2_PV = g4.PhysicalVolume(
        name="gemmMSeparator2_PV",
        rotation=[0, 0, np.pi],
        position=separator2_pos,
        logicalVolume=gemmMSeparator_LV,
        motherVolume=gem_assembly,
        registry=reg
    )
    gemmMSeparatorFixer2_PV = g4.PhysicalVolume(
        name="gemmMSeparatorFixer2_PV",
        rotation=[0, 0, 0],
        position=separator2_pos + fixer_wrt_separator2_pos,
        logicalVolume=gemmMSeparatorFixer_LV,
        motherVolume=gem_assembly,
        registry=reg
    )

    return reg
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--vis", action="store_true")
    parser.add_argument("--gdml", action="store_true")
    args = parser.parse_args()
    
    reg = generate_gem_assembly(is_right_side=False)
    gem_assembly = reg.findLogicalVolumeByName("gem_assembly")[0]
    print(gem_assembly)

    if args.gdml:
        assembly_LV = gem_assembly.logicalVolume(material=galactic)
        reg.setWorld(assembly_LV.name)
        w = pyg4ometry.gdml.Writer()
        w.addDetector(reg)
        w.write('gem.gdml')

    if args.vis:
        v = pyg4ometry.visualisation.VtkViewerColouredMaterial()

        v.addLogicalVolume(gem_assembly.logicalVolume())

        v.addAxes(300)
        v.view()