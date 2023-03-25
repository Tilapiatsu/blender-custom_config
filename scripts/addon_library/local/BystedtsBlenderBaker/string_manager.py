import bpy
import string
import math

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

def to_color(string):
    ''' Used to convert material name to a color for material id bake '''

    color = [0]*4
    color[3] = 1 # Alpha

    # Sum asci character to color per channel
    chan = 0
    for i in range(0, len(string)):
        chan = i % 3
        color[chan] += ord(string[i])
        chan += 1


    print("\n After sum color = " + repr(color))

    # Arbitrary mult and divide between 0-1
    for chan in range(0, 3):
        #color[chan] = ((color[chan] * 6458193.16489) % 256) / 256
        color[chan] = math.modf(color[chan] * 6458193.16489)[0]

    print("\n material id:")
    for chan in range(0, 3):
        print("color[" + str(chan) + "] = " + str(color[chan]))

    return tuple(color)


