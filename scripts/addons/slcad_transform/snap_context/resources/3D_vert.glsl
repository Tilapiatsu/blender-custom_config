#version 120

uniform mat4 MVP;

attribute vec3 pos;
attribute float primitive_id;
flat varying float primitive_id_var;

void main()
{
	primitive_id_var = primitive_id;
	gl_Position = MVP * vec4(pos, 1.0);
}
