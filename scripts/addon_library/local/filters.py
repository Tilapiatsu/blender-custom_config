bl_info = {
    "name": "Filters",
    "author": "Simon Geoffriau",
    "version": (2, 0, 1),
    "blender": (2, 80, 0),
    "category": "Object",
    "location": "3D viewport",
    "description": "Create visibility filters",
    "warning": "",
    "doc_url": "",
    "tracker_url": "",
}

import bpy

# Master filter hide
class VIEW3D_OT_MASTER_FILTER_H(bpy.types.Operator):
    bl_idname = 'op.master_filter_h'
    bl_label = "Master filter hide"

    @classmethod
    def poll(cls, context):
        objs = masterScope(context)
        if len(objs) != 0:
            return True 

    def execute(self, context):
        # Define objects scope
        masterFiltered_objs = masterScope(context)
        show_objs = {o for o in masterFiltered_objs if not o.hide_get()}
        hide_objs = {o for o in masterFiltered_objs if o.hide_get()}

        # Show/Hide filtered objects
        if context.scene.master_hide:
            for o in hide_objs:
                o.hide_set(False)
            context.scene.master_hide = False
        else:
            for o in show_objs:
                o.hide_set(True)
            context.scene.master_hide = True
        return{'FINISHED'}

# Master filter isolate
class VIEW3D_OT_MASTER_FILTER_I(bpy.types.Operator):
    bl_idname = 'op.master_filter_i'
    bl_label = "Master filter isolate"

    @classmethod
    def poll(cls, context):
        objs = masterScope(context)
        if len(objs) != 0:
            return True 

    def execute(self, context):
        # Define objects scope
        masterFiltered_objs = masterScope(context)
        show_objs = {o for o in context.scene.objects if not o.hide_get() and o not in masterFiltered_objs}
        hide_objs = {o for o in context.scene.objects if o.hide_get() and o not in masterFiltered_objs}

        # Isolate/Un-isolate filtered objects
        if context.scene.master_isolate:
            for o in context.scene.objects:
                o.hide_set(False)
            context.scene.master_isolate = False
            context.scene.master_hide = False
            # Show everything else
            for i in range(0, len(bpy.context.scene.filtersProperties.items())):
                bpy.context.scene.filtersProperties[i].hide = False
                bpy.context.scene.filtersProperties[i].isolate = False
        else:
            for o in show_objs:
                o.hide_set(True)
            context.scene.master_isolate = True
        return{'FINISHED'}

# Show/Hide filtered objects
class VIEW3D_OT_FILTER_H(bpy.types.Operator):
    bl_idname = "op.filter_h"
    bl_label = "Filter hide"

    op_name : bpy.props.StringProperty(name='op_name')

    @classmethod
    def poll(cls, context):
        if (bpy.context.area.type == "VIEW_3D" or bpy.context.area.type == "OUTLINER"):
            return True

    def execute(self, context):
        # Define objects scope
        masterFiltered_objs = masterScope(context)
        # Check for other filters
        for p in context.scene.filtersProperties:
            if p.hide and p.name != self.op_name:
                hidFiltered = {o for o in masterFiltered_objs if o.name.find(p.name) != -1}
                for hid in hidFiltered:
                    masterFiltered_objs.remove(hid)
            if p.isolate and p.name != self.op_name:
                isoFiltered = {o for o in masterFiltered_objs if o.name.find(p.name) == -1}
                for iso in isoFiltered:
                    masterFiltered_objs.remove(iso) 
        filtered_objs = {o for o in masterFiltered_objs if o.name.find(self.op_name) != -1}
        show_objs = {o for o in filtered_objs if not o.hide_get()}
        hide_objs = {o for o in filtered_objs if o.hide_get()}

        # Show/Hide filtered objects
        filterHide = bpy.context.scene.filtersProperties[self.op_name].hide
        if len(filtered_objs) != 0:               
            if filterHide:
                for o in hide_objs:
                    o.hide_set(False)
                bpy.context.scene.filtersProperties[self.op_name].hide=False
            else:
                for o in show_objs:
                    o.hide_set(True)
                bpy.context.scene.filtersProperties[self.op_name].hide=True
        else:
            print('DISABLE')
        return {'FINISHED'}

# Isolate filtered objects
class VIEW3D_OT_FILTER_I(bpy.types.Operator):
    bl_idname = "op.filter_i"
    bl_label = "Filter isolate"

    op_name : bpy.props.StringProperty(name='op_name')

    # @classmethod
    # def poll(cls, context):
    #     print(cls)
    #     # for o in context.scene.filtersProperties:
    #     # #     if o.name.find() != -1:
    #     # #         return True

    def execute(self, context):
        # Define objects scope
        masterFiltered_objs = masterScope(context)
        # masterFiltered_objs = {o for o in context.scene.objects if o.name.find(context.scene.master_filter) != -1 and context.scene.master_filter != ''}
        # Check for other filters
        for p in context.scene.filtersProperties:
            if p.hide and p.name != self.op_name:
                hidFiltered = {o for o in masterFiltered_objs if o.name.find(p.name) != -1}
                for hid in hidFiltered:
                    masterFiltered_objs.remove(hid)
            if p.isolate and p.name != self.op_name:
                isoFiltered = {o for o in masterFiltered_objs if o.name.find(p.name) == -1}
                for iso in isoFiltered:
                    masterFiltered_objs.remove(iso) 

        filtered_objs = {o for o in masterFiltered_objs if o.name.find(self.op_name) != -1}

        show_objs = {o for o in masterFiltered_objs if not o.hide_get() and o not in filtered_objs}
        hide_objs = {o for o in masterFiltered_objs if o.hide_get() and o not in filtered_objs}

        # Isolate/Un-isolate filtered objects        
        filterIsolate = bpy.context.scene.filtersProperties[self.op_name].isolate
        if len(filtered_objs) != 0:
            if filterIsolate:
                for o in hide_objs:
                    o.hide_set(False)
                bpy.context.scene.filtersProperties[self.op_name].isolate=False
            else:
                for o in show_objs:
                    o.hide_set(True)
                bpy.context.scene.filtersProperties[self.op_name].isolate=True
        else:
            print('DISABLE')
        return {'FINISHED'}

# Add a new filter
class VIEW3D_OT_FILTER_ADD(bpy.types.Operator):
    bl_idname = "op.filter_add"
    bl_label = "Add Filter"

    op_name : bpy.props.StringProperty(name='op_name')

    @classmethod
    def poll(cls, context):
        objs = masterScope(context)
        if len(objs) != 0:
            return True 

    def execute(self, context):
        newFilter = addFilterItem(self.op_name)
        # if newFilter != None:
        return {'FINISHED'}

# Remove a filter
class VIEW3D_OT_FILTER_DEL(bpy.types.Operator):
    bl_idname = "op.filter_del"
    bl_label = "Remove Filter"

    op_name : bpy.props.StringProperty(name='op_name')

    def execute(self,context):

        # Remove a filter
        bpy.context.scene.filtersProperties[self.op_name].delete=True
        # bpy.context.scene.filtersProperties[self.op_name].hide=False
        # bpy.context.scene.filtersProperties[self.op_name].isolate=False
        # Show hidden object and disable isolate
        masterFiltered_objs = {o for o in context.scene.objects if o.name.find(context.scene.master_filter) != -1 and context.scene.master_filter != ''}
        if context.scene.master_isolate:
            filtered_objs = {o for o in masterFiltered_objs if o.name.find(self.op_name) != -1}
        else:
            filtered_objs = {o for o in context.scene.objects if o.name.find(self.op_name) != -1}
        # show_objs = {o for o in filtered_objs if not o.hide_get()}
        hide_objs = {o for o in filtered_objs if o.hide_get()}
        for o in hide_objs:
            o.hide_set(False)

        # Delete properties
        for i in range(0, len(bpy.context.scene.filtersProperties.items())):
            if bpy.context.scene.filtersProperties[i].name == self.op_name:
                bpy.context.scene.filtersProperties.remove(i)
                break
        return {'FINISHED'}

# UI Panel
class VIEW3D_PT_FILTERS(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tools'
    bl_label = 'Filters'

    def draw(self, context):
        layout = self.layout
        filterCol = layout.column()
        row_add = layout.row()
        row_master = layout.row()

        # Master filter
        row_master.label(text='', icon='FILTER')
        row_master.prop(context.scene, 'master_filter', text='')
        op_master_h = row_master.operator('op.master_filter_h',  text='', icon='HIDE_ON' if context.scene.master_hide else 'HIDE_OFF', emboss=False)
        op_master_i = row_master.operator('op.master_filter_i', text='', icon='CHECKBOX_HLT' if context.scene.master_isolate else 'CHECKBOX_DEHLT', emboss=False)      

        # Add Filters
        for p in context.scene.filtersProperties:
            if not p.delete:
                OPs = addFilterOPs(p.name, filterCol)
                for op in OPs:
                    op.op_name = p.name           

        # Add button
        op_add = row_add.operator('op.filter_add', text='', icon='ADD', emboss=False)
        row_add.prop(context.scene, 'filter_add', text='')
        op_add.op_name = context.scene.filter_add

# Update visibility when changing master filter
def masterFilterUpdate(self, context):
    # Show everything in masterFiltered_objs
    for o in context.scene.objects:
        o.hide_set(False)
    # Reset hide and isolate operators
    context.scene.master_hide = False
    context.scene.master_isolate = False
    # Reset all filters
    for i in range(0, len(bpy.context.scene.filtersProperties.items())):
        bpy.context.scene.filtersProperties[i].hide = False
        bpy.context.scene.filtersProperties[i].isolate = False
    return None

# Classes and Properties
blender_classes = [
    VIEW3D_OT_MASTER_FILTER_H,
    VIEW3D_OT_MASTER_FILTER_I,
    VIEW3D_OT_FILTER_H,
    VIEW3D_OT_FILTER_I,
    VIEW3D_OT_FILTER_ADD,
    VIEW3D_OT_FILTER_DEL,
    VIEW3D_PT_FILTERS,
]

blender_props = [
    ('filter_add', bpy.props.StringProperty(name='', default='')),
    ('master_filter', bpy.props.StringProperty(name='', default='', update=masterFilterUpdate)),
    ('master_hide', bpy.props.BoolProperty(name='', default=False)),
    ('master_isolate', bpy.props.BoolProperty(name='', default=False))
]

# Set master filter scope   
def masterScope(context):
    objs = []
    valid = False
    for o in context.scene.objects:
        valid = False
        for m in context.scene.master_filter.split(";"):
            if o.name.find(m) != -1 and m != '':
                valid = True
            else:
                valid = False
                break
        if valid:
            objs.append(o)
    return objs

# Add a full set of filter operators
def addFilterOPs(filterName, layout):
    OPs = []
    filterRow = layout.row()
    delOP = filterRow.operator('op.filter_del', text='', icon="REMOVE", emboss=False)
    filterRow.label(text=filterName)
    hOP = filterRow.operator('op.filter_h', text='', icon= "HIDE_ON" if bpy.context.scene.filtersProperties[filterName].hide else "HIDE_OFF", emboss=False)
    iOP = filterRow.operator('op.filter_i', text='', icon= "CHECKBOX_HLT" if bpy.context.scene.filtersProperties[filterName].isolate else "CHECKBOX_DEHLT", emboss=False)
    OPs=[delOP,hOP,iOP]
    return(OPs)

# Add a set of properties for a new filter
def addFilterItem(filterName):
    # Check name
    filterExists = False
    for i in bpy.context.scene.filtersProperties:
        if i.name == filterName:
            filterExists=True
    if filterExists or filterName == '':
        print("Filter already exists, or invalid name provided")
    else:
        testFilter = bpy.context.scene.filtersProperties.add()
        testFilter.name = filterName
        testFilter.hide = False
        testFilter.isolate = False
        return(testFilter)
    return(None)

# Filter properties
class FilterProperties(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    hide: bpy.props.BoolProperty()
    isolate: bpy.props.BoolProperty()
    delete: bpy.props.BoolProperty(default=False)

blender_classes.append(FilterProperties)

def register():
    for (prop_name, prop_value) in blender_props:
        setattr(bpy.types.Scene, prop_name, prop_value)

    for blender_class in blender_classes:
        bpy.utils.register_class(blender_class)

    bpy.types.Scene.filtersProperties = bpy.props.CollectionProperty(type=FilterProperties)

def unregister():
    for (prop_name, _) in blender_props:
        delattr(bpy.types.Scene, prop_name)

    for blender_class in blender_classes:
        bpy.utils.unregister_class(blender_class)

    for p in bpy.context.scene.filtersProperties:
        bpy.context.scene.filtersProperties.remove(0)

    del bpy.types.Scene.filtersProperties