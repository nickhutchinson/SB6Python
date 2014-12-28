#version 410 core

layout (location=0) in vec4 position;

layout (std140) uniform MyUniformBlock {
    mat4 mv_matrix;
    mat4 proj_matrix;
} u;

void main()
{
    gl_Position = u.proj_matrix * u.mv_matrix * position;
}
