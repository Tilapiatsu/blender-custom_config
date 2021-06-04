# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

# Contact for more information about the Addon:
# Email:    germano.costa@ig.com.br
# Twitter:  wii_mano @mano_wii

import bgl

def check_shaderError(shader, flag, isProgram, errorMessage):
    success = bgl.Buffer(bgl.GL_INT, 1)
    slen = 1024
    if isProgram:
        bgl.glGetProgramiv(shader, flag, success)
        check_error("glGetProgramiv")

    else:
        bgl.glGetShaderiv(shader, flag, success)
        check_error("glGetShaderiv")

    import numpy as np
    from .bgl_ext import VoidBufValue

    offset = VoidBufValue(None)
    error = bgl.Buffer(bgl.GL_BYTE, slen)

    if isProgram:
        bgl.glGetProgramInfoLog(shader, slen, offset.buf, error)
        check_error("glGetProgramInfoLog")
    else:
        bgl.glGetShaderInfoLog(shader, slen, offset.buf, error)
        check_error("glGetShaderInfoLog")

    print(np.bytes_(error).decode("utf-8"))

    del offset
    if success[0] != bgl.GL_TRUE:
        print(errorMessage, np.bytes_(error).decode("utf-8"))
        raise RuntimeError(errorMessage, error)


def create_shader(source, shaderType):
    shader = bgl.glCreateShader(shaderType)

    if shader == 0:
        raise RuntimeError("Error: Shader creation failed!")

    bgl.glShaderSource(shader, source)
    print(source)
    check_error("glShaderSource")
    bgl.glCompileShader(shader)
    check_error("glCompileShader")

    check_shaderError(shader, bgl.GL_COMPILE_STATUS, False, "Error: Shader compilation failed:")

    return shader

def check_error(msg):
    err = bgl.glGetError()
    if err != bgl.GL_NO_ERROR:
        print("slcad_snap GL Error:", msg, err)

class Shader():

    def __init__(self, vertexcode, geomcode, fragcode):

        success = bgl.Buffer(bgl.GL_INT, 1)
        program = bgl.glCreateProgram()

        shader1 = bgl.glCreateShader(bgl.GL_VERTEX_SHADER)
        bgl.glShaderSource(shader1, vertexcode)
        check_error("glShaderSource")
        bgl.glCompileShader(shader1)
        check_error("glCompileShader")
        bgl.glGetShaderiv(shader1, bgl.GL_COMPILE_STATUS, success)
        if success[0] != bgl.GL_TRUE:
            print("shader vertexcode compile error")

        shader2 = bgl.glCreateShader(bgl.GL_FRAGMENT_SHADER)
        bgl.glShaderSource(shader2, fragcode)
        check_error("glShaderSource")
        bgl.glCompileShader(shader2)
        check_error("glCompileShader")
        bgl.glGetShaderiv(shader2, bgl.GL_COMPILE_STATUS, success)
        check_error("glGetShaderiv")
        if success[0] != bgl.GL_TRUE:
            print("shader fragcode compile error")

        bgl.glAttachShader(program, shader1)
        check_error("glAttachShader")

        bgl.glAttachShader(program, shader2)
        check_error("glAttachShader")

        bgl.glLinkProgram(program)
        check_error("glLinkProgram")

        bgl.glGetProgramiv(program, bgl.GL_LINK_STATUS, success)
        check_error("glGetProgramiv")
        if success[0] != bgl.GL_TRUE:
            print("Program link error")

        bgl.glValidateProgram(program)
        check_error("glValidateProgram")
        bgl.glGetProgramiv(program, bgl.GL_VALIDATE_STATUS, success)
        check_error("glGetProgramiv")
        if success[0] != bgl.GL_TRUE:
            print("Program invalid")

        self.program = program

        #
        # self.shaders = []
        # self.program = bgl.glCreateProgram()
        # check_error("glCreateProgram")
        #
        # if self.program == 0:
        #     raise RuntimeError("Error: Program creation failed!")
        #
        # check_error("glCreateProgram")
        #
        # if vertexcode:
        #     self.shaders.append(create_shader(vertexcode, bgl.GL_VERTEX_SHADER))
        # if geomcode:
        #     self.shaders.append(create_shader(geomcode, bgl.GL_GEOMETRY_SHADER))
        # if fragcode:
        #     self.shaders.append(create_shader(fragcode, bgl.GL_FRAGMENT_SHADER))
        #
        # for shad in self.shaders:
        #     bgl.glAttachShader(self.program, shad)
        #     check_error("glAttachShader")
        #
        # bgl.glLinkProgram(self.program)
        # check_error("glLinkProgram")
        #
        # check_shaderError(self.program, bgl.GL_LINK_STATUS, True, "Error: Program linking failed:")
        # bgl.glValidateProgram(self.program)
        # check_error("glValidateProgram")
        # check_shaderError(self.program, bgl.GL_VALIDATE_STATUS, True, "Error: Program is invalid:")

    def __del__(self):
        for shad in self.shaders:
            bgl.glDetachShader(self.program, shad)
            bgl.glDeleteShader(shad)
        bgl.glDeleteProgram(self.program)
        print('shader_del')
