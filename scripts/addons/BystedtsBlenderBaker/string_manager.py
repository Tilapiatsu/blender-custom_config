import bpy
import string

def to_camelcase(string_to_change):
    # Returns string as camelcase
    # example ThisIsCamelCase

    new_string = string.capwords(string_to_change)
    new_string = new_string.replace(" ", "")

    return new_string

def to_underscore(string):
    # Returns string as underscore
    # example this_is_underscore
    
    new_string = ""

    for i in range(0,len(string)):
        if string[i] == " ":
            new_string += "_"
        else:
            new_string += string[i].lower()

    return new_string