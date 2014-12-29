#!/usr/bin/env python
# encoding: utf-8
from __future__ import print_function, division

import click
import contextlib
import logging
import math
import numpy as np
import os
import pkg_resources
import random

from .app import (
    Object as SB6Object,
    Application as SB6App,
    IApplicationDelegate as ISB6AppDelegate
)
from .util import (
    BufferObject,
    ProgramObject,
    ShaderObject,
    TextureObject,
    VertexArrayObject,
    override,
    texture_load_from_file,
)
from enum import Enum
from lazy import lazy
from OpenGL.GL import *
from pyrr import Matrix44, Vector4

NULL_GL_OBJECT = 0

logging.basicConfig()

NUM_ALIENS = 256


class Droplet_t(ctypes.Structure):
    _fields_ = (
        ("offset", ctypes.c_float * 2),
        ("orientation", ctypes.c_float),
        ("_padding", ctypes.c_float),
    )


class MyUniformBlock(ctypes.Structure):
    _fields_ = (
        ("droplet", Droplet_t * NUM_ALIENS),
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
        # self._vertices_buffer = BufferObject()
        self._uniform_buffer = BufferObject()
        self._texture = TextureObject()

        self._droplets = np.zeros(NUM_ALIENS, dtype=[
            ('x_offset', 'f4'), ('rot_speed', 'f4'), ('fall_speed', 'f4'), ])

    @property
    def alien_index_attrib_index(self):
        return 0

    @property
    def uniform_bind_point(self):
        return 0

    @override(ISB6AppDelegate)
    def application_did_finish_launching(self, app):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self._program = self.create_shader_program([
            (GL_VERTEX_SHADER, pkg_resources.resource_string(
                __name__, 'shaders/ex2.vert')),
            (GL_FRAGMENT_SHADER, pkg_resources.resource_string(
                __name__, 'shaders/ex2.frag')),
        ])

        self._vao = VertexArrayObject(glGenVertexArrays(1))
        glBindVertexArray(self._vao.identifier)
        try:
            ##################################################################
            # Uniform block
            self._uniform_buffer = BufferObject(glGenBuffers(1))
            glBindBuffer(
                GL_UNIFORM_BUFFER, self._uniform_buffer.identifier)
            glBufferData(GL_UNIFORM_BUFFER, ctypes.sizeof(MyUniformBlock),
                         None, GL_DYNAMIC_DRAW)

            block_index = glGetUniformBlockIndex(
                self._program.identifier, "MyUniformBlock")
            assert(block_index != GL_INVALID_INDEX)

            glUniformBlockBinding(
                self._program.identifier,
                block_index,
                self.uniform_bind_point)
            glBindBufferBase(GL_UNIFORM_BUFFER, self.uniform_bind_point,
                             self._uniform_buffer.identifier)

        finally:
            glBindVertexArray(NULL_GL_OBJECT)

        ##################################################################
        # Textures
        self._texture = TextureObject.create()
        texture_load_from_file(
            self._texture.identifier,
            pkg_resources.resource_filename(__file__, "resources/aliens.ktx"))
        glBindTexture(GL_TEXTURE_2D_ARRAY, self._texture.identifier)
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MIN_FILTER,
                        GL_LINEAR_MIPMAP_LINEAR)

        # Droplet properties
        for i in xrange(NUM_ALIENS):
            droplet = self._droplets[i]
            droplet['x_offset'] = random.random() * 2 - 1
            droplet['rot_speed'] = (
                random.random() * 0.5 + ((i & 1) and -3 or 3))
            droplet['fall_speed'] = random.random() + 0.2

    @override(ISB6AppDelegate)
    def application_will_terminate(self, app):
        self._vao.invalidate()
        self._program.invalidate()
        # self._vertices_buffer.invalidate()
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

            uniform_block = MyUniformBlock.from_address(glMapBufferRange(
                GL_UNIFORM_BUFFER,
                0,
                ctypes.sizeof(MyUniformBlock),
                GL_MAP_WRITE_BIT | GL_MAP_INVALIDATE_BUFFER_BIT))

            for i in xrange(NUM_ALIENS):
                props = self._droplets[i]
                droplet = uniform_block.droplet[i]

                offset_x = props['x_offset']
                offset_y = 2.0 - math.fmod(
                    (currentTime + i) * props['fall_speed'], 4.31)

                droplet.offset = (offset_x, offset_y)
                droplet.orientation = (
                    currentTime * props['rot_speed'])

            glUnmapBuffer(GL_UNIFORM_BUFFER)

            for i in xrange(NUM_ALIENS):
                glVertexAttribI1i(self.alien_index_attrib_index, i)
                glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)

        finally:
            glBindVertexArray(NULL_GL_OBJECT)

    def run(self):
        self._app.run()


@click.command()
def main():
    app = MyApplication()
    app.run()

