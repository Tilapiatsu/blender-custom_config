import bpy
import bmesh

bl_info = {
    "name": "Tila : Select Face by Area",
    "author": "Tilapiatsu",
    "version": (1, 0, 0, 0),
    "blender": (2, 80, 0),
    "location": "View3D",
    "category": "Mesh",
}

class TILA_SelectFaceByAreaOperator(bpy.types.Operator):
    """Select all faces with area between min and max thresholds"""
    bl_idname = "mesh.select_face_by_area"
    bl_label = "Select Face by Area"
    bl_options = {'REGISTER', 'UNDO'}
    
    min_threshold: bpy.props.FloatProperty(
        name="Minimum Threshold",
        default=0.0,
        min=0.0,
        description="Select Faces with area above this Threshold"
    )
    
    max_threshold: bpy.props.FloatProperty(
        name="Maximum Threshold",
        default=1.0,
        min=0.0,
        description="Select Faces with area below this Threshold"
    )

    selection_mode: bpy.props.EnumProperty(items=[("ADD", "Add", ""), ("REMOVE", "Remove", ""), ("REPLACE", "Replace", ""), ("INTERSECT", "Intersect", "")])
        
    def execute(self, context):
        obj = context.edit_object
        if obj is None or obj.type != 'MESH':
            self.report({'ERROR'}, "Active object is not a mesh")
            return {'CANCELLED'}
        
        mesh = obj.data
        
        # Create a bmesh from the mesh
        bm = bmesh.from_edit_mesh(mesh)
        
        # Loop through the faces and select those with area between the thresholds
        for face in bm.faces:
            area = face.calc_area()
            if self.selection_mode == 'ADD':
                if self.min_threshold <= area <= self.max_threshold:
                    face.select = True
            elif self.selection_mode == 'REMOVE':
                if self.min_threshold <= area <= self.max_threshold:
                    face.select  = False
            elif self.selection_mode == 'REPLACE':
                if self.min_threshold <= area <= self.max_threshold:
                    face.select = True
                else:
                    face.select = False
            elif self.selection_mode == 'INTERSECT':
                if face.select == True:
                    if self.min_threshold <= area <= self.max_threshold:
                        pass
                    else:
                        face.select = False
        
        # Update the mesh with the selected faces
        bmesh.update_edit_mesh(mesh)   
        bm.free()  
        return {'FINISHED'}
    
classes = (
	TILA_SelectFaceByAreaOperator,
)

def menu_func(self, context):
    self.layout.separator()
    self.layout.operator(TILA_SelectFaceByAreaOperator.bl_idname, text="Select Face by Area")

# register, unregister = bpy.utils.register_classes_factory(classes)

def register():
	for cl in classes:
		bpy.utils.register_class(cl)
	bpy.types.VIEW3D_MT_select_edit_mesh.append(menu_func)  # Adds the new operator to an existing menu.
        
def unregister():
	for cl in classes:
		bpy.utils.unregister_class(cl)
	bpy.types.VIEW3D_MT_select_edit_mesh.remove(menu_func)  # Adds the new operator to an existing menu.

if __name__ == "__main__":
    register()