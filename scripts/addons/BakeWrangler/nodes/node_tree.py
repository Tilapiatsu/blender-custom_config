import os
import sys
import threading, queue
import subprocess
from datetime import datetime, timedelta
import bpy
from bpy.types import NodeTree, Node, NodeSocket, NodeSocketColor, NodeSocketFloat



# Message formatter
def _print(str, node=None, ret=False, tag=False, wrap=True, enque=None, textdata="BakeWrangler"):
    output = "%s" % (str)
    endl = ''
    flsh = False
    
    if node:
        output = "[%s]: %s" % (node.get_name(), output)
        
    if tag:
        output.replace("<", "<_")
        output = "<%s>%s" % ("PBAKE", output)
        flsh = True
        if wrap:
            output = "%s</%s>" % (output, "PWRAP")
        else:
            output = "%s</%s>" % (output, "PBAKE")
        
    if wrap:
        endl = '\n'
        
    if enque != None:
        eout = "%s%s" % (output, endl)
        enque.put(eout)
        return None
        
    if ret:
        return output
    
    if textdata != None and _prefs('text_msgs'):
        if not textdata in bpy.data.texts.keys():
            bpy.data.texts.new(textdata)
        text = bpy.data.texts[textdata]
        end = len(text.lines[len(text.lines) - 1].body) - 1
        text.cursor_set(len(text.lines) - 1, character=end)
        tout = "%s%s" % (output, endl)
        text.write(tout)
    
    print(output, end=endl, flush=flsh)



# Preference reader
default_true  = ["text_msgs", "clear_msgs", "wind_msgs", "def_filter_mesh", "def_filter_curve", "def_filter_surface",
                 "def_filter_meta", "def_filter_font", "def_filter_light",]
default_false = ["def_filter_collection", "def_show_adv", "ignore_vis", "save_pass", "make_dirs",]
default_res   = ["def_xres", "def_yres", "def_xout", "def_yout",]
default_zero  = ["def_margin", "def_mask_margin",]
def _prefs(key):
    try:
        name = __package__.split('.')
        prefs = bpy.context.preferences.addons[name[0]].preferences
    except:
        pref = False
    else:
        pref = True
        
    if pref and key in prefs:
        return prefs[key]
    else:
        # Default values to fall back on
        if key == 'debug':
            #return True
            return False
        elif key in default_true:
            return True
        elif key in default_false:
            return False
        elif key in default_res:
            return 1024
        elif key in default_zero:
            return 0
        elif key == 'def_device':
            return 0 # CPU
        elif key == 'def_samples':
            return 1
        elif key == 'def_format':
            return 2 # PNG
        elif key == 'def_raydist':
            return 0.01
        elif key == 'def_outpath':
            return ""
        elif key == 'def_outname':
            return "Image"
        else:
            return None



# Material validation recursor (takes a shader node and descends the tree via recursion)
def material_recursor(node):
    # Accepted node types are OUTPUT_MATERIAL, BSDF_PRINCIPLED and MIX_SHADER (plus REROUTE)
    if node.type == 'BSDF_PRINCIPLED':
        return True
    if node.type == 'OUTPUT_MATERIAL' and node.inputs['Surface'].is_linked:
        return material_recursor(node.inputs['Surface'].links[0].from_node)
    if node.type == 'MIX_SHADER':
        inputA = False
        if node.inputs[1].is_linked:
            inputA = material_recursor(node.inputs[1].links[0].from_node)
        inputB = False
        if node.inputs[2].is_linked:
            inputB = material_recursor(node.inputs[2].links[0].from_node)
        return inputA and inputB
    if node.type == 'REROUTE' and node.inputs[0].is_linked:
        return material_recursor(node.inputs[0].links[0].from_node)
    return False



# Follow an input link through any reroutes
def follow_input_link(link):
    if link.from_node.type == 'REROUTE':
        if link.from_node.inputs[0].is_linked:
            try: # During link insertion this can have weird states
                return follow_input_link(link.from_node.inputs[0].links[0])
            except:
                pass
    return link



# Gather all links from an output, going past any reroutes
def gather_output_links(output):
    links = []
    for link in output.links:
        if link.is_valid:
            if link.to_node.type == 'REROUTE':
                if link.to_node.outputs[0].is_linked:
                    links += gather_output_links(link.to_node.outputs[0])
            else:
                links.append(link)
    return links



#
# Bake Wrangler Operators
#

# Base class for all bakery operators, provides data to find owning node, etc.
class BakeWrangler_Operator:
    # Use strings to store their names, since Node isn't a subclass of ID it can't be stored as a pointer
    tree: bpy.props.StringProperty()
    node: bpy.props.StringProperty()

    @classmethod
    def poll(type, context):
        if context.area is not None:
            return context.area.type == "NODE_EDITOR" and context.space_data.tree_type == "BakeWrangler_Tree"
        else:
            return True


# Dummy operator to draw when a bake is in progress
class BakeWrangler_Operator_Dummy(BakeWrangler_Operator, bpy.types.Operator):
    '''Bake currently in progress, either cancel the current bake or wait for it to finish'''
    bl_idname = "bake_wrangler_op.dummy"
    bl_label = ""
    
    @classmethod
    def poll(type, context):
        # This operator is always supposed to be disabled
        return False
    
    
# Kill switch to stop a bake in progress
class BakeWrangler_Operator_BakeStop(BakeWrangler_Operator, bpy.types.Operator):
    '''Cancel currently running bake'''
    bl_idname = "bake_wrangler_op.bake_stop"
    bl_label = "Cancel Bake"
    
    # Stop the currently running bake
    def execute(self, context):
        tree = bpy.data.node_groups[self.tree]
        if tree.baking != None:
            tree.baking.stop()
            tree.interface_update(context)
        return {'FINISHED'}
    
    # Ask the user if they really want to cancel bake
    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
    
    
# Operator for bake pass node
class BakeWrangler_Operator_BakePass(BakeWrangler_Operator, bpy.types.Operator):
    '''Perform requested bake action(s)'''
    bl_idname = "bake_wrangler_op.bake_pass"
    bl_label = "Bake Pass"

    _timer = None
    
    _thread = None
    _kill = False
    _success = False
    _finish = False
    _lock = threading.Lock()
    _queue = queue.SimpleQueue()
    stopping = False
    
    open_ed = None
    node_ed = None
    
    start = None
    valid = None
    blend_copy = None
    blend_log = None
    bake_proc = None
    was_dirty = False
    img_list = []
    
    # Stop this bake if it's currently running
    def stop(self, kill=True):
        if self._thread and self._thread.is_alive() and kill:
            with self._lock:
                self.stopping = self._kill = True
        return self.stopping
    
    # Runs a blender subprocess
    def thread(self, node_name, tree_name, file_name, exec_name, script_name):
        tree = bpy.data.node_groups[self.tree]
        node = tree.nodes[self.node]
        debug = _prefs('debug')
        savepass = _prefs('save_pass')
        ignorevis = _prefs('ignore_vis')
             
        _print("Launching background process:", node=node, enque=self._queue)
        _print("================================================================================", enque=self._queue)
        sub = subprocess.Popen([
            exec_name,
            file_name,
            "--background",
            "--python", script_name,
            "--",
            "--tree", tree_name,
            "--node", node_name,
            "--debug", str(int(debug)),
            "--savepass", str(int(savepass)),
            "--ignorevis", str(int(ignorevis)),
            ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
        
        # Read output from subprocess and print tagged lines
        out = ""
        kill = False
        while sub.poll() == None:
            # Check for kill flag
            if self._lock.acquire(blocking=False):
                if self._kill:
                    _print("Bake canceled, terminating process...", enque=self._queue)
                    sub.kill()
                    out, err = sub.communicate()
                    kill = True
                self._lock.release()
            
            if not kill:
                out = sub.stdout.read(1)
                # Collect tagged lines and display them in console
                if out == '<':
                    out += sub.stdout.read(6)
                    if out == "<PBAKE>":
                        tag_end = False
                        tag_line = ""
                        out = ""
                        tag_out = ""
                        # Read until end tag is found
                        while not tag_end:
                            tag = sub.stdout.read(1)
                            
                            if tag == '<':
                                tag_line = sub.stdout.read(1)
                                if tag_line != '_':
                                    tag_line = tag + tag_line + sub.stdout.read(6)
                                    if tag_line == "</PBAKE>":
                                        tag_end = True
                                        out += '\n'
                                    elif tag_line == "</PWRAP>":
                                        tag_end = True
                                        tag_out += '\n'
                                        #sys.stdout.write('\n')
                                        #sys.stdout.flush()
                                    elif tag_line == "<FINISH>":
                                        tag_line += sub.stdout.read(8)
                                        tag_end = True
                                        self._success = True
                                        self._finish = True
                                    elif tag_line == "<ERRORS>":
                                        tag_line += sub.stdout.read(8)
                                        tag_end = True
                                        self._success = False
                                        self._finish = True
                            if tag != '' and not tag_end:
                                tag_out += tag
                                #sys.stdout.write(tag_line)
                                #sys.stdout.flush()
                                out += tag
                        _print(tag_out, enque=self._queue, wrap=False)
        
            # Write to log
            if out != '' and self.blend_log:
                self.blend_log.write(out)
                self.blend_log.flush()
        _print("================================================================================", enque=self._queue)
        _print("Background process ended", node=node, enque=self._queue)

    # Event handler
    def modal(self, context, event):
        tree = bpy.data.node_groups[self.tree]
        node = tree.nodes[self.node]
        
        # Check if the bake thread has ended every timer event
        if event.type == 'TIMER':
            self.print_queue(context)
            # Reapply dirt by pushing something to undo stack (not ideal)
            if self.was_dirty and not bpy.data.is_dirty:
                bpy.ops.node.select_all(action='INVERT')
                bpy.ops.node.select_all(True, action='INVERT')
                self.was_dirty = False
            if not self._thread.is_alive():
                self.cancel(context)
                if self._kill:
                    _print("Bake canceled after %s" % (str(datetime.now() - self.start)), node=node, enque=self._queue)
                    _print("Canceled\n", node=node, enque=self._queue)
                    self.report({'WARNING'}, "Bake Canceled")
                    return {'CANCELLED'}
                else:
                    if self._success and self._finish:
                        _print("Bake finished in %s" % (str(datetime.now() - self.start)), node=node, enque=self._queue)
                        _print("Success\n", node=node, enque=self._queue)
                        self.report({'INFO'}, "Bake Completed")
                    elif self._finish:
                        _print("Bake finished with errors after %s" % (str(datetime.now() - self.start)), node=node, enque=self._queue)
                        _print("Errors\n", node=node, enque=self._queue)
                        self.report({'WARNING'}, "Bake Finished with Errors")
                        self.show_log()
                    else:
                        _print("Bake failed after %s" % (str(datetime.now() - self.start)), node=node, enque=self._queue)
                        _print("Failed\n", node=node, enque=self._queue)
                        self.report({'ERROR'}, "Bake Failed")
                        self.show_log()
                    self.update_images()
                    self.print_queue(context)
                    return {'FINISHED'}
        return {'PASS_THROUGH'}
            
    # Print queued messages
    def print_queue(self, context):
        try:
            # An Empty exception will be raised when nothing is in the queue
            while True:
                msg = self._queue.get_nowait()
                _print(msg, wrap=False)
        except:
            return
        
    # Display log file if debugging is enabled and the bake failed or had errors
    def show_log(self):
        if _prefs('debug') and self.blend_log:
            bpy.ops.screen.area_dupli({'area': self.node_ed}, 'INVOKE_DEFAULT')
            open_ed = bpy.context.window_manager.windows[len(bpy.context.window_manager.windows) - 1].screen.areas[0]
            open_ed.type = 'TEXT_EDITOR'
            log = bpy.data.texts.load(self.blend_copy + ".log")
            open_ed.spaces[0].text = log
            open_ed.spaces[0].show_line_numbers = False
            open_ed.spaces[0].show_syntax_highlight = False            
            
    # Update any loaded images that might be changed by the bake
    def update_images(self):
        if len(self.img_list) and len(bpy.data.images):
            cwd = os.path.dirname(bpy.data.filepath)
            for img in bpy.data.images:
                img_path = os.path.normpath(os.path.join(cwd, bpy.path.abspath(img.filepath_raw)))
                if img_path in self.img_list:
                    img.reload()
    
    # Called after invoke to perform the bake if everything passed validation
    def execute(self, context):
        # If message log in new window is enabled
        if _prefs("text_msgs") and _prefs("wind_msgs"):
            bpy.ops.screen.area_dupli('INVOKE_DEFAULT')
            self.open_ed = context.window_manager.windows[len(context.window_manager.windows) - 1].screen.areas[0]
            self.open_ed.type = 'TEXT_EDITOR'
            self.open_ed.spaces[0].text = bpy.data.texts["BakeWrangler"]
            self.open_ed.spaces[0].show_line_numbers = False
            self.open_ed.spaces[0].show_syntax_highlight = False
        
        if self.valid == None:
            self.report({'ERROR'}, "Call invoke first")
            return {'CANCELLED'}
        elif not self.valid[0]:
            self.cancel(context)
            self.report({'ERROR'}, "Validation failed")
            return {'CANCELLED'}
        
        self.start = datetime.now()
        tree = bpy.data.node_groups[self.tree]
        node = tree.nodes[self.node]
        
        # Save a temporary copy of the blend file and store the path. Make sure the path doesn't exist first.
        # All baking will be done using this copy so the user can continue working in this session.
        blend_name = bpy.path.clean_name(bpy.path.display_name_from_filepath(bpy.data.filepath))
        blend_temp = bpy.path.abspath(bpy.app.tempdir)
        node_cname = bpy.path.clean_name(node.get_name())
        blend_copy = os.path.join(blend_temp, "BW_" + blend_name)
        
        # Increment file name until it doesn't exist
        if os.path.exists(blend_copy + "_000.blend"):
            fno = 1
            while os.path.exists(blend_copy + "_%03i.blend" % (fno)):
                fno = fno + 1
            blend_copy = blend_copy + "_%03i.blend" % (fno)
        else:
            blend_copy = blend_copy + "_000.blend"
        
        # Print out start message and temp path
        _print("")
        _print("=== Bake starts ===", node=node)
        _print("Creating temporary files in %s" % (blend_temp), node=node)
        
        # Maintain dirt
        if bpy.data.is_dirty:
            self.was_dirty = True
            
        bpy.ops.wm.save_as_mainfile(filepath=blend_copy, copy=True)
             
        # Check copy exists
        if not os.path.exists(blend_copy):
            self.report({'ERROR'}, "Blend file copy failed")
            return {'CANCELLED'}
        else:
            self.blend_copy = blend_copy
            
        # Open a log file at the same location with a .log appended to the name
        log_err = None
        blend_log = None
        try:
            blend_log = open(blend_copy + ".log", "a", encoding="utf-8", errors="replace")
        except OSError as err:
            self.report({'WARNING'}, "Couldn't create log file")
            log_err = err.strerror
        else:
            self.blend_log = blend_log
        
        # Print out blend copy and log names
        _print(" - %s" % (os.path.basename(self.blend_copy)), node=node) 
        if self.blend_log and not log_err:
            _print(" - %s" % (os.path.basename(self.blend_copy + ".log")), node=node)
        else:
            _print(" - Log file creation failed: %s" % (log_err), node=node)
        
        # Create a thread which will launch a background instance of blender running a script that does all the work.
        # Process is complete when thread exits. Will need full path to blender, node, temp file and proc script.
        blend_exec = bpy.path.abspath(bpy.app.binary_path)
        self._thread = threading.Thread(target=self.thread, args=(self.node, self.tree, self.blend_copy, blend_exec, self.bake_proc,))
        
        # Get a list of image file names that will be updated by the bake so they can be reloaded on success
        self.img_list = []
        if node.bl_idname == 'BakeWrangler_Output_Batch_Bake':
            for input in node.inputs:
                if input.islinked() and input.valid:
                    img_name = os.path.join(follow_input_link(input.links[0]).from_node.img_path, follow_input_link(input.links[0]).from_node.name_with_ext())
                    if not self.img_list.count(img_name):
                        self.img_list.append(img_name)
        elif node.bl_idname == 'BakeWrangler_Bake_Pass':
            for output in node.outputs:
                for link in gather_output_links(output):
                    if link.to_socket.valid:
                        img_name = os.path.join(link.to_node.img_path, link.to_node.name_with_ext())
                        if not self.img_list.count(img_name):
                            self.img_list.append(img_name)
        elif node.bl_idname == 'BakeWrangler_Output_Image_Path':
            img_name = os.path.join(node.img_path, node.name_with_ext())
            if not self.img_list.count(img_name):
                self.img_list.append(img_name)
        
        # Add a timer to periodically check if the bake has finished
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.5, window=context.window)
        wm.modal_handler_add(self)
        
        self._thread.start()
                
        # Go modal
        return {'RUNNING_MODAL'}
    
    # Called by UI when the button is clicked. Will validate settings and prepare files for execute
    def invoke(self, context, event):
        # Are text editor messages enabled?
        if _prefs("text_msgs"):
            # Make sure the text block exists
            if not "BakeWrangler" in bpy.data.texts.keys():
                bpy.data.texts.new("BakeWrangler")
            # Clear the block if option set
            if _prefs("clear_msgs"):
                bpy.data.texts["BakeWrangler"].clear()
                
        # Do full validation of bake so it can be reported in the popup dialog
        self.node_ed = context.area
        tree = bpy.data.node_groups[self.tree]
        node = tree.nodes[self.node]
        tree.baking = self
        tree.interface_update(context)
        self.valid = node.validate(is_primary=True)
        
        # Check processing script exists
        bake_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        bake_proc = bpy.path.abspath(os.path.join(bake_path, "baker.py"))
        if not os.path.exists(bake_proc):
            self.valid[0] = False
            self.valid.append([_print("File missing", node=node, ret=True), ": Bake processing script wasn't found at '%s'" % (bake_proc)])
        else:
            self.bake_proc = bake_proc
        
        # Check baking scene file exists
        scene_file = bpy.path.abspath(os.path.join(bake_path, "resources", "BakeWrangler_Scene.blend"))
        if not os.path.exists(scene_file):
            self.valid[0] = False
            self.valid.append([_print("File missing", node=node, ret=True), ": Bake scene library wasn't found at '%s'" % (scene_file)])
        
        # Draw pop-up that will use custom draw function to display any validation errors
        return context.window_manager.invoke_props_dialog(self, width=400)
    
    # Cancel the bake
    def cancel(self, context):
        tree = bpy.data.node_groups[self.tree]
        if self._timer:
            wm = context.window_manager
            wm.event_timer_remove(self._timer)
        if self.blend_log:
            self.blend_log.close()
        if tree.baking != None:
            tree.baking = None
            tree.interface_update(context)
    
    # Draw custom pop-up
    def draw(self, context):
        tree = bpy.data.node_groups[self.tree]
        node = tree.nodes[self.node]
        layout = self.layout
        if not self.valid[0]:
            layout.label(text="!!! Validation FAILED:")
            _print("")
            _print("!!! Validation FAILED:", node=node)
            col = layout.column()
            for i in range(len(self.valid) - 1):
                col.label(text=self.valid[i + 1][0])
                _print(self.valid[i + 1][0] + self.valid[i + 1][1])
            layout.label(text="See console for details")
            _print("")
        else:
            layout.label(text="%s ready to bake:" % (node.get_name()))
            if len(self.valid) > 1:
                layout.label(text="")
                layout.label(text="!!! Material Warnings:")
                _print("")
                _print("!!! Material Warnings:")
                col = layout.column()
                for i in range(len(self.valid) - 1):
                    col.label(text=self.valid[i + 1][0])
                    _print(self.valid[i + 1][0] + self.valid[i + 1][1])
            layout.label(text="See console for progress information and warnings")



#
# Bake Wrangler nodes system
#

BW_TREE_VERSION = 4

# Node tree definition that shows up in the editor type list. Sets the name, icon and description.
class BakeWrangler_Tree(NodeTree):
    '''Improved baking system to extend and replace existing internal bake system'''
    bl_label = 'Bake Node Editor'
    bl_icon = 'NODETREE'
    
    # Does this need a lock for modal event access?
    baking = None
    
    # Do some initial set up when a new tree is created
    initialised: bpy.props.BoolProperty(name="Initialized", default=False)
    tree_version: bpy.props.IntProperty(name="Tree Version", default=0)
        


# Custom Sockets:

# Base class for all bakery sockets
class BakeWrangler_Tree_Socket:
    # Workaround for link.is_valid being un-usable
    valid: bpy.props.BoolProperty()
    
    def socket_label(self, text):
        if self.name == "A" and self.is_linked and self.valid and self.node.bl_idname == "BakeWrangler_Output_Image_Path" and \
           self.node.img_type in ['IRIS', 'PNG', 'JPEG2000', 'TARGA', 'TARGA_RAW', 'DPX', 'OPEN_EXR_MULTILAYER', 'OPEN_EXR', 'TIFF'] and \
           self.node.img_color_mode != 'RGBA':
            return text + " [RGBA Only]"
        elif self.is_output or (self.is_linked and self.valid) or (not self.is_output and not self.is_linked):
            return text
        else:
            return text + " [invalid]"
            
    def socket_color(self, color):
        if not self.is_output and self.is_linked and not self.valid:
            return (1.0, 0.0, 0.0, 1.0)
        else:
            return color
    
    # Follows through reroutes
    def islinked(self):
        if self.is_linked and not self.is_output:
            try: # During link removal this can be in a weird state
                node = self.links[0].from_node
                while node.type == "REROUTE":
                    if node.inputs[0].is_linked and node.inputs[0].links[0].is_valid:
                        node = node.inputs[0].links[0].from_node
                    else:
                        return False
                return True
            except:
                pass
        return False                



# Socket for an object or list of objects to be used in a bake pass in some way
class BakeWrangler_Socket_Object(NodeSocket, BakeWrangler_Tree_Socket):
    '''Socket for baking relevant objects'''
    bl_label = 'Object'
    
    object_types = ['MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'LIGHT']
    
    # Called to filter objects listed in the value search field
    def value_prop_filter(self, object):
        return self.node.input_filter(self.name, object)
        
    def cage_prop_filter(self, cage):
        return cage.type == 'MESH'
    
    # Try to auto locate the cage by name when enabled
    def use_cage_update(self, context):
        if self.use_cage and not self.cage and self.value:
            for obj in bpy.data.objects:
                if obj.name.startswith(self.value.name) and obj.name.lower().startswith("cage", len(self.value.name) + 1):
                    self.cage = obj
                    break
            
    # Called when the value property changes
    def value_prop_update(self, context):
        self.type = 'NONE'
        if self.value:
            if self.value.rna_type.identifier == 'Collection':
                self.type = 'GROUP'
            elif self.value.rna_type.identifier == 'Object':
                if self.value.type in self.object_types:
                    self.type = '%s_DATA' % (self.value.type)                
        if self.node:
            self.node.update_inputs()
            
    # Get own objects or the full linked tree
    def get_objects(self, only_mesh=False, no_lights=False):
        objects = []
        # Follow links
        if self.islinked() and self.valid:
            return follow_input_link(self.links[0]).from_node.get_objects(only_mesh, no_lights)
        # Otherwise return self values
        if self.value and self.type and self.type != 'NONE' and not self.is_linked:
            # Only interested in mesh types?
            if self.type not in ['MESH_DATA', 'GROUP'] and only_mesh:
                return []
            if self.type == 'LIGHT_DATA' and no_lights:
                return []
            # Need to get all the grouped objects
            if self.type == 'GROUP':
                filter = list(self.object_types)
                if no_lights:
                    filter.remove('LIGHT')
                if only_mesh:
                    filter = ['MESH']
                # Iterate over the objects applying the type filter
                for obj in self.get_grouped():
                    if obj.type in filter:
                        objects.append([obj])
            # Mesh data can have a few extra properties
            elif self.type == 'MESH_DATA':
                uv_map = ""
                if self.pick_uv and self.uv_map:
                    uv_map = self.uv_map
                cage = None
                if self.use_cage and self.cage:
                    cage = self.cage
                objects.append([self.value, uv_map, cage])
            else:
                objects.append([self.value])
        return objects
    
    # Return objects contained in a group
    def get_grouped(self):
        if self.recursive:
            return self.value.all_objects
        else:
            return self.value.objects
            
    # Validate value(s)
    def validate(self, check_materials=False, check_as_active=False, check_multi=False):
        valid = [True]
        # Follow links
        if self.islinked() and self.valid:
            return follow_input_link(self.links[0]).from_node.validate(check_materials, check_as_active, check_multi)
        # Has a value and isn't linked
        if self.value and self.type and not self.islinked():
            objs = [self.value]
            if self.type == 'GROUP':
                objs = self.get_grouped()
                
            # Iterate over objs, it will just be one object unless the type is group (but maintains a single algo for both)
            for obj in objs:
                # Perform checks needed for an active bake target
                if check_as_active:
                    # Only a mesh type object can be a valid target, it will just be silently ignored
                    if obj.type != 'MESH':
                        return valid
                    # Check the cage is valid if one is in use (can't be done for grouped objects)
                    if self.type != 'GROUP' and not check_multi and self.use_cage and self.cage:
                        if len(obj.data.polygons) != len(self.cage.data.polygons):
                            valid[0] = False
                            valid.append([_print("Cage error", node=self.node, ret=True), ": Cage <%s> face count does not match object <%s>." % (self.cage.name, obj.name)])
                    # Any UV map?
                    if len(obj.data.uv_layers) < 1:
                        valid[0] = False
                        valid.append([_print("UV error", node=self.node, ret=True), ": No UV Maps found on object <%s>." % (obj.name)])
                    # Custom UV map still exists? (can't be done for grouped objects)
                    if self.type != 'GROUP' and self.pick_uv and self.uv_map not in obj.data.uv_layers and self.uv_map != "":
                        valid[0] = False
                        valid.append([_print("UV error", node=self.node, ret=True), ": Selected UV map <%s> not present on object <%s> (it could have been deleted or renamed)" % (self.uv_map, obj.name)])
                    # Check for a valid multi-res mod if enabled 
                    if check_multi:
                        has_multi_mod = False
                        if len(obj.modifiers):
                            for mod in obj.modifiers:
                                if mod.type == 'MULTIRES' and mod.total_levels > 0:
                                    has_multi_mod = True
                                    break
                        if not has_multi_mod:
                            valid[0] = False
                            valid.append([_print("Multires error", node=self.node, ret=True), ": No multires data on object <%s>." % (obj.name)])
                # Check that materials can be converted to enable PBR data bakes
                if check_materials and obj.type in self.object_types:
                    mats = []
                    if len(obj.material_slots):
                        for slot in obj.material_slots:
                            mat = slot.material
                            if mat != None and not mat in mats:
                                mats.append(mat)
                                # Is node based?
                                if not mat.node_tree or not mat.node_tree.nodes:
                                    valid.append([_print("Material warning", node=self.node, ret=True), ": <%s> not a node based material" % (mat.name)])
                                    continue
                                # Is a 'principled' material?
                                passed = False
                                for node in mat.node_tree.nodes:
                                    if node.type == 'OUTPUT_MATERIAL' and node.target in ['CYCLES', 'ALL']:
                                        if material_recursor(node):
                                            passed = True
                                            break
                                if not passed:
                                    valid.append([_print("Material warning", node=self.node, ret=True), ": <%s> Output doesn't appear to be a valid combination of Principled and Mix shaders. Baked values will not be correct for this material." % (mat.name)])     
        return valid
            
    # Blender Properties
    value: bpy.props.PointerProperty(name="Object", description="Object to be used in some way in a bake pass", type=bpy.types.ID, poll=value_prop_filter, update=value_prop_update)
    type: bpy.props.StringProperty(name="Type", description="ID String of value type", default="NONE")
    recursive: bpy.props.BoolProperty(name="Recursive Selection", description="When enabled all collections within the selected collection will be used", default=False)
    pick_uv: bpy.props.BoolProperty(name="Pick UV Map", description="Enables selecting which UV map to use instead of the active one", default=False)
    uv_map: bpy.props.StringProperty(name="UV Map", description="UV Map to use instead of active if value is a mesh", default="")
    use_cage: bpy.props.BoolProperty(name="Use Cage", description="Enables cage usage and selection of cage mesh", default=False, update=use_cage_update)
    cage: bpy.props.PointerProperty(name="Cage", description="Mesh to use a cage", type=bpy.types.Object, poll=cage_prop_filter)
    
    def draw(self, context, layout, node, text):
        if not self.is_output and not self.islinked():
            row = layout.row(align=True)
            label = ""
            if self.name in ['Target', 'Source', 'Scene']:
                label = self.name
            if self.name in ['Target', 'Source'] or (hasattr(node, "filter_collection") and not node.filter_collection):
                row.prop_search(self, "value", bpy.data, "objects", text=label, icon=self.type)
            else:
                row.prop_search(self, "value", bpy.data, "collections", text=label, icon=self.type)
            if self.value and self.type:
                if self.type == 'GROUP':
                    row.prop(self, "recursive", icon='OUTLINER', text="")
                if self.type == 'MESH_DATA':
                    row.prop(self, "pick_uv", icon='UV', text="")
                    if self.pick_uv:
                        row.prop_search(self, "uv_map", self.value.data, "uv_layers", text="", icon='UV_DATA')
                    row.prop(self, "use_cage", icon='FILE_VOLUME', text="")
                    if self.use_cage:
                        row.prop_search(self, "cage", bpy.data, "objects", text="", icon='MESH_DATA')
        else:
            layout.label(text=BakeWrangler_Tree_Socket.socket_label(self, text))

    def draw_color(self, context, node):
        return BakeWrangler_Tree_Socket.socket_color(self, (0.0, 0.2, 1.0, 1.0))
        
    
# Socket for sharing a target mesh
class BakeWrangler_Socket_Mesh(NodeSocket, BakeWrangler_Tree_Socket):
    '''Socket for connecting a mesh node'''
    bl_label = 'Mesh'
    
    def draw(self, context, layout, node, text):
        layout.label(text=BakeWrangler_Tree_Socket.socket_label(self, text))

    def draw_color(self, context, node):
        return BakeWrangler_Tree_Socket.socket_color(self, (0.0, 0.5, 1.0, 1.0))
    
    
# Socket for RGB(A) data, extends the base color node
class BakeWrangler_Socket_Color(NodeSocketColor, BakeWrangler_Tree_Socket):
    '''Socket for RGB(A) data'''
    bl_label = 'Color'
    
    def draw(self, context, layout, node, text):
        layout.label(text=BakeWrangler_Tree_Socket.socket_label(self, text))
        
    def draw_color(self, context, node):
        return BakeWrangler_Tree_Socket.socket_color(self, (0.78, 0.78, 0.16, 1.0))


# Socket for Float data, extends the base float node
class BakeWrangler_Socket_Float(NodeSocketFloat, BakeWrangler_Tree_Socket):
    '''Socket for Float data'''
    bl_label = 'Float'
    
    def draw(self, context, layout, node, text):
        layout.label(text=BakeWrangler_Tree_Socket.socket_label(self, text))
    
    def draw_color(self, context, node):
        return BakeWrangler_Tree_Socket.socket_color(self, (0.631, 0.631, 0.631, 1.0))


# Socket for connecting an output image to a batch job node
class BakeWrangler_Socket_Bake(NodeSocket, BakeWrangler_Tree_Socket):
    '''Socket for connecting an output image node to a batch node'''
    bl_label = 'Bake'
    
    def draw(self, context, layout, node, text):
        layout.label(text=BakeWrangler_Tree_Socket.socket_label(self, text))

    def draw_color(self, context, node):
        return BakeWrangler_Tree_Socket.socket_color(self, (1.0, 0.5, 1.0, 1.0))


# Custom Nodes:

# Base class for all bakery nodes. Identifies that they belong in the bakery tree.
class BakeWrangler_Tree_Node:
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'BakeWrangler_Tree_Node'
    
    def get_name(self):
        name = self.name
        #if self.label:
        #    name += ".%s" % (self.label)
        return name
    
    def validate(self):
        return [True]
        
    # Makes sure there is always one empty input socket at the bottom by adding and removing sockets
    def update_inputs(self, socket_type, socket_name):
        idx = 0
        for socket in self.inputs:
            if socket.is_linked or (hasattr(socket, 'value') and socket.value):
                if len(self.inputs) == idx + 1:
                    self.inputs.new(socket_type, socket_name)
            else:
                if len(self.inputs) > idx + 1:
                    self.inputs.remove(socket)
                    idx = idx - 1
            idx = idx + 1
    
    # Update inputs and links on updates
    def update(self):
        self.update_inputs()
        # Links can get inserted without calling insert_link, but update is called.
        for socket in self.inputs:
            if socket.islinked():
                self.insert_link(socket.links[0])
    
    # Validate incoming links
    def insert_link(self, link):
        if link.to_node == self:
            if follow_input_link(link).from_socket.bl_idname == link.to_socket.bl_idname and link.is_valid:
                link.to_socket.valid = True
            else:
                link.to_socket.valid = False
                
    # Draw bake button in correct state
    def draw_bake_button(self, layout, icon, label):
        if self.id_data.baking != None:
            if self.id_data.baking.node == self.name:
                if self.id_data.baking.stop(kill=False):
                    layout.operator("bake_wrangler_op.dummy", icon='CANCEL', text="Stopping...")
                else:
                    op = layout.operator("bake_wrangler_op.bake_stop", icon='CANCEL')
                    op.tree = self.id_data.name
                    op.node = self.name
            else:
                layout.operator("bake_wrangler_op.dummy", icon=icon, text=label)
        else:
            op = layout.operator("bake_wrangler_op.bake_pass", icon=icon, text=label)
            op.tree = self.id_data.name
            op.node = self.name


# Input node that contains a list of objects relevant to baking
class BakeWrangler_Input_ObjectList(Node, BakeWrangler_Tree_Node):
    '''Object list node'''
    bl_label = 'Objects'
    bl_width_default = 198
    
    # Makes sure there is always one empty input socket at the bottom by adding and removing sockets
    def update_inputs(self):
        BakeWrangler_Tree_Node.update_inputs(self, 'BakeWrangler_Socket_Object', "Object")
        
    # Determine if object meets current input filter
    def input_filter(self, input_name, object):
        if self.filter_collection:
            if object.rna_type.identifier == 'Collection':
                return True
        elif object.rna_type.identifier == 'Object':
            if (self.filter_mesh and object.type == 'MESH') or \
               (self.filter_curve and object.type == 'CURVE') or \
               (self.filter_surface and object.type == 'SURFACE') or \
               (self.filter_meta and object.type == 'META') or \
               (self.filter_font and object.type == 'FONT') or \
               (self.filter_light and object.type == 'LIGHT'):
                return True
        return False
    
    # Get all objects in tree from this node (mostly just uses the sockets methods)
    def get_objects(self, only_mesh=False, no_lights=False):
        objects = []
        for input in self.inputs:
            in_objs = input.get_objects(only_mesh, no_lights)
            if len(in_objs):
                objects += in_objs
        return objects
        
    # Validate all objects in tree from this node (mostly just uses the sockets methods)
    def validate(self, check_materials=False, check_as_active=False, check_multi=False):
        valid = [True]
        for input in self.inputs:
            valid_input = input.validate(check_materials, check_as_active, check_multi)
            if not valid_input.pop(0):
                valid[0] = False
            if len(valid_input):
                valid += valid_input
        return valid
        
    filter_mesh: bpy.props.BoolProperty(name="Meshes", description="Show mesh type objects", default=True)
    filter_curve: bpy.props.BoolProperty(name="Curves", description="Show curve type objects", default=True)
    filter_surface: bpy.props.BoolProperty(name="Surfaces", description="Show surface type objects", default=True)
    filter_meta: bpy.props.BoolProperty(name="Metas", description="Show meta type objects", default=True)
    filter_font: bpy.props.BoolProperty(name="Fonts", description="Show font type objects", default=True)
    filter_light: bpy.props.BoolProperty(name="Lights", description="Show light type objects", default=True)
    filter_collection: bpy.props.BoolProperty(name="Collections", description="Toggle only collections", default=False)
        
    def init(self, context):
        # Sockets IN
        self.inputs.new('BakeWrangler_Socket_Object', "Object")
        # Sockets OUT
        self.outputs.new('BakeWrangler_Socket_Object', "Objects")
        # Prefs
        self.filter_mesh = _prefs("def_filter_mesh")
        self.filter_curve = _prefs("def_filter_curve")
        self.filter_surface = _prefs("def_filter_surface")
        self.filter_meta = _prefs("def_filter_meta")
        self.filter_font = _prefs("def_filter_font")
        self.filter_light = _prefs("def_filter_light")
        self.filter_collection = _prefs("def_filter_collection")
         
    def draw_buttons(self, context, layout):
        row = layout.row(align=True)
        row0 = row.row()
        row0.label(text="Filter:")
        
        row1 = row.row(align=True)
        row1.alignment = 'RIGHT'
        row1.prop(self, "filter_mesh", text="", icon='MESH_DATA')
        row1.prop(self, "filter_curve", text="", icon='CURVE_DATA')
        row1.prop(self, "filter_surface", text="", icon='SURFACE_DATA')
        row1.prop(self, "filter_meta", text="", icon='META_DATA')
        row1.prop(self, "filter_font", text="", icon='FONT_DATA')
        row1.prop(self, "filter_light", text="", icon='LIGHT_DATA')
        if self.filter_collection:
            row1.enabled = False
        
        row2 = row.row(align=False)
        row2.alignment = 'RIGHT'
        row2.prop(self, "filter_collection", text="", icon='GROUP')
        
        
# Mesh settings to be used when baking attached objects
class BakeWrangler_Bake_Mesh(Node, BakeWrangler_Tree_Node):
    '''Mesh settings node'''
    bl_label = 'Mesh'
    bl_width_default = 240
    
    # Inputs are static on this node
    def update_inputs(self):
        pass
        
    # Determine if object meets current input filter
    def input_filter(self, input_name, object):
        if input_name == "Target":
            if object.type == 'MESH':
                return True
        elif input_name == "Source":
            if object.type in ['MESH', 'CURVE', 'SURFACE', 'META', 'FONT']:
                return True
        elif input_name == "Scene":
            if object.rna_type.identifier == 'Collection':
                return True
        return False
        
    # Check node settings are valid to bake. Returns true/false, plus error message.
    def validate(self, check_materials=False, multires=False):
        valid = [True]
        # Check source objects
        has_selected = False
        if not multires:
            has_selected = len(self.inputs["Source"].get_objects()) > 0
        if has_selected and check_materials:
            valid_selected = self.inputs["Source"].validate(check_materials)
            # Add any generated messages to the stack. Material errors wont stop bake
            if len(valid_selected) > 1:
                valid_selected.pop(0)
                valid += valid_selected
                
        # Check target meshes
        has_active = len(self.inputs["Target"].get_objects(True)) > 0
        if has_active:
            valid_active = self.inputs["Target"].validate(check_materials, True, multires)
            valid[0] = valid_active.pop(0)
            # Add any generated messages to the stack. Errors here will stop bake
            if len(valid_active):
                valid += valid_active
        else:
            valid[0] = False
            valid.append([_print("Target error", node=self, ret=True), ": No valid target objects selected"])
        return valid
        
    # Return the requested set of objects from the appropriate input socket
    def get_objects(self, set):
        _print("Getting objects in %s" % (set))
        objs = []
        count = []
        dups = []
        if set == 'TARGET':
            objs = self.inputs["Target"].get_objects(only_mesh=True)
        elif set == 'SOURCE':
            objs = self.inputs["Source"].get_objects(no_lights=True)
        elif set == 'SCENE':
            objs = self.inputs["Scene"].get_objects()      
        # First remove duplicates
        for obj in objs:
            if objs.count(obj) > 1:
                objs.remove(obj)
        # Then remove non duplicate entries that reference the same object where appropriate
        for obj in objs:
            # Get a list of just the referenced objects to count them
            count.append(obj[0])
        for obj in count:
            # Create a list of objects with multiple refs and count how many
            if count.count(obj) > 1:
                found = False
                for dup in dups:
                    if dup[0] == obj:
                        found = True
                        dup[1] += 1
                        break
                if not found:
                    dups.append([obj, 1])
        for obj in dups:
            # Go over all the duplicate entries and prune appropriately
            num = obj[1]
            for dup in objs:
                if dup[0] == obj[0]:
                    # For target set, remove only dups that came from a group (the user may
                    # want the same object with different settings)
                    if set == 'TARGET':
                        if len(dup) == 1:
                            objs.remove(dup)
                            num -= 1
                    # For other sets just reduce to one reference
                    else:
                        objs.remove(dup)
                        num -= 1
                    # Break out when/if one dup remains
                    if num == 1:
                        break
                
        if _prefs('debug'):
            _print("%s objects:" % (set))
            for obj in objs:
                _print(obj)
                
        # Return pruned object list
        return objs
        
    ray_dist: bpy.props.FloatProperty(name="Ray Distance", description="Distance to use for inward ray cast when using a selected to active bake", default=0.01, step=1, min=0.0, unit='LENGTH')
    margin: bpy.props.IntProperty(name="Margin", description="Extends the baked result as a post process filter", default=0, min=0, subtype='PIXEL')
    mask_margin: bpy.props.IntProperty(name="Mask Margin", description="Adds extra padding to the mask bake. Use if edge details are being cut off when masking is enabled", default=0, min=0, subtype='PIXEL')
    
    def init(self, context):
        # Sockets IN
        self.inputs.new('BakeWrangler_Socket_Object', "Target")
        self.inputs.new('BakeWrangler_Socket_Object', "Source")
        self.inputs.new('BakeWrangler_Socket_Object', "Scene")
        # Sockets OUT
        self.outputs.new('BakeWrangler_Socket_Mesh', "Mesh")
        # Prefs
        self.ray_dist = _prefs("def_raydist")
        self.margin = _prefs("def_margin")
        self.mask_margin = _prefs("def_mask_margin")
        
    def draw_buttons(self, context, layout):
        col = layout.column(align=False)
        col.prop(self, "margin")
        col.prop(self, "mask_margin")
        col.prop(self, "ray_dist")

        
        
# Baking node that holds all the settings for a type of bake 'pass'. Takes one or more mesh input nodes as input.
class BakeWrangler_Bake_Pass(Node, BakeWrangler_Tree_Node):
    '''Baking pass node'''
    bl_label = 'Pass'
    bl_width_default = 160
    
    # Returns the most identifing string for the node
    def get_name(self):
        name = BakeWrangler_Tree_Node.get_name(self)
        if self.bake_pass:
            name += " (%s)" % (self.bake_pass)
        return name
    
    # Makes sure there is always one empty input socket at the bottom by adding and removing sockets
    def update_inputs(self):
        BakeWrangler_Tree_Node.update_inputs(self, 'BakeWrangler_Socket_Mesh', "Mesh")
        
    # Update node label based on selected pass
    def update_pass(self, context):
        if self.label == "":
            pass_label = ""
            for pas in self.bake_passes:
                if pas[0] == self.bake_pass:
                    self.label = "Pass: " + pas[1]
        elif ":" in self.label:
            start, sep, end = self.label.rpartition(":")
            for val in self.bake_passes:
                if val[1] in end:
                    pass_label = ""
                    for pas in self.bake_passes:
                        if pas[0] == self.bake_pass:
                            pass_label = pas[1]
                    end = end.replace(val[1], pass_label)
                    self.label = start + sep + end
                    break
        
    # Check node settings are valid to bake. Returns true/false, plus error message(s).
    def validate(self, is_primary=False):
        valid = [True]
        # Validate inputs
        has_valid_input = False
        is_multires = (self.bake_pass == 'MULTIRES')
        for input in self.inputs:
            if input.islinked() and input.valid:
                if self.bake_pass in self.bake_pbr:
                    input_valid = follow_input_link(input.links[0]).from_node.validate(check_materials=True)
                else:
                    input_valid = follow_input_link(input.links[0]).from_node.validate(multires=is_multires)
                if not input_valid.pop(0):
                    valid[0] = False
                else:
                    has_valid_input = True
                if len(input_valid):
                    valid += input_valid
        errs = len(valid)
        if not has_valid_input and errs < 2:
            valid[0] = False
            valid.append([_print("Input error", node=self, ret=True), ": No valid inputs connected"])
        # Validate outputs
        if is_primary:
            has_valid_output = False
            for output in self.outputs:
                if output.is_linked:
                    for link in gather_output_links(output):
                        if link.is_valid and link.to_socket.valid:
                            output_valid = link.to_node.validate()
                            if not output_valid.pop(0):
                                valid[0] = False
                            else:
                                has_valid_output = True
                            if len(output_valid):
                                valid += output_valid
            if not has_valid_output and errs == len(valid):
                valid[0] = False
                valid.append([_print("Output error", node=self, ret=True), ": No valid outputs connected"])
        # Validated
        return valid
    
    bake_passes = (
        ('ALBEDO', "Albedo", "Surface color without lighting (Principled shader only)"),
        ('METALLIC', "Metallic", "Surface 'metalness' values (Principled shader only)"),
        ('SPECULAR', "Specular", "Surface specular values (Princpled shader only)"),
        ('ALPHA', "Alpha", "Surface transparency values (Principled shader only)"),
        
        ('NORMAL', "Normal", "Surface normals"),
        ('CURVATURE', "Curvature", "Surface curvature map computed from tangent normals"),
        ('ROUGHNESS', "Roughness", "Surface roughness values"),
        ('SMOOTHNESS', "Smoothness", "Surface inverted roughness values"),
        ('AO', "Ambient Occlusion", "Surface self occlusion values"),
        ('CAVITY', "Cavity", "Surface cavity occlusion map"),
        
        #('SUBSURFACE', "Subsurface", "Subsurface color"),
        ('TRANSMISSION', "Transmission", "Colors of light passing through a material"),
        ('GLOSSY', "Glossy", "Colors of a surface generated by a glossy shader"),
        ('DIFFUSE', "Diffuse", "Colors of a surface generated by a diffuse shader"),
        ('ENVIRONMENT', "Environment", "Colors coming from the environment"),
        ('EMIT', "Emit", "Surface self emission color values"),
        ('UV', "UV", "UV Layout"),
        ('SHADOW', "Shadow", "Shadow map"),
        ('COMBINED', "Combined", "Combine multiple passes into a single bake"),
        
        ('MULTIRES', "Multiresolution", "Data from a multiresolution modifier"),
    )
    
    bake_built_in = ['NORMAL', 'ROUGHNESS', 'AO', 'SUBSURFACE', 'TRANSMISSION', 'GLOSSY', 'DIFFUSE', 'ENVIRONMENT', 'EMIT', 'UV', 'SHADOW', 'COMBINED']
    bake_pbr = ['ALBEDO', 'METALLIC', 'ALPHA', 'CAVITY', 'SPECULAR']
    bake_has_influence = ['SUBSURFACE', 'TRANSMISSION', 'GLOSSY', 'DIFFUSE', 'COMBINED']
    
    normal_spaces = (
        ('TANGENT', "Tangent", "Bake the normals in tangent space"),
        ('OBJECT', "Object", "Bake the normals in object space"),
    )
    
    normal_swizzle = (
        ('POS_X', "+X", ""),
        ('POS_Y', "+Y", ""),
        ('POS_Z', "+Z", ""),
        ('NEG_X', "-X", ""),
        ('NEG_Y', "-Y", ""),
        ('NEG_Z', "-Z", ""),
    )
    
    multires_subpasses = (
        ('NORMALS', "Normals", "Bake Normals"),
        ('DISPLACEMENT', "Displacement", "Bake Displacement"),
    )
    
    multires_sampling = (
        ('MAXIMUM', "Max to Min", "Bake the highest resolution down to the lowest"),
        ('FROMMOD', "Modifier Values", "Bake from the current render resolution to the current preview resolution"),
        ('CUSTOM', "Custom Values", "Choose custom values for the target and source resolutions"),
    )
    
    cycles_devices = (
        ('CPU', "CPU", "Use CPU for baking"),
        ('GPU', "GPU", "Use GPU for baking"),
    )

    bake_pass: bpy.props.EnumProperty(name="Pass", description="Type of pass to bake", items=bake_passes, default='NORMAL', update=update_pass)
    bake_samples: bpy.props.IntProperty(name="Bake Samples", description="Number of samples to bake for each pixel. Use 25 to 50 samples for most bake types (AO may look better with more).\nQuality is gained by increaseing resolution rather than samples past that point", default=32, min=1)
    bake_xres: bpy.props.IntProperty(name="Bake X resolution", description="Number of horizontal pixels in bake. Power of 2 image sizes are recommended for exporting", default=1024, min=1, subtype='PIXEL')
    bake_yres: bpy.props.IntProperty(name="Bake Y resolution", description="Number of vertical pixels in bake. Power of 2 image sizes are recommended for exporting", default=1024, min=1, subtype='PIXEL')
    use_mask: bpy.props.BoolProperty(name="Use Masking", description="Generate a map of changed UV islands to use as a mask when updating pixel values. Allows layering of multiple passes onto a single image so long as they don't overlap", default=False)
    norm_space: bpy.props.EnumProperty(name="Space", description="Space to bake the normals in", items=normal_spaces, default='TANGENT')
    norm_R: bpy.props.EnumProperty(name="R", description="Axis to bake in Red channel", items=normal_swizzle, default='POS_X')
    norm_G: bpy.props.EnumProperty(name="G", description="Axis to bake in Green channel", items=normal_swizzle, default='POS_Y')
    norm_B: bpy.props.EnumProperty(name="B", description="Axis to bake in Blue channel", items=normal_swizzle, default='POS_Z')
    bake_device: bpy.props.EnumProperty(name="Device", description="Bake device", items=cycles_devices, default='CPU')
    use_direct: bpy.props.BoolProperty(name="Direct", description="Add direct lighting contribution", default=True)
    use_indirect: bpy.props.BoolProperty(name="Indirect", description="Add indirect lighting contribution", default=True)
    use_color: bpy.props.BoolProperty(name="Color", description="Color the pass", default=True)
    use_diffuse: bpy.props.BoolProperty(name="Diffuse", description="Add diffuse contribution", default=True)
    use_glossy: bpy.props.BoolProperty(name="Glossy", description="Add glossy contribution", default=True)
    use_transmission: bpy.props.BoolProperty(name="Transmission", description="Add transmission contribution", default=True)
    use_subsurface: bpy.props.BoolProperty(name="Subsurface", description="Add subsurface contribution", default=True)
    use_ao: bpy.props.BoolProperty(name="Ambient Occlusion", description="Add ambient occlusion contribution", default=True)
    use_emit: bpy.props.BoolProperty(name="Emit", description="Add emission contribution", default=True)
    curve_val: bpy.props.FloatProperty(name="Curvature Width", description="Controls the relative thickness (UV space) a curve takes up", default=1.0, min=0.1, max=2.0, step=1)
    use_world: bpy.props.BoolProperty(name="Use World", description="Enabled to pick a world to use (empty to use active), instead of Bake Wranglers default", default=False)
    the_world: bpy.props.PointerProperty(name="World", description="World to use instead of Bake Wranglers default (empty to use active)", type=bpy.types.World)
    cpy_render: bpy.props.BoolProperty(name="Copy Settings", description="Copy render settings from selected scene (empty to use active), instead of using defaults", default=False)
    cpy_from: bpy.props.PointerProperty(name="Render Scene", description="Scene to copy render settings from (empty to use active)", type=bpy.types.Scene)
    cavity_samp: bpy.props.IntProperty(name="Cavity Over Samples", description="Number of cavity samples per point (more gives a better result but takes longer)", default=16)
    cavity_dist: bpy.props.FloatProperty(name="Cavity Sample Distance", description="How far away a face can be to contribute to the cavity calculation (may need larger distances for larger objects)", default=0.4, step=1, min=0.0, unit='LENGTH')
    cavity_gamma: bpy.props.FloatProperty(name="Cavity Gamma", description="Gamma transform to be performed on cavity values", default=1.0, step=1)
    multi_pass: bpy.props.EnumProperty(name="Multires Type", description="Type of multiresolution pass to bake", items=multires_subpasses, default='NORMALS')
    multi_samp: bpy.props.EnumProperty(name="Multires Method", description="Method to pick multiresolution source and target", items=multires_sampling, default='MAXIMUM')
    multi_targ: bpy.props.IntProperty(name="Multires Target", description="Subdivision level for target of bake", default=0, min=0, soft_max=16)
    multi_sorc: bpy.props.IntProperty(name="Multires Source", description="Subdivision level for source of bake", default=8, min=0, soft_max=16)
    adv_settings: bpy.props.BoolProperty(name="Advanced Settings", description="Show or hide advanced settings", default=False)
    
    def init(self, context):
        # Set label to pass
        for pas in self.bake_passes:
            if pas[0] == self.bake_pass:
                self.label = "Pass: " + pas[1]
        # Sockets IN
        self.inputs.new('BakeWrangler_Socket_Mesh', "Mesh")
        # Sockets OUT
        self.outputs.new('BakeWrangler_Socket_Color', "Color")
        self.outputs.new('BakeWrangler_Socket_Float', "R")
        self.outputs.new('BakeWrangler_Socket_Float', "G")
        self.outputs.new('BakeWrangler_Socket_Float', "B")
        self.outputs.new('BakeWrangler_Socket_Float', "Value")
        # Prefs
        self.bake_samples = _prefs("def_samples")
        self.bake_xres = _prefs("def_xres")
        self.bake_yres = _prefs("def_yres")
        self.bake_device = self.cycles_devices[int(_prefs("def_device"))][0]
        self.adv_settings = _prefs("def_show_adv")

    def draw_buttons(self, context, layout):
        BakeWrangler_Tree_Node.draw_bake_button(self, layout, 'RENDER_STILL', "Bake Pass")
        colnode = layout.column(align=False)
        
        colpass = colnode.column(align=True)
        colpass.prop(self, "bake_pass")
        
        colbake = colnode.column(align=True)
        split = colbake.split(factor=0.4)
        split.label(text="Samples:")
        split.prop(self, "bake_samples", text="")
        
        colres = colnode.column(align=True)
        colres.prop(self, "bake_xres", text="X")
        colres.prop(self, "bake_yres", text="Y")
        
        advrow = colnode.row()
        advrow.alignment = 'LEFT'
        
        if not self.adv_settings:
            advrow.prop(self, "adv_settings", icon="DISCLOSURE_TRI_RIGHT", emboss=False, text="Advanced Settings:")
            advrow.separator()
        else:
            advrow.prop(self, "adv_settings", icon="DISCLOSURE_TRI_DOWN", emboss=False, text="Advanced Settings:")
            advrow.separator()
            
            split = colnode.split(factor=0.4)
            split.label(text="Device:")
            split.prop(self, "bake_device", text="")
            
            colnode.prop(self, "use_mask")
            
            row = colnode.row(align=True)
            row.prop(self, "use_world", text="Use My World", toggle=True)
            if self.use_world:
                row.prop_search(self, "the_world", bpy.data, "worlds", text="")
                
            row = colnode.row(align=True)
            row.prop(self, "cpy_render", text="Use My Settings", toggle=True)
            if self.cpy_render:
                row.prop_search(self, "cpy_from", bpy.data, "scenes", text="")
            
            rowpassopt = colnode.row()
            rowpassopt.alignment = 'RIGHT'
            splitopt = colnode.split(factor=0.5)
            colopttxt = splitopt.column(align=True)
            colopttxt.alignment = 'RIGHT'
            coloptval = splitopt.column(align=True)
            
            if self.bake_pass == 'NORMAL':
                rowpassopt.label(text="Normal Options:")
                
                colopttxt.label(text="Space:")
                colopttxt.label(text="R:")
                colopttxt.label(text="G:")
                colopttxt.label(text="B:")
                
                coloptval.prop(self, "norm_space", text="")
                coloptval.prop(self, "norm_R", text="")
                coloptval.prop(self, "norm_G", text="")
                coloptval.prop(self, "norm_B", text="")
            elif self.bake_pass == 'MULTIRES':
                rowpassopt.label(text="Multires Options:")
                
                colopttxt.label(text="Type:")
                colopttxt.label(text="Method:")
                
                coloptval.prop(self, "multi_pass", text="")
                coloptval.prop(self, "multi_samp", text="")
                if self.multi_samp == 'CUSTOM':
                    colopttxt.label(text="Target Divs:")
                    colopttxt.label(text="Source Divs:")
                    
                    coloptval.prop(self, "multi_targ", text="")
                    coloptval.prop(self, "multi_sorc", text="")
            elif self.bake_pass == 'CURVATURE':
                rowpassopt.label(text="Curvature Options:")
                
                colopttxt.label(text="Width:")
                
                coloptval.prop(self, "curve_val", text="")
            elif self.bake_pass == 'CAVITY':
                rowpassopt.label(text="Cavity Options:")
                
                colopttxt.label(text="Over Samples:")
                colopttxt.label(text="Distance:")
                colopttxt.label(text="Gamma:")
                
                coloptval.prop(self, "cavity_samp", text="")
                coloptval.prop(self, "cavity_dist", text="")
                coloptval.prop(self, "cavity_gamma", text="")
            elif self.bake_pass in self.bake_has_influence:
                rowpassopt.label(text="Influence Options:")
                
                row = colnode.row(align=True)
                row.use_property_split = False
                row.prop(self, "use_direct", toggle=True)
                row.prop(self, "use_indirect", toggle=True)
                if self.bake_pass != 'COMBINED':
                    row.prop(self, "use_color", toggle=True)
                else:
                    col = colnode.column(align=True)
                    col.prop(self, "use_diffuse")
                    col.prop(self, "use_glossy")
                    col.prop(self, "use_transmission")
                    #col.prop(self, "use_subsurface")
                    col.prop(self, "use_ao")
                    col.prop(self, "use_emit")

# Output node that specifies the path to a file where a bake should be saved along with size and format information.
# Takes input from the outputs of a bake pass node. Connecting multiple inputs will cause higher position inputs to
# be over written by lower ones. Eg: Having a color input and an R input would cause the R channel of the color data
# to be overwritten by the data connected tot he R input.
class BakeWrangler_Output_Image_Path(Node, BakeWrangler_Tree_Node):
    '''Output image path node'''
    bl_label = 'Output Image Path'
    bl_width_default = 160
    
    # Returns the most identifying string for the node
    def get_name(self):
        name = BakeWrangler_Tree_Node.get_name(self)
        if self.img_name:
            name += " (%s)" % (self.img_name)
        return name
        
    def update_inputs(self):
        pass
    
    # Check node settings are valid to bake. Returns true/false, plus error message(s).
    def validate(self, is_primary=False):
        valid = [True]
        # Validate inputs
        has_valid_input = False
        for input in self.inputs:
            if input.islinked() and input.valid:
                if not is_primary:
                    has_valid_input = True
                    break
                else:
                    input_valid = follow_input_link(input.links[0]).from_node.validate()
                    valid[0] = input_valid.pop(0)
                    if valid[0]:
                        has_valid_input = True
                    valid += input_valid    
        errs = len(valid)
        if not has_valid_input and errs < 2:
            valid[0] = False
            valid.append([_print("Input error", node=self, ret=True), ": No valid inputs connected"])
        # Validate file path
        if not os.path.isdir(os.path.abspath(self.img_path)):
            # Try creating the path if enabled in prefs
            if _prefs("make_dirs") and not os.path.exists(os.path.abspath(self.img_path)):
                try:
                    os.makedirs(os.path.abspath(self.img_path))
                except OSError as err:
                    valid[0] = False
                    valid.append([_print("Path error", node=self, ret=True), ": Trying to create path at '%s'" % (err.strerror)])
                    return valid
            else:
                valid[0] = False
                valid.append([_print("Path error", node=self, ret=True), ": Invalid path '%s'" % (os.path.abspath(self.img_path))])
                return valid
        # Check if there is read/write access to the file/directory
        file_path = os.path.join(os.path.abspath(self.img_path), self.name_with_ext())
        if os.path.exists(file_path):
            if os.path.isfile(file_path):
                # It exists so try to open it r/w
                try:
                    file = open(file_path, "a")
                except OSError as err:
                    valid[0] = False
                    valid.append([_print("File error", node=self, ret=True), ": Trying to open file at '%s'" % (err.strerror)])
                else:
                    # See if it can be read as an image
                    file.close()
                    file_img = bpy.data.images.load(file_path)
                    if not len(file_img.pixels):
                        valid[0] = False
                        valid.append([_print("File error", node=self, ret=True), ": File exists but doesn't seem to be a known image format"])
                    bpy.data.images.remove(file_img)
            else:
                # It exists but isn't a file
                valid[0] = False
                valid.append([_print("File error", node=self, ret=True), ": File exists but isn't a regular file '%s'" % (file_path)])
        else:
            # See if it can be created
            try:
                file = open(file_path, "a")
            except OSError as err:
                valid[0] = False
                valid.append([_print("File error", node=self, ret=True), ": %s trying to create file at '%s'" % (err.strerror, file_path)])
            else:
                file.close()
                os.remove(file_path)
        # Validated
        return valid
    
    # Get full path, removing any relative references
    def get_full_path(self, context):
        cwd = os.path.dirname(bpy.data.filepath)
        self.img_path = os.path.normpath(os.path.join(cwd, bpy.path.abspath(self.disp_path)))
    
    # Return the file name with the correct image type extension (unless it has an existing unknown extension)
    def name_with_ext(self):
        name, ext = os.path.splitext(self.img_name)
        if ext not in [".", "", None]:
            for enum, iext in self.img_ext:
                if ext.lower() == iext:
                    for enum, iext in self.img_ext:
                        if self.img_type == enum:
                            return (name + iext)
                    break
            return self.img_name
        else:
            for enum, iext in self.img_ext:
                if self.img_type == enum:
                    return (name + iext)
    
    # Recreate image format drop down as the built in one doesn't seem usable? Also most of the settings
    # for the built in image settings selector don't seem applicable to saving from script...
    img_format = (
        ('BMP', "BMP", "Output image in bitmap format."),
        ('IRIS', "Iris", "Output image in (old!) SGI IRIS format."),
        ('PNG', "PNG", "Output image in PNG format."),
        ('JPEG', "JPEG", "Output image in JPEG format."),
        ('JPEG2000', "JPEG 2000", "Output image in JPEG 2000 format."),
        ('TARGA', "Targa", "Output image in Targa format."),
        ('TARGA_RAW', "Targa Raw", "Output image in uncompressed Targa format."),
        ('CINEON', "Cineon", "Output image in Cineon format."),
        ('DPX', "DPX", "Output image in DPX format."),
        ('OPEN_EXR_MULTILAYER', "OpenEXR MultiLayer", "Output image in multilayer OpenEXR format."),
        ('OPEN_EXR', "OpenEXR", "Output image in OpenEXR format."),
        ('HDR', "Radiance HDR", "Output image in Radiance HDR format."),
        ('TIFF', "TIFF", "Output image in TIFF format."),
    )
    
    img_ext = (
        ('BMP', ".bmp"),
        ('IRIS', ".rgb"),
        ('PNG', ".png"),
        ('JPEG', ".jpg"),
        ('JPEG2000', ".jp2"),
        ('TARGA', ".tga"),
        ('TARGA_RAW', ".tga"),
        ('CINEON', ".cin"),
        ('DPX', ".dpx"),
        ('OPEN_EXR_MULTILAYER', ".exr"),
        ('OPEN_EXR', ".exr"),
        ('HDR', ".hdr"),
        ('TIFF', ".tif"),
    )
    
    img_color_modes = (
        ('BW', "BW", "Image saved in 8 bit grayscale"),
        ('RGB', "RGB", "Image saved with RGB (color) data"),
        ('RGBA', "RGBA", "Image saved with RGB and Alpha data"),
    )
    
    img_color_modes_noalpha = (
        ('BW', "BW", "Image saved in 8 bit grayscale"),
        ('RGB', "RGB", "Image saved with RGB (color) data"),
    )
    
    img_color_depths_8_16 = (
        ('8', "8", "8 bit color channels"),
        ('16', "16", "16 bit color channels"),
    )
    
    img_color_depths_8_12_16 = (
        ('8', "8", "8 bit color channels"),
        ('12', "12", "12 bit color channels"),
        ('16', "16", "16 bit color channels"),
    )
    
    img_color_depths_8_10_12_16 = (
        ('8', "8", "8 bit color channels"),
        ('10', "10", "10 bit color channels"),
        ('12', "12", "12 bit color channels"),
        ('16', "16", "16 bit color channels"),
    )
    
    img_color_depths_16_32 = (
        ('16', "Float (Half)", "16 bit color channels"),
        ('32', "Float (Full)", "32 bit color channels"),
    )
    
    img_codecs_jpeg2k = (
        ('JP2', "JP2", ""),
        ('J2K', "J2K", ""),
    )
    
    img_codecs_openexr = (
        ('DWAA', "DWAA (lossy)", ""),
        ('B44A', "B44A (lossy)", ""),
        ('ZIPS', "ZIPS (lossless)", ""),
        ('RLE', "RLE (lossless)", ""),
        ('RLE', "RLE (lossless)", ""),
        ('PIZ', "PIZ (lossless)", ""),
        ('ZIP', "ZIP (lossless)", ""),
        ('PXR24', "Pxr24 (lossy)", ""),
        ('NONE', "None", ""),
    )    
    
    img_codecs_tiff = (
        ('PACKBITS', "Pack Bits", ""),
        ('LZW', "LZW", ""),
        ('DEFLATE', "Deflate", ""),
        ('NONE', "None", ""),
    )
    
    img_color_spaces = (
        ('Filmic Log', "Filmic Log", "Log based filmic shaper with 16.5 stops of latitude, and 25 stops of dynamic range"),
        ('Linear', "Linear", "Rec. 709 (Full Range), Blender native linear space"),
        ('Linear ACES', "Linear ACES", "ACES linear space"),
        ('Non-Color', "Non-Color", "Color space used for images which contains non-color data (i,e, normal maps)"),
        ('Raw', "Raw", "Raw"),
        ('sRGB', "sRGB", "Standard RGB Display Space"),
        ('XYZ', "XYZ", "XYZ"),
    )
    
    # Return a dict of format settings
    def get_format(self):
        format = {}
        for prop in self.rna_type.properties.keys():
            format[prop] = getattr(self, prop)
        return format
    
    # Properties that are part of the ImageFormatSettings data, recreated here because that data block isn't usable by mods
    # Color Modes
    img_clear: bpy.props.BoolProperty(name="Clear Image", description="Clear image before writing bake data", default=False)
    img_use_float: bpy.props.BoolProperty(name="Use 32 Bit Float", description="Generate all input passes using 32 bit floating point color (128 bits per pixel). Note this isn't very useful if your image format isn't set to a high bit depth", default=False)
    img_color_mode: bpy.props.EnumProperty(name="Color", description="Choose BW for saving grayscale images, RGB for saving red, green and blue channels, and RGBA for saving red, green, blue and alpha channels", items=img_color_modes, default='RGB')
    img_color_mode_noalpha: bpy.props.EnumProperty(name="Color", description="Choose BW for saving grayscale images, RGB for saving red, green and blue channels", items=img_color_modes_noalpha, default='RGB')
    
    # Color Depths
    img_color_depth_8_16: bpy.props.EnumProperty(name="Color Depth", description="Bit depth per channel", items=img_color_depths_8_16, default='8')
    img_color_depth_8_12_16: bpy.props.EnumProperty(name="Color Depth", description="Bit depth per channel", items=img_color_depths_8_12_16, default='8')
    img_color_depth_8_10_12_16: bpy.props.EnumProperty(name="Color Depth", description="Bit depth per channel", items=img_color_depths_8_10_12_16, default='8')
    img_color_depth_16_32: bpy.props.EnumProperty(name="Color Depth", description="Bit depth per channel", items=img_color_depths_16_32, default='16')
    
    # Compression / Quality
    img_compression: bpy.props.IntProperty(name="Compression", description="Amount of time to determine best compression: 0 = no compression, 100 = maximum lossless compression", default=15, min=0, max=100, subtype='PERCENTAGE')
    img_quality: bpy.props.IntProperty(name="Quality", description="Quality for image formats that support lossy compression", default=90, min=0, max=100, subtype='PERCENTAGE')
    
    # Codecs
    img_codec_jpeg2k: bpy.props.EnumProperty(name="Codec", description="Codec settings for jpeg2000", items=img_codecs_jpeg2k, default='JP2')
    img_codec_openexr: bpy.props.EnumProperty(name="Codec", description="Codec settings for OpenEXR", items=img_codecs_openexr, default='ZIP')
    img_codec_tiff: bpy.props.EnumProperty(name="Compression", description="Compression mode for TIFF", items=img_codecs_tiff, default='DEFLATE')
    
    # Other random image format settings
    img_jpeg2k_cinema: bpy.props.BoolProperty(name="Cinema", description="Use Openjpeg Cinema Preset", default=True)
    img_jpeg2k_cinema48: bpy.props.BoolProperty(name="Cinema (48)", description="Use Openjpeg Cinema Preset (48 fps)", default=False)
    img_jpeg2k_ycc: bpy.props.BoolProperty(name="YCC", description="Save luminance-chrominance-chrominance channels instead of RGB colors", default=False)
    img_dpx_log: bpy.props.BoolProperty(name="Log", description="Convert to logarithmic color space", default=False)
    img_openexr_zbuff: bpy.props.BoolProperty(name="Z Buffer", description="Save the z-depth per pixel (32 bit unsigned int z-buffer)", default=True)
    
    # Core settings
    img_color_space: bpy.props.EnumProperty(name="Color Space", description="Color space to use when saving the image", items=img_color_spaces, default='sRGB')
    disp_path: bpy.props.StringProperty(name="Output Path", description="Path to save image in", default="", subtype='DIR_PATH', update=get_full_path)
    img_path: bpy.props.StringProperty(name="Output Path", description="Path to save image in", default="", subtype='DIR_PATH')
    img_name: bpy.props.StringProperty(name="Output File", description="File to save image in", default="Image", subtype='FILE_NAME')
    img_type: bpy.props.EnumProperty(name="Image Format", description="File format to save bake as", items=img_format, default='PNG')
    img_xres: bpy.props.IntProperty(name="Image X resolution", description="Number of horizontal pixels in image. Bake pass data will be scaled to fit the image size. Power of 2 sizes are usually best for exporting", default=2048, min=1, subtype='PIXEL')
    img_yres: bpy.props.IntProperty(name="Image Y resolution", description="Number of vertical pixels in image. Bake pass data will be scaled to fit the image size. Power of 2 sizes are usually best for exporting", default=2048, min=1, subtype='PIXEL')
    adv_settings: bpy.props.BoolProperty(name="Advanced Settings", description="Display or hide advanced settings", default=False)
    
    def init(self, context):
        # Sockets IN
        self.inputs.new('BakeWrangler_Socket_Color', "Color")
        self.inputs.new('BakeWrangler_Socket_Float', "R")
        self.inputs.new('BakeWrangler_Socket_Float', "G")
        self.inputs.new('BakeWrangler_Socket_Float', "B")
        self.inputs.new('BakeWrangler_Socket_Float', "A")
        # Sockets OUT
        self.outputs.new('BakeWrangler_Socket_Bake', "Bake")
        # Prefs
        self.img_type = self.img_format[_prefs("def_format")][0]
        self.img_xres = _prefs("def_xout")
        self.img_yres = _prefs("def_yout")
        self.disp_path = _prefs("def_outpath")
        self.img_name = _prefs("def_outname")
        self.adv_settings = _prefs("def_show_adv")
        
    def draw_buttons(self, context, layout):
        BakeWrangler_Tree_Node.draw_bake_button(self, layout, 'IMAGE', "Bake Image")
        colnode = layout.column(align=False)
        
        split = colnode.split(factor=0.35)
        split.label(text="Format:")
        split.prop(self, "img_type", text="")
        
        colpath = colnode.column(align=True)
        colpath.prop(self, "disp_path", text="")
        colpath.prop(self, "img_name", text="")
        
        colres = colnode.column(align=True)
        colres.prop(self, "img_xres", text="X")
        colres.prop(self, "img_yres", text="Y")
        
        advrow = colnode.row()
        advrow.alignment = 'LEFT'
        
        if not self.adv_settings:
            advrow.prop(self, "adv_settings", icon="DISCLOSURE_TRI_RIGHT", emboss=False, text="Advanced Settings:")
            advrow.separator()
        else:
            advrow.prop(self, "adv_settings", icon="DISCLOSURE_TRI_DOWN", emboss=False, text="Advanced Settings:")
            advrow.separator()
            
            coladv = colnode.column(align=True)
            coladv.prop(self, "img_clear")
            coladv.prop(self, "img_use_float")
            
            splitadv = coladv.split(factor=0.4)
            coladvtxt = splitadv.column(align=True)
            coladvopt = splitadv.column(align=True)
            
            # Color Spaces
            if self.img_type != 'CINEON':
                coladvtxt.label(text="Space:")
                coladvopt.prop(self, "img_color_space", text="")
            # Color Modes
            if self.img_type in ['BMP', 'JPEG', 'CINEON', 'HDR']:
                coladvtxt.label(text="Color:")
                coladvopt.prop(self, "img_color_mode_noalpha", text="")
            if self.img_type in ['IRIS', 'PNG', 'JPEG2000', 'TARGA', 'TARGA_RAW', 'DPX', 'OPEN_EXR_MULTILAYER', 'OPEN_EXR', 'TIFF']:
                coladvtxt.label(text="Color:")
                coladvopt.prop(self, "img_color_mode", text="")
            # Color Depths
            if self.img_type in ['PNG', 'TIFF']:
                coladvtxt.label(text="Depth:")
                coladvopt.prop(self, "img_color_depth_8_16", text="")
            if self.img_type == 'JPEG2000':
                coladvtxt.label(text="Depth:")
                coladvopt.prop(self, "img_color_depth_8_12_16", text="")
            if self.img_type == 'DPX':
                coladvtxt.label(text="Depth:")
                coladvopt.prop(self, "img_color_depth_8_10_12_16", text="")
            if self.img_type in ['OPEN_EXR_MULTILAYER', 'OPEN_EXR']:
                coladvtxt.label(text="Depth:")
                coladvopt.prop(self, "img_color_depth_16_32", text="")
            # Compression / Quality
            if self.img_type == 'PNG':
                coladvtxt.label(text="Compression:")
                coladvopt.prop(self, "img_compression", text="")
            if self.img_type in ['JPEG', 'JPEG2000']:
                coladvtxt.label(text="Quality:")
                coladvopt.prop(self, "img_quality", text="")
            # Codecs
            if self.img_type == 'JPEG2000':
                coladvtxt.label(text="Codec:")
                coladvopt.prop(self, "img_codec_jpeg2k", text="")
            if self.img_type in ['OPEN_EXR', 'OPEN_EXR_MULTILAYER']:
                coladvtxt.label(text="Codec:")
                coladvopt.prop(self, "img_codec_openexr", text="")
            if self.img_type == 'TIFF':
                coladvtxt.label(text="Compression:")
                coladvopt.prop(self, "img_codec_tiff", text="")
            # Other random image settings
            if self.img_type == 'JPEG2000':
                coladv.prop(self, "img_jpeg2k_cinema")
                coladv.prop(self, "img_jpeg2k_cinema48")
                coladv.prop(self, "img_jpeg2k_ycc")
            if self.img_type == 'DPX':
                coladv.prop(self, "img_dpx_log")
            if self.img_type == 'OPEN_EXR':
                coladv.prop(self, "img_openexr_zbuff")
          
    # Validate incoming links
    def insert_link(self, link):
        if link.to_node == self:
            if follow_input_link(link).from_node.bl_idname == 'BakeWrangler_Bake_Pass':
                link.to_socket.valid = True
            else:
                link.to_socket.valid = False
        

# Output controller node provides batch execution of multiple conntected bake passes. 
class BakeWrangler_Output_Batch_Bake(Node, BakeWrangler_Tree_Node):
    '''Output controller oven node'''
    bl_label = 'Batch Bake'
        
    # Makes sure there is always one empty input socket at the bottom by adding and removing sockets
    def update_inputs(self):
        BakeWrangler_Tree_Node.update_inputs(self, 'BakeWrangler_Socket_Bake', "Bake")
        
    # Check node settings are valid to bake. Returns true/false, plus error message(s).
    def validate(self, is_primary=True):
        valid = [True]
        # Batch mode needs to avoid validating the same things more than once. Collect a
        # unique list of the passes before validating them.
        img_node_list = []
        pass_node_list = []
        for input in self.inputs:
            if input.islinked() and input.valid:
                img_node = follow_input_link(input.links[0]).from_node
                if not img_node_list.count(img_node):
                    img_node_list.append(img_node)
                    for img_node_input in img_node.inputs:
                        if img_node_input.islinked() and img_node_input.valid:
                            pass_node = follow_input_link(img_node_input.links[0]).from_node
                            if not pass_node_list.count(pass_node):
                                pass_node_list.append(pass_node)
        # Validate all the listed nodes
        has_valid_input = False
        for node in img_node_list:
            img_node_valid = node.validate()
            valid[0] = img_node_valid.pop(0)
            if valid[0]:
                has_valid_input = True
            valid += img_node_valid
        for node in pass_node_list:
            pass_node_valid = node.validate()
            valid[0] = pass_node_valid.pop(0)
            valid += pass_node_valid
        errs = len(valid)
        if not has_valid_input and errs < 2:
            valid[0] = False
            valid.append([_print("Input error", node=self, ret=True), ": No valid inputs connected"])
        # Everything validated
        return valid

    def init(self, context):
        self.inputs.new('BakeWrangler_Socket_Bake', "Bake")

    def draw_buttons(self, context, layout):
        BakeWrangler_Tree_Node.draw_bake_button(self, layout, 'OUTLINER', "Bake All")
        layout.label(text="Bake Images:")
        


#
# Node Categories
#

import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

# Base class for the node category menu system
class BakeWrangler_Node_Category(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'BakeWrangler_Tree'

# List of all bakery nodes put into categories with identifier, name
BakeWrangler_Node_Categories = [
    BakeWrangler_Node_Category('BakeWrangler_Nodes', "Bake Wrangler", items=[
        NodeItem("BakeWrangler_Input_ObjectList"),
        NodeItem("BakeWrangler_Bake_Mesh"),
        NodeItem("BakeWrangler_Bake_Pass"),
        NodeItem("BakeWrangler_Output_Image_Path"),
        NodeItem("BakeWrangler_Output_Batch_Bake"),
    ]),
]



#
# Registration
#

# All bakery classes that need to be registered
classes = (
    BakeWrangler_Operator_Dummy,
    BakeWrangler_Operator_BakeStop,
    BakeWrangler_Operator_BakePass,
    BakeWrangler_Tree,
    BakeWrangler_Socket_Object,
    BakeWrangler_Socket_Mesh,
    BakeWrangler_Socket_Color,
    BakeWrangler_Socket_Float,
    BakeWrangler_Socket_Bake,
    BakeWrangler_Input_ObjectList,
    BakeWrangler_Bake_Mesh,
    BakeWrangler_Bake_Pass,
    BakeWrangler_Output_Image_Path,
    BakeWrangler_Output_Batch_Bake,
)


# Use a handler on depsgraph update to detect creation of new trees and switching to
# the bake tree editor - Because I can't really see a better way to get the desired
# behavior: New trees need a dummy user so they don't get deleted, new trees should
# get a better name than 'node tree' and switching to the editor should load the last
# active tree up instead of nothing.
from bpy.app.handlers import persistent
post_hook_index = -1                   
@persistent
def BakeWranger_Hook_Post_NewTree(dummy):
    debug = _prefs('debug')
    ctx = bpy.context
    if ctx.area and ctx.area.ui_type == 'BakeWrangler_Tree':
        # Context may actually not be the active area if multiple BakeWrangler areas are open, so check for more
        spaces = []
        for area in ctx.screen.areas:
            if area.ui_type == 'BakeWrangler_Tree':
                if len(area.spaces) > 0:
                    for spc in area.spaces:
                        if spc.type == 'NODE_EDITOR' and hasattr(spc, 'node_tree'):
                            spaces.append(spc)
                            break
        for space in spaces:
            tree = space.node_tree
            # Init a new tree
            if tree and not tree.initialised:
                if debug: _print("New/Uninitialized node tree active")
                tree.use_fake_user = True
                # Give tree a nice name
                if tree.name.startswith("NodeTree"):
                    num = 0
                    for nodes in bpy.data.node_groups:
                        if nodes.name.startswith("Bake Recipe"):
                            if num == 0:
                                num = 1
                            splt = nodes.name.split('.')
                            if len(splt) > 1 and splt[1].isnumeric:
                                num = int(splt[1]) + 1
                    if num == 0:
                        name = "Bake Recipe"
                    else:
                        if debug: _print("Next highest name number selected '%d'" % (num))
                        name = "Bake Recipe.%03d" % (num)
                    tree.name = tree.name.replace("NodeTree", name, 1)
                # Add initial basic node set up
                if len(tree.nodes) == 0:
                    bake_mesh = tree.nodes.new('BakeWrangler_Bake_Mesh')
                    bake_pass = tree.nodes.new('BakeWrangler_Bake_Pass')
                    output_img = tree.nodes.new('BakeWrangler_Output_Image_Path')
                    
                    bake_mesh.location[0] -= 300
                    output_img.location[0] += 200
                    
                    tree.links.new(bake_pass.inputs[0], bake_mesh.outputs[0])
                    tree.links.new(output_img.inputs[0], bake_pass.outputs[0])
                    tree.tree_version = BW_TREE_VERSION
                tree.initialised = True
                if debug: _print("Tree initialized")
            # Update an out of date tree
            if tree and tree.tree_version < BW_TREE_VERSION:
                if debug: _print("Tree out of date (tree: v%i current: v%i)" % (tree.tree_version, BW_TREE_VERSION))
                # Version zero or one tree to version 2 tree
                if tree.tree_version in [0, 1]:
                    # Import old tree classes
                    from . import node_tree_v1
                    node_tree_v1.register()
                    if debug: _print("Loaded node_tree_v1")
                    if debug: _print("Updating to: v2")
                    # Replace superseded nodes with updated variants
                    for node in list(tree.nodes):
                        id = BakeWranger_Hook_RNA_Repair(node)
                        # Input_Mesh's must be replaced with Bake_Mesh's
                        if id == 'BakeWrangler_Input_Mesh':
                            replace = tree.nodes.new('BakeWrangler_Bake_Mesh')
                            replace.width = node.width
                            replace.location = node.location
                            # Re-create links to replacement node (these only had one input and output)
                            if node.inputs[0].is_linked:
                                tree.links.new(replace.inputs['Source'], node.inputs[0].links[0].from_socket)
                            if node.outputs[0].is_linked:
                                # Output could still be linked to multiple things
                                for link in node.outputs[0].links:
                                    tree.links.new(link.to_socket, replace.outputs[0])
                            # Copy settings that are common in replacement
                            if node.mesh_object:
                                active_obj = replace.inputs['Target']
                                active_obj.value = node.mesh_object
                                if node.cage:
                                    active_obj.use_cage = True
                                if node.cage_obj:
                                    active_obj.cage = node.cage_obj
                                if node.uv_map:
                                    active_obj.pick_uv = True
                                    active_obj.uv_map = node.uv_map
                            replace.ray_dist = node.ray_dist
                            replace.margin = node.margin
                            replace.mask_margin = node.mask_margin
                            replace.multi_res = node.multi_res
                            replace.multi_res_pass = node.multi_res_pass
                            # Delete old node
                            tree.nodes.remove(node)
                        # HighPolyMesh nodes are replaced by ObjectList nodes
                        if id == 'BakeWrangler_Input_HighPolyMesh':
                            replace = tree.nodes.new('BakeWrangler_Input_ObjectList')
                            replace.width = node.width
                            replace.location = node.location
                            # Recreate input links or copy values
                            for input in node.inputs:
                                sock = replace.inputs[-1]
                                if input.is_linked:
                                    tree.links.new(sock, input.links[0].from_socket)
                                elif input.value:
                                    sock.value = input.value
                                    if input.collection and input.recursive:
                                        sock.recursive = True
                            # Recreate output links
                            if node.outputs[0].is_linked:
                                for link in node.outputs[0].links:
                                    tree.links.new(link.to_socket, replace.outputs[0])
                            # Delete old node
                            tree.nodes.remove(node)
                    # Unregister old classes
                    node_tree_v1.unregister()
                    del node_tree_v1
                    # Fix version number
                    tree.tree_version = 2
                # Update from v2 to v3
                if tree.tree_version == 2:
                    # Replace superseded nodes with updated variants
                    for node in list(tree.nodes):
                        id = BakeWranger_Hook_RNA_Repair(node)
                        # Bake_Mesh has renamed inputs that require replacing old ones
                        if id == 'BakeWrangler_Bake_Mesh':
                            # Active becomes Target
                            target = node.inputs.new("BakeWrangler_Socket_Object", "Target")
                            active = node.inputs[0]
                            if active.is_linked:
                                tree.links.new(target, active.links[0].from_socket)
                            if active.value:
                                target.value = active.value
                            # Selected becomes Source
                            source = node.inputs.new("BakeWrangler_Socket_Object", "Source")
                            select = node.inputs[1]
                            if select.is_linked:
                                tree.links.new(source, select.links[0].from_socket)
                            if select.value:
                                source.value = select.value
                            # Remove the old sockets and fix positions
                            node.inputs.remove(active)
                            node.inputs.remove(select)
                            node.inputs.move(0, 2)
                        # Pass label should be set to the pass name if currently empty
                        if id == 'BakeWrangler_Bake_Pass':
                            if node.label == "":
                                for pas in node.bake_passes:
                                    if pas[0] == node.bake_pass:
                                        node.label = "Pass: " + pas[1]
                                        break
                    # Fix version number
                    tree.tree_version = 3
                # Update from v3 to v4
                if tree.tree_version == 3:
                    # Alpha channel on image output is moved to last input slot and renamed to "A"
                    for node in list(tree.nodes):
                        id = BakeWranger_Hook_RNA_Repair(node)
                        if id == 'BakeWrangler_Output_Image_Path':
                            node.inputs.move(1, 4) # Move second input (Alpha) to the 5th position
                            node.inputs[4].name = "A" # Change it's name to "A" which also changes its array key
                    # Change version number
                    tree.tree_version = 4
                                        


# RNA repair looper (sometimes an error happens, but retrying fixes it?)
def BakeWranger_Hook_RNA_Repair(object):
    try:
        return object.bl_idname
    except:
        _print("RNA Fail")
        BakeWranger_Hook_RNA_Repair(object)



def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    nodeitems_utils.register_node_categories('BakeWrangler_Nodes', BakeWrangler_Node_Categories)
    bpy.app.handlers.depsgraph_update_post.append(BakeWranger_Hook_Post_NewTree)
    global post_hook_fn
    post_hook_fn = bpy.app.handlers.depsgraph_update_post[-1]


def unregister():
    hook_index = None
    for idx in range(len(bpy.app.handlers.depsgraph_update_post)):
        if bpy.app.handlers.depsgraph_update_post[idx] == post_hook_fn:
            hook_index = idx
    if hook_index != None:
        bpy.app.handlers.depsgraph_update_post.pop(hook_index)
        
    nodeitems_utils.unregister_node_categories('BakeWrangler_Nodes')

    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)



if __name__ == "__main__":
    register()
