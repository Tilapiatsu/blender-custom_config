import bpy

def operator_exists(operator):
    ''''
    Returns True if operator exists
    operator should be like:
    object.voxel_remesh
    '''
    operator = "bpy.ops." + operator + ".get_rna_type()"
    exists = False
    try:
        result = exec(operator)
        exists = True
    except:
        pass

    return exists