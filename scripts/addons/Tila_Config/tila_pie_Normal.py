from mathutils import Matrix
from bpy.props import BoolProperty
from bpy.types import Operator
from bpy.types import Menu
import bpy
import bmesh

bl_info = {
    "name": "Pie Normal",
    "description": "",
    "author": "Tilapiatsu",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "",
    "warning": "",
    "wiki_url": "",
    "category": "Pie Menu"
}


class TILA_MT_pie_normal(Menu):
    bl_idname = "TILA_MT_pie_normal"
    bl_label = "Normal"

    def draw(self, context):
        layout = self.layout
        view = context.space_data
        obj = context.active_object
        pie = layout.menu_pie()
        # Left
        split = pie.split()
        split.scale_y = 3
        split.scale_x = 1.5
        if context.mode == "OBJECT":
            text = 'Smooth'
        else:
            text = 'Merge'

        split.operator("view3d.tila_normalsmartmerge", icon='NODE_MATERIAL', text=text)

        # Right
        split = pie.split()
        split.scale_y = 3
        split.scale_x = 1.5
        split.operator("view3d.tila_normalsmartsplit", icon='MESH_CUBE', text="Split")

        # Top
        split = pie.split()
        col = split.column()
        col.scale_y = 3
        col.scale_x = 1
        col.operator("mesh.tila_normalaverage", icon='META_CUBE', text="Average Normal")
        col = split.column()
        col.scale_y = 3
        col.scale_x = 1
        col.operator("mesh.tila_normalsmoothen", icon='INVERSESQUARECURVE', text="Smoothen Normal")

        # Bottom
        split = pie.split()
        col = split.column()
        col.scale_y = 1.5
        col.scale_x = 1

        col = split.column()
        col.scale_y = 1.5
        col.scale_x = 1

        # Top Left

        split = pie.split()

        # Top Right
        split = pie.split()

        # Bottom Left

        split = pie.split()
        col = split.column()
        col.scale_y = 1.5
        col.scale_x = 1

        # Bottom Right
        split = pie.split()
        col = split.column()
        col.scale_y = 3
        col.scale_x = 1
        col.prop(view.overlay, "show_split_normals", text="Show Vertex Normal", icon='NORMALS_VERTEX_FACE')
        col = split.column()
        col.prop(view.overlay, "normals_length", text="Size")

        # bpy.context.space_data.overlay.show_split_normals = True


def element_is_selected(object):
    bm = bmesh.from_edit_mesh(object.data)
    if bpy.context.scene.tool_settings.mesh_select_mode[0]:
        for v in bm.verts:
            if v.select:
                return True
        else:
            return False
    if bpy.context.scene.tool_settings.mesh_select_mode[1]:
        for e in bm.edges:
            if e.select:
                return True
        else:
            return False
    if bpy.context.scene.tool_settings.mesh_select_mode[2]:
        for f in bm.faces:
            if f.select:
                return True
        else:
            return False


def run_on_selection(context, functions):
    def run_cmd(object, functions, mode):
        def run():
            if functions[mode]:
                for f in functions[mode]:
                    kwargs = f[1]
                    if kwargs:
                        f[0](**kwargs)
                    else:
                        f[0]()

        if mode == 'OBJECT':
            run()
        else:
            if element_is_selected(object):
                run()

    active = bpy.context.active_object

    if active:
        selection = bpy.context.selected_objects
        if active not in selection:
            selection.append(active)

        for o in selection:
            context.view_layer.objects.active = o
            if context.mode == "EDIT_MESH":
                if bpy.context.scene.tool_settings.mesh_select_mode[0]:
                    run_cmd(o, functions, 'VERT')
                if bpy.context.scene.tool_settings.mesh_select_mode[1]:
                    run_cmd(o, functions, 'EDGE')
                if bpy.context.scene.tool_settings.mesh_select_mode[2]:
                    run_cmd(o, functions, 'FACE')
            elif context.mode == "OBJECT":
                run_cmd(o, functions, 'OBJECT')


class TILA_OT_selectBorderEdges(bpy.types.Operator):
    bl_idname = "mesh.tila_selectborderedges"
    bl_label = "Tilapiatsu select border edge of current face selection"
    bl_options = {'REGISTER', 'UNDO'}

    mode = bpy.props.EnumProperty(name='mode', items=(('ACTIVE', 'Active', 'Active'), ('SELECTED', 'Selected', 'Selected')), default='SELECTED')

    def select_border(self, context, object):
        if context.mode == "EDIT_MESH":
            if bpy.context.scene.tool_settings.mesh_select_mode[2]:
                try:
                    if element_is_selected(object):
                        bpy.ops.mesh.region_to_loop()
                        if not element_is_selected(object):
                            bpy.ops.mesh.select_all(action='INVERT')
                except Exception as e:
                    print(e)

    def execute(self, context):
        active = bpy.context.active_object
        if active:
            if self.mode == 'SELECTED':
                selection = bpy.context.selected_objects
                if active not in selection:
                    selection.append(active)

                for o in selection:
                    context.view_layer.objects.active = o
                    self.select_border(context, o)
            elif self.mode == 'ACTIVE' and active is not None:
                self.select_border(context, active)
        return {'FINISHED'}


class TILA_OT_normalaverage(bpy.types.Operator):
    bl_idname = "mesh.tila_normalaverage"
    bl_label = "Tilapiatsu Average Normals"
    bl_options = {'REGISTER', 'UNDO'}

    func = {'VERT': ((bpy.ops.view3d.tila_autosmooth, None), (bpy.ops.mesh.average_normals, {'average_type': 'FACE_AREA'}),),
            'EDGE': ((bpy.ops.view3d.tila_autosmooth, None), (bpy.ops.mesh.average_normals, {'average_type': 'FACE_AREA'}),),
            'FACE': ((bpy.ops.view3d.tila_autosmooth, None), (bpy.ops.mesh.average_normals, {'average_type': 'FACE_AREA'}))}

    def execute(self, context):

        run_on_selection(context, self.func)

        return {'FINISHED'}


class TILA_OT_normalsmoothen(bpy.types.Operator):
    bl_idname = "mesh.tila_normalsmoothen"
    bl_label = "Tilapiatsu Smoothen Normals"
    bl_options = {'REGISTER', 'UNDO'}

    func = {'VERT': ((bpy.ops.view3d.tila_autosmooth, None), (bpy.ops.mesh.smoothen_normals, {'factor': 1}),),
            'EDGE': ((bpy.ops.view3d.tila_autosmooth, None), (bpy.ops.mesh.smoothen_normals, {'factor': 1}),),
            'FACE': ((bpy.ops.view3d.tila_autosmooth, None), (bpy.ops.mesh.smoothen_normals, {'factor': 1}))}

    def execute(self, context):

        run_on_selection(context, self.func)

        return {'FINISHED'}


class TILA_OT_smartsplit(bpy.types.Operator):
    bl_idname = "view3d.tila_normalsmartsplit"
    bl_label = "Tilapiatsu Smartly Split vertex normal"
    bl_options = {'REGISTER', 'UNDO'}

    func = {'VERT': ((bpy.ops.view3d.tila_autosmooth, None), (bpy.ops.mesh.normals_tools, {'mode': 'RESET'}), (bpy.ops.view3d.tila_splitnormal, None)),
            'EDGE': ((bpy.ops.view3d.tila_splitnormal, None),),
            'FACE': ((bpy.ops.mesh.tila_selectborderedges, {'mode': 'ACTIVE'}), (bpy.ops.view3d.tila_splitnormal, None)),
            'OBJECT': ((bpy.ops.object.shade_flat, None),)}

    def execute(self, context):

        run_on_selection(context, self.func)

        return {'FINISHED'}


class TILA_OT_normalsmartmerge(bpy.types.Operator):
    bl_idname = "view3d.tila_normalsmartmerge"
    bl_label = "Tilapiatsu Smartly merge vertex normal"

    bl_options = {'REGISTER', 'UNDO'}

    func = {'VERT': ((bpy.ops.view3d.tila_autosmooth, None), (bpy.ops.mesh.smoothen_normals, {'factor': 1}), (bpy.ops.view3d.tila_smoothnormal, None)),
            'EDGE': ((bpy.ops.view3d.tila_smoothnormal, None),),
            'FACE': ((bpy.ops.mesh.tila_selectborderedges, {'mode': 'ACTIVE'}), (bpy.ops.view3d.tila_smoothnormal, None)),
            'OBJECT': ((bpy.ops.object.shade_smooth, None),)}

    def execute(self, context):

        run_on_selection(context, self.func)

        return {'FINISHED'}


class TILA_OT_autoSmooth(bpy.types.Operator):
    bl_idname = "view3d.tila_autosmooth"

    bl_label = "Tilapiatsu Auto Smooth"
    bl_options = {'REGISTER', 'UNDO'}

    value = bpy.props.BoolProperty(name='value', default=True)

    def execute(self, context):
        active = bpy.context.active_object

        if active:
            sel = bpy.context.selected_objects
            if active not in sel:
                sel.append(active)

            for obj in sel:
                obj.data.use_auto_smooth = self.value

        return {'FINISHED'}


class TILA_OT_splitNormal(bpy.types.Operator):
    bl_idname = "view3d.tila_splitnormal"
    bl_label = "Tilapiatsu Split Normal"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.view3d.tila_autosmooth(value=True)
        bpy.ops.mesh.split_normals()
        return {'FINISHED'}


class TILA_OT_smoothNormal(bpy.types.Operator):
    bl_idname = "view3d.tila_smoothnormal"
    bl_label = "Tilapiatsu Smooth Normal"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.view3d.tila_autosmooth(value=True)
        bpy.ops.mesh.merge_normals()
        return {'FINISHED'}


classes = (
    TILA_MT_pie_normal,
    TILA_OT_autoSmooth


)
# register, unregister = bpy.utils.register_classes_factory(classes)


def register():
    pass


def unregister():
    pass


if __name__ == "__main__":
    register()
