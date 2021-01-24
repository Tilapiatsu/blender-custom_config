import bpy
import re


class TILA_CopyMirrorVertexGroup(bpy.types.Operator):
    bl_idname = "object.tila_copy_mirror_vertex_group"
    bl_label = "TILA: Copy and Mirror Vertex Group"
    bl_options = {'REGISTER', 'UNDO'}

    left : bpy.props.StringProperty(name='left', default='.L')
    right : bpy.props.StringProperty(name='right', default='.R')
    top : bpy.props.StringProperty(name='top', default='.T')
    bottom : bpy.props.StringProperty(name='bottom', default='.B')
    all_groups : bpy.props.BoolProperty(name='all groups', default=False)
    use_topology : bpy.props.BoolProperty(name='use_topology', default=False)

    def execute(self, context):
        active_vertex_group = context.active_object.vertex_groups.active

        name = active_vertex_group.name

        keyword_pattern = re.compile(r'({0})|({1})|({2})|({3})*([a-zA-Z0-9-_)]+)'.format(self.left, self.right, self.top, self.bottom))
        sliced = keyword_pattern.finditer(name)

        side_couples = {1:(2, self.right),
                        2:(1, self.left),
                        3:(4, self.bottom),
                        4:(3, self.top),
                        5:(5, None)}
                        
        flipped_side = ''

        def append_flipped_name(sliced, number):
            group = sliced.group(number)
            if group is not None:
                if number == 5:
                    new_name = sliced.group(side_couples[number][0])
                else:
                    new_name = side_couples[number][1] if sliced.group(number) is not None else ''
                
            else :
                new_name = ''
            
            return new_name
            
        for w in sliced:
            flipped_side += append_flipped_name(w,1)
            flipped_side += append_flipped_name(w,2)
            flipped_side += append_flipped_name(w,3)
            flipped_side += append_flipped_name(w,4)
            flipped_side += append_flipped_name(w,5)


        bpy.ops.object.vertex_group_copy()
        bpy.ops.object.vertex_group_mirror(mirror_weights=True, flip_group_names=False, all_groups=self.all_groups, use_topology=self.use_topology)
        bpy.context.active_object.vertex_groups.active.name = flipped_side

        return {'FINISHED'}

def menu_draw(self, context):
    self.layout.operator("object.tila_copy_mirror_vertex_group")

bpy.types.MESH_MT_vertex_group_context_menu.append(menu_draw)

classes = (TILA_CopyMirrorVertexGroup,)

register, unregister = bpy.utils.register_classes_factory(classes)


if __name__ == "__main__":
    register()
