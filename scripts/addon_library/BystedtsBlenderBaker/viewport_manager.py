import bpy

def get_local_view(context):
    
    is_in_local_view = False
    area = context.area
    
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                if not space.local_view == None:
                    is_in_local_view = True

    return is_in_local_view

classes = (

)