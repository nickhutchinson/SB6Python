#version 410 core

layout (location=0) in vec4 position;
layout (location=4) in vec2 tc;

layout (std140) uniform MyUniformBlock {
    mat4 mv_matrix;
    mat4 proj_matrix;
} u;

out VS_OUT {
    vec2 tc;
} vs_out;

void main()
{
    vs_out.tc = tc;
    gl_Position = u.proj_matrix * u.mv_matrix * position;
}
