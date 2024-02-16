import bpy

###################################################################################
# DISPLAY TOOLTIPS
###################################################################################
class BAGABATCH_tooltips(bpy.types.Operator):
    """Display a tooltips"""
    bl_idname = "bagabatch.tooltips"
    bl_label = "Display Tooltip"

    message: bpy.props.StringProperty(default="None")
    title: bpy.props.StringProperty(default="Tooltip")
    icon: bpy.props.StringProperty(default="INFO")
    size: bpy.props.IntProperty(default=50)
    url: bpy.props.StringProperty(default="None")

    def execute(self, context):
        Tooltip(self.message, self.title, self.icon, self.size, self.url) 
        return {'FINISHED'}

def Tooltip(message = "", title = "Message Box", icon = 'INFO', size = 50, url = "None"):

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        # DIRTY LAZY CODE START
        count = 0
        mess = message
        length = int(size)
        caracter = length
        temp = 0
        for i in message:            
            if count == 0:
                if mess[0] == " ":
                    o = length
                    if len(mess) > o:
                        while mess[o] != " ":
                            o += 1
                            if len(mess) == o:
                                break
                    col.label(text=mess[1:o])
                    caracter = length

                elif mess == message:
                    o = length
                    if o >= len(mess):
                        o = len(mess)-1
                    while message[o] != " ":
                        o += 1
                        if len(mess) == o:
                            break
                    col.label(text=mess[0:o])
                    caracter = length                    
                else :
                    count = temp
                    caracter += 1
            count += 1
            temp = count
            mess = mess[1:]
            if count == caracter:
                count = 0
        # DIRTY LAZY CODE END
        if url != "None":
            col.separator(factor = 1.5)
            row = col.row()
            row.scale_y = 2
            row.operator("wm.url_open", text="Video Demo", icon = 'PLAY', depress = False).url = url


    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

classes = [
    BAGABATCH_tooltips,
]