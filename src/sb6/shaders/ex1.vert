#version 410 core

layout (location=0) in vec4 position;

layout (std140) uniform MyUniformBlock {
    mat4 mv_matrix;
    mat4 proj_matrix;
} u;

out VS_OUT {
    vec4 color;
} vs_out;

void main()
{
    gl_Position = u.proj_matrix * u.mv_matrix * position;
    vs_out.color = position * 2.0 + vec4(0.5, 0.5, 0.5, 0.0);
}
