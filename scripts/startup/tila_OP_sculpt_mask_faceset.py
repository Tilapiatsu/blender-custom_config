import bpy

bl_info = {
	"name": "Tila : Sculpt Mask FaceSet",
	"author": "Tilapiatsu",
	"version": (1, 0, 0, 0),
	"blender": (2, 80, 0),
	"location": "View3D",
	"category": "Sculpt",
}

class TILA_SculptMaskFaceSet(bpy.types.Operator):
    bl_idname = "sculpt.tila_mask_faceset"
    bl_label = "Mask/Unmask Faceset under the cursor"

    mode : bpy.props.EnumProperty(name="mode", items=[("MASK", "Mask", ""), ("TOGGLE", "Toggle", "")])

    def invoke(self, context, event):
        if self.mode == 'MASK':
            bpy.ops.sculpt.reveal_all()
            bpy.ops.paint.mask_flood_fill(mode='VALUE', value=0.0)
            bpy.ops.sculpt.face_set_change_visibility(mode='TOGGLE')
            bpy.ops.paint.mask_flood_fill(mode='INVERT')
            bpy.ops.sculpt.reveal_all()
            bpy.ops.paint.mask_flood_fill(mode='INVERT')
        elif self.mode == 'TOGGLE':
            bpy.ops.sculpt.reveal_all()
            bpy.ops.paint.mask_flood_fill(mode='INVERT')
            bpy.ops.sculpt.face_set_change_visibility(mode='TOGGLE')
            bpy.ops.paint.mask_flood_fill(mode='INVERT')
            bpy.ops.sculpt.reveal_all()
            bpy.ops.paint.mask_flood_fill(mode='INVERT')
            bpy.ops.sculpt.mask_filter(filter_type='GROW', auto_iteration_count=True)
            bpy.ops.sculpt.mask_filter(filter_type='SHRINK', auto_iteration_count=True)
        return{'FINISHED'}


classes = (
    TILA_SculptMaskFaceSet,
)


register, unregister = bpy.utils.register_classes_factory(classes)


if __name__ == "__main__":
    register()