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

    def run_tool(self, context, event):
        try:
            if self.action_center == 'AUTO':
                self.report({'INFO'}, 'Automatic Action Center')
            if self.action_center == 'SELECTION':
                self.report({'INFO'}, 'Selection Action Center')
            if self.action_center == 'SELECTION_BORDER':
                self.report({'INFO'}, 'Selection Border Action Center')
            if self.action_center == 'SELECTION_CENTER_AUTO_AXIS':
                self.report({'INFO'}, 'Selection Center Auto Axis Action Center')
            if self.action_center == 'ELEMENT':
                self.report({'INFO'}, 'Element Action Center')
            if self.action_center == 'VIEW':
                self.report({'INFO'}, 'View Action Center')
                context.scene.transform_orientation_slots[0].type = 'VIEW'
            if self.action_center == 'ORIGIN':
                self.report({'INFO'}, 'Origin Action Center')
            if self.action_center == 'PARENT':
                self.report({'INFO'}, 'Parent Action Center')
            if self.action_center == 'LOCAL':
                self.report({'INFO'}, 'Local Action Center')
                context.scene.transform_orientation_slots[0].type = 'LOCAL'
            if self.action_center == 'PIVOT_CENTER_PARENT_AXIS':
                self.report({'INFO'}, 'Pivot Center Parent Axis Action Center')
            if self.action_center == 'PIVOT_WORLD_AXIS':
                self.report({'INFO'}, 'Pivot Wold Axis Action Center')
            if self.action_center == 'CURSOR':
                self.report({'INFO'}, 'Cursor Action Center')
            if self.action_center == 'CUSTOM':
                self.report({'INFO'}, 'Custom Action Center')
        except RuntimeError as e:
            print('Runtime Error :\n{}'.format(e))

    def modal(self, context, event):
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            self.run_tool(context, event)
            return {'RUNNING_MODAL'}
        if event.type in {'ESC'}:  # Cancel
            self.run_tool(context, event)
            return {'CANCELLED'}
        elif event.type == 'MOUSEMOVE' and event.value == 'RELEASE':
            self.run_tool(context, event)
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}

    def execute(self, context):
        if self.action_center in self.compatible_action_center:
            self.report({'INFO'}, 'Action Center {} is compatible'.format(self.action_center))
            context.window_manager.modal_handler_add(self)
        else:
            return{'FINISHED'}
        return {'RUNNING_MODAL'}

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