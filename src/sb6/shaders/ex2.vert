#version 410 core

layout (location=0) in int alien_idx;

#define NUM_ALIENS 256

struct droplet_t {
    float x_offset, y_offset;
    float orientation;
    float _padding;
};

layout (std140) uniform MyUniformBlock {
    droplet_t droplets[NUM_ALIENS];
} u;

out VS_OUT {
    flat int alien;
    vec2 tc;
} vs_out;

void main()
{
    const vec2[4] pos = vec2[4](
            vec2(-0.5, -0.5),
            vec2(0.5, -0.5),
            vec2(-0.5, 0.5),
            vec2(0.5, 0.5)
            );

    vs_out.tc = pos[gl_VertexID].xy + vec2(0.5);
    vs_out.alien = alien_idx % 64;

    float co = cos(u.droplets[alien_idx].orientation);
    float so = sin(u.droplets[alien_idx].orientation);

    mat2 rot = mat2(vec2(co,so), vec2(-so, co));
    vec2 pos_p = 0.25 * rot * pos[gl_VertexID];

    gl_Position = vec4(
            pos_p.x + u.droplets[alien_idx].x_offset,
            pos_p.y + u.droplets[alien_idx].y_offset,
            0.5,
            1.0);
}
