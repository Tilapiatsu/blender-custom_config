bl_info = {
    "name": "Exporter",
    "author": "Simon Geoffriau",
    "version": (2, 1, 4),
    "blender": (2, 80, 0),
    "category": "Scene",
    "location": "3D viewport",
    "description": "Convert collections to empties and export",
    "warning": "",
    "doc_url": "",
    "tracker_url": "",
}


''' scene structure
PR_ANN_0185_A (collection)
    PR_ANN_0185_A_Metal (collection)
        Metal_1
        Metal_2
    PR_ANN_0185_A_Stone (collection)
        Stone_1
        Stone_2
        Stone_3
    PR_ANN_0185_A_COL (collection)
        PR_ANN_0185_A_Metal_COL
    Origin_A (empty) > define pivot point for convertion to empties
>>>
PR_ANN_0185_A (empty)
    PR_ANN_0185_A_Metal_COL
    PR_ANN_0185_A_Metal_LOD (empty)
        PR_ANN_0185_A_Metal_LOD0
    PR_ANN_0185_A_Stone_LOD (empty)
        PR_ANN_0185_A_Stone_LOD0


TO DO     
    5 . Multi select Add    //done
'''

import bpy
import os

# -------------------------------------------------------------------
#   Operators
# -------------------------------------------------------------------

class CUSTOM_OT_actions(bpy.types.Operator):
    """Move items up and down, add and remove"""
    bl_idname = "custom.list_action"
    bl_label = "List Actions"
    bl_description = "Move items up and down, add and remove"
    bl_options = {'REGISTER'}

    action: bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", "")))

    def invoke(self, context, event):
        scn = context.scene
        idx = scn.custom_index

        try:
            item = scn.custom[idx]
        except IndexError:
            pass
        else:
            if self.action == 'DOWN' and idx < len(scn.custom) - 1:
                item_next = scn.custom[idx+1].name
                scn.custom.move(idx, idx+1)
                scn.custom_index += 1
                info = 'Item "%s" moved to position %d' % (item.name, scn.custom_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'UP' and idx >= 1:
                item_prev = scn.custom[idx-1].name
                scn.custom.move(idx, idx-1)
                scn.custom_index -= 1
                info = 'Item "%s" moved to position %d' % (item.name, scn.custom_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'REMOVE':
                info = 'Item "%s" removed from list' % (scn.custom[idx].name)
                scn.custom_index -= 1
                scn.custom.remove(idx)
                self.report({'INFO'}, info)

        if self.action == 'ADD':
            for o in context.selected_objects:
                if o and findProp(o) not in scn.custom.keys():
                    item = scn.custom.add()
                    item.name = findProp(o)
                    item.obj_type = o.type
                    item.obj_id = len(scn.custom)
                    scn.custom_index = len(scn.custom)-1
                    info = '"%s" added to list' % (item.name)
                    self.report({'INFO'}, info)
                else:
                    self.report({'INFO'}, "Nothing selected in the Viewport or prop already in the list")
        return {"FINISHED"}


class CUSTOM_OT_export(bpy.types.Operator):
    bl_idname = "op.export"
    bl_label = "Export"
    bl_options = {'REGISTER', 'UNDO'}

    # CONVERT FROM COLLECTIONS TO EMPTIES STRUCTURE AND EXPORT FBX
    def HExport(self, context):

        # Check scene structure
        if bool(bpy.context.scene.collection):
            # Variables
            parentCol = dict()
            empties = dict()
            props = bpy.context.scene.collection.children
            selectedProps = bpy.context.scene.custom.keys()

            # Convert each props
            for p in props:
                # Variables
                topCol = p
                colCol = []
                parentCol.clear()
                empties.clear()

                # Naming convention
                propL = p.name.split('_')[-1]

                # Clear Selection
                bpy.ops.object.select_all(action='DESELECT')    

                # Get Origin location
                # Check if Origin is present / if not 0 0 0 
                if bpy.context.scene.objects.get('Origin_'+propL):
                    originPos = context.scene.objects['Origin_'+propL].location
                else:
                    originPos = (0,0,0)

                # CREATE AN EMPTIES HIERARCHY BASED ON COLLECTIONS HIERARCHY
                newEmpty = addEmpty(p.name, originPos)
                empties[p.name] = newEmpty
                for c in p.children:       
                    parentCol[c.name] = None
                    # EXCEPTIONS HANDLING
                    exceptions = ['_COL', '_SCOL', '_MCOL']
                    found = False
                    for ex in exceptions:
                        if (c.name).find(ex) != -1:
                            found = True
                    if found:
                        colCol.append(c)

                    # Create empties
                    else:
                        newName = c.name+'_LOD'
                        newEmpty = addEmpty(newName, originPos)
                        empties[c.name] = newEmpty

                # Props objects
                for c in p.children:
                    if c not in colCol:
                        parentCol[c.name] = c.name
                        
                        # Parent empties
                        keepTransform = empties[c.name].matrix_world
                        empties[c.name].parent = empties[p.name]
                        empties[c.name].matrix_world = keepTransform
                        
                        # MERGE OBJECTS INTO LOD0 AND RE-PARENT TO EMPTIES (!_COL, _MCOL, _SCOL)
                        colObjs = c.objects.values() 
                        for o in colObjs:
                            o.select_set(True)
                            # Unlink from collection
                            bpy.context.scene.collection.objects.link(o)
                            bpy.data.collections[c.name].objects.unlink(o)
                        # Parent to corresponding empty
                        bpy.context.view_layer.objects.active = empties[c.name]
                        bpy.ops.object.parent_set(keep_transform=True)
                        # RUN CHECKS BEFORE JOIN (more than one?, ...)
                        bpy.context.view_layer.objects.active = colObjs[0]
                        bpy.ops.object.join() 
                        bpy.context.active_object.name = (c.name+'_LOD0')
                        bpy.ops.object.select_all(action='DESELECT')
                    else:
                        # Deal with exceptions objects
                        colObjs = c.objects.values() 
                        for o in colObjs:
                            o.select_set(True)
                            # Parent to top empty
                            bpy.context.view_layer.objects.active = empties[topCol.name]
                            bpy.ops.object.parent_set(keep_transform=True)
                            # Unlink from collections
                            bpy.context.scene.collection.objects.link(o)
                            for c in linkedCollections(o):
                                c.objects.unlink(o)      
                            # o.select_set(False)
                        # Merge multiple objects  
                        bpy.context.view_layer.objects.active = colObjs[0]
                        bpy.ops.object.join()
                        bpy.context.active_object.name = (c.name)
                        bpy.ops.object.select_all(action='DESELECT')   
                     
            # REMOVE COLLECTIONS
            for c in bpy.data.collections:
                bpy.data.collections.remove(c)

            # SAVE FILE
            for p in selectedProps:
                bpy.data.objects[p].select_set(True)
                for o in bpy.data.objects[p].children_recursive:
                    o.select_set(True)

                # Create filepath
                bfilepath = bpy.data.filepath
                directory = os.path.dirname(bfilepath)

                # Creates the path for the exported fbx.
                filepath = os.path.join(directory, p + "." + "fbx")
                bpy.ops.export_scene.fbx(filepath=filepath, use_selection=True)

            # Back to normal
            bpy.ops.object.select_all(action='DESELECT')           
            bpy.ops.ed.undo_push()
            bpy.ops.ed.undo()

            # Return exported prop list
            return(selectedProps)
        else:
            print("Info: Export not possible, wrong scene structure.")

    @classmethod
    def poll(cls, context):
        return bool(context.scene.custom)

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        if len(bpy.data.collections) != 0:
            exportedProps = self.HExport(context)
            self.report({'INFO'}, str(exportedProps)+" exported") 
        else:
            self.report({'INFO'}, "Warning - Wrong scene structure, nothing was exported ...") 
        return {'FINISHED'}


class CUSTOM_OT_printItems(bpy.types.Operator):
    """Print all items and their properties to the console"""
    bl_idname = "custom.print_items"
    bl_label = "Print Items to Console"
    bl_description = "Print all items and their properties to the console"
    bl_options = {'REGISTER', 'UNDO'}

    reverse_order: bpy.props.BoolProperty(
        default=False,
        name="Reverse Order")

    @classmethod
    def poll(cls, context):
        return bool(context.scene.custom)

    def execute(self, context):
        scn = context.scene
        if self.reverse_order:
            for i in range(scn.custom_index, -1, -1):        
                item = scn.custom[i]
                print ("Name:", item.name,"-",item.obj_type,item.obj_id)
        else:
            for item in scn.custom:
                print ("Name:", item.name,"-",item.obj_type,item.obj_id)
        return{'FINISHED'}


class CUSTOM_OT_clearList(bpy.types.Operator):
    """Clear all items of the list"""
    bl_idname = "custom.clear_list"
    bl_label = "Clear List"
    bl_description = "Clear all items of the list"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return bool(context.scene.custom)

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        if bool(context.scene.custom):
            context.scene.custom.clear()
            self.report({'INFO'}, "All items removed")
        else:
            self.report({'INFO'}, "Nothing to remove")
        return{'FINISHED'}


class CUSTOM_OT_removeDuplicates(bpy.types.Operator):
    """Remove all duplicates"""
    bl_idname = "custom.remove_duplicates"
    bl_label = "Remove Duplicates"
    bl_description = "Remove all duplicates"
    bl_options = {'INTERNAL'}

    def find_duplicates(self, context):
        """find all duplicates by name"""
        name_lookup = {}
        for c, i in enumerate(context.scene.custom):
            name_lookup.setdefault(i.name, []).append(c)
        duplicates = set()
        for name, indices in name_lookup.items():
            for i in indices[1:]:
                duplicates.add(i)
        return sorted(list(duplicates))

    @classmethod
    def poll(cls, context):
        return bool(context.scene.custom)

    def execute(self, context):
        scn = context.scene
        removed_items = []
        # Reverse the list before removing the items
        for i in self.find_duplicates(context)[::-1]:
            scn.custom.remove(i)
            removed_items.append(i)
        if removed_items:
            scn.custom_index = len(scn.custom)-1
            info = ', '.join(map(str, removed_items))
            self.report({'INFO'}, "Removed indices: %s" % (info))
        else:
            self.report({'INFO'}, "No duplicates")
        return{'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)


class CUSTOM_OT_selectItems(bpy.types.Operator):
    """Select Items in the Viewport"""
    bl_idname = "custom.select_items"
    bl_label = "Select Item(s) in Viewport"
    bl_description = "Select Items in the Viewport"
    bl_options = {'REGISTER', 'UNDO'}

    select_all: bpy.props.BoolProperty(
        default=False,
        name="Select all Items of List",
        options={'SKIP_SAVE'})

    @classmethod
    def poll(cls, context):
        return bool(context.scene.custom)

    def execute(self, context):
        scn = context.scene
        idx = scn.custom_index

        try:
            item = scn.custom[idx]
        except IndexError:
            self.report({'INFO'}, "Nothing selected in the list")
            return{'CANCELLED'}

        obj_error = False
        bpy.ops.object.select_all(action='DESELECT')
        if not self.select_all:
            obj = scn.objects.get(scn.custom[idx].name, None)
            if not obj: 
                obj_error = True
            else:
                obj.select_set(True)
                info = '"%s" selected in Viewport' % (obj.name)
        else:
            selected_items = []
            unique_objs = set([i.name for i in scn.custom])
            for i in unique_objs:
                obj = scn.objects.get(i, None)
                if obj:
                    obj.select_set(True)
                    selected_items.append(obj.name)

            if not selected_items: 
                obj_error = True
            else:
                missing_items = unique_objs.difference(selected_items)
                if not missing_items:
                    info = '"%s" selected in Viewport' \
                        % (', '.join(map(str, selected_items)))
                else:
                    info = 'Missing items: "%s"' \
                        % (', '.join(map(str, missing_items)))
        if obj_error: 
            info = "Nothing to select, object removed from scene"
        self.report({'INFO'}, info)    
        return{'FINISHED'}

# -------------------------------------------------------------------
#   Drawing
# -------------------------------------------------------------------

class CUSTOM_UL_items(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        split = layout.split(factor=0.7)
        # split.label(text="Index: %d" % (index))
        # custom_icon = "OUTLINER_OB_%s" % item.obj_type
        custom_icon = "OUTLINER_COLLECTION"
        #split.prop(item, "name", text="", emboss=False, translate=False, icon=custom_icon)
        split.label(text=item.name, icon=custom_icon) # avoids renaming the item by accident

    def invoke(self, context, event):
        pass   

class CUSTOM_PT_objectList(bpy.types.Panel):
    """Adds a custom panel to the TEXT_EDITOR"""
    bl_idname = 'TEXT_PT_my_panel'
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Helix"
    bl_label = "Props Exporter"

    def draw(self, context):
        layout = self.layout
        scn = bpy.context.scene

        rows = 2
        row = layout.row()
        col = row.column(align=True)
        col.operator("custom.list_action", icon='ADD', text="").action = 'ADD'
        col.operator("custom.list_action", icon='REMOVE', text="").action = 'REMOVE'
        col.operator("custom.clear_list", icon="X", text="")
        # col.separator()
        # col.operator("custom.list_action", icon='TRIA_UP', text="").action = 'UP'
        # col.operator("custom.list_action", icon='TRIA_DOWN', text="").action = 'DOWN'

        row.template_list("CUSTOM_UL_items", "", scn, "custom", scn, "custom_index", rows=rows)

        row = layout.row()
        col = row.column(align=True)
        # row = col.row(align=True)
        # row.operator("custom.print_items", icon="LINENUMBERS_ON") #LINENUMBERS_OFF, ANIM
        # row = col.row(align=True)
        # row.operator("custom.select_items", icon="VIEW3D", text="Select Item")
        # row.operator("custom.select_items", icon="GROUP", text="Select all Items").select_all = True
        row = col.row(align=True)
        row.operator("op.export", text='Export', icon='SETTINGS')

        # row.operator("custom.remove_duplicates", icon="GHOST_ENABLED")
        # row = col.row(align=True)
        
class CUSTOM_objectCollection(bpy.types.PropertyGroup):
    #name: StringProperty() -> Instantiated by default
    obj_type: bpy.props.StringProperty()
    obj_id: bpy.props.IntProperty()

# CONVERT FROM EMPTIES TO COLLECTIONS STRUCTURE
def HImport(context):

    # STATE
    if len(bpy.data.collections) == 0:

        # Variables
        coliders = ['_COL','_SCOL','_MCOL']
        empties = []

        # For each empties, create a Collection and parent objects
        for o in bpy.data.objects:
            if o.type == 'EMPTY' and o.name != "Origin_":
                # List objects
                objs = []
                for obj in o.children:
                    if obj.type != 'EMPTY':
                        found = False
                        for co in coliders:
                            if obj.name.find(co) != -1:
                                found = True
                        if not found:
                            objs.append(obj)
                # Create a collection to replace Empty # TO DO : Trim _LOD
                col = bpy.data.collections.new(o.name.rstrip('_LOD'))
                bpy.context.scene.collection.children.link(col)
                # Parent Objects
                for ob in objs:
                    # UnParent from Empty               
                    ob.select_set(True)
                    bpy.ops.object.parent_clear(type='CLEAR')
                    bpy.ops.object.select_all(action='DESELECT')
                    # Link To collection
                    col.objects.link(ob)
                    bpy.context.scene.collection.objects.unlink(ob)

                # List Empties
                empties.append(o)

        # EXCEPTIONS HANDLING
        topCol = bpy.data.collections[0]
        for o in bpy.data.objects:
            for co in coliders:
                if (o.name).find(co) != -1:
                    # If COL collection does not exist create it
                    found = False
                    for c in bpy.data.collections:
                        if c.name.find(co) != -1:
                            found = True
                    if not found:
                        coColName = topCol.name+co
                        coCol = bpy.data.collections.new(coColName)
                        bpy.context.scene.collection.children.link(coCol)
                    # UnParent from Empty               
                    o.select_set(True)
                    bpy.ops.object.parent_clear(type='CLEAR')
                    bpy.ops.object.select_all(action='DESELECT')
                    # Link objects to COL collection
                    bpy.data.collections[coColName].objects.link(o)
                    bpy.context.scene.collection.objects.unlink(o)


        # Hierarchy
        for c in bpy.data.collections:
            # Unless it is the top col
            if c is not topCol:
                topCol.children.link(c)
                bpy.context.scene.collection.children.unlink(c)

        # Origin A re-link
        if 'Origin_A' in bpy.data.objects.keys():
            origin_A = bpy.data.objects['Origin_A']
            topCol.objects.link(origin_A)

        # Delete empties
        for e in empties:
            e.select_set(True)
            bpy.ops.object.delete()

# Add an empty object
def addEmpty(name, location, collectionName=None):
    empty_obj = bpy.data.objects.new("empty", None)
    bpy.context.scene.collection.objects.link(empty_obj)
    if collectionName is not None:
        bpy.data.collections[collectionName].objects.link(empty_obj)
    empty_obj.name = name
    empty_obj.empty_display_size = 1 
    empty_obj.empty_display_type = 'PLAIN_AXES'   
    empty_obj.location = location

    return empty_obj

# Check if an object is in a collection
def isInCollection(collectionName, obj):
    try:
        col = bpy.data.collections[collectionName]
        for o in col.objects:
            if obj is o:
                return True
        return False
    except KeyError:
        return False

# Get a list of all the collections an object is linked to
def linkedCollections(obj):
    collectionList = []
    for c in bpy.data.collections:
        for o in c.objects:
            if o is obj:
                collectionList.append(c)
    return collectionList

# Find top collection, prop name, for a given object
def findProp(obj):
    for c in bpy.data.collections:
        for o in c.objects:
            if o == obj:
                pSplit = c.name.split('_')[0:4]
                propName = ''
                for i in range(0, 3):
                    try:
                        propName = propName+pSplit[i]+"_"
                    except:
                        return
                propName = propName+pSplit[3]
                return propName


blender_classes = [
    CUSTOM_OT_export,
    CUSTOM_OT_actions,
    CUSTOM_OT_printItems,
    CUSTOM_OT_clearList,
    CUSTOM_OT_removeDuplicates,
    CUSTOM_OT_selectItems,
    CUSTOM_UL_items,
    CUSTOM_PT_objectList,
    CUSTOM_objectCollection,
]

blender_props = []


def register():
    for (prop_name, prop_value) in blender_props:
        setattr(bpy.types.Scene, prop_name, prop_value)

    for blender_class in blender_classes:
        bpy.utils.register_class(blender_class)

    # Custom scene properties
    bpy.types.Scene.custom = bpy.props.CollectionProperty(type=CUSTOM_objectCollection)
    bpy.types.Scene.custom_index = bpy.props.IntProperty()

def unregister():
    for (prop_name, _) in blender_props:
        delattr(bpy.types.Scene, prop_name)

    for blender_class in blender_classes:
        bpy.utils.unregister_class(blender_class)

    del bpy.types.Scene.custom
    del bpy.types.Scene.custom_index