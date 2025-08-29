from .keymaps import TILA_Config_Keymaps_Base

addon_name = "PolyQuilt"
class TILA_Config_Keymaps(TILA_Config_Keymaps_Base):
    addon_name = addon_name

    def __init__(self):
        super().__init__()

    @TILA_Config_Keymaps_Base.print_assigning_keymap()
    def set_keymaps(self):
        if self.kmi_init(name='Mesh', space_type='EMPTY', region_type='WINDOW', addon=False, restore_to_default=False):
            self.kmi_set_replace('wm.tool_set_by_id', 'F', 'PRESS', shift=True, properties={'name': 'mesh_tool.poly_quilt'}, disable_double=True)

        ###### 3D View Tool: Edit Mesh, PolyQuilt
        if self.kmi_init(name='3D View Tool: Edit Mesh, PolyQuilt', space_type='VIEW_3D', region_type='WINDOW', addon=False, restore_to_default=False):
            self.kmi_set_active(False, idname='mesh.poly_quilt', type='LEFTMOUSE', value='PRESS', ctrl=False, shift=False, alt=False, oskey=False)
            self.kmi_set_active(False, idname='mesh.poly_quilt', type='LEFTMOUSE', value='PRESS', ctrl=True, shift=True, alt=False, oskey=False)
            self.kmi_set_active(False, idname='mesh.poly_quilt', type='LEFTMOUSE', value='PRESS', ctrl=True, shift=False, alt=False, oskey=False)
            self.kmi_set_replace('mesh.poly_quilt', self.k_manip, 'PRESS', properties={'tool_mode': 'LOWPOLY'}, disable_double=True)
            self.kmi_set_replace('mesh.poly_quilt', self.k_manip, 'PRESS', shift=True, properties={'tool_mode': 'BRUSH', 'brush_type': 'SMOOTH'})
            self.kmi_set_replace('mesh.poly_quilt', self.k_cursor, 'PRESS', shift=True, properties={'tool_mode': 'BRUSH', 'brush_type': 'MOVE'}, disable_double=True)
            self.kmi_set_replace('mesh.poly_quilt', self.k_manip, 'PRESS', ctrl=True, properties={'tool_mode': 'EXTRUDE'}, disable_double=True)
            self.kmi_set_replace('mesh.poly_quilt', self.k_manip, 'PRESS', ctrl=True, shift=True, properties={'tool_mode': 'EDGELOOP'}, disable_double=True)
            self.kmi_set_replace('mesh.poly_quilt', self.k_cursor, 'PRESS', ctrl=True, properties={'tool_mode': 'KNIFE'}, disable_double=True)
            self.kmi_set_replace('mesh.poly_quilt', self.k_context, 'PRESS', ctrl=True, shift=True, properties={'tool_mode': 'LOOPCUT'}, disable_double=True)
            self.kmi_set_replace('mesh.poly_quilt', self.k_manip, 'PRESS', ctrl=True, alt=True, shift=True, properties={'tool_mode': 'DELETE'}, disable_double=True)
