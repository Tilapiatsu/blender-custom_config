bl_info = {
    "name" : "Select Border",
    "author" : "DarkosDK",
    "version" : (1, 0),
    "blender" : (2, 78, 0),
    "location" : "View3D > W > Select Border",
    "description" : "Add to selection all boundary edges linked to active edge. Even if it is not a loop",
    "warning" : "",
    "wiki_url" : "",
    "category" : "Mesh",
    }

import bpy
import bmesh

def find_neighbours_boundary(bm, edge_index):
    vrts = bm.edges[edge_index].verts
    bound_edge = []
    for i in vrts:
        edges = [edge for edge in i.link_edges if edge.is_boundary]
        for d in edges:
            bound_edge.append(d.index)
    bound_edge_arr = set(bound_edge)
    bound_edge = list(bound_edge_arr)
    bound_edge.remove(edge_index)
    return (bound_edge)
    
#operator Select Border
class VIEW3D_MT_edit_mesh_selectborder(bpy.types.Operator):
    """Add to selection all boundary edges linked to active edge"""
    bl_idname = "mesh.select_border"
    bl_label = "Select Border Edges"
    bl_options = {'REGISTER', 'UNDO'}
    
    extend : bpy.props.BoolProperty(name='extend', default=False)
    deselect : bpy.props.BoolProperty(name='deselect', default=False)
 
    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return (ob and context.mode == 'EDIT_MESH' and context.tool_settings.mesh_select_mode[1] == True)
    
    def execute(self, context):
        # Get the active mesh
        obj = bpy.context.edit_object
        me = obj.data
        
        # Get a BMesh representation
        bm = bmesh.from_edit_mesh(me)
        
        self.selected_items = [e.index for e  in bm.select_history]
            
        # check if any element selected
        if len(bm.select_history) == 0:
            self.report({'WARNING'}, 'Select edge')
        else:
            my_edge = bm.select_history.active.index

            border_edges = [my_edge]
            border_check = [my_edge]

            if bm.edges[my_edge].is_boundary:
                i = True
                while i:
                    check_edges = []
                    for j in border_check:
                        arr = find_neighbours_boundary(bm, j)
                        check_edges.extend(arr)
                    new_edges = list(set(check_edges) - set(border_edges))
                    if len(new_edges) == 0:
                        i = False
                    else:
                        border_edges.extend(new_edges)
                        border_check = new_edges

                # print(border_edges)
                
                border_edges += self.selected_items

                for k in border_edges:
                    bm.edges[k].select = not self.deselect
            else:
                self.report({'WARNING'}, 'Select edge is not a boundary edge')#print("Select edge is not a boundary edge")

            # Show the updates in the viewport
            # and recalculate n-gon tessellation.
            bmesh.update_edit_mesh(mesh=me, loop_triangles=True)
            
        
        return {'FINISHED'}
    

classes = (
	VIEW3D_MT_edit_mesh_selectborder,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()



