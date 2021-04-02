"""
 * ***** BEGIN GPL LICENSE BLOCK *****
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software Foundation,
 * Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
 *
 * Contributor(s): Julien Duroure.
 *
 * ***** END GPL LICENSE BLOCK *****
 """

import bpy
from mathutils import Quaternion, Matrix

from ..com.gltf2_blender_conversion import *
from ...io.imp.gltf2_io_binary import *

# Version management
from ..blender_version import Version

class BlenderBoneAnim():

    @staticmethod
    def set_interpolation(interpolation, kf):
        if interpolation == "LINEAR":
            kf.interpolation = 'LINEAR'
        elif interpolation == "STEP":
            kf.interpolation = 'CONSTANT'
        elif interpolation == "CATMULLROMSPLINE":
            kf.interpolation = 'BEZIER' #TODO
        elif interpolation == "CUBICSPLINE":
            kf.interpolation = 'BEZIER' #TODO
        else:
            kf.interpolation = 'BEZIER'

    @staticmethod
    def parse_translation_channel(gltf, node, obj, bone, channel, animation):
        fps = bpy.context.scene.render.fps
        blender_path = "location"

        keys   = BinaryData.get_data_from_accessor(gltf, animation.samplers[channel.sampler].input)
        values = BinaryData.get_data_from_accessor(gltf, animation.samplers[channel.sampler].output)
        inv_bind_matrix = Version.mat_mult(
            node.blender_bone_matrix.to_quaternion().to_matrix().to_4x4().inverted(),
            Matrix.Translation(node.blender_bone_matrix.to_translation()).inverted()
        )

        for idx, key in enumerate(keys):
            translation_keyframe = Conversion.loc_gltf_to_blender(values[idx])
            if not node.parent:
                parent_mat = Matrix()
            else:
                if not gltf.data.nodes[node.parent].is_joint: # TODO if Node in another scene
                    parent_mat = bpy.data.objects[gltf.data.nodes[node.parent].blender_object].matrix_world
                else:
                    parent_mat = gltf.data.nodes[node.parent].blender_bone_matrix

            # Pose is in object (armature) space and it's value if the offset from the bind pose (which is also in object space)
            # Scale is not taken into account
            final_trans = Version.mat_mult(parent_mat, Matrix.Translation(translation_keyframe)).to_translation()
            bone.location = Version.mat_mult(inv_bind_matrix, final_trans)
            bone.keyframe_insert(blender_path, frame = key[0] * fps, group="location")

        for fcurve in [curve for curve in obj.animation_data.action.fcurves if curve.group.name == "location"]:
            for kf in fcurve.keyframe_points:
                BlenderBoneAnim.set_interpolation(animation.samplers[channel.sampler].interpolation, kf)

    @staticmethod
    def parse_rotation_channel(gltf, node, obj, bone, channel, animation):
        # Note: some operations lead to issue with quaternions. Converting to matrix and then back to quaternions breaks quaternion continuity
        # (see antipodal quaternions). Blender interpolates between two antipodal quaternions, which causes glitches in animation.
        # Converting to euler and then back to quaternion is a dirty fix preventing this issue in animation, until a better solution is found
        # This fix is skipped when parent matrix is identity
        fps = bpy.context.scene.render.fps
        blender_path = "rotation_quaternion"

        keys   = BinaryData.get_data_from_accessor(gltf, animation.samplers[channel.sampler].input)
        values = BinaryData.get_data_from_accessor(gltf, animation.samplers[channel.sampler].output)
        bind_rotation = node.blender_bone_matrix.to_quaternion()

        for idx, key in enumerate(keys):
            quat_keyframe = Conversion.quaternion_gltf_to_blender(values[idx])
            if not node.parent:
                bone.scale =  Version.mat_mult(bind_scale.inverted(), scale_mat)
            else:
                if not gltf.data.nodes[node.parent].is_joint: # TODO if Node in another scene
                    parent_mat = bpy.data.objects[gltf.data.nodes[node.parent].blender_object].matrix_world
                else:
                    parent_mat = gltf.data.nodes[node.parent].blender_bone_matrix

                if parent_mat != parent_mat.inverted():
                    final_rot = Version.mat_mult(parent_mat, quat_keyframe.to_matrix().to_4x4()).to_quaternion()
                    bone.rotation_quaternion = bind_rotation.rotation_difference(final_rot).to_euler().to_quaternion()
                else:
                    bone.rotation_quaternion = bind_rotation.rotation_difference(quat_keyframe)

            bone.keyframe_insert(blender_path, frame = key[0] * fps, group='rotation')

        for fcurve in [curve for curve in obj.animation_data.action.fcurves if curve.group.name == "rotation"]:
            for kf in fcurve.keyframe_points:
                BlenderBoneAnim.set_interpolation(animation.samplers[channel.sampler].interpolation, kf)

    @staticmethod
    def parse_scale_channel(gltf, node, obj, bone, channel, animation):
        fps = bpy.context.scene.render.fps
        blender_path = "scale"

        keys   = BinaryData.get_data_from_accessor(gltf, animation.samplers[channel.sampler].input)
        values = BinaryData.get_data_from_accessor(gltf, animation.samplers[channel.sampler].output)
        bind_scale = Conversion.scale_to_matrix(node.blender_bone_matrix.to_scale())

        for idx, key in enumerate(keys):
            scale_mat = Conversion.scale_to_matrix(Conversion.loc_gltf_to_blender(values[idx]))
            if not node.parent:
                bone.scale =  Version.mat_mult(bind_scale.inverted(), scale_mat)
            else:
                if not gltf.data.nodes[node.parent].is_joint: # TODO if Node in another scene
                    parent_mat = bpy.data.objects[gltf.data.nodes[node.parent].blender_object].matrix_world
                else:
                    parent_mat = gltf.data.nodes[node.parent].blender_bone_matrix

                bone.scale = Version.mat_mult(bind_scale.inverted(), Version.mat_mult(Conversion.scale_to_matrix(parent_mat.to_scale()), scale_mat) ).to_scale()

            bone.keyframe_insert(blender_path, frame = key[0] * fps, group='scale')

        for fcurve in [curve for curve in obj.animation_data.action.fcurves if curve.group.name == "scale"]:
            for kf in fcurve.keyframe_points:
                BlenderBoneAnim.set_interpolation(animation.samplers[channel.sampler].interpolation, kf)


    @staticmethod
    def anim(gltf, anim_idx, node_idx):
        node  = gltf.data.nodes[node_idx]
        obj   = bpy.data.objects[gltf.data.skins[node.skin_id].blender_armature_name]
        bone  = obj.pose.bones[node.blender_bone_name]
        fps = bpy.context.scene.render.fps

        if anim_idx not in node.animations.keys():
            return

        animation = gltf.data.animations[anim_idx]

        if animation.name:
            name = animation.name + "_" + obj.name
        else:
            name = "Animation_" + str(anim_idx) + "_" + obj.name
        if name not in bpy.data.actions:
            action = bpy.data.actions.new(name)
        else:
            action = bpy.data.actions[name]
        if not obj.animation_data:
            obj.animation_data_create()
        obj.animation_data.action = bpy.data.actions[action.name]

        for channel_idx in node.animations[anim_idx]:
            channel = animation.channels[channel_idx]

            if channel.target.path == "translation":
                BlenderBoneAnim.parse_translation_channel(gltf, node, obj, bone, channel, animation)

            elif channel.target.path == "rotation":
                BlenderBoneAnim.parse_rotation_channel(gltf, node, obj, bone, channel, animation)

            elif channel.target.path == "scale":
                BlenderBoneAnim.parse_scale_channel(gltf, node, obj, bone, channel, animation)
