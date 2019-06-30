import bpy


class TILA_action_center(bpy.types.Operator):
    bl_idname = "view3d.tila_action_center"
    bl_label = "Set action center"
    bl_options = {'REGISTER', 'UNDO'}

    action_center = bpy.props.StringProperty(name="Action Center", default='AUTO')
    context = bpy.props.StringProperty(name="context", default='VIEW3D')

    compatible_action_center = ['AUTO',
                                'SELECTION',
                                'SELECTION_BORDER',
                                'SELECTION_CENTER_AUTO_AXIS',
                                'ELEMENT',
                                'VIEW',
                                'ORIGIN',
                                'PARENT',
                                'LOCAL',
                                'PIVOT',
                                'PIVOT_CENTER_PARENT_AXIS',
                                'PIVOT_WORLD_AXIS',
                                'CURSOR',
                                'CUSTOM']



    def run_tool(self, context, event=None):
        try:
            event_type = None if event is None else event.type
            
            if self.action_center == 'AUTO':
                self.report({'INFO'}, 'Automatic Action Center')
                if event_type == 'EVT_TWEAK_R':
                    bpy.ops.view3d.cursor3d('INVOKE_DEFAULT', use_depth=False, orientation='NONE')
                    bpy.ops.transform.translate(snap=True, snap_align=True, cursor_transform=True, release_confirm=True, orient_type='NORMAL')
                context.scene.transform_orientation_slots[0].type = 'GLOBAL'
            if self.action_center == 'SELECTION':
                self.report({'INFO'}, 'Selection Action Center')
                context.scene.transform_orientation_slots[0].type = 'NORMAL'
                context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
            if self.action_center == 'SELECTION_BORDER':
                self.report({'INFO'}, 'Selection Border Action Center')
                context.scene.tool_settings.transform_pivot_point = 'CURSOR'
            if self.action_center == 'SELECTION_CENTER_AUTO_AXIS':
                self.report({'INFO'}, 'Selection Center Auto Axis Action Center')
                context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
                context.scene.transform_orientation_slots[0].type = 'GLOBAL'
            if self.action_center == 'ELEMENT':
                self.report({'INFO'}, 'Element Action Center')
                context.scene.tool_settings.use_snap = True
                context.scene.tool_settings.snap_elements = {'VERTEX', 'EDGE'}
                if event_type == 'EVT_TWEAK_R':
                    bpy.ops.view3d.cursor3d('INVOKE_DEFAULT', use_depth=True, orientation='GEOM')
                    bpy.ops.transform.translate(snap=True, snap_align=True, cursor_transform=True, release_confirm=True, orient_type='NORMAL')
                context.scene.transform_orientation_slots[0].type = 'CURSOR'
                context.scene.tool_settings.transform_pivot_point = 'CURSOR'
                
            if self.action_center == 'VIEW':
                self.report({'INFO'}, 'View Action Center')
                context.scene.transform_orientation_slots[0].type = 'VIEW'
                context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
            if self.action_center == 'ORIGIN':
                self.report({'INFO'}, 'Origin Action Center')
                context.scene.transform_orientation_slots[0].type = 'CURSOR'
                context.scene.tool_settings.transform_pivot_point = 'CURSOR'
                context.scene.cursor.location[0] = 0
                context.scene.cursor.location[1] = 0
                context.scene.cursor.location[2] = 0
                context.scene.cursor.rotation_euler[0] = 0
                context.scene.cursor.rotation_euler[1] = 0
                context.scene.cursor.rotation_euler[2] = 0
            if self.action_center == 'PARENT':
                self.report({'INFO'}, 'Parent Action Center')
                context.scene.transform_orientation_slots[0].type = 'CURSOR'
                context.scene.tool_settings.transform_pivot_point = 'CURSOR'
                parent = context.object if context.object.parent is None else context.object.parent
                context.scene.cursor.location[0] = parent.location[0]
                context.scene.cursor.location[1] = parent.location[1]
                context.scene.cursor.location[2] = parent.location[2]
                context.scene.cursor.rotation_euler[0] = parent.rotation_euler[0]
                context.scene.cursor.rotation_euler[1] = parent.rotation_euler[1]
                context.scene.cursor.rotation_euler[2] = parent.rotation_euler[2]
            if self.action_center == 'LOCAL':
                self.report({'INFO'}, 'Local Action Center')
                context.scene.transform_orientation_slots[0].type = 'NORMAL'
                context.scene.tool_settings.transform_pivot_point = 'INDIVIDUAL_ORIGINS'
            if self.action_center == 'PIVOT':
                self.report({'INFO'}, 'Pivot Action Center')
                context.scene.transform_orientation_slots[0].type = 'LOCAL'
                context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
            if self.action_center == 'PIVOT_CENTER_PARENT_AXIS':
                self.report({'INFO'}, 'Pivot Center Parent Axis Action Center')
                context.scene.transform_orientation_slots[0].type = 'CURSOR'
                context.scene.tool_settings.transform_pivot_point = 'CURSOR'
                parent = context.object if context.object.parent is None else context.object.parent
                context.scene.cursor.location[0] = context.object.location[0]
                context.scene.cursor.location[1] = context.object.location[1]
                context.scene.cursor.location[2] = context.object.location[2]
                context.scene.cursor.rotation_euler[0] = parent.rotation_euler[0]
                context.scene.cursor.rotation_euler[1] = parent.rotation_euler[1]
                context.scene.cursor.rotation_euler[2] = parent.rotation_euler[2]
            if self.action_center == 'PIVOT_WORLD_AXIS':
                self.report({'INFO'}, 'Pivot Wold Axis Action Center')
                context.scene.transform_orientation_slots[0].type = 'GLOBAL'
                context.scene.tool_settings.transform_pivot_point = 'CURSOR'
                context.scene.cursor.location[0] = context.object.location[0]
                context.scene.cursor.location[1] = context.object.location[1]
                context.scene.cursor.location[2] = context.object.location[2]
            if self.action_center == 'CURSOR':
                self.report({'INFO'}, 'Cursor Action Center')
                context.scene.transform_orientation_slots[0].type = 'CURSOR'
                context.scene.tool_settings.transform_pivot_point = 'CURSOR'
            if self.action_center == 'CUSTOM':
                self.report({'INFO'}, 'Custom Action Center')
        except RuntimeError as e:
            print('Runtime Error :\n{}'.format(e))

    def modal(self, context, event):
        if event.type == 'SPACE' and event.value == 'PRESS':
            self.revert_state(context)
            return {'FINISHED'}
        if event.type in {'ESC'}:  # Cancel
            return {'CANCELLED'}
        if event.type == 'EVT_TWEAK_R' and event.value == 'ANY':
            self.run_tool(context, event)
            return {'RUNNING_MODAL'}
        if event.type == 'X' and event.value == 'PRESS' and event.alt and not event.ctrl and not event.shift:
            bpy.ops.wm.call_menu(name='TILA_MT_action_center')
            return {'FINISHED'}
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS' and event.alt and event.ctrl and not event.shift:
            bpy.ops.view3d.zoom('INVOKE_DEFAULT')
            return {'RUNNING_MODAL'}
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS' and event.alt and not event.ctrl and event.shift:
            bpy.ops.view3d.move('INVOKE_DEFAULT')
            return {'RUNNING_MODAL'}
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS' and event.alt and not event.ctrl and not event.shift:
            bpy.ops.view3d.rotate('INVOKE_DEFAULT')
            return {'RUNNING_MODAL'}

        # elif event.type == 'MOUSEMOVE' and event.value == 'RELEASE':
        #     self.run_tool(context, event)
        #     return {'RUNNING_MODAL'}
        return {'RUNNING_MODAL'}

    def execute(self, context):
        if self.action_center in self.compatible_action_center:
            self.report({'INFO'}, 'Action Center {} is compatible'.format(self.action_center))
            self.run_tool(context)
            context.window_manager.modal_handler_add(self)
        else:
            return{'FINISHED'}
        return {'RUNNING_MODAL'}

    def revert_state(self, context):
        context.scene.tool_settings.use_snap = False
        context.scene.tool_settings.snap_elements = set({})

class TILA_MT_action_center(bpy.types.Menu):
    bl_idname = "TILA_MT_action_center"
    bl_label = "Action Center"

    def draw(self, context):
        layout = self.layout
        view = context.space_data
        obj = context.active_object

        # if context.mode == "EDIT_MESH":
        layout.operator("view3d.tila_action_center", icon='ADD', text='Automatic').action_center = 'AUTO'
        layout.operator("view3d.tila_action_center", icon='ADD', text='Selection').action_center = 'SELECTION'
        layout.operator("view3d.tila_action_center", icon='ADD', text='Selection Border').action_center = 'SELECTION_BORDER'
        layout.operator("view3d.tila_action_center", icon='ADD', text='Selection Center Auto Axis').action_center = 'SELECTION_CENTER_AUTO_AXIS'
        layout.operator("view3d.tila_action_center", icon='ADD', text='Element').action_center = 'ELEMENT'
        layout.operator("view3d.tila_action_center", icon='ADD', text='View').action_center = 'VIEW'
        layout.operator("view3d.tila_action_center", icon='ADD', text='Origin').action_center = 'ORIGIN'
        layout.operator("view3d.tila_action_center", icon='ADD', text='Parent').action_center = 'PARENT'
        layout.operator("view3d.tila_action_center", icon='ADD', text='Local').action_center = 'LOCAL'
        layout.operator("view3d.tila_action_center", icon='ADD', text='Pivot').action_center = 'PIVOT'
        layout.operator("view3d.tila_action_center", icon='ADD', text='Pivot Center Parent Axis').action_center = 'PIVOT_CENTER_PARENT_AXIS'
        layout.operator("view3d.tila_action_center", icon='ADD', text='Pivot Wold Axis').action_center = 'PIVOT_WORLD_AXIS'
        layout.operator("view3d.tila_action_center", icon='ADD', text='Cursor').action_center = 'CURSOR'
        layout.operator("view3d.tila_action_center", icon='ADD', text='Custom').action_center = 'CUSTOM'


classes = (
    TILA_action_center,
    TILA_MT_action_center
)
# register, unregister = bpy.utils.register_classes_factory(classes)


def register():
    pass


def unregister():
    pass


if __name__ == "__main__":
    register()