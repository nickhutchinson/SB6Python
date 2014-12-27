#version 410 core

layout (location=0) in vec4 position;

layout (std140) uniform MyUniformBlock {
    vec4 offset;
} u;

void main()
{
    gl_Position = position + u.offset;
}
