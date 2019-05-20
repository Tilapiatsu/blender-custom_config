import time
import mathutils

bl_info = {
    "name": "Bevel After Boolean",
    "author": "Rodinkov Ilya",
    "version": (0, 2, 3, 1),
    "blender": (2, 80, 0),
    "location": "View3D > Tools > Boolean Bevel > Bevel",
    "description": "Create bevel after boolean",
    "warning": "This add-on is still in development.",
    "wiki_url": "",
    "category": "Object",
}
import bpy
import bmesh
from bpy.types import (
    Panel, PropertyGroup
)


class BooleanBevelPanel(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tools"
    bl_label = "Boolean Bevel"

    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        if 0 < len(bpy.context.selected_objects) < 2:
            if len(context.active_object.modifiers) > 0 and (
                    context.active_object.modifiers[len(
                        context.active_object.modifiers) - 1].type == "BOOLEAN") or context.active_object.data.is_editmode:
                box.operator("object.boolean_bevel", text="Bevel", icon='MOD_BEVEL')
                box.operator("object.boolean_bevel_make_pipe", text="Make Pipe", icon='MOD_BEVEL')


class ObjectBooleanBevelPipe(bpy.types.Operator):
    """Create the pipe on Object"""
    bl_idname = "object.boolean_bevel_make_pipe"
    bl_label = "Boolean Bevel Pipe"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()

        box.label(text="Show/Hide:")
        row = box.row(align=True)
        row.alignment = 'CENTER'
        if not self.editmode:
            row.prop(self, "wire")
            row.prop(self, "stop_calc")

        box = layout.box()
        box.label(text="Basic Parameters:")
        box.prop(self, "offset")
        box.prop(self, "number_cuts")
        box.prop(self, "method")

        if not self.editmode:
            box = layout.box()
            box.label(text="Subsurf:")

            if self.subsurf_boolean:
                box.prop(self, "subdiv_a")
            if self.subsurf_object:
                box.prop(self, "subdiv_b")

        box = layout.box()
        box.label(text="Patch Parameters:")
        box.prop(self, "smooth")
        box.prop(self, "factor")
        box.prop(self, "remove_doubles")
        box.prop(self, "subdivide")

        box = layout.box()
        box.label(text="Other:")


        box.separator()
        if self.method == 'METHOD_1':
            box.prop(self, "pipe_smooth")
        box.prop(self, "step")
        box.prop(self, "curve_tilt")

    stop_calc: bpy.props.BoolProperty(name="Stop calculations", default=False)
    # offset
    wire = bpy.props.BoolProperty(name="Wire", default=False)
    offset = bpy.props.FloatProperty(name="Pipe Radius", default=0.05, min=0.001, max=1000.0, step=1)
    number_cuts = bpy.props.IntProperty(name="Pipe Sides", default=8, min=1, max=5000)

    # patch
    remove_doubles = bpy.props.FloatProperty(name="Remove Doubles", default=0.0, min=0.0, max=1.0, step=1)
    subdivide = bpy.props.IntProperty(name="Subdivide Patch", default=0, min=0, max=5000)
    smooth = bpy.props.IntProperty(name="Smooth Patch", default=0, min=0, max=5000)
    factor = bpy.props.FloatProperty(name="Smooth Factor", default=0.5, min=0.0, max=1.0, step=1)

    pipe_smooth = bpy.props.IntProperty(name="Pipe Smooth", default=500, min=0, max=5000)
    curve_tilt = bpy.props.FloatProperty(name="Mean Tilt", default=45.0, min=-45.0, max=45.0)

    # method
    method = bpy.props.EnumProperty(name="Method",
                                    items=(("METHOD_1", "Pipe", "Use Union"),
                                           ("METHOD_2", "Custom Pipe", "Use Difference")),
                                    description="method",
                                    default="METHOD_1")

    # change_subdivide = bpy.props.BoolProperty(name="Change subdivide", default=False)
    subdiv_a = bpy.props.IntProperty(name="Subdiv A", default=1, min=0, max=6)
    subdiv_b = bpy.props.IntProperty(name="Subdiv B", default=1, min=0, max=6)
    step = bpy.props.IntProperty(name="AutoSmooth Step", default=10, min=1, max=1000)

    src_obj = False
    editmode = False
    guide = False
    curve_cut = False


    bool_obj = False
    # wire = False
    # stop_calc = False
    operation = 'UNION'
    subsurf_boolean = False
    subsurf_object = False
    transfer = False

    subsurf_object = False
    subsurf_boolean = False

    def invoke(self, context, event):
        self.src_obj = context.active_object
        self.editmode = self.src_obj.data.is_editmode
        if not self.editmode:
            # self.stop_calc = false
            self.bool_obj = self.src_obj.modifiers[len(self.src_obj.modifiers) - 1].object
            self.operation = self.src_obj.modifiers[len(self.src_obj.modifiers) - 1].operation
            # ищем последние модификаторы подразделения
            for modifier in self.bool_obj.modifiers:
                if modifier.type == "SUBSURF":
                    self.subsurf_object = modifier
                    self.subdiv_b = self.subsurf_object.levels
            for modifier in self.src_obj.modifiers:
                if modifier.type == "SUBSURF":
                    self.subsurf_boolean = modifier
                    self.subdiv_a = self.subsurf_boolean.levels
        return self.execute(context)

    def execute(self, context):
        self.src_obj = context.active_object
        self.editmode = self.src_obj.data.is_editmode
        # orign = bpy.context.space_data.pivot_point
        orign = bpy.context.scene.tool_settings.transform_pivot_point

        if self.editmode:
            index = bpy.data.objects.find('BOOLEAN_BEVEL_PIPE')

            if index != -1:
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.select_all(action='DESELECT')
                bpy.data.objects[index].select_set(True)
                bpy.ops.object.delete(use_global=False)
                #
                self.src_obj.select_set(True)
                context.view_layer.objects.active = self.src_obj
                # bpy.context.space_data.pivot_point = orign
                bpy.ops.object.mode_set(mode='EDIT')
            # self.src_obj.select = True
            # создаем копию пересечения
            bpy.ops.mesh.duplicate_move()
            # Удаляем дубли вершин
            if self.remove_doubles:
                bpy.ops.mesh.remove_doubles(threshold=self.remove_doubles, use_unselected=False)

            # Подразделяем, если нужно
            if self.subdivide:
                bpy.ops.mesh.subdivide(number_cuts=self.subdivide, smoothness=0.0)
            # Сглаживаем, если нужно
            if self.smooth:
                bpy.ops.mesh.vertices_smooth(factor=self.factor, repeat=self.smooth, xaxis=True, yaxis=True, zaxis=True)
            bpy.ops.mesh.separate(type='SELECTED')
            bpy.ops.object.mode_set(mode='OBJECT')
            self.guide = bpy.context.selected_objects[1]
            self.guide.name = "BOOLEAN_BEVEL_GUIDE"
            bpy.ops.object.select_all(action='DESELECT')
            context.view_layer.objects.active = self.guide
            self.guide.select_set(True)
            # создаем группу вершин
            self.guide.vertex_groups.new(name=self.src_obj.name)
            # добавляем в нее все вершины
            self.guide.vertex_groups.active.add(range(len(self.guide.data.vertices)), 1, 'ADD')
            if self.method == 'METHOD_1':
                pipe(self, context)
            else:
                bpy.context.scene.tool_settings.transform_pivot_point = 'INDIVIDUAL_ORIGINS'
                custom_pipe(self, context)

            smooth_modifier = self.curve_cut.modifiers.new(name="Boolean Bevel Smooth", type='CORRECTIVE_SMOOTH')
            smooth_modifier.smooth_type = "LENGTH_WEIGHTED"
            smooth_modifier.iterations = 0
            smooth_modifier.use_only_smooth = True

            while True:
                # self-intesect
                # context.depsgraph.update()
                context.scene.update()
                bm = bmesh.new()
                # print(bm.from_object.argv)
                bm.from_object(self.curve_cut, context.depsgraph, deform=True, cage=False)
                tree = mathutils.bvhtree.BVHTree.FromBMesh(bm, epsilon=0.00001)
                # tree = mathutils.bvhtree.BVHTree.FromObject(self.curve_cut, context.depsgraph, deform=True, cage=False,
                #                                             epsilon=0.00001)
                overlap = tree.overlap(tree)
                if not overlap or smooth_modifier.iterations >= 200:
                    break
                else:
                    smooth_modifier.iterations += self.step

            if overlap:
                self.report({'INFO'}, "Self-Intersect Pipe")
                # self.curve_cut.show_x_ray = True
                return {'FINISHED'}

            # self.curve_cut.select = True
            bpy.ops.object.select_all(action='DESELECT')
            self.guide.select_set(True)
            bpy.ops.object.delete(use_global=False)
            #
            self.src_obj.select_set(True)
            context.view_layer.objects.active = self.src_obj
            bpy.context.scene.tool_settings.transform_pivot_point = orign
            bpy.ops.object.mode_set(mode='EDIT')

            self.curve_cut.name = "BOOLEAN_BEVEL_PIPE"
            return {'FINISHED'}

        bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked": False, "mode": 'TRANSLATION'})
        dup = context.active_object
        bpy.ops.object.select_all(action='DESELECT')
        dup.select_set(True)


        if self.stop_calc:
            return {'FINISHED'}
        # self.src_obj = context.active_object
        prepare_object(self, context)

        if self.method == 'METHOD_1':
            pipe(self, context)
        else:
            bpy.context.scene.tool_settings.transform_pivot_point = 'INDIVIDUAL_ORIGINS'
            custom_pipe(self, context)

        smooth_modifier = self.curve_cut.modifiers.new(name="Boolean Bevel Smooth", type='CORRECTIVE_SMOOTH')
        smooth_modifier.smooth_type = "LENGTH_WEIGHTED"
        smooth_modifier.iterations = 0
        smooth_modifier.use_only_smooth = True

        while True:
            # self-intesect
            # context.depsgraph.update()
            context.scene.update()
            bm = bmesh.new()
            # print(bm.from_object.argv)
            bm.from_object(self.curve_cut, context.depsgraph, deform=True, cage=False)
            tree = mathutils.bvhtree.BVHTree.FromBMesh(bm, epsilon=0.00001)
            # tree = mathutils.bvhtree.BVHTree.FromObject(self.curve_cut, context.depsgraph, deform=True, cage=False,
            #                                             epsilon=0.00001)
            overlap = tree.overlap(tree)
            if not overlap or smooth_modifier.iterations >= 200:
                break
            else:
                smooth_modifier.iterations += self.step

        if overlap:
            self.report({'INFO'}, "Self-Intersect Pipe")
            # self.curve_cut.show_x_ray = True
            return {'FINISHED'}

        bpy.ops.object.select_all(action='DESELECT')
        self.guide.select_set(True)
        self.src_obj.select_set(True)
        bpy.ops.object.delete(use_global=False)

        bpy.context.scene.tool_settings.transform_pivot_point = orign
        self.curve_cut.name = "BOOLEAN_BEVEL_PIPE"
        return {'FINISHED'}


class ObjectBooleanBevel(bpy.types.Operator):
    """Create Bevel"""
    bl_idname = "object.boolean_bevel"
    bl_label = "Bevel"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()

        box.label(text="Show/Hide:")
        row = box.row(align=True)
        row.alignment = 'CENTER'
        if not self.editmode:
            row.prop(self, "wire")
            row.prop(self, "preview_curve")
        row.prop(self, "stop_calc")
        box = layout.box()
        box.label(text="Basic Parameters:")
        if not self.editmode:
            box.prop(self, "operation")
        box.prop(self, "offset")
        box.prop(self, "method")

        if not self.editmode:
            box = layout.box()
            box.label(text="Subsurf:")

            if self.subsurf_boolean:
                box.prop(self, "subdiv_a", text=self.src_obj.name)
            if self.subsurf_object:
                box.prop(self, "subdiv_b", text=self.bool_obj.name)
        box = layout.box()
        box.label(text="Bevel:")
        box.prop(self, "bevel_profile")
        box.prop(self, "bevel_segments")

        box.prop(self, "smoothBevel")
        if self.smoothBevel:
            box.prop(self, "smooth_bevel_value")
            box.prop(self, "smooth_bevel_step")

        if not self.editmode:
            box.prop(self, "transfer")
            if self.transfer:
                box.prop(self, "transfer_factor")
        box.prop(self, "triangulate")
        if self.triangulate:
            box.prop(self, "trmethod")
        box.separator()

        box = layout.box()
        box.label(text="Patch Parameters:")
        box.prop(self, "smooth")
        box.prop(self, "factor")
        box.prop(self, "remove_doubles")
        box.prop(self, "subdivide")

        box = layout.box()
        box.label(text="Other:")

        box.prop(self, "number_cuts")
        box.separator()
        if self.method == 'METHOD_1':
            box.prop(self, "pipe_smooth")
        box.prop(self, "step")
        box.prop(self, "curve_tilt")

    def invoke(self, context, event):
        self.src_obj = context.active_object
        self.editmode = self.src_obj.data.is_editmode

        if not self.editmode:
            # self.stop_calc = True
            self.bool_obj = self.src_obj.modifiers[len(self.src_obj.modifiers) - 1].object
            self.operation = self.src_obj.modifiers[len(self.src_obj.modifiers) - 1].operation
            # ищем последние модификаторы подразделения
            for modifier in self.bool_obj.modifiers:
                if modifier.type == "SUBSURF":
                    self.subsurf_object = modifier
                    self.subdiv_b = self.subsurf_object.levels
            for modifier in self.src_obj.modifiers:
                if modifier.type == "SUBSURF":
                    self.subsurf_boolean = modifier
                    self.subdiv_a = self.subsurf_boolean.levels
        return self.execute(context)

    # Other
    stop_calc: bpy.props.BoolProperty(name="Stop calculations", default=False)
    wire: bpy.props.BoolProperty(name="Wire", default=False)
    preview_curve: bpy.props.BoolProperty(name="Curve", default=False)

    # operation
    operation: bpy.props.EnumProperty(name="Operation",
                                      items=(("UNION", "Union", "Use Union"),
                                             ("DIFFERENCE", "Difference", "Use Difference"),
                                             ("INTERSECT", "Intersect", "Use Intersect"),
                                             ("SLICE", "Slice", "Use Slice")
                                             ),
                                      description="Boolean Operation",
                                      default="UNION")

    # offset
    offset: bpy.props.FloatProperty(name="Cut Radius", default=0.05, min=0.001, max=1000.0, step=1)
    number_cuts: bpy.props.IntProperty(name="Pipe Sides", default=8, min=1, max=5000)
    pipe_smooth: bpy.props.IntProperty(name="Pipe Smooth", default=500, min=0, max=5000)

    # bevel
    bevel_profile: bpy.props.FloatProperty(name="Bevel Profile", default=0.5, min=0, max=1.0)
    bevel_segments: bpy.props.IntProperty(name="Bevel Segments", default=10, min=1, max=2000)

    # patch
    remove_doubles: bpy.props.FloatProperty(name="Remove Doubles", default=0.0, min=0.0, max=1.0, step=1)
    subdivide: bpy.props.IntProperty(name="Subdivide Patch", default=0, min=0, max=5000)
    smooth: bpy.props.IntProperty(name="Smooth Patch", default=0, min=0, max=5000)
    factor: bpy.props.FloatProperty(name="Smooth Factor", default=0.5, min=0.0, max=1.0, step=1)

    smoothBevel: bpy.props.BoolProperty(name="Smooth Bevel", default=True)
    smooth_bevel_value: bpy.props.IntProperty(name="Smooth Value", default=5, min=0, max=2000)
    smooth_bevel_step: bpy.props.IntProperty(name="Smooth Step", default=3, min=0, max=1000)
    step: bpy.props.IntProperty(name="AutoSmooth Step", default=10, min=1, max=1000)

    transfer: bpy.props.BoolProperty(name="Transfer Normals", default=True)
    transfer_factor: bpy.props.FloatProperty(name="Transfer Factor", default=0.8, min=0.0, max=1.0, step=1)

    # pushPull : bpy.props.FloatProperty(name="Push/Pull", default=1.0, min=-5.0, max=5.0, step=1)

    # method
    method: bpy.props.EnumProperty(name="Method",
                                   items=(("METHOD_1", "Pipe", "Use Union"),
                                          ("METHOD_2", "Custom Pipe", "Use Difference")),
                                   description="method",
                                   default="METHOD_1")

    triangulate: bpy.props.BoolProperty(name="Split NGon", default=True)
    trmethod: bpy.props.EnumProperty(name="Method",
                                     items=(("BEAUTY", "BEAUTY", "Use BEAUTY"),
                                            ("CLIP", "CLIP", "Use CLIP")),
                                     description="Method for splitting the polygons into triangles",
                                     default="BEAUTY")

    # change_subdivide : bpy.props.BoolProperty(name="Change subdivide", default=False)
    subdiv_a: bpy.props.IntProperty(name="Subdiv A", default=1, min=0, max=6)
    subdiv_b: bpy.props.IntProperty(name="Subdiv B", default=1, min=0, max=6)

    curve_tilt: bpy.props.FloatProperty(name="Mean Tilt", default=45.0, min=-45.0, max=45.0)

    # Внутренние переменные

    src_obj = False
    bool_obj = False
    normals_object = False
    subsurf_boolean = False
    subsurf_object = False
    guide = False
    curve_cut = False
    editmode = False

    def execute(self, context):
        time_start = time.time()
        context.tool_settings.vertex_group_weight = 1.0

        orign = bpy.context.scene.tool_settings.transform_pivot_point

        if self.editmode:
            backTransfer = self.transfer
            self.transfer = False

            if self.stop_calc:
                return {'FINISHED'}
            self.src_obj = context.active_object
            # Удаляем группы вершин
            if len(self.src_obj.vertex_groups) != 0:
                self.src_obj.vertex_groups.clear()
            # создаем копию пересечения
            bpy.ops.mesh.duplicate_move()

            # Удаляем дубли вершин
            if self.remove_doubles:
                bpy.ops.mesh.remove_doubles(threshold=self.remove_doubles, use_unselected=False)

            # Подразделяем, если нужно
            if self.subdivide:
                bpy.ops.mesh.subdivide(number_cuts=self.subdivide, smoothness=0.0)
            # Сглаживаем, если нужно
            if self.smooth:
                bpy.ops.mesh.vertices_smooth(factor=self.factor, repeat=self.smooth, xaxis=True, yaxis=True, zaxis=True)

            # группа вершин для пересечения
            self.src_obj.vertex_groups.new(name="A")
            self.src_obj.vertex_groups.new(name="B")
            self.src_obj.vertex_groups.new(name="bevel")
            bpy.ops.object.vertex_group_assign()

            intersection = self.src_obj.vertex_groups.active.index
            # bpy.ops.mesh.duplicate_move()
            bpy.ops.mesh.separate(type='SELECTED')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.hide(unselected=False)
            bpy.ops.object.mode_set(mode='OBJECT')
            self.guide = bpy.context.selected_objects[1]
            self.guide.name = "BOOLEAN_BEVEL_GUIDE"
            bpy.ops.object.select_all(action='DESELECT')
            context.view_layer.objects.active = self.guide
            self.guide.select_set(True)

            if self.method == 'METHOD_1':
                pipe(self, context)
            else:
                bpy.context.scene.tool_settings.transform_pivot_point = 'INDIVIDUAL_ORIGINS'
                custom_pipe(self, context)

            smooth_modifier = self.curve_cut.modifiers.new(name="Boolean Bevel Smooth", type='CORRECTIVE_SMOOTH')
            smooth_modifier.smooth_type = "LENGTH_WEIGHTED"
            smooth_modifier.iterations = 0
            smooth_modifier.use_only_smooth = True

            while True:
                # self-intesect
                # context.depsgraph.update()
                context.scene.update()
                bm = bmesh.new()
                # print(bm.from_object.argv)
                bm.from_object(self.curve_cut, context.depsgraph, deform=True, cage=False)
                tree = mathutils.bvhtree.BVHTree.FromBMesh(bm, epsilon=0.00001)
                # tree = mathutils.bvhtree.BVHTree.FromObject(self.curve_cut, context.depsgraph, deform=True, cage=False,
                #                                             epsilon=0.00001)
                overlap = tree.overlap(tree)
                if not overlap or smooth_modifier.iterations >= 200:
                    break
                else:
                    smooth_modifier.iterations += self.step

            if overlap:
                self.report({'INFO'}, "Self-Intersect Pipe")
                self.curve_cut.show_in_front = True
                return {'FINISHED'}

            do_boolean(self, context, self.src_obj)

            # # test
            # self.curve_cut.select_set(True)
            # self.guide.select_set(True)
            # bpy.ops.object.delete(use_global=False)
            #
            # self.src_obj.select_set(True)
            # context.view_layer.objects.active = self.src_obj
            #
            # bpy.context.scene.tool_settings.transform_pivot_point = orign
            # bpy.ops.object.mode_set(mode='EDIT')
            #
            # self.transfer = backTransfer
            # return {'FINISHED'}

            create_bevel(self, context, self.src_obj)

            self.curve_cut.select_set(True)
            self.guide.select_set(True)
            bpy.ops.object.delete(use_global=False)

            self.src_obj.select_set(True)
            context.view_layer.objects.active = self.src_obj

            bpy.context.scene.tool_settings.transform_pivot_point = orign
            bpy.ops.object.mode_set(mode='EDIT')

            self.transfer = backTransfer
            return {'FINISHED'}
        prepare_object(self, context)

        if self.stop_calc:
            return {'FINISHED'}

        if self.method == 'METHOD_1':
            pipe(self, context)
        else:
            bpy.context.scene.tool_settings.transform_pivot_point = 'INDIVIDUAL_ORIGINS'
            custom_pipe(self, context)

        smooth_modifier = self.curve_cut.modifiers.new(name="Boolean Bevel Smooth", type='CORRECTIVE_SMOOTH')
        smooth_modifier.smooth_type = "LENGTH_WEIGHTED"
        smooth_modifier.iterations = 0
        smooth_modifier.use_only_smooth = True
        # modifiers["Boolean"].show_render
        while True:
            # self-intesect
            # context.depsgraph.update()
            context.scene.update()
            bm = bmesh.new()
            # print(bm.from_object.argv)
            bm.from_object(self.curve_cut, context.depsgraph, deform=True, cage=False)
            tree = mathutils.bvhtree.BVHTree.FromBMesh(bm, epsilon=0.00001)
            # tree = mathutils.bvhtree.BVHTree.FromObject(self.curve_cut, context.depsgraph, deform=True, cage=False,
            #                                             epsilon=0.00001)
            overlap = tree.overlap(tree)
            if not overlap or smooth_modifier.iterations >= 200:
                break
            else:
                smooth_modifier.iterations += self.step

        if overlap:
            self.report({'INFO'}, "Self-Intersect Pipe")
            self.curve_cut.show_in_front = True
            return {'FINISHED'}

        if self.preview_curve:
            self.curve_cut.show_in_front = True
            return {'FINISHED'}

        # return {'FINISHED'}
        do_boolean(self, context, self.src_obj)

        # return {'FINISHED'}

        create_bevel(self, context, self.src_obj)

        if self.operation == "SLICE":
            context.view_layer.objects.active = self.slice_object
            do_boolean(self, context, self.slice_object)

            create_bevel(self, context, self.slice_object)

            self.slice_object.name += "_"

        # bpy.ops.object.mode_set(mode='OBJECT')
        if self.transfer:
            self.normals_object.select_set(True)
        self.curve_cut.select_set(True)
        self.guide.select_set(True)
        bpy.ops.object.delete(use_global=False)

        self.src_obj.select_set(True)
        context.view_layer.objects.active = self.src_obj
        bpy.context.scene.tool_settings.transform_pivot_point = orign
        print("Общее время: %.4f sec\n" % (time.time() - time_start))
        return {'FINISHED'}


def prepare_object(self, context):
    time_start = time.time()
    self.src_obj = context.active_object
    self.bool_obj = self.src_obj.modifiers[len(self.src_obj.modifiers) - 1].object
    self.bool_obj.display_type = 'BOUNDS'
    # Включаем и выключаем сетку
    self.src_obj.show_wire = self.wire
    self.src_obj.show_all_edges = self.wire

    if self.stop_calc:
        return {'FINISHED'}

    # скрываем все модификаторы
    self.src_obj.modifiers.foreach_set('show_viewport', [False] * len(self.src_obj.modifiers))
    # Удаляем группы вершин
    if len(self.src_obj.vertex_groups) != 0:
        self.src_obj.vertex_groups.clear()
    # создаем группу вершин
    self.src_obj.vertex_groups.new(name=self.src_obj.name)
    # добавляем в нее все вершины
    self.src_obj.vertex_groups.active.add(range(len(self.src_obj.data.vertices)), 1, 'ADD')

    # Меняем оперцию
    if self.operation == "SLICE":
        self.src_obj.modifiers[len(self.src_obj.modifiers) - 1].operation = "DIFFERENCE"
    else:
        self.src_obj.modifiers[len(self.src_obj.modifiers) - 1].operation = self.operation

    # ищем последние модификаторы подразделения
    for modifier in self.bool_obj.modifiers:
        if modifier.type == "SUBSURF":
            self.subsurf_object = modifier
            # self.subdiv_b = self.subsurf_object.levels
    for modifier in self.src_obj.modifiers:
        if modifier.type == "SUBSURF":
            self.subsurf_boolean = modifier
            # self.subdiv_a = self.subsurf_boolean.levels

    # меняем подразделение
    if self.subsurf_boolean != False:
        if self.subdiv_a:
            self.subsurf_boolean.levels = self.subdiv_a
        else:
            bpy.ops.object.modifier_remove(modifier=self.subsurf_boolean.name)
    if self.subsurf_object != False:
        self.subsurf_object.levels = self.subdiv_b

    # Применяем все модификаторы
    for modifier in self.src_obj.modifiers:
        if modifier.type != "BOOLEAN":
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier=modifier.name)

    if self.transfer:
        bpy.ops.object.select_all(action='DESELECT')
        self.src_obj.select_set(True)

        bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked": False, "mode": 'TRANSLATION'})
        self.normals_object = context.active_object
        self.normals_object.name = self.src_obj.name + "_Normals"

        self.src_obj.select_set(False)
        self.normals_object.hide_render = True
        self.normals_object.display_type = 'BOUNDS'

    bpy.ops.object.select_all(action='DESELECT')
    context.view_layer.objects.active = self.src_obj
    self.src_obj.select_set(True)

    if self.operation == "SLICE":
        bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked": False, "mode": 'TRANSLATION'})
        self.slice_object = context.active_object
        self.slice_object.name = self.src_obj.name + "_SLICE"
        self.slice_object.modifiers[len(self.slice_object.modifiers) - 1].operation = "INTERSECT"
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=self.src_obj.modifiers[0].name)

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type='VERT')
        # Выделяем вершины без групп
        bpy.ops.mesh.select_ungrouped(extend=False)
        # группа вершин для части булена
        self.slice_object.vertex_groups.new(name=self.bool_obj.name)
        bpy.ops.object.vertex_group_assign()
        # Выделяем пересечение
        bpy.ops.mesh.region_to_loop()
        bpy.ops.object.vertex_group_remove_from()
        self.slice_object.vertex_groups.new(name="bevel")
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.hide(unselected=True)
        bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.select_all(action='DESELECT')
    context.view_layer.objects.active = self.src_obj
    self.src_obj.select_set(True)

    bpy.ops.object.modifier_apply(apply_as='DATA', modifier=self.src_obj.modifiers[0].name)

    # Применяем масштаб
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(type='VERT')
    # Выделяем вершины без групп
    bpy.ops.mesh.select_ungrouped(extend=False)
    # группа вершин для части булена
    self.src_obj.vertex_groups.new(name=self.bool_obj.name)
    bpy.ops.object.vertex_group_assign()
    bool_obj_vertex = self.src_obj.vertex_groups.active.index
    # Выделяем пересечение
    bpy.ops.mesh.region_to_loop()
    bpy.ops.object.vertex_group_remove_from()
    # создаем копию пересечения
    bpy.ops.mesh.duplicate_move()

    # Удаляем дубли вершин
    if self.remove_doubles:
        bpy.ops.mesh.remove_doubles(threshold=self.remove_doubles, use_unselected=False)

    # Подразделяем, если нужно
    if self.subdivide:
        bpy.ops.mesh.subdivide(number_cuts=self.subdivide, smoothness=0.0)
    # Сглаживаем, если нужно
    if self.smooth:
        bpy.ops.mesh.vertices_smooth(factor=self.factor, repeat=self.smooth, xaxis=True, yaxis=True, zaxis=True)

    # группа вершин для пересечения
    self.src_obj.vertex_groups.new(name="bevel")
    bpy.ops.object.vertex_group_assign()
    # bpy.ops.mesh.duplicate_move()
    bpy.ops.mesh.separate(type='SELECTED')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.hide(unselected=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    self.guide = bpy.context.selected_objects[1]
    self.guide.name = "BOOLEAN_BEVEL_GUIDE"
    bpy.ops.object.select_all(action='DESELECT')
    context.view_layer.objects.active = self.guide
    self.guide.select_set(True)
    print("Время prepare_object: %.4f sec\n" % (time.time() - time_start))


def pipe(self, context):
    time_start = time.time()
    bpy.ops.object.convert(target='CURVE', keep_original=True)
    self.curve_cut = bpy.context.object
    self.curve_cut.name = "BOOLEAN_BEVEL_CURVE"
    self.curve_cut.data.resolution_u = 1
    self.curve_cut.data.fill_mode = 'FULL'
    self.curve_cut.data.bevel_depth = self.offset
    self.curve_cut.data.bevel_resolution = self.number_cuts
    self.curve_cut.data.twist_smooth = self.pipe_smooth

    bpy.ops.object.select_all(action='DESELECT')
    context.view_layer.objects.active = self.curve_cut
    self.curve_cut.select_set(True)

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.transform.tilt(value=self.curve_tilt)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.convert(target='MESH', keep_original=False)

    # добавляем в нее все вершины
    self.curve_cut.vertex_groups.active.add(range(len(self.curve_cut.data.vertices)), 1, 'ADD')

    print("Время Create Curve: %.4f sec\n" % (time.time() - time_start))


def custom_pipe(self, context):
    time_start = time.time()
    bpy.ops.object.convert(target='MESH', keep_original=True)
    self.curve_cut = bpy.context.object
    self.curve_cut.name = "BOOLEAN_BEVEL_CURVE"
    bpy.ops.object.select_all(action='DESELECT')
    # bpy.context.view_layer.objects.active = guide
    self.curve_cut.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.edge_face_add()
    bpy.ops.transform.translate(value=(0.0, 0.0, -self.offset),
                                constraint_axis=(False, False, True),
                                orient_type='NORMAL', mirror=False, proportional='DISABLED',
                                proportional_edit_falloff='SMOOTH', proportional_size=1.0, snap=False,
                                snap_target='CLOSEST', snap_point=(0.0, 0.0, 0.0), snap_align=False,
                                snap_normal=(0.0, 0.0, 0.0), gpencil_strokes=False, texture_space=False,
                                remove_on_cancel=False, release_confirm=False)

    bpy.ops.mesh.extrude_region(mirror=False)
    bpy.ops.transform.translate(value=(0.0, 0.0, self.offset * 2),
                                constraint_axis=(False, False, True),
                                orient_type='NORMAL', mirror=False, proportional='DISABLED',
                                proportional_edit_falloff='SMOOTH', proportional_size=1.0, snap=False,
                                snap_target='CLOSEST', snap_point=(0.0, 0.0, 0.0), snap_align=False,
                                snap_normal=(0.0, 0.0, 0.0), gpencil_strokes=False, texture_space=False,
                                remove_on_cancel=False, release_confirm=False)

    bpy.ops.object.vertex_group_remove_from()
    bpy.ops.mesh.delete(type='FACE')

    bpy.ops.object.vertex_group_select()
    bpy.ops.mesh.delete(type='FACE')

    # выделяем связанные вершины
    bpy.ops.object.vertex_group_select()
    bpy.ops.mesh.select_linked()

    bpy.ops.mesh.bridge_edge_loops(type='PAIRS', use_merge=False, merge_factor=0.5, twist_offset=0,
                                   number_cuts=self.number_cuts, interpolation='LINEAR', smoothness=0.0,
                                   profile_shape_factor=self.offset * 1.2, profile_shape='SPHERE')

    # Выделяем края
    bpy.ops.mesh.region_to_loop()

    bpy.ops.mesh.bridge_edge_loops(type='PAIRS', use_merge=False, merge_factor=0.5, twist_offset=0,
                                   number_cuts=self.number_cuts, interpolation='LINEAR', smoothness=0.0,
                                   profile_shape_factor=-self.offset * 1.2, profile_shape='SPHERE')
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    context.view_layer.objects.active = self.curve_cut
    self.curve_cut.select_set(True)
    print("Время Create Curve: %.4f sec\n" % (time.time() - time_start))


def do_boolean(self, context, obj):
    time_start = time.time()
    self.curve_cut.display_type = 'BOUNDS'
    boolean_modifier = obj.modifiers.new(name="BooleanBevel", type='BOOLEAN')
    boolean_modifier.show_viewport = False
    boolean_modifier.object = self.curve_cut
    boolean_modifier.operation = "UNION"
    bpy.ops.object.select_all(action='DESELECT')
    context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier=boolean_modifier.name)
    print("Время Do Boolean: %.4f sec\n" % (time.time() - time_start))


def create_bevel(self, context, obj):
    time_start = time.time()
    # return {'FINISHED'}
    # выделяем нужные грани
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(type='VERT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.select_less(use_face_step=True)
    bpy.ops.object.vertex_group_assign()

    bpy.ops.mesh.select_more(use_face_step=False)
    bpy.ops.mesh.select_all(action='INVERT')
    # удаляем лишние вершины
    bpy.ops.mesh.edge_collapse()
    bpy.ops.mesh.dissolve_verts(use_face_split=True, use_boundary_tear=False)

    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.vertex_group_select()

    bpy.ops.mesh.hide(unselected=True)

    bpy.ops.mesh.select_mode(type='EDGE')
    bpy.ops.mesh.region_to_loop()
    bpy.ops.mesh.loop_multi_select(ring=True)
    bpy.ops.mesh.select_all(action='INVERT')
    bpy.ops.mesh.loop_multi_select(ring=False)
    # return
    bpy.ops.mesh.edge_collapse()

    # # Выравниваем кол-во вершин на всех краях
    # bpy.ops.mesh.select_more(use_face_step=False)
    # bpy.ops.mesh.select_all(action='INVERT')
    # # удаляем лишние вершины
    # bpy.ops.mesh.edge_collapse()
    # bpy.ops.mesh.dissolve_verts(use_face_split=True, use_boundary_tear=False)
    #
    # src_obj.vertex_groups.active_index = 2
    # bpy.ops.mesh.select_mode(type='EDGE')
    # bpy.ops.object.vertex_group_select()
    # bpy.ops.mesh.select_more(use_face_step=True)
    #
    # # Убираем оставшиеся вершины
    # bpy.ops.mesh.hide(unselected=True)
    # bpy.ops.mesh.select_face_by_sides(number=3, type='EQUAL', extend=False)
    # bpy.ops.object.vertex_group_deselect()
    # bpy.ops.mesh.edge_collapse()
    # # Дополнение
    # bpy.ops.object.vertex_group_select()
    # bpy.ops.mesh.select_mode(type='VERT')
    # bpy.ops.mesh.select_more(use_face_step=False)
    # bpy.ops.mesh.select_all(action='INVERT')
    # bpy.ops.mesh.edge_collapse()
    # bpy.ops.mesh.dissolve_verts(use_face_split=True, use_boundary_tear=False)
    # bpy.ops.mesh.select_mode(type='EDGE')
    # bpy.ops.object.vertex_group_select()
    # bpy.ops.mesh.delete(type='VERT')
    #
    bpy.ops.mesh.reveal()
    bpy.ops.mesh.select_all(action='DESELECT')
    obj.vertex_groups.active_index = 0
    bpy.ops.object.vertex_group_select()
    bpy.ops.mesh.select_more(use_face_step=True)
    # bpy.ops.object.vertex_group_deselect()
    # bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method=trmethod)
    bpy.context.tool_settings.vertex_group_weight = self.transfer_factor
    bpy.ops.object.vertex_group_deselect()
    bpy.ops.object.vertex_group_assign()

    #
    # try:
    #     bpy.ops.mesh.bridge_edge_loops(type='PAIRS', use_merge=False, merge_factor=0.5, twist_offset=0,
    #                                    number_cuts=0, interpolation='LINEAR', smoothness=0.0,
    #                                    profile_shape_factor=0.0, profile_shape='SMOOTH')
    # except:
    #     bpy.ops.object.mode_set(mode='OBJECT')
    #     self.report({'INFO'}, "Error creating bevel")
    #     return {'FINISHED'}
    #
    bpy.ops.mesh.select_all(action='DESELECT')
    obj.vertex_groups.active_index = 1
    bpy.ops.object.vertex_group_select()
    bpy.ops.mesh.select_more(use_face_step=True)
    # bpy.ops.object.vertex_group_deselect()
    # bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method=trmethod)
    bpy.ops.object.vertex_group_deselect()
    bpy.ops.object.vertex_group_assign()

    # bpy.ops.mesh.region_to_loop()
    obj.vertex_groups.active_index = 2
    # bpy.ops.object.vertex_group_select()
    #
    # try:
    #     bpy.ops.mesh.bridge_edge_loops(type='PAIRS', use_merge=False, merge_factor=0.5, twist_offset=0,
    #                                    number_cuts=0, interpolation='LINEAR', smoothness=0.0,
    #                                    profile_shape_factor=0.0, profile_shape='SMOOTH')
    #
    # except:
    #     bpy.ops.object.mode_set(mode='OBJECT')
    #     self.report({'INFO'}, "Error creating bevel")
    #     return {'FINISHED'}

    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.vertex_group_select()

    bpy.ops.object.mode_set(mode='OBJECT')

    shrinkwrap_modifier = obj.modifiers.new(name="shrinkwrap", type='SHRINKWRAP')
    shrinkwrap_modifier.wrap_method = 'NEAREST_VERTEX'
    shrinkwrap_modifier.vertex_group = obj.vertex_groups[2].name
    shrinkwrap_modifier.target = bpy.data.objects['BOOLEAN_BEVEL_GUIDE']
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier=shrinkwrap_modifier.name)

    # return {'FINISHED'}

    bpy.ops.object.mode_set(mode='EDIT')

    bpy.ops.mesh.select_mode(type='EDGE')
    bpy.ops.object.vertex_group_select()
    bpy.ops.mesh.select_more(use_face_step=True)

    # Убираем оставшиеся вершины
    bpy.ops.mesh.hide(unselected=True)
    bpy.ops.mesh.select_face_by_sides(number=3, type='EQUAL', extend=False)
    bpy.ops.object.vertex_group_deselect()
    bpy.ops.mesh.edge_collapse()

    # Убираем оставшиеся вершины
    bpy.ops.mesh.hide(unselected=True)
    bpy.ops.mesh.select_face_by_sides(number=3, type='EQUAL', extend=False)
    obj.vertex_groups.active_index = 0
    bpy.ops.object.vertex_group_deselect()
    obj.vertex_groups.active_index = 1
    bpy.ops.object.vertex_group_deselect()

    bpy.ops.mesh.edge_collapse()

    bpy.ops.mesh.reveal()
    bpy.ops.mesh.select_all(action='DESELECT')
    obj.vertex_groups.active_index = 2
    bpy.ops.object.vertex_group_select()

    # создаем Bevel
    if self.bevel_segments > 1:
        bevel_segments = self.bevel_segments - 1
        bevel_width = 100 - (200 / (bevel_segments + 3))
        bpy.ops.mesh.bevel(vertex_only=False, offset_type='PERCENT', profile=self.bevel_profile,
                           segments=bevel_segments,
                           clamp_overlap=False, offset_pct=bevel_width)
        

    if self.triangulate:
        bpy.ops.mesh.select_more(use_face_step=True)
        bpy.ops.mesh.select_more(use_face_step=True)
        bpy.ops.object.vertex_group_deselect()
        bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method=self.trmethod)

    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.context.tool_settings.vertex_group_weight = 1.0
    if self.smoothBevel:
        bpy.ops.object.vertex_group_select()
        obj.vertex_groups.new(name="Smooth")
        bpy.ops.object.vertex_group_assign()
        for i in range(self.smooth_bevel_step):
            bpy.context.tool_settings.vertex_group_weight = bpy.context.tool_settings.vertex_group_weight - 1 / self.smooth_bevel_step
            bpy.ops.mesh.select_more(use_face_step=True)
            bpy.ops.object.vertex_group_deselect()
            bpy.ops.object.vertex_group_assign()
        smooth_group = obj.vertex_groups.active.name

    bpy.ops.mesh.select_all(action='DESELECT')
    obj.vertex_groups.active_index = 2
    bpy.ops.object.vertex_group_select()

    bpy.context.tool_settings.vertex_group_weight = 1.0
    bpy.ops.object.mode_set(mode='OBJECT')

    if self.smoothBevel:
        smooth_modifier = obj.modifiers.new(name="Boolean Bevel Smooth", type='SMOOTH')
        smooth_modifier.show_viewport = False
        smooth_modifier.iterations = self.smooth_bevel_value
        smooth_modifier.vertex_group = smooth_group
        # smooth_modifier = src_obj.modifiers.new(name="Boolean Bevel Smooth", type='CORRECTIVE_SMOOTH')
        # smooth_modifier.show_viewport = False
        # smooth_modifier.smooth_type = "LENGTH_WEIGHTED"
        # smooth_modifier.iterations = self.smooth_bevel_value
        # smooth_modifier.use_only_smooth = True
        # smooth_modifier.vertex_group = smooth_group

    if self.transfer:
        data_transfer_modifier = obj.modifiers.new(name="Boolean Bevel Custom Normals", type="DATA_TRANSFER")
        data_transfer_modifier.show_viewport = False
        data_transfer_modifier.object = self.normals_object
        data_transfer_modifier.use_loop_data = True
        data_transfer_modifier.data_types_loops = {"CUSTOM_NORMAL"}
        data_transfer_modifier.loop_mapping = "POLYINTERP_NEAREST"
        data_transfer_modifier.vertex_group = obj.vertex_groups[0].name

        data_transfer_modifier = obj.modifiers.new(name="Boolean Bevel Custom Normals", type="DATA_TRANSFER")
        data_transfer_modifier.show_viewport = False
        data_transfer_modifier.object = self.bool_obj
        data_transfer_modifier.use_loop_data = True
        data_transfer_modifier.data_types_loops = {"CUSTOM_NORMAL"}
        data_transfer_modifier.loop_mapping = "POLYINTERP_NEAREST"
        data_transfer_modifier.vertex_group = obj.vertex_groups[1].name

        if self.operation == "DIFFERENCE" or self.operation == "SLICE":
            vert = self.bool_obj.data
            vert.flip_normals()
            vert.update()

    obj.select_set(True)

    if self.transfer:
        self.bool_obj.select_set(True)
        self.normals_object.select_set(True)
        bpy.ops.object.shade_smooth()

        # включаем автосглаживание
        bpy.context.object.data.use_auto_smooth = True
        bpy.context.object.data.auto_smooth_angle = 3.14159

    # применяем все модификаторы
    for modifier in obj.modifiers:
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=modifier.name)
    obj.vertex_groups.clear()

    bpy.ops.object.select_all(action='DESELECT')

    if self.transfer:
        if self.operation == "DIFFERENCE":
            vert = self.bool_obj.data
            vert.flip_normals()
            vert.update()

    #     normals_object.select_set(True)
    # curve_cut.select_set(True)
    # bpy.data.objects['BOOLEAN_BEVEL_GUIDE'].select_set(True)
    # bpy.ops.object.delete(use_global=False)
    #
    # src_obj.select_set(True)
    # context.view_layer.objects.active = src_obj

    print("Время Create Bevel: %.4f sec\n" % (time.time() - time_start))


classes = (
    BooleanBevelPanel,
    ObjectBooleanBevel,
    ObjectBooleanBevelPipe
)

register, unregister = bpy.utils.register_classes_factory(classes)

# def register():
#     bpy.utils.register_class(BooleanBevelPanel)
#     bpy.utils.register_class(ObjectBooleanBevel)
#
#
# def unregister():
#     bpy.utils.unregister_class(BooleanBevelPanel)
#     bpy.utils.unregister_class(ObjectBooleanBevel)
#     # del bpy.types.WindowManager.bab_props


if __name__ == "__main__":
    register()
