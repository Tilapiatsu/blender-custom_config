import os.path
import bpy
from datetime import datetime
try:
    from BakeWrangler.nodes import node_tree
    from BakeWrangler.nodes.node_tree import _print
    from BakeWrangler.nodes.node_tree import material_recursor
    from BakeWrangler.nodes.node_tree import follow_input_link
    from BakeWrangler.nodes.node_tree import gather_output_links
except:
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from nodes import node_tree
    from nodes.node_tree import _print
    from nodes.node_tree import material_recursor
    from nodes.node_tree import follow_input_link
    from nodes.node_tree import gather_output_links



# Information needed to create a desired output
class bake_solution():
    def __init__(self, output_node):
        self.node = output_node
        self.name = output_node.name
        self.passed = {}    # 'Pass Node Name': [bake, mask]
        self.inputs = {}    # 'Output Channel': ['Input Channel', Pass Node]



# Process the node tree with the given node as the starting point
def process_tree(tree_name, node_name):
    # Create a base scene to work from that has every object in it
    global base_scene
    global mesh_scene
    global active_scene
    base_scene = bpy.data.scenes.new("BakeWrangler_Base")
    mesh_scene = bpy.data.scenes.new("BakeWrangler_Mesh")
    active_scene = bpy.context.window.scene
    bpy.context.window.scene = base_scene
    # For now use active scenes current animation frame (maybe more advanced options later)
    base_scene.frame_current = active_scene.frame_current
    for obj in bpy.data.objects:
        base_scene.collection.objects.link(obj)
    # Add a property on objects that can link to a copy made
    bpy.types.Object.bw_copy = bpy.props.PointerProperty(name="Object Copy", description="Copy with modifiers applied", type=bpy.types.Object)
    
    # Get tree position
    tree = bpy.data.node_groups[tree_name]
    node = tree.nodes[node_name]
    err = False
    bakes = {}
    
    if debug: _print("> Debugging output enabled", tag=True)
    
    # Pack tree based on starting node point
    if node.bl_idname == 'BakeWrangler_Bake_Pass':
        # Add all valid outputs
        for output in node.outputs:
            if output.is_linked:
                for link in gather_output_links(output):
                    if link.to_socket.valid:
                        if link.to_node.name not in bakes.keys():
                            bakes[link.to_node.name] = bake_solution(link.to_node)
                        bakes[link.to_node.name].inputs[link.to_socket.name] = [output.name, node]
    else:
        if node.bl_idname == 'BakeWrangler_Output_Image_Path':
            # Just add this output
            bakes[node.name] = bake_solution(node)
        elif node.bl_idname == 'BakeWrangler_Output_Batch_Bake':
            # Add all connected valid inputs
            for input in node.inputs:
                if input.islinked() and input.valid and follow_input_link(input.links[0]).from_node.name not in bakes.keys():
                    bakes[follow_input_link(input.links[0]).from_node.name] = bake_solution(follow_input_link(input.links[0]).from_node)
        else:
            _print("> Invalid bake tree starting node", tag=True)
            return True
        # Add passes to their group(s)
        for bake in bakes.keys():
            # All valid inputs should be in this outputs group
            for input in bakes[bake].node.inputs:
                if input.islinked() and input.valid:
                    bakes[bake].inputs[input.name] = [follow_input_link(input.links[0]).from_socket.name, follow_input_link(input.links[0]).from_node]
                
    # Perform passes needed for each output group
    _print("> Processing [%s]: Creating %i images" % (node.get_name(), len(bakes.keys())), tag=True)
    _print(">", tag=True)
    error = 0
    for bake in bakes.keys():
        solution = bakes[bake]
        node = solution.node
        output_format = node.get_format()
        _print("> Output: [%s]" % (node.name_with_ext()), tag=True)
        clear_image(solution)
        for chan in solution.inputs.keys():
            data = solution.inputs[chan]
            if data[1].name not in solution.passed.keys():
                _print(">  Pass: [%s] " % (data[1].get_name()), tag=True, wrap=False)
                err, img_bake, img_mask = process_bake_pass_input(data[1], output_format)
                # Don't process a bake that returned an error
                if not err:
                    solution.passed[data[1].name] = [img_bake, img_mask]
                else:
                    solution.passed[data[1].name] = [None, None]
            if savepass:
                # Save output after each pass
                imgs = solution.passed[data[1].name]
                #err += process_bake_pass_output(node, imgs[0], imgs[1], output_format, data[0], chan)
                err += process_solution(solution, output_format, channel=chan)
            if err:
                error += err
        if not savepass:
            # Save output only after all passes
            error += process_solution(solution, output_format)
        _print(">", tag=True)
    return error
            
            
    
# Takes a bake pass node and returns the baked image and baked mask
def process_bake_pass_input(node, format):
    err = False
    
    # Gather pass settings
    bake_mesh = []
    img_bake = None
    img_mask = None
    bake_dev = node.bake_device
    bake_samp = node.bake_samples
    use_mask = node.use_mask
    bake_type = node.bake_pass
    bake_settings = {}
    bake_settings["x_res"] = node.bake_xres
    bake_settings["y_res"] = node.bake_yres
    bake_settings["node_name"] = node.get_name()
    # Settings for normal pass
    bake_settings["norm_s"] = node.norm_space
    bake_settings["norm_r"] = node.norm_R
    bake_settings["norm_g"] = node.norm_G
    bake_settings["norm_b"] = node.norm_B
    # Settings for multiresolution pass
    bake_settings["multi_pass"] = node.multi_pass
    bake_settings["multi_samp"] = node.multi_samp
    bake_settings["multi_targ"] = node.multi_targ
    bake_settings["multi_sorc"] = node.multi_sorc
    # Settings for curvature pass
    bake_settings["curve_val"] = node.curve_val
    # Settings for cavity pass
    bake_settings["cavity_samp"] = node.cavity_samp
    bake_settings["cavity_dist"] = node.cavity_dist
    bake_settings["cavity_gamma"] = node.cavity_gamma
    # Settings for passes with selectable influence
    infl_direct = node.use_direct
    infl_indirect = node.use_indirect
    infl_color = node.use_color
    # Settings for what to combine in combined pass
    comb_diffuse = node.use_diffuse
    comb_glossy = node.use_glossy
    comb_trans = node.use_transmission
    comb_subsurf = node.use_subsurface
    comb_ao = node.use_ao
    comb_emit = node.use_emit
    # Settings related to World and render
    use_world = node.use_world
    the_world = node.the_world
    cpy_render = node.cpy_render
    cpy_from = node.cpy_from
    
    # Set up the pass influences if the bake uses them
    bake_settings["pass_influences"] = set()
    if bake_type in node.bake_has_influence:
        if infl_direct:
            bake_settings["pass_influences"].add('DIRECT')
        if infl_indirect:
            bake_settings["pass_influences"].add('INDIRECT')
        if infl_color:
            bake_settings["pass_influences"].add('COLOR')
        if bake_type == 'COMBINED':
            if comb_diffuse:
                bake_settings["pass_influences"].add('DIFFUSE')
            if comb_glossy:
                bake_settings["pass_influences"].add('GLOSSY')
            if comb_trans:
                bake_settings["pass_influences"].add('TRANSMISSION')
            if comb_subsurf:
                bake_settings["pass_influences"].add('SUBSURFACE')
            if comb_ao:
                bake_settings["pass_influences"].add('AO')
            if comb_emit:
                bake_settings["pass_influences"].add('EMIT')
                
    # Get bake mesh inputs
    inputs = node.inputs
    for input in inputs:
        if input.islinked() and input.valid:
            if not bake_mesh.count(follow_input_link(input.links[0]).from_node):
                bake_mesh.append(follow_input_link(input.links[0]).from_node)
    
    _print(" [Mesh Nodes (%i)]" % (len(bake_mesh)), tag=True)
    
    # Generate the bake and mask images
    img_bake = bpy.data.images.new(node.get_name(), width=bake_settings["x_res"], height=bake_settings["y_res"])
    img_bake.alpha_mode = 'NONE'
    if format["img_use_float"]:
        img_bake.use_generated_float = True
    img_bake.colorspace_settings.name = format['img_color_space']
    if bake_type in ['NORMAL', 'CURVATURE'] or (bake_type == 'MULTIRES' and bake_settings["multi_pass"] == 'NORMALS'):
        img_bake.generated_color = (0.5, 0.5, 1.0, 1.0)
    
    if use_mask:
        img_mask = bpy.data.images.new("mask_" + node.get_name(), width=bake_settings["x_res"], height=bake_settings["y_res"])
        img_mask.alpha_mode = 'NONE'
        img_mask.colorspace_settings.name = 'Non-Color'
        img_mask.colorspace_settings.is_data = True
    
    # Begin processing bake meshes
    for mesh in bake_mesh:
        active_meshes = mesh.get_objects('TARGET')
        selected_objs = mesh.get_objects('SOURCE')
        scene_objs = mesh.get_objects('SCENE')
        
        _print(">   Mesh: [%s] [Targets (%i)]" % (mesh.get_name(), len(active_meshes)), tag=True)
        # Gather settings for this mesh. Validation should have been done before this script was ever run
        # so all settings will be assumed valid.
        bake_settings["margin"] = mesh.margin
        bake_settings["padding"] = mesh.mask_margin
        multi = (bake_type == 'MULTIRES')
        multi_pass = bake_settings["multi_pass"]
        bake_settings["ray_dist"] = mesh.ray_dist
        bake_settings["mesh_name"] = mesh.get_name()
        
        # Process each active mesh
        for active in active_meshes:
            # Load in template bake scene with mostly optimized settings for baking
            bake_scene_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources", "BakeWrangler_Scene.blend")
            with bpy.data.libraries.load(bake_scene_path, link=False, relative=False) as (file_from, file_to):
                file_to.scenes.append("BakeWrangler")
            bake_scene = file_to.scenes[0]
            bake_scene.name = "bake_" + node.get_name() + "_" + mesh.get_name() + "_" + active[0].name
            
            # Copy render settings if required
            if cpy_render:
                if cpy_from in [None, ""]:
                    cpy_from = active_scene
                copy_render_settings(cpy_from, bake_scene)
            
            # Set the device and sample count to override anything that could have been copied
            bake_scene.cycles.device = bake_dev
            bake_scene.cycles.samples = bake_samp
            bake_scene.cycles.aa_samples = bake_samp
            
            # Set custom world instead of default if enabled
            if use_world:
                if the_world not in [None, ""]:
                    bake_scene.world = the_world
                else:
                    bake_scene.world = active_scene.world
                        
            # Determine what strategy to use for this bake
            bake_settings["cage"] = False
            bake_settings["cage_object"] = None
            bake_settings["cage_obj_name"] = ""
            to_active = False
            selected = None
            if not multi:
                for obj in selected_objs:
                    # Let a duplicate of the target object count if they use different UV Maps
                    if obj[0] != active[0] or (len(obj) > 1 and len(active) > 1 and obj[1] != active[1]):
                        to_active = True
                        break
                # Copy all selected objects over if 'to active' pass
                if to_active:
                    selected = bpy.data.collections.new("Selected_" + active[0].name)
                    for obj in selected_objs:
                        # Let a duplicate of the target object in if they use different UV Maps
                        if obj[0] != active[0] or (len(obj) > 1 and len(active) > 1 and obj[1] != active[1]):
                            prep_object_for_bake(obj[0])
                            copy = obj[0].bw_copy.copy()
                            copy.data = obj[0].bw_copy.data.copy()
                            selected.objects.link(copy)
                            # Set UV map to use if one was selected
                            if len(obj) > 1 and obj[1] not in [None, ""]:
                                copy.data.uv_layers.active = copy.data.uv_layers[obj[1]]
                    bake_scene.collection.children.link(selected)
                    # Add the cage copy to the scene because it doesn't work properly in a different scene currently
                    if len(active) > 2 and active[2]:
                        bake_settings["cage"] = True
                        prep_object_for_bake(active[2])
                        bake_settings["cage_object"] = active[2].bw_copy.copy()
                        bake_settings["cage_object"].data = active[2].bw_copy.data.copy()
                        bake_settings["cage_obj_name"] = bake_settings["cage_object"].name
            else:
                # Collection of base objects for multi-res to link into
                base_col = bpy.data.collections.new("Base_" + active[0].name)
                bake_scene.collection.children.link(base_col)
                
            # Regardless of strategy the following data will be used. Copies are made so other passes can get the originals
            active_obj = active[0]
            if not multi:
                prep_object_for_bake(active[0])
                active_obj = active[0].bw_copy
            target = active_obj.copy()
            target.data = active_obj.data.copy()

            # Set UV map to use if one was selected
            if len(active) > 1 and active[1] not in [None, ""]:
                target.data.uv_layers.active = target.data.uv_layers[active[1]]
            
            # Materials should be removed from the target copy for To active
            if to_active:
                target.data.materials.clear()
                target.data.polygons.foreach_set('material_index', [0] * len(target.data.polygons))
                target.data.update()
            # Add target before doing mats
            else:
                bake_scene.collection.objects.link(target)
                
            # Create unique copies for every material in the scene before anything else is done
            unique_mats = make_materials_unique_to_scene(bake_scene, node.get_name() + "_" + mesh.get_name() + "_" + active[0].name, bake_type, bake_settings)
            
            # Add target after doing mats
            if to_active:
                bake_scene.collection.objects.link(target)
                
            # Copy all scene objects over if not a multi-res pass
            if not multi:
                scene = bpy.data.collections.new("Scene_" + active[0].name)
                for obj in scene_objs:
                    copy = obj[0].copy()
                    copy.data = obj[0].data.copy()
                    scene.objects.link(copy)
                bake_scene.collection.children.link(scene)
                # Add cage object
                if bake_settings["cage"]:
                    bake_scene.collection.objects.link(bake_settings["cage_object"])
              
            # Switch into bake scene
            bpy.context.window.scene = bake_scene
                
            # Select the target and make it active
            bpy.ops.object.select_all(action='DESELECT')
            target.select_set(True)
            bpy.context.view_layer.objects.active = target
            
            # Perform bake type needed
            if multi:
                err = bake_multi_res(img_bake, multi_pass, unique_mats, bake_settings, base_col, target, active_obj)
            elif to_active:
                err = bake_to_active(img_bake, bake_type, unique_mats, bake_settings, selected)
            else:
                err = bake_solo(img_bake, bake_type, unique_mats, bake_settings)
                
            # Bake the mask if samples are non zero
            if use_mask:
                # Set samples to the mask value
                bake_scene.cycles.device = bake_dev
                bake_scene.cycles.samples = 1
                bake_scene.cycles.aa_samples = 1
                err += bake_mask(img_mask, unique_mats, bake_settings, to_active, target, selected)
            
            # Switch back to main scene before next pass. Nothing will be deleted so that the file can be examined for debugging.
            bpy.context.window.scene = base_scene
    
    # Perform addition actions on baked data if required
    if bake_type in ['CURVATURE', 'SMOOTHNESS']:
        perr, img_bake = bake_post(img_bake, bake_type, bake_settings, format)
        err += perr
    
    # Finished inputs, return the bakes
    return [err, img_bake, img_mask]



# Takes an output node along with a bake and optional mask which are composited and saved
def process_bake_pass_output(node, bake, mask, format, in_chan, out_chan):
    err = False
   
    output_size = [node.img_xres, node.img_yres]
    output_path = node.img_path
    output_name = node.name_with_ext()
    output_file = os.path.join(os.path.realpath(output_path), output_name)
    
    orig_image = None
    orig_exists = False
    mux_image = bpy.data.images.new(bake.name + "_MUX", width=output_size[0], height=output_size[1])
    
    # Store the output plane and mixer material, etc in case they are required
    output_mux = output_scene.objects["BW_Channel_MUX"]
    output_mat = output_mux.material_slots[0].material.node_tree.nodes
    output_lnx = output_mux.material_slots[0].material.node_tree.links
    out_text = output_mat["bw_output_texture"]
    mux_mask = output_mat["bw_mask_img"]
    mux_orig = output_mat["bw_orig_img"]
    mux_bake = output_mat["bw_bake_img"]
    rgb_orig = output_mat["bw_orig_rgb"].outputs
    rgb_bake = output_mat["bw_bake_rgb"].outputs
    rgb_outp = output_mat["bw_out_rgb"].inputs
    val_bake = output_mat["bw_col_to_value"].outputs[0]
    def_mask = bpy.data.images["bw_default_masked"]
    def_orig = bpy.data.images["bw_default_orig"]
    
    # See if the output exists or if a new file should be created
    if os.path.exists(output_file):
        # Open it
        _print(">   -Loading existing file", tag=True)
        orig_image = bpy.data.images.load(os.path.abspath(output_file))
        orig_exists = True
    else:
        # Create it
        _print(">   -Creating new file", tag=True)
        orig_image = def_orig
    
    # Set format
    orig_image.alpha_mode = 'STRAIGHT'
    orig_image.file_format = format["img_type"]
    orig_image.colorspace_settings.name = format["img_color_space"]
    orig_image.colorspace_settings.is_data = bake.colorspace_settings.is_data
    
    mux_image.alpha_mode = 'STRAIGHT'
    mux_image.file_format = format["img_type"]
    mux_image.colorspace_settings.name = format["img_color_space"]
    mux_image.colorspace_settings.is_data = bake.colorspace_settings.is_data
    mux_image.use_generated_float = bake.use_generated_float
    
    # Scale all images to match
    bake.scale(output_size[0], output_size[1])
    orig_image.scale(output_size[0], output_size[1])
    if mask:
        mask.scale(output_size[0], output_size[1])
    if debug: _print(">    Loaded image: %i x %i, %i channels, %i bpp, %i px (%i values)" % (orig_image.size[0], orig_image.size[1], orig_image.channels, orig_image.depth, len(orig_image.pixels) / orig_image.channels, len(orig_image.pixels)), tag=True)
    if debug: _print(">    Baked  image: %i x %i, %i channels, %i bpp, %i px (%i values)" % (bake.size[0], bake.size[1], bake.channels, bake.depth, len(bake.pixels) / bake.channels, len(bake.pixels)), tag=True)
    
    # Switch into output scene and apply output format
    bpy.context.window.scene = output_scene
    apply_output_format(output_scene.render.image_settings, format)
    
    # Set up default mix
    out_text.image = mux_image
    mux_orig.image = orig_image
    mux_bake.image = bake
    mux_mask.image = def_mask
    if mask:
        mux_mask.image = mask
    for input in rgb_outp:
        links = []
        for link in input.links:
            links.append(link)
        for link in links:
            output_lnx.remove(link)
    output_lnx.new(rgb_outp["R"], rgb_orig["R"])
    output_lnx.new(rgb_outp["G"], rgb_orig["G"])
    output_lnx.new(rgb_outp["B"], rgb_orig["B"])
    
    # Determine how and if channels should be mixed
    mux_output = True
    if in_chan == "Color" and out_chan == "Color":
        # No mixing, but there could still be a mask
        if mask:
            output_lnx.new(rgb_outp["R"], rgb_bake["R"])
            output_lnx.new(rgb_outp["G"], rgb_bake["G"])
            output_lnx.new(rgb_outp["B"], rgb_bake["B"])
        else:
            # Skip mixing step
            mux_output = False
    # Any other combination will require some mixing
    elif in_chan == "Color" and out_chan in ["R", "G", "B"]:
        output_lnx.new(rgb_outp[out_chan], rgb_bake[out_chan])
    elif out_chan == "Color" and in_chan in ["R", "G", "B", "Value"]:
        if in_chan == "Value":
            output_lnx.new(rgb_outp["R"], val_bake)
            output_lnx.new(rgb_outp["G"], val_bake)
            output_lnx.new(rgb_outp["B"], val_bake)
        else:
            output_lnx.new(rgb_outp[in_chan], rgb_bake[in_chan])
    elif out_chan in ["R", "G", "B"]:
        if in_chan == "Value":
            output_lnx.new(rgb_outp[out_chan], val_bake)
        else:
            output_lnx.new(rgb_outp[out_chan], rgb_bake[in_chan])
    else:
        # No mixing, at least not of RGB and Alpha will be done later
        mux_output = False
    
    # Material should be set up for channel mixing and masking, set the scene and bake it to output
    if mux_output:
        start = datetime.now()
        _print(">   -Mixing image channels and/or mask: ", tag=True, wrap=False)
        bpy.ops.object.select_all(action='DESELECT')
        output_mux.select_set(True)
        bpy.context.view_layer.objects.active = output_mux
        bpy.context.view_layer.update()
        err = False
        try:
            bpy.ops.object.bake(
                type="EMIT",
                save_mode='INTERNAL',
                use_clear=False,
            )
        except RuntimeError as error:
            _print("%s" % (error), tag=True)
            err = True
        else:
            _print("Completed in %s" % (str(datetime.now() - start)), tag=True)
    else:
        # Just copy pixels
        if len(mux_image.pixels) == len(bake.pixels):
            if out_chan == "Color":
                mux_image.pixels = bake.pixels[:]
            elif orig_exists:
                mux_image.pixels = orig_image.pixels[:]
            mux_image.update()
        else:
            _print(">   -Copying pixels to output: Input/Output pixel count mismatch", tag=True)
            err = True
        
    # Check if an alpha pass needs to be done
    if (format["img_type"] not in ['BMP', 'JPEG', 'CINEON', 'HDR'] and format["img_color_mode"] == 'RGBA') and (orig_exists or out_chan == "A"):
        # Because of issues using the compositor and the fact that bakes can't write an alpha channel,
        # this has to be done in python by directly changing pixel values. Which is slow, and more slower
        # the more pixels in the image.
        start = datetime.now()
        _print(">   -Creating alpha channel: ", tag=True, wrap=False)
        aerr = alpha_pass(in_chan, out_chan, bake, mask, orig_image, mux_image)
        if not aerr:
            _print("Completed in %s" % (str(datetime.now() - start)), tag=True)
        else:
            err = True
    
    # Save the image to disk
    _print(">   -Writing changes to %s" % (output_file), tag=True)
    mux_image.save_render(output_file, scene=output_scene)
    return err



# Create and save output of a solution
def process_solution(solution, format, channel=None):
    err = False
    if channel == "A" and (format["img_type"] in ['BMP', 'JPEG', 'CINEON', 'HDR'] or format["img_color_mode"] != 'RGBA'):
        # Nothing to do for alpha input if image doesn't support alpha
        return err
   
    output_size = [solution.node.img_xres, solution.node.img_yres]
    output_path = solution.node.img_path
    output_name = solution.node.name_with_ext()
    output_file = os.path.join(os.path.realpath(output_path), output_name)
    
    orig_image = None
    orig_exists = False
    mux_image = bpy.data.images.new(solution.name + "_MUX", width=output_size[0], height=output_size[1])
    
    # Store the output plane and mixer material values
    output_mux = output_scene.objects["BW_Channel_MUX"]
    output_mat = output_mux.material_slots[0].material.node_tree.nodes
    output_lnx = output_mux.material_slots[0].material.node_tree.links
    
    # Store output node points in variables
    out_col = {"R": output_mat["R_Color_bw_output"].inputs["R"],
               "G": output_mat["G_Color_bw_output"].inputs["G"],
               "B": output_mat["B_Color_bw_output"].inputs["B"],}
    out_rgb = {"R": output_mat["R_bw_output"].inputs["R"],
               "G": output_mat["G_bw_output"].inputs["G"],
               "B": output_mat["B_bw_output"].inputs["B"],}
    
    # Default blank images when they don't exist
    def_masked = bpy.data.images["bw_default_masked"]
    def_unmask = bpy.data.images["bw_default_unmask"]
    def_orig = bpy.data.images["bw_default_orig"]
    def_orig.use_generated_float = format["img_use_float"]
    
    # See if the output exists or if a new file should be created
    if os.path.exists(output_file):
        # Open it
        _print(">  -Loading existing file", tag=True)
        orig_image = bpy.data.images.load(os.path.abspath(output_file))
        orig_exists = True
    else:
        # Create it
        _print(">  -Creating new file", tag=True)
        orig_image = def_orig
    
    # Set format
    orig_image.alpha_mode = 'STRAIGHT'
    orig_image.file_format = format["img_type"]
    orig_image.colorspace_settings.name = format["img_color_space"]
    
    mux_image.alpha_mode = 'STRAIGHT'
    mux_image.file_format = format["img_type"]
    mux_image.colorspace_settings.name = format["img_color_space"]
    mux_image.use_generated_float = format["img_use_float"]
    
    # Scale all images to match
    orig_image.scale(output_size[0], output_size[1])
    for pass_node in solution.passed.keys():
        for img in solution.passed[pass_node]:
            if img:
                img.scale(output_size[0], output_size[1])
                
    # Switch into output scene and apply output format
    bpy.context.window.scene = output_scene
    apply_output_format(output_scene.render.image_settings, format)
    
    # Set baseline output
    for chan in ["R", "G", "B"]:
        in_rgb = output_mat["Color_bw_rgb"].outputs
        output_lnx.new(in_rgb[chan], out_col[chan])
    
    # Configure output from solution
    output_mat["bw_orig_img"].image = orig_image
    output_mat["bw_output_texture"].image = mux_image
    has_mix = False
    for out_chan in ["Color", "R", "G", "B"]:
        tex_bake = output_mat[out_chan + "_bw_bake_img"]
        tex_mask = output_mat[out_chan + "_bw_mask_img"]
        if out_chan in solution.inputs.keys() and (channel == None or channel == out_chan):
            has_mix = True
            
            # Get solution data
            data = solution.inputs[out_chan]
            in_chan = data[0]
            images = solution.passed[data[1].name]
            bake = images[0]
            mask = images[1]
            
            if bake == None:
                bake = def_orig
                mask = def_unmask
            elif mask == None:
                mask = def_masked
                
            # Get nodes
            in_rgb = output_mat[out_chan + "_bw_rgb"].outputs
            in_val = output_mat[out_chan + "_bw_value"].outputs[0]
            output = out_rgb
            if out_chan == "Color":
                output = out_col
            
            # Set images and link nodes
            tex_bake.image = bake
            tex_mask.image = mask
            if in_chan == "Color":
                if out_chan == "Color":
                    for chan in ["R", "G", "B"]:
                        output_lnx.new(in_rgb[chan], output[chan])
                else:
                    output_lnx.new(in_rgb[out_chan], output[out_chan])
            elif in_chan == "Value":
                if out_chan == "Color":
                    for chan in ["R", "G", "B"]:
                        output_lnx.new(in_val, output[chan])
                else:
                    output_lnx.new(in_val, output[out_chan])
            else:
                if out_chan == "Color":
                    for chan in ["R", "G", "B"]:
                        output_lnx.new(in_rgb[in_chan], output[chan])
                else:
                    output_lnx.new(in_rgb[in_chan], output[out_chan])
        else:
            # Unused channels shouldn't contribute anything
            tex_bake.image = def_orig
            tex_mask.image = def_unmask
    
    # Generate final image sans alpha
    if has_mix:
        start = datetime.now()
        err = False
        _print(">  -Mixing image channels and/or mask: ", tag=True, wrap=False)
        try:
            bpy.ops.object.bake(
                type="EMIT",
                save_mode='INTERNAL',
                use_clear=False,
            )
        except RuntimeError as error:
            _print("%s" % (error), tag=True)
            err = True
        else:
            _print("Completed in %s" % (str(datetime.now() - start)), tag=True)
    else:
        # Just copy pixels
        if orig_exists and len(mux_image.pixels) == len(orig_image.pixels):
            mux_image.pixels = orig_image.pixels[:]
            mux_image.update()
        else:
            _print(">  -Copying pixels to output: Input/Output pixel count mismatch", tag=True)
            err = True
        
    # Add alpha pass if required
    if (format["img_type"] not in ['BMP', 'JPEG', 'CINEON', 'HDR'] and format["img_color_mode"] == 'RGBA') and (orig_exists or "A" in solution.inputs.keys()):
        # Because of issues using the compositor and the fact that bakes can't write an alpha channel,
        # this has to be done in python by directly changing pixel values. Which is slow, and more slower
        # the more pixels in the image.
        in_chan = None
        out_chan = None
        bake = None
        mask = None
        if "A" in solution.inputs.keys():
            data = solution.inputs["A"]
            in_chan = data[0]
            out_chan = "A"
            images = solution.passed[data[1].name]
            bake = images[0]
            mask = images[1]
        start = datetime.now()
        _print(">  -Creating alpha channel: ", tag=True, wrap=False)
        aerr = alpha_pass(in_chan, out_chan, bake, mask, orig_image, mux_image)
        if not aerr:
            _print("Completed in %s" % (str(datetime.now() - start)), tag=True)
        else:
            err = True
    
    # Save the image to disk
    _print(">  -Writing changes to %s" % (output_file), tag=True)
    mux_image.save_render(output_file, scene=output_scene)
    bpy.context.window.scene = base_scene
    return err



# Bake a multi-res pass
def bake_multi_res(img_bake, bake_type, materials, settings, base_col, target, original):
    # Set multi res levels on copy
    multi_mod = None
    for mod in target.modifiers:
        if mod.type == 'MULTIRES':
            multi_mod = mod
            break
    if multi_mod:
        multi_mod.levels = 0
        multi_mod.render_levels = multi_mod.total_levels
        if settings["multi_samp"] == 'FROMMOD':
            src_mod = None
            for mod in original.modifiers:
                if mod.type == 'MULTIRES':
                    src_mod = mod
                    break
            if src_mod:
                multi_mod.levels = src_mod.levels
                multi_mod.render_levels = src_mod.render_levels
        elif settings["multi_samp"] == 'CUSTOM':
            if settings["multi_targ"] >= 0 and settings["multi_targ"] <= multi_mod.total_levels:
                multi_mod.levels = settings["multi_targ"]
            if settings["multi_sorc"] >= 0 and settings["multi_sorc"] <= multi_mod.total_levels:
                multi_mod.render_levels = settings["multi_sorc"]
                            
    # Add a bake target image node to each material
    for mat in materials.values():
        if debug: _print(">    Preparing material [%s] for [Multi-Res %s] bake" % (mat.name, bake_type), tag=True)
        image_node = mat.node_tree.nodes.new("ShaderNodeTexImage")
        image_node.image = img_bake
        image_node.select = True
        mat.node_tree.nodes.active = image_node
        
    # Next link all the objects from the base scene to hopefully stop any modifier errors
    for obj in base_scene.objects:
        base_col.objects.link(obj)
        obj.select_set(False)
    
    # Bake it
    return bake(bake_type, settings, False, True)



# Bake a to-active pass
def bake_to_active(img_bake, bake_type, materials, settings, selected):
    # Make the source objects selected
    for obj in selected.objects:
        obj.select_set(True)
        
    # Add texture node set up to target object
    mat = bpy.data.materials.new(name="mat_" + settings["node_name"] + "_" + settings["mesh_name"])
    mat.use_nodes = True
    image_node = mat.node_tree.nodes.new("ShaderNodeTexImage")
    image_node.image = img_bake
    image_node.select = True
    mat.node_tree.nodes.active = image_node
    bpy.context.view_layer.objects.active.data.materials.append(mat)
    
    # Prepare the materials for the bake type
    for mat in materials.values():
        if debug: _print(">     Preparing material [%s] for [%s] bake" % (mat.name, bake_type), tag=True)
        prep_material_for_bake(mat.node_tree, bake_type)
        
    # Bake it
    return bake(bake_type, settings, True, False)



# Bake single object pass
def bake_solo(img_bake, bake_type, materials, settings):
    # Prepare the materials for the bake type
    for mat in materials.values():
        if debug: _print(">     Preparing material [%s] for [%s] bake" % (mat.name, bake_type), tag=True)
        prep_material_for_bake(mat.node_tree, bake_type)
        # For non To active bakes, add an image node to the material and make it selected + active for bake image
        image_node = mat.node_tree.nodes.new("ShaderNodeTexImage")
        image_node.image = img_bake
        image_node.select = True
        mat.node_tree.nodes.active = image_node
        
    # Bake it
    return bake(bake_type, settings, False, False)
        
        

# Bake a masking pass
def bake_mask(img_mask, materials, settings, to_active, target, selected):
    # Make sure every baked object has a material so the mask can bake
    mat = bpy.data.materials.new(name="mask_" + settings["node_name"] + "_" + settings["mesh_name"])
    mat.use_nodes = True
    objs = [target]
    for obj in selected.objects:
        objs.append(obj)
    for obj in objs:
        add_mat = True
        if len(obj.material_slots):
            for slot in obj.material_slots:
                if slot.material:
                    add_mat = False
                    break
        if add_mat:
            if mat.name not in materials:
                materials[mat.name] = mat
            obj.data.materials.append(mat)
        
    # Requires adding a pure while emit shader to all the materials first and changing target image
    for mat in materials.values():
        prep_material_for_bake(mat.node_tree, 'MASK')
        
        # Add image node to material and make it selected + active
        if not to_active:
            image_node = mat.node_tree.nodes.new("ShaderNodeTexImage")
            image_node.image = img_mask
            image_node.select = True
            mat.node_tree.nodes.active = image_node
    
    # Add image node to target and make it selected + active (should only be one material at this point)
    if to_active:
        image_node = bpy.context.view_layer.objects.active.material_slots[0].material.node_tree.nodes.new("ShaderNodeTexImage")
        image_node.image = img_mask
        image_node.select = True
        bpy.context.view_layer.objects.active.material_slots[0].material.node_tree.nodes.active = image_node
    
    # Bake it
    settings["margin"] += settings["padding"]
    return bake('MASK', settings, to_active, False)
    
    
    
# Call actual bake commands
def bake(bake_type, settings, to_active, multi):
    # Set 'real' bake pass. PBR use EMIT rather than the named pass, since those passes don't exist.
    if bake_type in ['ALBEDO', 'METALLIC', 'ALPHA', 'CAVITY', 'SPECULAR', 'MASK']:
        real_bake_type = 'EMIT'
    elif bake_type == 'SMOOTHNESS':
        real_bake_type = 'ROUGHNESS'
    elif bake_type in ['CURVATURE', 'CURVE_SMOOTH']:
        real_bake_type = 'NORMAL'
        settings["norm_s"] = 'TANGENT'
        settings["norm_r"] = 'POS_X'
        settings["norm_g"] = 'POS_Y'
        settings["norm_b"] = 'POS_Z'
    else:
        real_bake_type = bake_type
        
    if debug: _print(">     Real bake type set to [%s]" % (real_bake_type), tag=True)
        
    # Update view layer to be safe
    bpy.context.view_layer.update()
    start = datetime.now()
    _print(">    -Baking %s pass: " % (bake_type), tag=True, wrap=False)
    
    # Do the bake. Most of the properties can be passed as arguments to the operator.
    err = False
    try:
        if not multi:
            bpy.ops.object.bake(
                type=real_bake_type,
                pass_filter=settings["pass_influences"],
                margin=settings["margin"],
                use_selected_to_active=to_active,
                cage_extrusion=settings["ray_dist"],
                cage_object=settings["cage_obj_name"],
                normal_space=settings["norm_s"],
                normal_r=settings["norm_r"],
                normal_g=settings["norm_g"],
                normal_b=settings["norm_b"],
                save_mode='INTERNAL',
                use_clear=False,
                use_cage=settings["cage"],
            )
        else:
            bpy.context.scene.render.use_bake_multires = True
            bpy.context.scene.render.bake_margin = settings["margin"]
            bpy.context.scene.render.bake_type = bake_type
            bpy.context.scene.render.use_bake_clear = False
            bpy.ops.object.bake_image()
    except RuntimeError as error:
        _print("%s" % (error), tag=True)
        err = True
    else:
        _print("Completed in %s" % (str(datetime.now() - start)), tag=True)
    return err



# Handle post processes that need to be applied to the baked data to create the desired map
def bake_post(img_bake, bake_type, settings, format):
    post_obj = post_scene.objects["BW_Post_%s" % (bake_type)]
    post_mat = post_obj.material_slots[0].material.node_tree.nodes
    post_src = post_mat["bw_post_input"]
    post_out = post_mat["bw_post_output"]
    
    post_img = bpy.data.images.new(img_bake.name + "_POST", width=settings["x_res"], height=settings["y_res"])
    post_img.colorspace_settings.name = format['img_color_space']
    post_img.colorspace_settings.is_data = img_bake.colorspace_settings.is_data
    post_img.use_generated_float = img_bake.use_generated_float
    
    # Switch into post scene and set up the selection state
    bpy.context.window.scene = post_scene
    bpy.ops.object.select_all(action='DESELECT')
    post_obj.select_set(True)
    bpy.context.view_layer.objects.active = post_obj
    
    # Set up standard images
    post_src.image = img_bake
    post_out.image = post_img
    
    # Perform additional set up needed for specific process
    if bake_type == 'CURVATURE':
        post_src2 = post_mat["bw_post_input.001"]
        post_src2.image = img_bake
        post_src3 = post_mat["bw_post_input.002"]
        post_src3.image = img_bake
        post_src4 = post_mat["bw_post_input.003"]
        post_src4.image = img_bake
        post_val = post_mat["bw_post_value"].outputs[0]
        post_val.default_value = settings["curve_val"] * 0.001
        
    # Generate image
    bpy.context.view_layer.update()
    start = datetime.now()
    _print(">    -Performing post bake processes: ", tag=True, wrap=False)
    err = False
    try:
        bpy.ops.object.bake(
            type="EMIT",
            save_mode='INTERNAL',
            use_clear=False,
        )
    except RuntimeError as error:
        _print("%s" % (error), tag=True)
        err = True
    else:
        _print("Completed in %s" % (str(datetime.now() - start)), tag=True)
    return [err, post_img]



# Create correct alpha channel values in output image
def alpha_pass(in_chan, out_chan, bake, mask, orig, mux):
    stride = 4
    out_px = list(mux.pixels)
    orig_px = None
    mask_px = None
    src_chan = 3

    # If the output channel isn't Alpha, then just copy the original alpha values to the mux
    if out_chan != "A":
        in_px = orig.pixels[:]
    # Otherwise copy the input channel values from bake to mux (respecting mask if in play)
    else:
        in_px = bake.pixels[:]
        if mask:
            orig_px = orig.pixels[:]
            mask_px = mask.pixels[:]
        if in_chan in ["Color", "Value"]:
            src_chan = -1
        elif in_chan == "R":
            src_chan = 0
        elif in_chan == "G":
            src_chan = 1
        elif in_chan == "B":
            src_chan = 2
            
    # Sanity check
    if len(in_px) != len(out_px) or (mask and (len(orig_px) != len(in_px) or len(mask_px) != len(in_px))):
        _print("Input/Output pixel count mismatch", tag=True)
        return True
    
    # Write channel
    for pixel in range(int(len(out_px)/stride)):
        position = pixel * stride
        alpha_ch = position + 3
        srce_pos = position + src_chan
        if mask_px == None or mask_px[position]:
            if src_chan != -1:
                out_px[alpha_ch] = in_px[srce_pos]
            else:
                out_px[alpha_ch] = pixel_value(in_px[position:position+3])
        else:
            out_px[alpha_ch] = orig_px[alpha_ch]
    
    # Copy the changes back into the mux
    mux.pixels = out_px[:]
    mux.update()
    return False



# Clear an existing image to all black all transparent
def clear_image(solution):
    # Proceed if clear is set
    if solution.node.img_clear:
        output_path = solution.node.img_path
        output_name = solution.node.name_with_ext()
        output_file = os.path.join(os.path.realpath(output_path), output_name)
        
        # Nothing to do if image doesn't exist
        if os.path.exists(output_file):
            img = bpy.data.images.load(os.path.abspath(output_file))
            img.generated_type = 'BLANK'
            img.generated_color = (0.0, 0.0, 0.0, 0.0)
            img.generated_width = img.size[0]
            img.generated_height = img.size[1]
            img.source = 'GENERATED'
            img.filepath_raw = output_file
            img.save()
            _print(">  -Image Cleared", tag=True)



# Take a list of values and return the highest
def pixel_value(channels):
    value = 0
    for val in channels:
        if val > value:
            value = val
    return value



# Apply image format settings to scenes output settings
def apply_output_format(target_settings, format):
    # Configure output image settings
    target_settings.file_format = img_type = format["img_type"]
    
    # Color mode, split between formats that support alpha and those that don't
    if img_type in ['BMP', 'JPEG', 'CINEON', 'HDR']:
        # Non alpha formats
        target_settings.color_mode = format["img_color_mode_noalpha"]
    else:
        # Alpha supported formats
        target_settings.color_mode = format["img_color_mode"]
        
    # Color Depths, depends on format:
    if img_type in ['PNG', 'TIFF']:
        target_settings.color_depth = format["img_color_depth_8_16"]
    elif img_type == 'JPEG2000':
        target_settings.color_depth = format["img_color_depth_8_12_16"]
    elif img_type == 'DPX':
        target_settings.color_depth = format["img_color_depth_8_10_12_16"]
    elif img_type in ['OPEN_EXR_MULTILAYER', 'OPEN_EXR']:
        target_settings.color_depth = format["img_color_depth_16_32"]
    
    # Compression / Quality for formats that support it
    if img_type == 'PNG':
        target_settings.compression = format["img_compression"]
    elif img_type in ['JPEG', 'JPEG2000']:
        target_settings.quality = format["img_quality"]
        
    # Codecs for formats that use them
    if img_type == 'JPEG2000':
        target_settings.jpeg2k_codec = format["img_codec_jpeg2k"]
    elif img_type in ['OPEN_EXR', 'OPEN_EXR_MULTILAYER']:
        target_settings.exr_codec = format["img_codec_openexr"]
    elif img_type == 'TIFF':
        target_settings.tiff_codec = format["img_codec_tiff"]
        
    # Additional settings used by some formats
    if img_type == 'JPEG2000':
        target_settings.use_jpeg2k_cinema_preset = format["img_jpeg2k_cinema"]
        target_settings.use_jpeg2k_cinema_48 = format["img_jpeg2k_cinema48"]
        target_settings.use_jpeg2k_ycc = format["img_jpeg2k_ycc"]
    elif img_type == 'DPX':
        target_settings.use_cineon_log = format["img_dpx_log"]
    elif img_type == 'OPEN_EXR':
        target_settings.use_zbuffer = format["img_openexr_zbuff"]



# Copy render settings from source scene to active scene
def copy_render_settings(source, target):
    # Copy all Cycles settings
    for setting in source.cycles.bl_rna.properties.keys():
        if setting not in ["rna_type", "name"]:
            setattr(target.cycles, setting, getattr(source.cycles, setting))
    for setting in source.cycles_curves.bl_rna.properties.keys():
        if setting not in ["rna_type", "name"]:
            setattr(target.cycles_curves, setting, getattr(source.cycles_curves, setting))
    # Copy SOME Render settings
    for setting in source.render.bl_rna.properties.keys():
        if setting in ["tile_x",
                       "tile_y",
                       "dither_intensity",
                       "filter_size",
                       "film_transparent",
                       "use_freestyle",
                       "threads",
                       "threads_mode",
                       "hair_type",
                       "hair_subdiv",
                       "use_simplify",
                       "simplify_subdivision",
                       "simplify_child_particles",
                       "simplify_subdivision_render",
                       "simplify_child_particles_render",
                       "use_simplify_smoke_highres",
                       "simplify_gpencil",
                       "simplify_gpencil_onplay",
                       "simplify_gpencil_view_fill",
                       "simplify_gpencil_remove_lines",
                       "simplify_gpencil_view_modifier",
                       "simplify_gpencil_shader_fx",
                       "simplify_gpencil_blend",
                       "simplify_gpencil_tint",
                      ]:
            setattr(target.render, setting, getattr(source.render, setting))



# Pretty much everything here is about preventing blender crashing or failing in some way that only happens
# when it runs a background bake. Perhaps it wont be needed some day, but for now trying to keep all such
# things in one place. Modifiers are applied or removed and non mesh types are converted.
def prep_object_for_bake(object):
    # Create a copy of the object to modify and put it into the mesh only scene
    if not object.bw_copy:
        copy = object.copy()
        copy.data = object.data.copy()
        copy.name = "BW_" + object.name
        base_scene.collection.objects.link(copy)
        bpy.context.view_layer.update()
    else:
        # Object already preped
        return
    
    # Objects need to be selectable and visibile in the viewport in order to convert them
    copy.hide_select = False
    copy.hide_viewport = False
    
    # If ignoring visibility is enabled, also make the object shown for render
    if ignorevis:
        copy.hide_render = False
    
    # Make obj the only selected + active
    bpy.ops.object.select_all(action='DESELECT')
    copy.select_set(True)
    bpy.context.view_layer.objects.active = copy
                    
    # Deal with mods
    if len(copy.modifiers):
        for mod in copy.modifiers:
            if mod.show_render:
                # A mod can be disabled by invalid settings, which will throw an exception when trying to apply it
                try:
                    bpy.ops.object.modifier_apply(modifier=mod.name)
                except:
                    _print(">    Error applying modifier '%s' to object '%s'" % (mod.name, object.name), tag=True) 
                    bpy.ops.object.modifier_remove(modifier=mod.name)
            else:
                bpy.ops.object.modifier_remove(modifier=mod.name)
            
    # Deal with object type
    if object.type != 'MESH':
        # Apply render resolution if its set before turning into a mesh
        if object.type == 'META':
            if copy.data.render_resolution > 0:
                copy.data.resolution = copy.data.render_resolution
        else:
            if copy.data.render_resolution_u > 0:
                copy.data.resolution_u = copy.data.render_resolution_u
            if object.data.render_resolution_v > 0:
                copy.data.resolution_v = copy.data.render_resolution_v
        # Convert
        bpy.ops.object.convert(target='MESH')
        
        # Meta objects seem to get deleted and a new object replaces them, breaking the reference
        if object.type == 'META':
            copy = bpy.context.view_layer.objects.active
    
    # Link copy to original, remove from base scene and add to mesh scene
    object.bw_copy = copy
    mesh_scene.collection.objects.link(copy)
    base_scene.collection.objects.unlink(copy)



# Takes a materials node tree and makes any changes necessary to perform the given bake type. A material must
# end with principled shader(s) and mix shader(s) connected to a material output in order to be set up for any
# emission node bakes.
def prep_material_for_bake(node_tree, bake_type):
    # Bake types with built-in passes don't require any preparation
    if not node_tree or bake_type in ['NORMAL', 'ROUGHNESS', 'SMOOTHNESS', 'AO', 'SUBSURFACE', 'TRANSMISSION', 'GLOSSY', 'DIFFUSE', 'ENVIRONMENT', 'EMIT', 'UV', 'SHADOW', 'COMBINED', 'CURVATURE', 'CURVE_SMOOTH', 'CAVITY']:
        return
    
    # Mask is a special case where an emit shader and output can just be added to any material
    elif bake_type == 'MASK':
        nodes = node_tree.nodes
        
        # Add white emit and a new active output
        emit = nodes.new('ShaderNodeEmission')
        emit.inputs['Color'].default_value = [1.0, 1.0, 1.0, 1.0]
        outp = nodes.new('ShaderNodeOutputMaterial')
        node_tree.links.new(emit.outputs['Emission'], outp.inputs['Surface'])
        outp.target = 'CYCLES'
        
        # Make all outputs not active
        for node in nodes:
            if node.type == 'OUTPUT_MATERIAL':
                node.is_active_output = False
                
        outp.is_active_output = True
        return
        
    # The material has to have a node tree and it needs at least 2 nodes to be valid
    elif len(node_tree.nodes) < 2:
        return
    
    # All other bake types use an emission shader with the value plugged into it
    
    # A material can have multiple output nodes. Blender seems to preference the output to use like so:
    # 1 - Target set to current Renderer and Active (picks first if multiple are set active)
    # 2 - First output with Target set to Renderer if no others with that target are set Active
    # 3 - Active output (picks first if mutliple are active)
    #
    # Strategy will be to find all valid outputs and evaluate if they can be used in the same order as above.
    # The first usable output found will be selected and also changed to be the first choice for blender.
    # Four buckets: Cycles + Active, Cycles, Generic + Active, Generic
    nodes = node_tree.nodes
    node_cycles_out_active = []
    node_cycles_out = []
    node_generic_out_active = []
    node_generic_out = []
    node_selected_output = None
    
    # Collect all outputs
    for node in nodes:
        if node.type == 'OUTPUT_MATERIAL':
            if node.target == 'CYCLES':
                if node.is_active_output:
                    node_cycles_out_active.append(node)
                else:
                    node_cycles_out.append(node)
            elif node.target == 'ALL':
                if node.is_active_output:
                    node_generic_out_active.append(node)
                else:
                    node_generic_out.append(node)
                
    # Select the first usable output using the order explained above and make sure no other outputs are set active
    node_outputs = node_cycles_out_active + node_cycles_out + node_generic_out_active + node_generic_out
    for node in node_outputs:
        input = node.inputs['Surface']
        if not node_selected_output and material_recursor(node):
            node_selected_output = node
            node.is_active_output = True
        else:
            node.is_active_output = False
    
    if not node_selected_output:
        return
    
    # Output has been selected. An emission shader will now be built, replacing mix shaders with mix RGB
    # nodes and principled shaders with just the desired data for the bake type. Recursion used.
    if debug: _print(">      Chosen output [%s] descending tree:" % (node_selected_output.name), tag=True)
    return prep_material_rec(node_selected_output, node_selected_output.inputs['Surface'], bake_type)



# Takes a node of type OUTPUT_MATERIAL, BSDF_PRINCIPLED or MIX_SHADER. Starting with an output node it will
# recursively generate an emission shader to replace the output with the desired bake type. The link_socket
# is used for creating node tree links.
def prep_material_rec(node, link_socket, bake_type):
    tree = node.id_data
    nodes = tree.nodes
    links = tree.links
    # Three cases:
    if node.type == 'OUTPUT_MATERIAL':
        # Start of shader. Create new emission shader and connect it to the output
        next_node = follow_input_link(link_socket.links[0]).from_node
        node_emit = nodes.new('ShaderNodeEmission')
        links.new(node_emit.outputs['Emission'], link_socket)
        # Recurse
        return prep_material_rec(next_node, node_emit.inputs['Color'], bake_type)
        
    if node.type == 'MIX_SHADER':
        # Mix shader needs to generate a mix RGB maintaining the same Fac input if linked
        mix_node = nodes.new('ShaderNodeMixRGB')
        if node.inputs['Fac'].is_linked:
            # Connect Fac input
            links.new(follow_input_link(node.inputs['Fac'].links[0]).from_socket, mix_node.inputs['Fac'])
        else:
            # Set Fac value to match instead
            mix_node.inputs['Fac'].default_value = node.inputs['Fac'].default_value
        # Connect mix output to previous socket
        links.new(mix_node.outputs['Color'], link_socket)
        # Recurse
        branchA = prep_material_rec(follow_input_link(node.inputs[1].links[0]).from_node, mix_node.inputs['Color1'], bake_type)
        branchB = prep_material_rec(follow_input_link(node.inputs[2].links[0]).from_node, mix_node.inputs['Color2'], bake_type)
        return branchA and branchB
        
    if node.type == 'BSDF_PRINCIPLED':
        # End of a branch as far as the prep is concerned. Either link the desired bake value or set the
        # previous socket to the value if it isn't linked
        if bake_type == 'ALBEDO':
            bake_input = node.inputs['Base Color']
        elif bake_type == 'METALLIC':
            bake_input = node.inputs['Metallic']
        elif bake_type == 'ALPHA':
            bake_input = node.inputs['Alpha']
        elif bake_type == 'SPECULAR':
            bake_input = node.inputs['Specular']
        else:
            bake_input = None
            
        if debug: _print(">       Reached branch end, ", tag=True, wrap=False)
            
        if bake_input:
            if bake_input.is_linked:
                if debug: _print("Link found, [%s] will be connected" % (bake_input.links[0].from_socket.name), tag=True)
                # Connect the linked node up to the emit shader
                links.new(bake_input.links[0].from_socket, link_socket)
            else:
                if debug: _print("Not linked, value will be copied", tag=True)
                # Copy the value into the socket instead
                if bake_input.type == 'RGBA':
                    link_socket.default_value = bake_input.default_value
                else:
                    link_socket.default_value[0] = bake_input.default_value
                    link_socket.default_value[1] = bake_input.default_value
                    link_socket.default_value[2] = bake_input.default_value
                    link_socket.default_value[3] = 1.0
            # Branch completed
            return True
            
    # Something went wrong
    if debug: _print(">       Error: Reached unsupported node type", tag=True)
    return False



# Consider all materials in scene and create scene only copies
def make_materials_unique_to_scene(scene, suffix, bake_type, settings):
    # Go through all the materials on every object
    materials = {}
    
    if bake_type == 'CAVITY':
        # Configure shader
        nodes = cavity_shader.node_tree.nodes
        node_ao = nodes["bw_ao_cavity"]
        node_gamma = nodes["bw_ao_cavity_gamma"]
        node_ao.samples = settings["cavity_samp"]
        node_ao.inputs["Distance"].default_value = settings["cavity_dist"]
        node_gamma.inputs["Gamma"].default_value = settings["cavity_gamma"]
        
    for obj in scene.objects:
        # Some bake types replace materials with a special one
        if bake_type in ['CAVITY']:
            # Clear all materials
            obj.data.materials.clear()
            obj.data.polygons.foreach_set('material_index', [0] * len(obj.data.polygons))
            obj.data.update()
            # Add cavity shader
            obj.data.materials.append(cavity_shader)
            materials["cavity"] = cavity_shader
        # Otherwise normal processing
        elif len(obj.material_slots):
            for slot in obj.material_slots:
                if slot.material:
                    # If its a new material, create a copy (adding suffix) and add the pair to the list
                    if slot.material.name not in materials:
                        copy = slot.material.copy()
                        copy.name = slot.material.name + suffix
                        materials[slot.material.name] = copy
                        replace = copy
                    else:
                        replace = materials[slot.material.name]
                    # Replace with copy
                    slot.material = replace
    # Return the dict
    return materials



# It's a me, main
def main():
    import sys       # to get command line args
    import argparse  # to parse options for us and print a nice help message

    # get the args passed to blender after "--", all of which are ignored by
    # blender so scripts may receive their own arguments
    argv = sys.argv

    if "--" not in argv:
        argv = []  # as if no args are passed
    else:
        argv = argv[argv.index("--") + 1:]  # get all args after "--"

    # When --help or no args are given, print this help
    usage_text = (
        "This script is used internally by Bake Wrangler add-on."
    )

    parser = argparse.ArgumentParser(description=usage_text)

    # Possible types are: string, int, long, choice, float and complex.
    parser.add_argument(
        "-t", "--tree", dest="tree", type=str, required=True,
        help="Name of bakery tree where the starting node is",
    )
    parser.add_argument(
        "-n", "--node", dest="node", type=str, required=True,
        help="Name of bakery node to start process from",
    )
    parser.add_argument(
        "-s", "--savepass", dest="savepass", type=int, required=False,
        help="Save file after each pass",
    )
    parser.add_argument(
        "-v", "--ignorevis", dest="ignorevis", type=int, required=False,
        help="Treat all selected objects as visibile",
    )
    parser.add_argument(
        "-d", "--debug", dest="debug", type=int, required=False,
        help="Enable debug messages",
    )

    args = parser.parse_args(argv)

    if not argv:
        parser.print_help()
        return

    if not args.tree or not args.node:
        print("Error: Bake Wrangler baker required arguments not found")
        return
    
    global savepass
    if args.savepass:
        savepass = bool(args.savepass)
    else:
        savepass = False
        
    global ignorevis
    if args.ignorevis:
        ignorevis = bool(args.ignorevis)
    else:
        ignorevis = False
        
    global debug
    if args.debug:
        debug = bool(args.debug)
    else:
        debug = False
    
    # Make sure the node classes are registered
    try:
        node_tree.register()
    except:
        print("Info: Bake Wrangler nodes already registered")
    else:
        print("Info: Bake Wrangler nodes registered")
        
    # Make sure to be in object mode before doing anything
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    
    # Load shaders and scenes
    bake_scene_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources", "BakeWrangler_Scene.blend")
    with bpy.data.libraries.load(bake_scene_path, link=False, relative=False) as (file_from, file_to):
        file_to.materials.append("BW_Cavity_Map")
        file_to.scenes.append("BakeWrangler_Post")
        file_to.scenes.append("BakeWrangler_Output")
    global cavity_shader
    cavity_shader = file_to.materials[0]
    global post_scene
    post_scene = file_to.scenes[0]
    global output_scene
    output_scene = file_to.scenes[1]
    
    # Start processing bakery node tree
    err = process_tree(args.tree, args.node)
    
    # Send end tag
    if err:
        _print("<ERRORS>", tag=True)
    else:
        _print("<FINISH>", tag=True)
        
    # Save changes to the file for debugging and exit
    bpy.ops.wm.save_mainfile(filepath=bpy.data.filepath, exit=True)
    
    return 0


if __name__ == "__main__":
    main()
