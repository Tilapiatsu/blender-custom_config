from bpy.types import Menu


class KePieOverlays(Menu):
    bl_label = "keOverlays"
    bl_idname = "VIEW3D_MT_ke_pie_overlays"

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def draw(self, context):
        o = context.space_data.overlay
        s = context.space_data.shading
        cm = context.mode
        op = "view3d.ke_overlays"

        layout = self.layout
        pie = layout.menu_pie()

        c = pie.column()
        cbox = c.box().column()
        cbox.scale_y = 1.15
        cbox.ui_units_x = 7

        if s.show_backface_culling:
            cbox.operator(op, text="Backface Culling", icon="XRAY", depress=True).overlay = "BACKFACE"
        else:
            cbox.operator(op, text="Backface Culling", icon="XRAY",
                          depress=False).overlay = "BACKFACE"

        cbox.separator(factor=0.25)

        row = cbox.row(align=True)
        if o.show_floor:
            row.operator(op, text="Floor", depress=True).overlay = "GRID"
        else:
            row.operator(op, text="Floor", depress=False).overlay = "GRID"

        if o.show_ortho_grid:
            row.operator(op, text="Grid", depress=True).overlay = "GRID_ORTHO"
        else:
            row.operator(op, text="Grid", depress=False).overlay = "GRID_ORTHO"

        row.operator(op, text="Both").overlay = "GRID_BOTH"

        cbox.separator(factor=0.25)

        if o.show_extras:
            cbox.operator(op, text="Extras", icon="LIGHT_SUN", depress=True).overlay = "EXTRAS"
        else:
            cbox.operator(op, text="Extras", icon="LIGHT_SUN", depress=False).overlay = "EXTRAS"

        if o.show_cursor:
            cbox.operator(op, text="Cursor", icon="CURSOR", depress=True).overlay = "CURSOR"
        else:
            cbox.operator(op, text="Cursor", icon="CURSOR", depress=False).overlay = "CURSOR"

        if o.show_object_origins:
            cbox.operator(op, text="Origins", icon="OBJECT_ORIGIN", depress=True).overlay = "ORIGINS"
        else:
            cbox.operator(op, text="Origins", icon="OBJECT_ORIGIN", depress=False).overlay = "ORIGINS"

        if o.show_bones:
            cbox.operator(op, text="Bones", icon="BONE_DATA", depress=True).overlay = "BONES"
        else:
            cbox.operator(op, text="Bones", icon="BONE_DATA", depress=False).overlay = "BONES"

        if o.show_relationship_lines:
            cbox.operator(op, text="Relationship Lines", icon="CON_TRACKTO",
                          depress=True).overlay = "LINES"
        else:
            cbox.operator(op, text="Relationship Lines", icon="CON_TRACKTO",
                          depress=False).overlay = "LINES"

        cbox.separator(factor=0.25)

        if o.show_wireframes:
            cbox.operator(op, text="Object Wireframes", icon="MOD_WIREFRAME",
                          depress=True).overlay = "WIREFRAMES"
        else:
            cbox.operator(op, text="Object Wireframes", icon="MOD_WIREFRAME",
                          depress=False).overlay = "WIREFRAMES"

        if o.show_outline_selected:
            cbox.operator(op, text="Select Outline", icon="MESH_CIRCLE",
                          depress=True).overlay = "OUTLINE"
        else:
            cbox.operator(op, text="Select Outline", icon="MESH_CIRCLE",
                          depress=False).overlay = "OUTLINE"

        if s.show_object_outline:
            cbox.operator(op, text="Object Outline", icon="MESH_CIRCLE",
                          depress=True).overlay = "OBJ_OUTLINE"
        else:
            cbox.operator(op, text="Object Outline", icon="MESH_CIRCLE",
                          depress=False).overlay = "OBJ_OUTLINE"

        c = pie.column()
        cbox = c.box().column()
        cbox.scale_y = 1.15
        cbox.ui_units_x = 7
        if cm == "OBJECT":
            cbox.enabled = False

        if o.show_edge_seams:
            cbox.operator(op, text="Edge Seams", icon="UV_ISLANDSEL", depress=True).overlay = "SEAMS"
        else:
            cbox.operator(op, text="Edge Seams", icon="UV_ISLANDSEL", depress=False).overlay = "SEAMS"

        if o.show_edge_sharp:
            cbox.operator(op, text="Edge Sharp", icon="MESH_CUBE", depress=True).overlay = "SHARP"
        else:
            cbox.operator(op, text="Edge Sharp", icon="MESH_CUBE", depress=False).overlay = "SHARP"

        if o.show_edge_crease:
            cbox.operator(op, text="Edge Crease", icon="META_CUBE", depress=True).overlay = "CREASE"
        else:
            cbox.operator(op, text="Edge Crease", icon="META_CUBE", depress=False).overlay = "CREASE"

        if o.show_edge_bevel_weight:
            cbox.operator(op, text="Edge Bevel Weight", icon="MOD_BEVEL",
                          depress=True).overlay = "BEVEL"
        else:
            cbox.operator(op, text="Edge Bevel Weight", icon="MOD_BEVEL",
                          depress=False).overlay = "BEVEL"

        cbox.separator(factor=0.25)

        if o.show_vertex_normals:
            cbox.operator(op, text="Vertex Normals", icon="NORMALS_VERTEX",
                          depress=True).overlay = "VN"
        else:
            cbox.operator(op, text="Vertex Normals", icon="NORMALS_VERTEX",
                          depress=False).overlay = "VN"

        if o.show_split_normals:
            cbox.operator(op, text="Split Normals", icon="NORMALS_VERTEX_FACE",
                          depress=True).overlay = "SN"
        else:
            cbox.operator(op, text="Split Normals", icon="NORMALS_VERTEX_FACE",
                          depress=False).overlay = "SN"

        if o.show_face_normals:
            cbox.operator(op, text="Face Normals", icon="NORMALS_FACE", depress=True).overlay = "FN"
        else:
            cbox.operator(op, text="Face Normals", icon="NORMALS_FACE", depress=False).overlay = "FN"

        cbox.separator(factor=0.25)

        if o.show_face_orientation:
            cbox.operator(op, text="Face Orientation", icon="FACESEL",
                          depress=True).overlay = "FACEORIENT"
        else:
            cbox.operator(op, text="Face Orientation", icon="FACESEL",
                          depress=False).overlay = "FACEORIENT"

        if o.show_weight:
            cbox.operator(op, text="Vertex Weights", icon="GROUP_VERTEX",
                          depress=True).overlay = "WEIGHT"
        else:
            cbox.operator(op, text="Vertex Weights", icon="GROUP_VERTEX",
                          depress=False).overlay = "WEIGHT"

        cbox.separator(factor=0.25)

        row = cbox.row(align=True)
        if o.show_extra_indices:
            row.operator(op, text="Indices", depress=True).overlay = "INDICES"
        else:
            row.operator(op, text="Indices",
                         depress=False).overlay = "INDICES"

        row.separator(factor=0.1)

        if o.show_extra_edge_length:
            row.operator(op, text="Edge Lengths", depress=True).overlay = "LENGTHS"
        else:
            row.operator(op, text="Edge Lengths",
                         depress=False).overlay = "LENGTHS"

        c = pie.column()
        c.separator(factor=4)
        cbox = c.box().column()
        cbox.scale_y = 1.15
        cbox.ui_units_x = 7
        cbox.use_property_split = False

        obj = context.object
        if obj:
            obj_type = obj.type
            is_geometry = (obj_type in {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'VOLUME', 'HAIR', 'POINTCLOUD'})
            has_bounds = (is_geometry or obj_type in {'LATTICE', 'ARMATURE'})
            is_wire = (obj_type in {'CAMERA', 'EMPTY'})
            is_dupli = (obj.instance_type != 'NONE')

            col = cbox.column(align=True)
            row = col.row()
            if o.show_stats:
                row.operator(op, text="Stats", icon="LINENUMBERS_ON", depress=True).overlay = "STATS"
            else:
                row.operator(op, text="Stats", icon="LINENUMBERS_ON", depress=False).overlay = "STATS"
            row = col.row()
            row.scale_y = 0.8
            row.enabled = False
            row.label(text="Show Active Object:")
            col.prop(obj, "show_name", text="Name")
            col.prop(obj, "show_axis", text="Axis")

            if is_geometry or is_dupli:
                col.prop(obj, "show_wire", text="Wireframe")
            if obj_type == 'MESH' or is_dupli:
                col.prop(obj, "show_all_edges", text="All Edges")
            if is_geometry:
                col.prop(obj, "show_texture_space", text="Texture Space")
                col.prop(obj.display, "show_shadows", text="Shadow")
            col.prop(obj, "show_in_front", text="In Front")

            if has_bounds:
                col.prop(obj, "show_bounds")

            sub = col.row(align=True)
            if is_wire:
                # wire objects only use the max. display type for duplis
                sub.active = is_dupli

            if has_bounds:
                sub.prop(obj, "display_bounds_type", text="")
            sub.prop(obj, "display_type", text="")
        else:
            col = cbox.column()
            col.enabled = False
            col.label(text="No Active Object")

        c = pie.column()
        cbox = c.box().row(align=True)
        cbox.scale_y = 1.2
        cbox.operator(op, text="All Overlays", icon="OVERLAY").overlay = "ALL"
        cbox.operator(op, text="All Edge Overlays", icon="UV_EDGESEL").overlay = "ALLEDIT"
        c.separator(factor=7)
