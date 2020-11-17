import bpy
import bmesh
import os
from bpy.types import Operator, Panel, Menu
import bpy.utils.previews

def activate():
    if bpy.context.active_object != None:
        #if bpy.context.active_object.select_get():
        return bpy.context.object.type == 'MESH'


class PS_PT_settings_draw_mesh(Panel):
    bl_idname = 'PS_PT_settings_draw_mesh'
    bl_label = 'Draw Mesh Settings'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'

    @classmethod
    def poll(self, context):
        return activate()

    def draw(self, context):
        props = context.preferences.addons[__package__.split(".")[0]].preferences
        settings = context.scene.ps_set_

        layout = self.layout
     

    
        if settings.retopo_mode == False: 
            layout.prop(settings, "retopo_mode", toggle=True)

        else:
            box = layout.box()
            box.prop(settings, "retopo_mode", toggle=True)


            box.prop(props, "verts_size")
            box.prop(props, "edge_width")
            box.prop(props, "z_bias", text="Z-Bias:")
            box.prop(props, "opacity", text="Opacity:")
            box.prop(props, "xray_ret")



        if settings.mesh_check == False: 
            layout.prop(settings, "mesh_check", toggle=True)
                
        else:
            box = layout.box()
            box.prop(settings, "mesh_check", toggle=True)
    
            row = box.row()
            col = row.column()
            col.scale_y = 1.5
            col.prop(props, "v_alone", toggle=True)
            col.prop(props, "v_bound", toggle=True)
            col.prop(props, "e_pole", toggle=True)
            col.prop(props, "n_pole", toggle=True)
            col.prop(props, "f_pole", toggle=True)

            col = row.column()
            col.scale_y = 1.5
            col.prop(props, "tris", toggle=True)
            col.prop(props, "ngone", toggle=True)
            col.prop(props, "non_manifold_check", toggle=True)
            
            box.prop(props, "xray_che")

        layout.prop(props, "max_points")
        layout.prop(context.space_data.overlay, "show_occlude_wire")



        if settings.polycount == False:
            layout.prop(settings, "polycount", toggle=True)
        
        else:
            box = layout.box()
            box.prop(settings, "polycount", toggle=True)
        
            row = box.row(align=True)
            row.prop(settings, "tris_count")
            row.scale_x = 0.4
            row.prop(props, "low_suffix", toggle=True)



def draw_panel(self, context, row):
    props = context.preferences.addons[__package__.split(".")[0]].preferences
    pcoll = preview_collections["main"]

    obj = context.active_object
    
    if context.region.alignment != 'RIGHT':
        if activate():
            
            
            tris = 0
            quad = 0
            ngon = 0
            
            if len(obj.data.vertices) < props.max_points:
                if context.mode != 'EDIT_MESH': 
                    for loop in obj.data.polygons:
                        count = loop.loop_total
                        if count == 3:
                            tris += 1
                        elif count == 4:
                            quad += 1
                        else:
                            ngon += 1 


                else: 
                    bm = bmesh.from_edit_mesh(obj.data)
                    for face in bm.faces:
                        verts = 0
                        for i in face.verts:
                            verts += 1

                        if verts == 3:
                            tris += 1
                        elif verts == 4:
                            quad += 1
                        else:
                            ngon += 1 
            


            

                #bmesh.update_edit_mesh(obj.data) 

                polyNGon = str(ngon)
                polyQuad = str(quad)
                polyTris = str(tris)
                

                
                #layout = self.layout
                #layout.separator()
                #row = layout.row(align=True) 
                #row.alignment='LEFT'
                ngon_icon = pcoll["ngon_icon"] 
                quad_icon = pcoll["quad_icon"]
                tris_icon = pcoll["tris_icon"] 
                
                row.operator("mesh.ps_ngons", text=polyNGon, icon_value=ngon_icon.icon_id)    
                row.operator("mesh.ps_quads", text=polyQuad, icon_value=quad_icon.icon_id)
                row.operator("mesh.ps_tris", text=polyTris, icon_value=tris_icon.icon_id)

            else:
                box = row.box()
                point_max = str(props.max_points)
                box.label(text="Points > " + point_max, icon='ERROR')





def header_panel(self, context):
    props = context.preferences.addons[__package__].preferences

    if activate():
        if props.header == True:
            layout = self.layout
            row = layout.row(align=True) 
            draw_panel(self, context, row)


def viewHeader_L_panel(self, context):
    props = context.preferences.addons[__package__].preferences
    if activate():
        if props.viewHeader_L == True:
            layout = self.layout
            row = layout.row(align=True) 
            draw_panel(self, context, row)
            row.popover(panel='PS_PT_settings_draw_mesh', text="")


def viewHeader_R_panel(self, context):
    props = context.preferences.addons[__package__].preferences
    if activate():
        if props.viewHeader_R == True:
            layout = self.layout
            row = layout.row(align=True) 
            draw_panel(self, context, row)
            row.popover(panel='PS_PT_settings_draw_mesh', text="")





def tool_panel(self, context):
    props = context.preferences.addons[__package__].preferences
    if activate():
        layout = self.layout
        row = layout.row(align=True) 
        """ # Gizmo PRO
        if hasattr(bpy.types, bpy.ops.gizmopro.reset_location_object.idname()):
            draw_panel(self, context, row)
            row.popover(panel='PS_PT_settings_draw_mesh', text="") """

        if props.toolHeader == True:
            draw_panel(self, context, row)
            row.popover(panel='PS_PT_settings_draw_mesh', text="")

        






#OPERATOR
class MESH_OT_ps_ngons(Operator):
    bl_idname = "mesh.ps_ngons"
    bl_label = "NGons"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Number Of NGons. Click To Select"
             
    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH'

    def execute(self, context):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        context.tool_settings.mesh_select_mode=(False, False, True)
        bpy.ops.mesh.select_face_by_sides(number=4, type='GREATER')
        return {'FINISHED'}


class MESH_OT_ps_quads(Operator):
    bl_idname = "mesh.ps_quads"
    bl_label = "Quads"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Number Of Quads. Click To Select"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH'

    def execute(self, context):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        context.tool_settings.mesh_select_mode=(False, False, True)
        bpy.ops.mesh.select_face_by_sides(number=4, type='EQUAL')
        return {'FINISHED'}


class MESH_OT_ps_tris(Operator):
    bl_idname = "mesh.ps_tris"
    bl_label = "Tris"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Number Of Tris. Click To Select"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH'

    def execute(self, context):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        context.tool_settings.mesh_select_mode=(False, False, True)
        bpy.ops.mesh.select_face_by_sides(number=3, type='EQUAL')
        return {'FINISHED'}







preview_collections = {}



classes = [
    PS_PT_settings_draw_mesh,
    MESH_OT_ps_ngons,
    MESH_OT_ps_quads,
    MESH_OT_ps_tris,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    pcoll = bpy.utils.previews.new()
    my_icons_dir = os.path.join(os.path.dirname(__file__), "icons")
    pcoll.load("ngon_icon", os.path.join(my_icons_dir, "ngon.png"), 'IMAGE')
    pcoll.load("quad_icon", os.path.join(my_icons_dir, "quad.png"), 'IMAGE')
    pcoll.load("tris_icon", os.path.join(my_icons_dir, "triangle.png"), 'IMAGE')
    preview_collections["main"] = pcoll

    
    
    bpy.types.TOPBAR_HT_upper_bar.append(header_panel)
    bpy.types.VIEW3D_MT_editor_menus.append(viewHeader_L_panel)
    bpy.types.VIEW3D_HT_header.append(viewHeader_R_panel)
    bpy.types.VIEW3D_HT_tool_header.append(tool_panel)
   

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.types.TOPBAR_HT_upper_bar.remove(header_panel)
    bpy.types.VIEW3D_MT_editor_menus.remove(viewHeader_L_panel)
    bpy.types.VIEW3D_HT_header.remove(viewHeader_R_panel)
    bpy.types.VIEW3D_HT_tool_header.remove(tool_panel)