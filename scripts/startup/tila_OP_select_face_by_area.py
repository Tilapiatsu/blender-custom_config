import bpy
import bmesh

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
    def invoke(self, context, event):
        self.obj = context.edit_object
        if self.obj is None or self.obj.type != 'MESH':
            self.report({'ERROR'}, "Active object is not a mesh")
            return {'CANCELLED'}
        
        return self.execute(context)
        
    def execute(self, context):
        mesh = self.obj.data
        
        # Create a bmesh from the mesh
        bm = bmesh.from_edit_mesh(mesh)
        
        # Loop through the faces and select those with area between the thresholds
        for face in bm.faces:
            area = face.calc_area()
            if self.min_threshold <= area <= self.max_threshold:
                face.select = True
        
        # Update the mesh with the selected faces
        bmesh.update_edit_mesh(mesh)        
        return {'FINISHED'}
    
classes = (
	TILA_SelectFaceByAreaOperator,
)


register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()