import bpy
from .object_handlers import  MeshHandler, GpHandler,LatticeHandler, SoftWidgetHandler, SoftArmatureHandler
from mathutils import Vector

def create_softMod_armature(name,radius, object_handler, active_object,
                            location=[0.0,0.0,0.0], widget_position=[0.0,0.0,0.0]):



    bpyscene = bpy.context.scene
    # ids, weights = influence
    context = bpy.context
    surf_falloff = context.scene.soft_mod.surf_falloff
    influence = object_handler.calculate_map (location , radius , surf_falloff)

    # we need to switch from Edit mode to Object mode so the selection gets updated
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT')
    if active_object.type not in {"MESH", "GPENCIL","LATTICE"}:
        print("Not in range")
        return

    #create or pick the softMod collection
    collection_name = "{}_SoftMods".format(active_object.name)
    softMod_collection = None
    all_collections = bpy.data.collections
    for collection in all_collections:
        if collection.name == collection_name:
            softMod_collection = collection
    if not softMod_collection:
        softMod_collection = bpy.data.collections.new(collection_name)
        bpyscene.collection.children.link(softMod_collection)

    softMod_collection.hide_viewport = False

    # setting the base parameters

    base_map_val = 0.25
    widget_base_scale = (0.75 , 0.75 , 0.75)

    if object_handler.type == "GPENCIL":
        base_map_val = 0.0
        widget_base_scale=(1.0,1.0,1.0)

    widget_size_scale = 25
    widget_size =object_handler.volume/widget_size_scale

    if object_handler.type == "GPENCIL":
        widget_size = widget_size/2

    v_groups_names = [vgroup.name for vgroup in active_object.vertex_groups]
    v_groups = []

    if bpyscene.soft_mod.widget_global_size == 0.0:
        bpyscene.soft_mod.widget_global_size = widget_size


    widget = SoftWidgetHandler.create(name = name,
                                      location=widget_position,
                                      widget_size=widget_size,
                                      collection=softMod_collection,
                                      base_scale=widget_base_scale)
    ############################################################################

    deform_bone_name = '{}_softMod_deform'.format(name)
    i=1
    while deform_bone_name in v_groups_names:
            deform_bone_name=  '{}_softMod_deform.{}'.format(name, str(i).zfill(3))
            i+=1

    armature_def_name = "{}_softMod_deformer".format(name)
    i=1
    existing_modifiers = [mod.name for mod in active_object.modifiers]
    while deform_bone_name in existing_modifiers:
        armature_def_name = '{}_softMod_deform.{}'.format(name, str(i).zfill(3))
        i+=1

    mod = object_handler.add_armature(armature_def_name)
    # TODO: Include this in the classes
    local_bbox_center = 0.125 * sum ((Vector (b) for b in active_object.bound_box) , Vector ())
    mirror_origin = active_object.matrix_world @ local_bbox_center


    softMod_armature = SoftArmatureHandler.create(deform_bone_name, widget.widget, mod,
                                                  widget_position, mirror_origin,softMod_collection)

    softMod_armature.edit_base_bone.head_radius = object_handler.volume * 10
    widget.widget["radius"] = radius
    widget.set_radius_max(object_handler.volume)
    bpy.context.view_layer.objects.active = active_object

    if "softMod_base" not in v_groups_names:
        v_groups.append( object_handler.add_vertex_group ("softMod_base"))

    v_groups.append (object_handler.add_vertex_group (name=softMod_armature.deform_bone.name))

    for v_group in v_groups:
        if v_group.name == "softMod_base":
            object_handler.set_vertex_group_value (v_group , base_map_val)
        else:
            object_handler.set_vertex_group_values(v_group, influence)
            if object_handler.type == "GPENCIL":
                mod.vertex_group =v_group.name

    widget.get_armature()
    widget.smooth_weights(iter=2, factor=1.0, expand=0.1)
    widget.mirror_weights()

    widget.symmetry = False

    for obj in bpy.context.scene.objects:
        obj.select_set (False)
    widget.widget.select_set(True)
    bpy.context.view_layer.objects.active = widget.widget
