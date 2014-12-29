#!/usr/bin/env python
# encoding: utf-8
from __future__ import print_function, division

import os
import click
import logging
import math
import numpy as np
import pkg_resources
import contextlib

from .app import (
    Object as SB6Object,
    Application as SB6App,
    IApplicationDelegate as ISB6AppDelegate)
from .util import (
    override,
    BufferObject,
    VertexArrayObject,
    ShaderObject,
    ProgramObject,
    TextureObject)
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


@contextlib.contextmanager
def gl_cleanup():
    objects = set()
    yield objects
    for elem in objects:
        elem.invalidate()


class MyApplication(ISB6AppDelegate):

    def __init__(self):
        self._app = SB6App(self)

        self._program = ProgramObject()
        self._vao = VertexArrayObject()
        self._vertices_buffer = BufferObject()
        self._uniform_buffer = BufferObject()
        self._texture = TextureObject()

        self._torus_obj = None

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
            # Objects
            torus_path = pkg_resources.resource_filename(
                __name__, "resources/torus_nrms_tc.sbm")
            self._torus_obj = SB6Object(torus_path)

        finally:
            glBindVertexArray(NULL_GL_OBJECT)

        ###################################################################
        # Textures
        self._texture = TextureObject.create()
        glBindTexture(GL_TEXTURE_2D, self._texture.identifier)
        glTexStorage2D(GL_TEXTURE_2D,
                       8,  # mipmap level
                       GL_RGBA32F,
                       256,
                       256)

        data = np.zeros((256, 256, 4), dtype='f4', order='F')
        self.generate_texture(data)
        glTexSubImage2D(
            GL_TEXTURE_2D,
            0,  # level 0
            0, 0,  # offset
            256, 256,  # size
            GL_RGBA,
            GL_FLOAT,
            data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

    @override(ISB6AppDelegate)
    def application_will_terminate(self, app):
        self._vao.invalidate()
        self._program.invalidate()
        self._vertices_buffer.invalidate()
        self._uniform_buffer.invalidate()
        self._texture.invalidate()

    @classmethod
    def create_shader_program(cls, shader_descriptions):
        with gl_cleanup() as cleanup:
            program = ProgramObject(glCreateProgram())
            cleanup.add(program)

            for shader_type, shader_source in shader_descriptions:
                s = ShaderObject.create(shader_type)
                cleanup.add(s)

                glShaderSource(s.identifier, shader_source)
                glCompileShader(s.identifier)
                success = glGetShaderiv(s.identifier, GL_COMPILE_STATUS)
                if not success:
                    raise RuntimeError(glGetShaderInfoLog(s.identifier))

                glAttachShader(program.identifier, s.identifier)

            glLinkProgram(program.identifier)

            cleanup.remove(program)
            return program

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

            self._torus_obj.render()

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

