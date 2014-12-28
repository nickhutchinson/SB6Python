#!/usr/bin/env python
# encoding: utf-8
from __future__ import print_function, division

import click
import logging
import math
import numpy as np
import pkg_resources

from .app import Application as SB6App, IApplicationDelegate as ISB6AppDelegate
from .util import override, BufferObject, VertexArrayObject, ProgramObject, TextureObject
from enum import Enum
from lazy import lazy
from OpenGL.GL import *
from pyrr import Matrix44, Vector4

NULL_GL_OBJECT = 0

logging.basicConfig()


class MyUniformBlock(ctypes.Structure):
    _fields_ = (
        ("mv_matrix", ctypes.c_float * 16),
        ("proj_matrix", ctypes.c_float * 16),
    )


class MyApplication(ISB6AppDelegate):

    def __init__(self):
        self._app = SB6App(self)

        self._program = ProgramObject()
        self._vao = VertexArrayObject()
        self._vertices_buffer = BufferObject()
        self._uniform_buffer = BufferObject()
        self._texture = TextureObject()

        self._uniform_block = MyUniformBlock()

    @property
    def position_attrib_index(self):
        return 0

    @property
    def uniform_bind_point(self):
        return 0

    @override(ISB6AppDelegate)
    def window_did_resize(self, application, width, height):
        aspect = width / height
        proj_matrix = Matrix44.perspective_projection(
            50.0, aspect, 0.1, 100.0,
            dtype='f4')
        self._uniform_block.proj_matrix[:] = proj_matrix.reshape(16)

    @override(ISB6AppDelegate)
    def application_did_finish_launching(self, app):
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glFrontFace(GL_CW)

        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)

        self._program = self.create_shader_program([
            (GL_VERTEX_SHADER, pkg_resources.resource_string(
                __name__, 'shaders/ex1.vert')),
            (GL_FRAGMENT_SHADER, pkg_resources.resource_string(
                __name__, 'shaders/ex1.frag')),
        ])

        self._vao = VertexArrayObject(glGenVertexArrays(1))
        glBindVertexArray(self._vao.identifier)
        try:
            ###################################################################
            # Vertex array
            self._vertices_buffer = BufferObject(glGenBuffers(1))
            glBindBuffer(GL_ARRAY_BUFFER, self._vertices_buffer.identifier)
            data = np.array([
                -0.25, 0.25, -0.25,
                -0.25, -0.25, -0.25,
                0.25, -0.25, -0.25,

                0.25, -0.25, -0.25,
                0.25, 0.25, -0.25,
                -0.25, 0.25, -0.25,

                0.25, -0.25, -0.25,
                0.25, -0.25, 0.25,
                0.25, 0.25, -0.25,

                0.25, -0.25, 0.25,
                0.25, 0.25, 0.25,
                0.25, 0.25, -0.25,

                0.25, -0.25, 0.25,
                -0.25, -0.25, 0.25,
                0.25, 0.25, 0.25,

                -0.25, -0.25, 0.25,
                -0.25, 0.25, 0.25,
                0.25, 0.25, 0.25,

                -0.25, -0.25, 0.25,
                -0.25, -0.25, -0.25,
                -0.25, 0.25, 0.25,

                -0.25, -0.25, -0.25,
                -0.25, 0.25, -0.25,
                -0.25, 0.25, 0.25,

                -0.25, -0.25, 0.25,
                0.25, -0.25, 0.25,
                0.25, -0.25, -0.25,

                0.25, -0.25, -0.25,
                -0.25, -0.25, -0.25,
                -0.25, -0.25, 0.25,

                -0.25, 0.25, -0.25,
                0.25, 0.25, -0.25,
                0.25, 0.25, 0.25,

                0.25, 0.25, 0.25,
                -0.25, 0.25, 0.25,
                -0.25, 0.25, -0.25
            ], dtype='f4')

            glBufferData(GL_ARRAY_BUFFER, data, GL_STATIC_DRAW)
            glVertexAttribPointer(
                self.position_attrib_index,
                3,
                GL_FLOAT,
                GL_FALSE,
                0,
                None)
            glEnableVertexAttribArray(self.position_attrib_index)

            ###################################################################
            # Uniform block
            self._uniform_buffer = BufferObject(glGenBuffers(1))
            glBindBuffer(
                GL_UNIFORM_BUFFER, self._uniform_buffer.identifier)
            glBufferData(
                GL_UNIFORM_BUFFER,
                ctypes.sizeof(self._uniform_block),
                ctypes.byref(self._uniform_block),
                GL_STREAM_DRAW)

            glUniformBlockBinding(
                self._program.identifier,
                glGetUniformBlockIndex(
                    self._program.identifier,
                    "MyUniformBlock"),
                self.uniform_bind_point)
            glBindBufferBase(GL_UNIFORM_BUFFER, self.uniform_bind_point,
                             self._uniform_buffer.identifier)


            ###################################################################
            # Textures

            self._texture = TextureObject.create()
            glBindTexture(GL_TEXTURE_2D, self._texture.identifier)
            glTexStorage2D(GL_TEXTURE_2D,
                           8, # mipmap level
                           GL_RGBA32F,
                           256,
                           256)

            data = np.zeros((256, 256, 4), dtype='f4', order='F')
            self.generate_texture(data)
            glTexSubImage2D(
                GL_TEXTURE_2D,
                0, #level 0
                0, 0, #offset
                256, 256, #size
                GL_RGBA,
                GL_FLOAT,
                data)

        finally:
            glBindVertexArray(NULL_GL_OBJECT)

    @override(ISB6AppDelegate)
    def application_will_terminate(self, app):
        self._vao.invalidate()
        self._program.invalidate()
        self._vertices_buffer.invalidate()
        self._uniform_buffer.invalidate()
        self._texture.invalidate()

    @classmethod
    def create_shader_program(cls, shader_descriptions):
        program = ProgramObject(glCreateProgram())
        try:
            for shader_type, shader_source in shader_descriptions:
                s = glCreateShader(shader_type)
                try:
                    glShaderSource(s, shader_source)
                    glCompileShader(s)
                    success = glGetShaderiv(s, GL_COMPILE_STATUS)
                    if not success:
                        raise RuntimeError(glGetShaderInfoLog(s))

                    glAttachShader(program.identifier, s)
                finally:
                    glDeleteShader(s)

            glLinkProgram(program.identifier)

            ret, program = program, None
            return ret

        finally:
            if program:
                program.invalidate()

    @override(ISB6AppDelegate)
    def render(self, app, currentTime):
        glBindVertexArray(self._vao.identifier)
        try:
            glUseProgram(self._program.identifier)

            bg_color = (
                math.sin(currentTime) * 0.5 + 0.5,
                math.cos(currentTime) * 0.5 + 0.5,
                0.0,
                1.0
            )
            glClearBufferfv(GL_COLOR, 0, bg_color)
            glClearBufferfv(GL_DEPTH, 0, [1])

            f = currentTime * 0.3
            mv_matrix = Matrix44.identity(dtype='f4')
            mv_matrix *= Matrix44.from_x_rotation(
                currentTime * math.radians(81))
            mv_matrix *= Matrix44.from_y_rotation(
                currentTime * math.radians(45))
            mv_matrix *= Matrix44.from_translation([
                math.sin(2.1 * f) * 0.5,
                math.cos(1.7 * f) * 0.5,
                math.sin(1.3 * f) * math.cos(1.5 * f) * 2.0])
            mv_matrix *= Matrix44.from_translation([0.0, 0.0, -4.0])

            self._uniform_block.mv_matrix[:] = mv_matrix.reshape(16)

            glBufferSubData(
                GL_UNIFORM_BUFFER,
                0,
                ctypes.sizeof(self._uniform_block),
                ctypes.byref(self._uniform_block))

            glDrawArrays(GL_TRIANGLES, 0, 36)

        finally:
            glBindVertexArray(NULL_GL_OBJECT)

    def run(self):
        self._app.run()

    @classmethod
    def generate_texture(cls, data):
        height, width, n = data.shape
        for y in xrange(height):
            for x in xrange(width):
                data[y][x] = [
                    ((x & y) & 0xFF) / 255,
                    ((x | y) & 0xFF) / 255,
                    ((x ^ y) & 0xFF) / 255,
                    1.0
                ]

@click.command()
def main():
    app = MyApplication()
    app.run()

