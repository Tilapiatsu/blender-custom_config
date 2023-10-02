import bpy
from bpy.props import EnumProperty
from bpy.types import Operator


class KePurge(Operator):
    bl_idname = "view3d.ke_purge"
    bl_label = "Purge Unused Data"
    bl_description = "Purge specific unused data blocks\n" \
                     "Note: Deleted meshes will still 'use' materials: Purge meshes first"
    bl_options = {'REGISTER', 'UNDO'}

    block_type: EnumProperty(
        items=[("MESH", "Mesh", "", 1),
               ("MATERIAL", "Materials", "", 2),
               ("TEXTURE", "Textures", "", 3),
               ("IMAGE", "Images", "", 4)],
        name="Purge Data",
        default="MATERIAL")

    def execute(self, context):
        if self.block_type == "MESH":
            for block in bpy.data.meshes:
                if block.users == 0:
                    bpy.data.meshes.remove(block)
        elif self.block_type == "MATERIAL":
            for block in bpy.data.materials:
                if block.users == 0:
                    bpy.data.materials.remove(block)
        elif self.block_type == "TEXTURE":
            for block in bpy.data.textures:
                if block.users == 0:
                    bpy.data.textures.remove(block)
        elif self.block_type == "IMAGE":
            for block in bpy.data.images:
                if block.users == 0:
                    bpy.data.images.remove(block)

        return {'FINISHED'}
