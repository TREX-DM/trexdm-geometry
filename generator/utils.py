from pyg4ometry import geant4 as g4
import pyg4ometry.transformation as tf
from pyg4ometry.exceptions import IdenticalNameError
import numpy as np

def substract_daughters_from_mother(mother, solid_mother=None, rotation_mother=[0, 0, 0], position_mother=[0, 0, 0], base_name="", registry=None):
    """
    Subtracts the daughter volumes from the mother volume.
    This is a utility function to create a subtraction solid.
    """
    if registry is None:
        reg = g4.Registry()
    else:
        reg = registry

    daughters = []
    mother_solid = None
    #mother_material = None
    if isinstance(mother, g4.PhysicalVolume):
        daughters = mother.logicalVolume.daughterVolumes
        mother_solid = mother.logicalVolume.solid
        #mother_material = mother.logicalVolume.material
    elif isinstance(mother, g4.LogicalVolume):
        daughters = mother.daughterVolumes
        mother_solid = mother.solid
        #mother_material = mother.material
    elif isinstance(mother, g4.AssemblyVolume):
        daughters = mother.daughterVolumes
        if solid_mother is None:
            raise TypeError("solid_mother must be provided for AssemblyVolume")
        mother_solid = solid_mother
        #mother_material = mother.material
    else:
        raise TypeError("mother must be a PhysicalVolume, LogicalVolume or AssemblyVolume")

    if not base_name:
        solid_name_base = mother_solid.name
    else:
        solid_name_base = base_name

    for i, daughter in enumerate(daughters):
        daughter_logical = daughter.logicalVolume
        solid_name = f"{solid_name_base}-{i}"
        if isinstance(daughter_logical, g4.AssemblyVolume):
            assembly_pos = daughter.position.eval()
            assembly_rot = daughter.rotation.eval()
            rot = tf.matrix2tbxyz( tf.tbxyz2matrix(assembly_rot) @ tf.tbxyz2matrix(rotation_mother) )
            pos = np.array(position_mother) + tf.tbxyz2matrix(rotation_mother) @ assembly_pos
            mother_solid = substract_daughters_from_mother(
                                            daughter_logical,
                                            solid_mother=mother_solid,
                                            rotation_mother=rot, # assembly_rot, ??
                                            position_mother=pos, #assembly_pos, ??
                                            base_name=solid_name,
                                            registry=reg
                                        )
            continue
        daughter_solid = daughter_logical.solid
        daughter_rotation = np.array(daughter.rotation.eval())
        daughter_position = np.array(daughter.position.eval())
        final_rot = tf.matrix2tbxyz( tf.tbxyz2matrix(daughter_rotation) @ tf.tbxyz2matrix(rotation_mother) )
        final_pos = np.array(position_mother) + tf.tbxyz2matrix(rotation_mother) @ daughter_position
        try:
            print(f"Subtracting {daughter_logical.name} from {mother_solid.name} to create {solid_name}: rot={final_rot}, pos={final_pos}")
            mother_solid = g4.solid.Subtraction(
                name=solid_name,
                obj1=mother_solid,
                obj2=daughter_solid,
                tra2=[final_rot, final_pos.tolist()],
                registry=reg
            )
        except IdenticalNameError:
            print(f"Solid with name {solid_name} already exists, retrieving it.")
            mother_solid = get_solid_by_name(solid_name, reg)
    
    #subtracted_solid = g4.LogicalVolume(mother_solid, mother_material, solid_name_base + "_subtracted", reg)
    
    return mother_solid

def get_solid_by_name(name, registry):
    """
    Returns the solid with the given name from the registry.
    If the solid is not found, it raises a KeyError.
    """
    solids = registry.findSolidByName(name)
    if not solids:
        raise KeyError(f"Solid with name '{name}' not found in registry.")

    if len(solids) > 1:
        for solid in solids:
            if solid.name == name:
                return solid
        raise KeyError(f"Solid with name '{name}' not found in registry, similar names found: {', '.join(s.name for s in solids)}")
    
    return solids[0]

def get_logical_volume_by_name(name, registry):
    """
    Returns the logical volume with the given name from the registry.
    If the logical volume is not found, it raises a KeyError.
    """
    logical_volumes = registry.findLogicalVolumeByName(name)
    if not logical_volumes:
        raise KeyError(f"Logical volume with name '{name}' not found in registry.")

    if len(logical_volumes) > 1:
        for lv in logical_volumes:
            if lv.name == name:
                return lv
        raise KeyError(f"Logical volume with name '{name}' not found in registry, similar names found: {', '.join(lv.name for lv in logical_volumes)}")
    
    return logical_volumes[0]

def get_physical_volume_by_name(name, registry):
    """
    Returns the physical volume with the given name from the registry.
    If the physical volume is not found, it raises a KeyError.
    """
    physical_volumes = registry.findPhysicalVolumeByName(name)
    if not physical_volumes:
        raise KeyError(f"Physical volume with name '{name}' not found in registry.")

    if len(physical_volumes) > 1:
        for pv in physical_volumes:
            if pv.name == name:
                return pv
        raise KeyError(f"Physical volume with name '{name}' not found in registry, similar names found: {', '.join(pv.name for pv in physical_volumes)}")
    
    return physical_volumes[0]

def get_position_of_physical_volume(name, registry):
    """
    Returns the position of the physical volume with the given name from the registry.
    If the physical volume is not found, it raises a KeyError.
    """
    physical_volume = get_physical_volume_by_name(name, registry)
    return physical_volume.position.eval()

def get_rotation_of_physical_volume(name, registry):
    """
    Returns the rotation of the physical volume with the given name from the registry.
    If the physical volume is not found, it raises a KeyError.
    """
    physical_volume = get_physical_volume_by_name(name, registry)
    return physical_volume.rotation.eval()

def get_material_by_name(name, registry):
    """
    Returns the material with the given name from the registry.
    If the material is not found, it raises a KeyError.
    """
    materials = registry.findMaterialByName(name)
    if not materials:
        raise KeyError(f"Material with name '{name}' not found in registry.")

    if len(materials) > 1:
        for mat in materials:
            if mat.name == name:
                return mat
        raise KeyError(f"Material with name '{name}' not found in registry, similar names found: {', '.join(mat.name for mat in materials)}")
    
    return materials[0]

def get_childless_volume(volume, base_name="", position=[0, 0, 0], rotation=[0, 0, 0], world_volume=None, is_world_volume=True, registry=None):
    reg = registry if registry is not None else g4.Registry()
    print(f"Getting childless volume for: {volume.name}, pos={position}, rot={rotation}, base_name={base_name}")
    mother_logical = volume
    mother_pos = np.array(position) if isinstance(position, (list, tuple)) else position
    mother_rot_matrix = tf.tbxyz2matrix(rotation)
    if volume.daughterVolumes and not is_world_volume and not isinstance(volume, g4.AssemblyVolume):
        print(f"Removing children from solid of volume: {volume}")
        subtracted_solid = substract_daughters_from_mother(volume,
                                                           #position_mother=position,
                                                           #rotation_mother=rotation,
                                                           registry=reg)
        #try:
        print(f"Creating LV: {base_name + volume.name + '_childless_LV'} with solid {subtracted_solid.name}")
        subtracted_logical = g4.LogicalVolume(
            name=base_name +volume.name + "_childless_LV",
            solid=subtracted_solid,
            material=volume.material,
            registry=reg
        )
        #except IdenticalNameError:
            #subtracted_logical = get_logical_volume_by_name(volume.name + "_childless_LV", reg)
        print(f"Creating PV at pos {mother_pos}, rot {tf.matrix2tbxyz(mother_rot_matrix)}")
        g4.PhysicalVolume(
            name=base_name + volume.name + "_childless_PV",
            logicalVolume=subtracted_logical,
            motherVolume=world_volume,
            position=mother_pos,
            rotation=tf.matrix2tbxyz(mother_rot_matrix), # rotation better to avoid converting to matrix and back to tbxyz
            registry=reg
        )
    elif is_world_volume:
        try:
            print(f"Adding world volume: {volume.name}")
            g4.LogicalVolume(
                name=base_name + volume.name,
                solid=volume.solid,
                material=volume.material,
                registry=reg
            )
        except IdenticalNameError:
            print(f"World volume {volume.name} already exists, skipping creation.")

    for physical in volume.daughterVolumes:
        pos = np.array(physical.position.eval())
        rot_matrix= tf.tbxyz2matrix(physical.rotation.eval())
        logical = physical.logicalVolume
        if not logical.daughterVolumes:
            print(f"Creating PV {base_name + physical.name} at pos {mother_pos + mother_rot_matrix @ pos},  rot  {tf.matrix2tbxyz(mother_rot_matrix @ rot_matrix)}")
            reg.transferLogicalVolume(logical)
            g4.PhysicalVolume(
                name=base_name + physical.name,
                logicalVolume=logical,
                motherVolume=world_volume,
                position=mother_pos + mother_rot_matrix @ pos,
                rotation=tf.matrix2tbxyz(rot_matrix @ mother_rot_matrix),
                registry=reg
            )
        else:
            get_childless_volume(logical,
                                base_name=base_name + physical.name + "/",
                                position=mother_pos + mother_rot_matrix @ pos,
                                rotation=tf.matrix2tbxyz(rot_matrix @ mother_rot_matrix),
                                world_volume=world_volume,
                                is_world_volume=False,
                                registry=reg
                                )

def transfer_childless_world(origin_registry):
    """
    Transfers the childless world volume from origin_registry to target_registry.
    This function is used to create a new registry without daughter volumes.
    """
    if not isinstance(origin_registry, g4.Registry):
        raise TypeError("Both origin_registry and target_registry must be instances of g4.Registry")
    world_volume = origin_registry.getWorldVolume()
    print(f"Transferring world volume: {world_volume.name}")
    if world_volume is None:
        raise ValueError("No world volume found in origin_registry")

    target_registry = g4.Registry()

    for name, solid in origin_registry.solidDict.items():
        #print(f"Transferring solid: {name}")
        target_registry.transferSolid(solid)
    for name, material in origin_registry.materialDict.items():
        #print(f"Transferring material: {name}")
        target_registry.transferMaterial(material)
    world_volume_target = g4.LogicalVolume(world_volume.solid, world_volume.material, "world", target_registry)
    get_childless_volume(world_volume, world_volume=world_volume_target, is_world_volume=True, registry=target_registry)
    
    for name, solid in origin_registry.solidDict.items():
        if name not in target_registry.solidDict.keys():
            print(f"Transferring missing solid: {name}")
            target_registry.transferSolid(solid)

    print(world_volume_target.name)
    target_registry.setWorld(world_volume_target.name)
    return target_registry
