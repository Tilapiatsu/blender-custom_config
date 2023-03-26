
import bpy
import re

def bversion():
    bversion_string = bpy.app.version_string
    bversion_reg = re.match("^(\d\.\d?\d)", bversion_string)
    return float(bversion_reg.group(0))
