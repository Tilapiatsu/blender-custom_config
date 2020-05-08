#version 120

uniform float offset;

flat varying float primitive_id_var;

void main()
{
	gl_FragColor = vec4(offset + primitive_id_var, 0, 0, 0);
}
