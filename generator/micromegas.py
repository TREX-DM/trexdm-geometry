import vtk
import pyg4ometry
from pyg4ometry import geant4 as g4
from pyg4ometry import transformation as tf
import numpy as np
import utils

mMBaseLength = 324.0 # 324 mm is the full length, so half is 162 mm
mMBaseRadius = 187.0 # 187 mm is the radius of the corners
mMBaseThickness = 4.0 # 4 mm is the thickness of the base
mMBaseRecessLength = 180.0 # mm
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

capSupportBaseLength = 90 # mm
capSupportBaseHeight = 37 # mm
capSupportBaseThickness = 10 # mm

capSupportBaseCutLength = 28 # mm
capSupportBaseCutHeight = 15 # mm


capSupportColumnHeightA = 45# mm
capSupportColumnHeightB = 57.2 # mm
capSupportColumnHeightC = 3 # mm

capSupportColumnLengthA = 34 # mm
capSupportColumnLengthB = 18 # mm
capSupportColumnLengthC = 12 # mm. this is a diameter in reality

capSupportColumnThicknessA = 15 # mm
capSupportColumnThicknessB = 12
capSupportColumnThicknessC = capSupportColumnLengthC # mm. this is a diameter in reality

capSupportColumnProtrusionAtoB = 2.5 # mm
capSupportColumnBtoBase = -2 # mm. In the CAD it is -1 mm, but it is adjustable in real life. Negative means that the column B starts below the base, positive means that it starts above the base.

capSupportColumnCtoTriangularSupport = 5.45 + 5.05 # mm. 5.05mm should be the columnCradius (6mm) but the hole of the triangular support is smaller (5.05mm radius) in the CAD

rollerCylinderRadius = 5.0 # mm
rollerCylinderLength = 164.0 # mm
rollerCutShift = 1.0 # mm, this is the shift of the cut to avoid the cylinder to be cut in the middle

capSupportFinalHeight = capSupportBaseThickness + capSupportColumnHeightB + capSupportColumnBtoBase + capSupportColumnHeightC + mMTriangularSupportThickness


mMLength = 250 # 25cm of active Micromegas area
mMCopperFoilThickness = 0.017 # 17um
mMKaptonFoilThickness = 0.05 # 50um. This is the amplification gap
mMKaptonFoil2Thickness = 0.15 # 150um. This is the kapton foil that separates the channels Y from the ground plane (see Hector Mirallas Thesis)

mMBoardLength = mMBaseLength
mMBoardRadius = mMBaseRadius - 5 # it is a bit smaller than the base radius. 5mm less estimated by eye inspection of the pictures we have :)
mMBoardThickness = mMCopperFoilThickness*4 + mMKaptonFoilThickness*2 + mMKaptonFoil2Thickness
mMBoardFoldInnerRadius = mMBaseThickness/2 + mMBaseBracketThickness/2 + mMTeflonSpacerPadThickness/2

limandeBracketSideLength = mMBaseBracketLength
limandeBracketSideWidth = 40 # mm. It is slightly wider than the bracket
limandeCopperThickness = 0.017 # 17um, same as the micromegas copper layers
limandeThickness = limandeCopperThickness*4 + 0.350*2 + 0.050 # mm. 350um and 50um is Kapton and 17um is copper (see Hector Mirallas Thesis section 8.2)

limandeHalfTriangleHeight = 77.95

limandeFoldDistance = 20
limandeTrapezoidLength = 40.4
limandeWidth = 60
limandeStraightLength = capSupportFinalHeight - mMBaseBracketThickness - mMTeflonSpacerPadThickness - mMBoardThickness - limandeThickness*2 - limandeFoldDistance # up to the vessel cap

def generate_micromegas_board(name="mMBoard", suffix="", thickness_in_mm=1, thickness_below_in_mm=0, registry=None):
    """ Generates the micromegas board geometry. It is done in this function because the board has several layers with the same shape but different materials.
    The function is meant to generate the solid of each layer which each has different thickness. Also, the inner layer is inside the other, so the inner radius
    of the fold has to be increased by the thickness_below_in_mm parameter.

    param name: Name of the final solid. This will NOT include the suffix.
    param suffix: Suffix to append to the solids needed to generate the final solid. If you call this function multiple times with the same registry,
    you must use a different suffix for each call to avoid solid name conflicts.
    param thickness_in_mm: Thickness of the layer of the board in mm.
    param thickness_below_in_mm: Thickness below the board in mm, used for the inner radius of the fold.
    param registry: Registry to use for the Geant4 objects. If None, a new registry is created.
    Returns the registry with the board geometry.
    """

    # Registry
    if registry is None:
        reg = g4.Registry()
    else:
        reg = registry

    boardThickness = thickness_in_mm
    innerRadius = mMBoardFoldInnerRadius + thickness_below_in_mm
    mMBoardSquare = g4.solid.Box(
        name="mMBoardSquare" + suffix,
        pX=mMBoardLength,
        pY=mMBoardLength,
        pZ=boardThickness,
        lunit="mm",
        registry=reg
    )
    mMBoardCornersCut = g4.solid.Tubs(
        name="mMBoardCornersCut" + suffix,
        pRMin=0,
        pRMax=mMBoardRadius,
        pDz=boardThickness,
        pSPhi=0,
        pDPhi=360,
        aunit="deg",
        lunit="mm",
        registry=reg
    )

    mMBoard0 = g4.solid.Intersection(
        name="mMBoard0" + suffix,
        obj1=mMBoardSquare,
        obj2=mMBoardCornersCut,
        tra2=[[0, 0, 0], [0, 0, 0]],
        registry=reg
    )

    mMBoardFold = g4.solid.Tubs(
        name="mMBoardFold" + suffix,
        pRMin=innerRadius,
        pRMax=innerRadius + boardThickness,
        pDz=rollerCylinderLength,
        pSPhi=0,
        pDPhi=180,
        aunit="deg",
        lunit="mm",
        registry=reg
    )

    mMBoardConnectorWidth = mMBaseBracketWidth + mMBaseEndToBracketDistance
    mMBoardConnectorBox = g4.solid.Box(
        name="mMBoardConnectorBox" + suffix,
        pX=mMBaseBracketLength,
        pY=mMBoardConnectorWidth,
        pZ=boardThickness,
        lunit="mm",
        registry=reg
    )
    
    connector_hipotenuse = np.sqrt(mMBaseEndToBracketDistance**2+((mMBaseBracketLength-rollerCylinderLength)/2)**2)
    connector_cut_angle = np.arcsin(mMBaseEndToBracketDistance / connector_hipotenuse)
    connector_cut_rotation_matrix = tf.axisangle2matrix(
        axis=[0, 0, 1],  # rotation around Z-axis
        angle=connector_cut_angle
    )
    corner_pos = np.array([-mMBaseBracketLength/2, mMBoardConnectorWidth/2 - mMBaseEndToBracketDistance, 0]) 
    cornerCut_pos = np.array([connector_hipotenuse/2, connector_hipotenuse/2, 0])
    mMBoardConnectorCut = g4.solid.Box(
        name="mMBoardConnectorCut" + suffix,
        pX=connector_hipotenuse,
        pY=connector_hipotenuse,
        pZ=boardThickness + 0.01,
        lunit="mm",
        registry=reg
    )
    mMBoardConnector0 = g4.solid.Subtraction(
        name="mMBoardConnector0" + suffix,
        obj1=mMBoardConnectorBox,
        obj2=mMBoardConnectorCut,
        tra2=[[0, 0, connector_cut_angle], list(corner_pos + connector_cut_rotation_matrix @ cornerCut_pos)],
        registry=reg
    )
    corner_pos = np.array([mMBaseBracketLength/2, mMBoardConnectorWidth/2 - mMBaseEndToBracketDistance, 0])
    cornerCut_pos = np.array([-connector_hipotenuse/2, connector_hipotenuse/2, 0])
    connector_cut_rotation_matrix = tf.axisangle2matrix(
        axis=[0, 0, 1],  # rotation around Z-axis
        angle=-connector_cut_angle
    )
    mMBoardConnector = g4.solid.Subtraction(
        name="mMBoardConnector" + suffix,
        obj1=mMBoardConnector0,
        obj2=mMBoardConnectorCut,
        tra2=[[0, 0, -connector_cut_angle], list(corner_pos + connector_cut_rotation_matrix @ cornerCut_pos)],
        registry=reg
    )

    mMBoardWithFold1 = g4.solid.Union(
        name="mMBoardWithFold1" + suffix,
        obj1=mMBoard0,
        obj2=mMBoardFold,
        tra2=[[np.pi/2, -np.pi/2, 0], [-mMBoardLength/2, 0, -(innerRadius+boardThickness/2)]],
        registry=reg
    )

    mMBoardWithFold2 = g4.solid.Union(
        name="mMBoardWithFold2" + suffix,
        obj1=mMBoardWithFold1,
        obj2=mMBoardFold,
        tra2=[[np.pi/2, np.pi/2, 0], [mMBoardLength/2, 0, -(innerRadius+boardThickness/2)]],
        registry=reg
    )

    mMBoardWithFold3 = g4.solid.Union(
        name="mMBoardWithFold3" + suffix,
        obj1=mMBoardWithFold2,
        obj2=mMBoardFold,
        tra2=[[0, np.pi/2, np.pi], [0, -mMBoardLength/2, -(innerRadius+boardThickness/2)]],
        registry=reg
    )

    mMBoardWithFold = g4.solid.Union(
        name="mMBoardWithFold" + suffix,
        obj1=mMBoardWithFold3,
        obj2=mMBoardFold,
        tra2=[[0, np.pi/2, 0], [0, mMBoardLength/2, -(innerRadius+boardThickness/2)]],
        registry=reg
    )

    mMBoardWithFoldAndConnector0 = g4.solid.Union(
        name="mMBoardWithFoldAndConnector0" + suffix,
        obj1=mMBoardWithFold,
        obj2=mMBoardConnector,
        tra2=[[0, 0, 0], [0, mMBoardLength/2 - mMBoardConnectorWidth/2, -(innerRadius*2+boardThickness)]],
        registry=reg
    )

    mMBoardWithFoldAndConnector1 = g4.solid.Union(
        name="mMBoardWithFoldAndConnector1" + suffix,
        obj1=mMBoardWithFoldAndConnector0,
        obj2=mMBoardConnector,
        tra2=[[0, 0, np.pi], [0, -mMBoardLength/2 + mMBoardConnectorWidth/2, -(innerRadius*2+boardThickness)]],
        registry=reg
    )

    mMBoardWithFoldAndConnector2 = g4.solid.Union(
        name="mMBoardWithFoldAndConnector2" + suffix,
        obj1=mMBoardWithFoldAndConnector1,
        obj2=mMBoardConnector,
        tra2=[[0, 0, -np.pi/2], [mMBoardLength/2 - mMBoardConnectorWidth/2, 0, -(innerRadius*2+boardThickness)]],
        registry=reg
    )

    mMBoard = g4.solid.Union(
        name=name,
        obj1=mMBoardWithFoldAndConnector2,
        obj2=mMBoardConnector,
        tra2=[[0, 0, np.pi/2], [-mMBoardLength/2 + mMBoardConnectorWidth/2, 0, -(innerRadius*2+boardThickness)]],
        registry=reg
    )

    return reg

def generate_limandes(name="limande", suffix="", thickness_in_mm=1, thickness_below_in_mm=0, is_right_side=True, registry=None):
    """
    Generates the limandes (A and B) solids.
    param name: Name of the volume.
    param suffix: Suffix to append to the solid names.
    param thickness_in_mm: Thickness of the solid parts in mm.
    param thickness_below_in_mm:
    param registry: Registry to use for the Geant4 objects. If None, a new registry is created.
    """
    # Registry
    if registry is None:
        reg = g4.Registry()
    else:
        reg = registry

    side_z_dir = 1
    if is_right_side:
        side_z_dir = -1

    thickness = thickness_in_mm
    foldDistance = limandeFoldDistance + thickness_below_in_mm*2
    straightLength = limandeStraightLength + thickness_below_in_mm

    limandeBracketSide = g4.solid.Box(
        name="limandeBracketSide" + suffix,
        pX=limandeBracketSideLength,
        pY=limandeBracketSideWidth,
        pZ=thickness,
        lunit="mm",
        registry=reg
    )

    limandeHalfTriangleBox = g4.solid.Box(
        name="limandeHalfTriangleBox" + suffix,
        pX=limandeBracketSideLength/2,
        pY=limandeHalfTriangleHeight,
        pZ=thickness,
        lunit="mm",
        registry=reg
    )

    limandeHipotenuse = np.sqrt(limandeHalfTriangleHeight**2 + (limandeBracketSideLength/2)**2)  # sqrt(2) * height
    limandeHalfTriangleCut = g4.solid.Box(
        name="limandeHalfTriangleCut" + suffix,
        pX=limandeHipotenuse,
        pY=limandeHalfTriangleHeight,
        pZ=thickness + 0.1, # to ensure cut
        lunit="mm",
        registry=reg
    )

    rotation_angle = np.arcsin(limandeHalfTriangleHeight/limandeHipotenuse) #np.arctan2(limandeHalfTriangleHeight, limandeBracketSideLength/2)  # angle in radians
    rotation_matrix = tf.axisangle2matrix(
        axis=[0, 0, 1],  # rotation around Z-axis
        angle=-rotation_angle
    )
    corner_pos = np.array([-limandeBracketSideLength/4, limandeHalfTriangleHeight/2, 0])
    cornerCut_pos = np.array([limandeHipotenuse/2, limandeHalfTriangleHeight/2, 0])
    limandeHalfTriangle = g4.solid.Subtraction(
        name="limandeHalfTriangle" + suffix,
        obj1=limandeHalfTriangleBox,
        obj2=limandeHalfTriangleCut,
        tra2=[[0, 0, -rotation_angle], list(corner_pos + rotation_matrix @ cornerCut_pos)],
        registry=reg
    )

    limandeBase0 = g4.solid.Union(
        name="limandeBase0" + suffix,
        obj1=limandeBracketSide,
        obj2=limandeHalfTriangle,
        tra2=[[0, 0, 0], [limandeBracketSideLength/4, limandeBracketSideWidth/2 + limandeHalfTriangleHeight/2, 0]],
        registry=reg
    )
    limandeBase = g4.solid.Union(
        name="limandeBase" + suffix,
        obj1=limandeBase0,
        obj2=limandeHalfTriangle,
        tra2=[[0, np.pi, 0], [-limandeBracketSideLength/4, +limandeBracketSideWidth/2 + limandeHalfTriangleHeight/2, 0]],
        registry=reg
    )

    limandeFold = g4.solid.Box(
        name="limandeFold" + suffix,
        pX=limandeHipotenuse,
        pY=thickness,
        pZ=foldDistance,
        lunit="mm",
        registry=reg
    )

    triangle_hipotenuseA_pos = np.array([-limandeBracketSideLength/4, limandeBracketSideWidth/2 + limandeHalfTriangleHeight/2, side_z_dir*(thickness/2 + foldDistance/2)])
    triangle_hipotenuseB_pos = np.array([limandeBracketSideLength/4, limandeBracketSideWidth/2 + limandeHalfTriangleHeight/2, side_z_dir*(thickness/2 + foldDistance/2)])
    fold_thickness_pos = np.array([0, -thickness/2-thickness_below_in_mm, 0])
    rotation_matrix_A = tf.axisangle2matrix(
        axis=[0, 0, 1],  # rotation around Z-axis
        angle=+rotation_angle
    )
    rotation_matrix_B = tf.axisangle2matrix(
        axis=[0, 0, 1],  # rotation around Z-axis by pi
        angle=-rotation_angle
    )
    limandeBaseAndFoldA = g4.solid.Union(
        name="limandeBaseAndFoldA" + suffix,
        obj1=limandeBase,
        obj2=limandeFold,
        tra2=[[0, 0, rotation_angle], list(triangle_hipotenuseA_pos + rotation_matrix_A @ fold_thickness_pos)],
        registry=reg
    )
    # Mirrored version for the other side
    limandeBaseAndFoldB = g4.solid.Union(
        name="limandeBaseAndFoldB" + suffix,
        obj1=limandeBase,
        obj2=limandeFold,
        tra2=[[0, 0, -rotation_angle], list(triangle_hipotenuseB_pos + rotation_matrix_B @ fold_thickness_pos)],
        registry=reg
    )

    limandeTrapezoidBox = g4.solid.Box(
        name="limandeTrapezoidBox" + suffix,
        pX=limandeHipotenuse,
        pY=limandeTrapezoidLength,
        pZ=thickness,
        lunit="mm",
        registry=reg
    )

    limandeTrapezoidCutHipotenuse = np.sqrt((limandeHipotenuse-limandeWidth)**2 + (limandeTrapezoidLength)**2)  # sqrt(2) * height
    limandeTrapezoidCut = g4.solid.Box(
        name="limandeTrapezoidCut" + suffix,
        pX=limandeHipotenuse, # whatever but it needs to be big enough to do the cut
        pY=limandeTrapezoidCutHipotenuse,
        pZ=thickness + 0.1,  # to ensure cut
        lunit="mm",
        registry=reg
    )
    rotation_angle_2 = np.arccos(limandeTrapezoidLength/limandeTrapezoidCutHipotenuse)
    rotation_matrix_2 = tf.axisangle2matrix(
        axis=[0, 0, 1],  # rotation around Z-axis
        angle=rotation_angle_2
    )
    corner_pos = np.array([-limandeHipotenuse/2, +limandeTrapezoidLength/2-thickness-thickness_below_in_mm*2, 0])
    cornerCut_pos = np.array([-limandeHipotenuse/2, -limandeTrapezoidCutHipotenuse/2, 0])

    limandeTrapezoid = g4.solid.Subtraction(
        name="limandeTrapezoid" + suffix,
        obj1=limandeTrapezoidBox,
        obj2=limandeTrapezoidCut,
        tra2=[[0, 0, rotation_angle_2], list(corner_pos + rotation_matrix_2 @ cornerCut_pos)],
        registry=reg
    )

    triangle_hipotenuseA_pos = np.array([-limandeBracketSideLength/4, limandeBracketSideWidth/2 + limandeHalfTriangleHeight/2, side_z_dir*(thickness + foldDistance)])
    triangle_hipotenuseB_pos = np.array([+limandeBracketSideLength/4, limandeBracketSideWidth/2 + limandeHalfTriangleHeight/2, side_z_dir*(thickness + foldDistance)])
    trapezoid_long_side_pos = -np.array([0, limandeTrapezoidLength/2, 0])
    rotation_matrixA = tf.axisangle2matrix(
        axis=[0, 0, 1],  # rotation around Z-axis
        angle=+rotation_angle
    )
    limandeBaseFoldTrapezoidA = g4.solid.Union(
        name="limandeBaseFoldTrapezoidA" + suffix,
        obj1=limandeBaseAndFoldA,
        obj2=limandeTrapezoid,
        tra2=[[0, 0, rotation_angle], list(triangle_hipotenuseA_pos + rotation_matrixA @ trapezoid_long_side_pos)],
        registry=reg
    )

    rotation_matrixB = tf.tbxyz2matrix(
        angles=[0, np.pi, -rotation_angle],  # rotation around Z-axis by pi
    )
    limandeBaseFoldTrapezoidB = g4.solid.Union(
        name="limandeBaseFoldTrapezoidB" + suffix,
        obj1=limandeBaseAndFoldB,
        obj2=limandeTrapezoid,
        tra2=[[0, np.pi, -rotation_angle], list(triangle_hipotenuseB_pos + rotation_matrixB @ trapezoid_long_side_pos)],
        registry=reg
    )

    limandeStraight = g4.solid.Box(
        name="limandeStraight" + suffix,
        pX=limandeWidth,
        pY=thickness,
        pZ=straightLength,
        lunit="mm",
        registry=reg
    )

    trapezoidA_short_side_pos = np.array([limandeHipotenuse/2-limandeWidth/2, -limandeTrapezoidLength + thickness/2 + thickness_below_in_mm, side_z_dir*(straightLength/2 + thickness/2)])
    trapezoidB_short_side_pos = np.array([-(limandeHipotenuse/2-limandeWidth/2), -limandeTrapezoidLength + thickness/2 + thickness_below_in_mm, side_z_dir*(straightLength/2 + thickness/2)])
    limandeA = g4.solid.Union(
        name=name + "A",
        obj1=limandeBaseFoldTrapezoidA,
        obj2=limandeStraight,
        tra2=[[0, 0, rotation_angle], list(triangle_hipotenuseA_pos + rotation_matrixA @ trapezoidA_short_side_pos)],
        registry=reg
    )
    rotation_matrixB = tf.tbxyz2matrix(
        angles=[0, 0, -rotation_angle],  # rotation around Z-axis by pi
    )
    limandeB = g4.solid.Union(
        name=name + "B",
        obj1=limandeBaseFoldTrapezoidB,
        obj2=limandeStraight,
        tra2=[[0, 0, -rotation_angle], list(triangle_hipotenuseB_pos + rotation_matrixB @ trapezoidB_short_side_pos)],
        registry=reg
    )

    return reg

def generate_micromegas_assembly(name="micromegas_assembly", registry=None, is_right_side=True, simple_geometry=False):
    """
    Generates the micromegas assembly with all its components.
    param name: Name of the assembly volume.
    param registry: Registry to use for the Geant4 objects. If None, a new registry is created.
    param is_right_side: If True, the assembly is for the right side, otherwise for the left side. The sides are mirrored.
    Returns the assembly volume.
    """

    # Registry
    if registry is None:
        reg = g4.Registry()
    else:
        reg = registry

    # Materials
    # Use this for the pyg4ometry coloured material visualisation
    """
    copper = g4.MaterialPredefined("G4_Cu")
    teflon = g4.MaterialPredefined("G4_TEFLON")
    kapton = g4.MaterialPredefined("G4_KAPTON")
    """
    # Use this to generate gdmls with NIST materials definitions
    copper = g4.nist_material_2geant4Material("G4_Cu")
    teflon = g4.nist_material_2geant4Material("G4_TEFLON")
    kapton = g4.nist_material_2geant4Material("G4_KAPTON")

    # Make different side by z->-z transformation.
    # We use rotation to easily mirror the volumes which are symmetric y->-y.
    side_rot = np.array([0, 0, 0])
    if not is_right_side:
        side_rot = np.array([np.pi, 0, 0])
    # The rest are done by applying z->-z transformation.
    side_z_dir = 1
    if is_right_side:
        side_z_dir = -1

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
        pX=mMBaseLength,
        pY=mMBaseLength,
        pZ=mMBaseThickness,
        lunit="mm",
        registry=reg
    )

    mMBaseCornersCut = g4.solid.Tubs(
        name="mMBaseCornersCut",
        pRMin=0,
        pRMax=mMBaseRadius,
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
        tra2=[[0, 0, 0], [0, mMBaseLength/2 - mMBaseBracketWidth/2 - mMBaseEndToBracketDistance, -(mMBaseThickness/2 + mMBaseBracketThickness/2)]],
        registry=reg
    )
    mMBaseSquare2 = g4.solid.Union(
        name="mMBaseSquare2",
        obj1=mMBaseSquare1,
        obj2=mMBaseBracket,
        tra2=[[0, 0, 0], [0, -(mMBaseLength/2 - mMBaseBracketWidth/2 - mMBaseEndToBracketDistance), -(mMBaseThickness/2 + mMBaseBracketThickness/2)]],
        registry=reg
    )
    mMBaseSquare3 = g4.solid.Union(
        name="mMBaseSquare3",
        obj1=mMBaseSquare2,
        obj2=mMBaseBracket,
        tra2=[[0, 0, 90*3.1416/180], [mMBaseLength/2 - mMBaseBracketWidth/2 - mMBaseEndToBracketDistance, 0, -(mMBaseThickness/2 + mMBaseBracketThickness/2)]],
        registry=reg
    )
    mMBaseSquare = g4.solid.Union(
        name="mMBaseSquare",
        obj1=mMBaseSquare3,
        obj2=mMBaseBracket,
        tra2=[[0, 0, 90*3.1416/180], [-(mMBaseLength/2 - mMBaseBracketWidth/2 - mMBaseEndToBracketDistance), 0, -(mMBaseThickness/2 + mMBaseBracketThickness/2)]],
        registry=reg
    )

    mMBaseRecessSquare = g4.solid.Box(
        name="mMBaseRecessSquare",
        pX=mMBaseRecessLength,
        pY=mMBaseRecessLength,
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

    if not simple_geometry:
        ### Micromegas to Cap separator (and support)
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
            pZ=mMTriangularSupportThickness + 0.001,  # to ensure cut
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

        capSupportBase0 = g4.solid.Box(
            name="capSupportBase0",
            pX=capSupportBaseLength,
            pY=capSupportBaseHeight,
            pZ=capSupportBaseThickness,
            lunit="mm",
            registry=reg
        )
        capSupportBaseCut = g4.solid.Box(
            name="capSupportBaseCut",
            pX=capSupportBaseCutLength,
            pY=capSupportBaseCutHeight,
            pZ=capSupportBaseThickness,
            lunit="mm",
            registry=reg
        )

        capSupportBase = g4.solid.Subtraction(
            name="capSupportBase",
            obj1=capSupportBase0,
            obj2=capSupportBaseCut,
            tra2=[[0, 0, 0], [0, capSupportBaseHeight/2 - capSupportBaseCutHeight/2, 0]],
            registry=reg
        )

        capSupportColumnA = g4.solid.Box(
            name="capSupportColumnA",
            pX=capSupportColumnLengthA,
            pY=capSupportColumnThicknessA,
            pZ=capSupportColumnHeightA,
            lunit="mm",
            registry=reg
        )
        capSupportColumnB = g4.solid.Box(
            name="capSupportColumnB",
            pX=capSupportColumnLengthB,
            pY=capSupportColumnThicknessB,
            pZ=capSupportColumnHeightB,
            lunit="mm",
            registry=reg
        )
        capSupportColumnC = g4.solid.Tubs(
            name="capSupportColumnC",
            pRMin=0,
            pRMax=capSupportColumnThicknessC/2,
            pDz=capSupportColumnHeightC,
            pSPhi=0,
            pDPhi=360,
            aunit="deg",
            lunit="mm",
            registry=reg
        )

        capSupportBaseA = g4.solid.Union(
            name="capSupportBaseA",
            obj1=capSupportBase,
            obj2=capSupportColumnA,
            tra2=[[0, 0, 0], [0, -capSupportBaseHeight/2 + capSupportColumnThicknessA/2, capSupportBaseThickness/2 +capSupportColumnHeightA/2]],
            registry=reg
        )

        capSupportBaseACutted = g4.solid.Subtraction(
            name="capSupportBaseACutted",
            obj1=capSupportBaseA,
            obj2=capSupportColumnB,
            tra2=[[0, 0, 0], [0, -capSupportBaseHeight/2 + capSupportColumnThicknessB/2 -capSupportColumnProtrusionAtoB, -capSupportBaseThickness/2 + capSupportColumnHeightB/2]],
            registry=reg
        )
        capSupportColumnBC = g4.solid.Union(
            name="capSupportColumnBC",
            obj1=capSupportColumnB,
            obj2=capSupportColumnC,
            tra2=[[0, 0, 0], [0, 0, capSupportColumnHeightB/2 + capSupportColumnHeightC/2]],
            registry=reg
        )

        capSupportBaseColumn = g4.solid.Union(
            name="capSupportBaseColumn",
            obj1=capSupportBaseACutted,
            obj2=capSupportColumnBC,
            tra2=[[0, 0, 0], [0, -capSupportBaseHeight/2 + capSupportColumnThicknessB/2 - capSupportColumnProtrusionAtoB, capSupportBaseThickness/2 + capSupportColumnHeightB/2 + capSupportColumnBtoBase]],
            registry=reg
        )

        mMSupport = g4.solid.Union(
            name="mMSupport",
            obj1=capSupportBaseColumn,
            obj2=mMTriangularSupport,
            tra2=[[0, 0, -135*3.1416/180], [0, - capSupportColumnCtoTriangularSupport - capSupportBaseHeight/2 + capSupportColumnThicknessB/2-capSupportColumnProtrusionAtoB, capSupportBaseThickness/2 + capSupportColumnHeightB + capSupportColumnHeightC + capSupportColumnBtoBase + mMTriangularSupportThickness/2 ]],
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


    mMCopperFoil = g4.solid.Box(
        name="mMCopperFoil",
        pX=mMLength,
        pY=mMLength,
        pZ=mMCopperFoilThickness,
        lunit="mm",
        registry=reg
    )

    mMKaptonFoil = g4.solid.Box(
        name="mMKaptonFoil",
        pX=mMLength,
        pY=mMLength,
        pZ=mMKaptonFoilThickness,
        lunit="mm",
        registry=reg
    )

    mMKaptonFoil2 = g4.solid.Box(
        name="mMKaptonFoil2",
        pX=mMLength,
        pY=mMLength,
        pZ=mMKaptonFoil2Thickness,
        lunit="mm",
        registry=reg
    )

    # micromegas board will be a sandwich of kapton between copper foils of thickness mMCopperFoilThickness. On the active area we include the other copper foils
    generate_micromegas_board(name="mMBoardCopper", suffix="Copper", thickness_in_mm=mMBoardThickness, registry=reg)
    generate_micromegas_board(name="mMBoardKapton", suffix="Kapton", thickness_in_mm=mMBoardThickness - mMCopperFoilThickness*2, thickness_below_in_mm=mMCopperFoilThickness, registry=reg)
    mMBoardCopper = utils.get_solid_by_name("mMBoardCopper", reg)
    mMBoardKapton = utils.get_solid_by_name("mMBoardKapton", reg)

    if not simple_geometry:
        generate_limandes(name="limande", suffix="Copper", thickness_in_mm=limandeThickness, thickness_below_in_mm=0, is_right_side=is_right_side, registry=reg)
        generate_limandes(name="limandeInner", suffix="Kapton", thickness_in_mm=limandeThickness - limandeCopperThickness*2, thickness_below_in_mm=limandeCopperThickness, is_right_side=is_right_side, registry=reg)
        limandeA = utils.get_solid_by_name("limandeA", reg)
        limandeB = utils.get_solid_by_name("limandeB", reg)
        limandeInnerA = utils.get_solid_by_name("limandeInnerA", reg)
        limandeInnerB = utils.get_solid_by_name("limandeInnerB", reg)


    ### JOIN THE SOLIDS INTO THE ASSEMBLY
    micromegas_assembly = g4.AssemblyVolume(
        name=name,
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
    if not simple_geometry:
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

    mMBoardCopper_LV = g4.LogicalVolume(
        solid=mMBoardCopper,
        material=copper,
        name="mMBoardCopper_LV",
        registry=reg
    )
    mMBoardKapton_LV = g4.LogicalVolume(
        solid=mMBoardKapton,
        material=kapton,
        name="mMBoardKapton_LV",
        registry=reg
    )

    mMCopperFoil_LV = g4.LogicalVolume(
        solid=mMCopperFoil,
        material=copper,
        name="mMCopperFoil_LV",
        registry=reg
    )
    mMKaptonFoil_LV = g4.LogicalVolume(
        solid=mMKaptonFoil,
        material=kapton,
        name="mMKaptonFoil_LV",
        registry=reg
    )
    mMKaptonFoil2_LV = g4.LogicalVolume(
        solid=mMKaptonFoil2,
        material=kapton,
        name="mMKaptonFoil2_LV",
        registry=reg
    )
    
    if not simple_geometry:
        limandeA_LV = g4.LogicalVolume(
            solid=limandeA,
            material=copper,
            name="limandeA_LV",
            registry=reg
        )
        limandeB_LV = g4.LogicalVolume(
            solid=limandeB,
            material=copper,
            name="limandeB_LV",
            registry=reg
        )
        
        limandeInnerA_LV = g4.LogicalVolume(
            solid=limandeInnerA,
            material=kapton,
            name="limandeInnerA_LV",
            registry=reg
        )
        limandeInnerB_LV = g4.LogicalVolume(
            solid=limandeInnerB,
            material=kapton,
            name="limandeInnerB_LV",
            registry=reg
        )


    # Create the physical volumes and add them to the assembly
    
    mMBase_PV = g4.PhysicalVolume(
        rotation=side_rot.tolist(),
        position=[0, 0, 0],
        name="mMBase",
        logicalVolume=mMBase_LV,
        motherVolume=micromegas_assembly,
        registry=reg
    )

    teflonspacerpad_pos_xory = mMBaseLength/2 - mMBaseBracketWidth/2 - mMBaseEndToBracketDistance
    teflonspacerpad_pos_z = mMBaseThickness/2 + mMBaseBracketThickness + mMTeflonSpacerPadThickness/2
    mMTeflonSpacerPad1_PV = g4.PhysicalVolume(
        rotation=[0, 0, 0],
        position=[0, teflonspacerpad_pos_xory, side_z_dir*teflonspacerpad_pos_z],
        name="mMTeflonSpacerPad1",
        logicalVolume=mMTeflonSpacerPad_LV,
        motherVolume=micromegas_assembly,
        registry=reg
    )
    mMTeflonSpacerPad2_PV = g4.PhysicalVolume(
        rotation=[0, 0, 0],
        position=[0, -teflonspacerpad_pos_xory, side_z_dir*teflonspacerpad_pos_z],
        name="mMTeflonSpacerPad2",
        logicalVolume=mMTeflonSpacerPad_LV,
        motherVolume=micromegas_assembly,
        registry=reg
    )
    mMTeflonSpacerPad3_PV = g4.PhysicalVolume(
        rotation=[0, 0, 90*np.pi/180],
        position=[teflonspacerpad_pos_xory, 0, side_z_dir*teflonspacerpad_pos_z],
        name="mMTeflonSpacerPad3",
        logicalVolume=mMTeflonSpacerPad_LV,
        motherVolume=micromegas_assembly,
        registry=reg
    )
    mMTeflonSpacerPad4_PV = g4.PhysicalVolume(
        rotation=[0, 0, 90*np.pi/180],
        position=[-teflonspacerpad_pos_xory, 0, side_z_dir*teflonspacerpad_pos_z],
        name="mMTeflonSpacerPad4",
        logicalVolume=mMTeflonSpacerPad_LV,
        motherVolume=micromegas_assembly,
        registry=reg
    )

    closingbracket_pos_xory = teflonspacerpad_pos_xory
    closingbracket_pos_z = teflonspacerpad_pos_z + mMTeflonSpacerPadThickness/2 + mMBaseBracketThickness/2 + mMBoardThickness + limandeThickness

    mMBaseClosingBracket1_PV = g4.PhysicalVolume(
        rotation=[0, 0, 0],
        position=[0, closingbracket_pos_xory, side_z_dir*closingbracket_pos_z],
        name="mMBaseClosingBracket1",
        logicalVolume=mMBaseClosingBracket_LV,
        motherVolume=micromegas_assembly,
        registry=reg
    )
    mMBaseClosingBracket2_PV = g4.PhysicalVolume(
        rotation=[0, 0, 0],
        position=[0, -closingbracket_pos_xory, side_z_dir*closingbracket_pos_z],
        name="mMBaseClosingBracket2",
        logicalVolume=mMBaseClosingBracket_LV,
        motherVolume=micromegas_assembly,
        registry=reg
    )
    mMBaseClosingBracket_3_PV = g4.PhysicalVolume(
        rotation=[0, 0, 90*np.pi/180],
        position=[closingbracket_pos_xory, 0, side_z_dir*closingbracket_pos_z],
        name="mMBaseClosingBracket3",
        logicalVolume=mMBaseClosingBracket_LV,
        motherVolume=micromegas_assembly,
        registry=reg
    )
    mMBaseClosingBracket_4_PV = g4.PhysicalVolume(
        rotation=[0, 0, 90*np.pi/180],
        position=[-closingbracket_pos_xory, 0, side_z_dir*closingbracket_pos_z],
        name="mMBaseClosingBracket4",
        logicalVolume=mMBaseClosingBracket_LV,
        motherVolume=micromegas_assembly,
        registry=reg
    )
    ### Rollers. In the CAD design there are 4 (one on each side), but in the real life there are only 2
    mMBaseTeflonRoller1_PV = g4.PhysicalVolume(
        rotation=(np.array([90*3.1416/180, 0, 0]) + side_rot).tolist(),
        position=[-mMBaseLength/2, 0, side_z_dir*(mMBaseThickness/2 + rollerCutShift)],
        name="mMBaseTeflonRoller1",
        logicalVolume=roller_LV,
        motherVolume=micromegas_assembly,
        registry=reg
    )
    mMBaseTeflonRoller2_PV = g4.PhysicalVolume(
        rotation=(np.array([-90*3.1416/180, 0, np.pi]) + side_rot).tolist(),
        position=[mMBaseLength/2, 0, side_z_dir*(mMBaseThickness/2 + rollerCutShift)],
        name="mMBaseTeflonRoller2",
        logicalVolume=roller_LV,
        motherVolume=micromegas_assembly,
        registry=reg
    )

    if not simple_geometry:
        ### Micromegas support
        mMSupportDistanceToCenter_XorY = 220.79/2 #mm
        mMSupport_pos_z = mMBaseThickness/2 + capSupportBaseThickness/2 + capSupportColumnHeightB + capSupportColumnHeightC + capSupportColumnBtoBase + mMTriangularSupportThickness
        mMSupport1_PV = g4.PhysicalVolume(
            rotation=(np.array([0, 0, side_z_dir*45*np.pi/180]) + side_rot).tolist(),  # 45 degrees rotation
            position=[-side_z_dir*mMSupportDistanceToCenter_XorY, side_z_dir*mMSupportDistanceToCenter_XorY, side_z_dir*mMSupport_pos_z],
            name="mMSupport1",
            logicalVolume=mMSupport_LV,
            motherVolume=micromegas_assembly,
            registry=reg
        )
        mMSupport2_PV = g4.PhysicalVolume(
            rotation=(np.array([0, 0, -side_z_dir*135*np.pi/180]) + side_rot).tolist(),  # 45 degrees rotation
            position=[side_z_dir*mMSupportDistanceToCenter_XorY, -side_z_dir*mMSupportDistanceToCenter_XorY, side_z_dir*mMSupport_pos_z],
            name="mMSupport2",
            logicalVolume=mMSupport_LV,
            motherVolume=micromegas_assembly,
            registry=reg
        )
        #print("height of the support: ", mMSupport_pos_z-mMBaseThickness/2+capSupportBaseThickness/2, " mm")

    mMCopperFoilLayer2_PV = g4.PhysicalVolume(
        rotation=[0, 0, 0],
        position=[0, 0, mMBoardThickness/2 - mMKaptonFoilThickness - mMCopperFoilThickness -mMKaptonFoilThickness - mMCopperFoilThickness/2],
        name="mMCopperFoilLayer2",
        logicalVolume=mMCopperFoil_LV,
        motherVolume=mMBoardKapton_LV,
        registry=reg
    )
    mMCopperFoilLayer3_PV = g4.PhysicalVolume(
        rotation=[0, 0, 0],
        position=[0, 0, mMBoardThickness/2 - mMKaptonFoilThickness - mMCopperFoilThickness*2 - mMKaptonFoilThickness*2 - mMCopperFoilThickness/2],
        name="mMCopperFoilLayer3",
        logicalVolume=mMCopperFoil_LV,
        motherVolume=mMBoardKapton_LV,
        registry=reg
    )

    mMBoardKapton_PV = g4.PhysicalVolume(
        rotation=[0, 0, 0],
        position=[0, 0, 0],
        name="mMBoardKapton",
        logicalVolume=mMBoardKapton_LV,
        motherVolume=mMBoardCopper_LV,
        registry=reg
    )

    mMBoardCopper_PV = g4.PhysicalVolume(
        rotation=side_rot.tolist(),
        position=[0, 0, -side_z_dir*(mMBaseThickness/2 + mMBoardThickness/2)],
        name="mMBoardCopper",
        logicalVolume=mMBoardCopper_LV,
        motherVolume=micromegas_assembly,
        registry=reg
    )

    if not simple_geometry:
        limandeInnerA_PV = g4.PhysicalVolume(
            rotation=[0, 0, 0],
            position=[0, 0, 0],
            name="limandeInnerA",
            logicalVolume=limandeInnerA_LV,
            motherVolume=limandeA_LV,
            registry=reg
        )
        limandeInnerB_PV = g4.PhysicalVolume(
            rotation=[0, 0, 0],
            position=[0, 0, 0],
            name="limandeInnerB",
            logicalVolume=limandeInnerB_LV,
            motherVolume=limandeB_LV,
            registry=reg
        )
        
        limande_z_pos = side_z_dir*(mMBaseThickness/2 + mMBaseBracketThickness + mMTeflonSpacerPadThickness + mMBoardThickness + limandeThickness/2)
        limande_x_or_y = mMBaseLength/2 - mMBaseEndToBracketDistance - limandeBracketSideWidth/2
        limande1_PV = g4.PhysicalVolume(
            rotation=[0, 0, 0],
            position=[0, -limande_x_or_y, limande_z_pos],
            name="limande1",
            logicalVolume=limandeA_LV,
            motherVolume=micromegas_assembly,
            registry=reg
        )
        limande2_PV = g4.PhysicalVolume(
            rotation=[0, 0, np.pi],
            position=[0, +limande_x_or_y, limande_z_pos],
            name="limande2",
            logicalVolume=limandeA_LV,
            motherVolume=micromegas_assembly,
            registry=reg
        )
        limande3_PV = g4.PhysicalVolume(
            rotation=[0, 0, -np.pi/2],
            position=[+limande_x_or_y, 0, limande_z_pos],
            name="limande3",
            logicalVolume=limandeB_LV,
            motherVolume=micromegas_assembly,
            registry=reg
        )
        limande4_PV = g4.PhysicalVolume(
            rotation=[0, 0, +np.pi/2],
            position=[-limande_x_or_y, 0, limande_z_pos],
            name="limande4",
            logicalVolume=limandeB_LV,
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
    
    reg = generate_micromegas_assembly(is_right_side=False)
    micromegas_assembly = utils.get_logical_volume_by_name("micromegas_assembly", reg)

    if args.gdml:
        galactic = g4.nist_material_2geant4Material("G4_Galactic")
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
