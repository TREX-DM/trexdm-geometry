from pyg4ometry import geant4 as g4

def substract_daughters_from_mother(mother, registry=None):
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
    mother_material = None
    if isinstance(mother, g4.PhysicalVolume):
        daughters = mother.logicalVolume.daughterVolumes
        mother_solid = mother.logicalVolume.solid
        mother_material = mother.logicalVolume.material
    elif isinstance(mother, g4.LogicalVolume) or isinstance(mother, g4.AssemblyVolume):
        daughters = mother.daughterVolumes
        mother_solid = mother.solid
        mother_material = mother.material
    else:
        raise TypeError("mother must be a PhysicalVolume, LogicalVolume or AssemblyVolume")

    solid_name = mother_solid.name + "_minus"
    for daughter in daughters:
        daughter_logical = daughter.logicalVolume
        daughter_solid = daughter_logical.solid
        daughter_rotation = daughter.rotation
        daughter_position = daughter.position
        solid_name = f"{solid_name}_{daughter_solid.name}"
        mother_solid = g4.solid.Subtraction(
            name=solid_name,
            obj1=mother_solid,
            obj2=daughter_solid,
            tra2=[daughter_rotation, daughter_position],
            registry=reg
        )
    
    g4.LogicalVolume(mother_solid, mother_material, mother.name + "_subtracted", reg)
    
    return reg

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
