
from bpy.props import IntProperty, BoolProperty, EnumProperty
from mathutils import Vector
import bgl
import bpy
bl_info = {
    "name": "Smart Edit Mode",
    "description": "Automatically switch to edit mode when selecting vertex, edge or polygon mode",
    "author": ("Tilapiatsu"),
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "",
    "warning": "",
    "doc_url": "",
    "category": "3D View"
}


class TILA_smart_editmode(bpy.types.Operator):
    bl_idname = "view3d.tila_smart_editmode"
    bl_label = "Smart Edit Mode"
    bl_options = {'REGISTER', 'UNDO'}

    mode = bpy.props.IntProperty(name='mode', default=0)
    use_extend = bpy.props.BoolProperty(name='use_extend', default=False)
    use_expand = bpy.props.BoolProperty(name='use_expand', default=False)
    get_border = bpy.props.BoolProperty(name='get_border', default=False)
    alt_mode = bpy.props.BoolProperty(name='alt_mode', default=False)

    mesh_mode = ['VERT', 'EDGE', 'FACE']
    gpencil_mode = ['POINT', 'STROKE', 'SEGMENT']
    uv_mode = ['VERTEX', 'EDGE', 'FACE', 'ISLAND']
    particle_mode = ['PATH', 'POINT', 'TIP']

    @classmethod
    def poll(cls, context):
        return context.space_data.type in ['VIEW_3D']

    def modal(self, context, event):
        pass

    def invoke(self, context, event):
        def switch_mesh_mode(self, current_mode):
            if self.mesh_mode[self.mode] == current_mode:
                bpy.ops.object.editmode_toggle()
            else:
                bpy.ops.mesh.select_mode(use_extend=self.use_extend, use_expand=self.use_expand, type=self.mesh_mode[self.mode])

        def switch_gpencil_mode(self, current_mode):
            if self.gpencil_mode[self.mode] == current_mode:
                bpy.ops.gpencil.editmode_toggle()
            else:
                bpy.context.scene.tool_settings.gpencil_selectmode_edit = self.gpencil_mode[self.mode]

        def switch_uv_mode(self, current_mode):
            if bpy.context.scene.tool_settings.use_uv_select_sync:
                switch_mesh_mode(self, self.mesh_mode[mesh_mode_link(self, current_mode)])
            else:
                bpy.context.scene.tool_settings.uv_select_mode = self.uv_mode[self.mode]
        
        def mesh_mode_link(self, mode):
            for m in self.mesh_mode:
                if mode in m:
                    return self.mesh_mode.index(m)
                else:
                    return 0

        def select_border(self, current_mode):
            # if self.mesh_mode[self.mode] != current_mode:
            if self.mesh_mode[self.mode] != 'FACE':
                bpy.ops.mesh.region_to_loop()
                switch_mesh_mode(self, current_mode)
            else:
                pass

        def switch_particle_mode(self):
                bpy.context.scene.tool_settings.particle_edit.select_mode = self.particle_mode[self.mode] 
                    

        if bpy.context.mode == 'OBJECT':
            if bpy.context.active_object is None:
                return {'CANCELLED'}
            if bpy.context.active_object.type == 'MESH':
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.select_mode(use_extend=self.use_extend, use_expand=self.use_expand, type=self.mesh_mode[self.mode])

            elif bpy.context.active_object.type == 'GPENCIL':
                if self.alt_mode:
                    bpy.ops.object.mode_set(mode='EDIT_GPENCIL')
                else:
                    bpy.ops.gpencil.editmode_toggle()
                    bpy.context.scene.tool_settings.gpencil_selectmode_edit = self.gpencil_mode[self.mode]
            
            else:
                bpy.ops.object.editmode_toggle()

        elif bpy.context.mode == 'EDIT_CURVE':
            if self.alt_mode:
                bpy.ops.object.mode_set(mode='OBJECT')
            else:
                pass
        
        elif bpy.context.mode == 'EDIT_MESH':
            if self.alt_mode:
                bpy.ops.object.mode_set(mode='OBJECT')
            else:
                method = None
                if bpy.context.space_data.type == 'IMAGE_EDITOR':
                    method = switch_uv_mode
                    if bpy.context.scene.tool_settings.uv_select_mode == 'VERTEX':
                        method(self, 'VERTEX')
                    elif bpy.context.scene.tool_settings.uv_select_mode == 'EDGE':
                        method(self, 'EDGE')
                    elif bpy.context.scene.tool_settings.uv_select_mode == 'FACE':
                        method(self, 'FACE')
                    elif bpy.context.scene.tool_settings.uv_select_mode == 'ISLAND':
                        method(self, 'ISLAND')
                else:
                    if self.get_border:
                        method = select_border
                        if bpy.context.scene.tool_settings.mesh_select_mode[0]:
                            method(self, 'VERT')
                        elif bpy.context.scene.tool_settings.mesh_select_mode[1]:
                            method(self, 'EDGE')
                        elif bpy.context.scene.tool_settings.mesh_select_mode[2]:
                            method(self, 'FACE')
                    else:
                        method = switch_mesh_mode
                        if bpy.context.scene.tool_settings.mesh_select_mode[0]:
                            method(self, 'VERT')
                        elif bpy.context.scene.tool_settings.mesh_select_mode[1]:
                            method(self, 'EDGE')
                        elif bpy.context.scene.tool_settings.mesh_select_mode[2]:
                            method(self, 'FACE')

        elif bpy.context.mode in ['EDIT_GPENCIL', 'PAINT_GPENCIL', 'SCULPT_GPENCIL', 'WEIGHT_GPENCIL']:
            if self.alt_mode:
                bpy.ops.object.mode_set(mode='OBJECT')
            else:
                switch_gpencil_mode(self, bpy.context.scene.tool_settings.gpencil_selectmode_edit)

        elif bpy.context.mode in ['PAINT_WEIGHT', 'PAINT_VERTEX']:
            if self.alt_mode:
                bpy.ops.object.mode_set(mode='OBJECT')
            else:
                if self.mode == 0 and not bpy.context.object.data.use_paint_mask_vertex:                   
                    bpy.context.object.data.use_paint_mask_vertex = True
                elif self.mode == 2 and not bpy.context.object.data.use_paint_mask:
                    bpy.context.object.data.use_paint_mask = True
                elif self.mode == 1:
                    pass
                else:
                    bpy.context.object.data.use_paint_mask_vertex = False
                    bpy.context.object.data.use_paint_mask = False
        
        elif bpy.context.mode in ['PARTICLE']:
            if self.alt_mode:
                bpy.ops.object.mode_set(mode='OBJECT')
            else:
                switch_particle_mode(self)

        else:
            bpy.ops.object.mode_set(mode='OBJECT')

        return {'FINISHED'}


classes = (
    TILA_smart_editmode
)
# register, unregister = bpy.utils.register_classes_factory(classes)


def register():
    pass


def unregister():
    pass


if __name__ == "__main__":
    register()
