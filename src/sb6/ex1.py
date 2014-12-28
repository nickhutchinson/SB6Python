#!/usr/bin/env python
# encoding: utf-8
from .app import Application as SB6App, IApplicationDelegate as ISB6AppDelegate
from OpenGL.GL import *
import click
import math
import pkg_resources
from .util import override, BufferObject, VertexArrayObject, ProgramObject
from enum import Enum
import logging
import numpy as np
from lazy import lazy
from pyrr import Matrix44, Vector4

NULL_GL_OBJECT = 0

logging.basicConfig()


class MyUniformBlock(ctypes.Structure):
    _fields_ = (
        ("offset", ctypes.c_float * 4),
    )


class MyApplication(ISB6AppDelegate):

    def __init__(self):
        self._app = SB6App(self)

        self._program = ProgramObject()
        self._vao = VertexArrayObject()
        self._vertices_buffer = BufferObject()
        self._uniform_buffer = BufferObject()

        self._uniform_block = MyUniformBlock()

    @property
    def position_attrib_index(self):
        return 0

    @property
    def uniform_bind_point(self):
        return 0

    @override(ISB6AppDelegate)
    def window_did_resize(self, application, width, height):
        pass
        # print("Resize {}x{}".format(width, height))

    @override(ISB6AppDelegate)
    def application_did_finish_launching(self, app):
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glFrontFace(GL_CW)

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
            data = np.array((
                0.25, -0.25, 0.5, 1.0,
                -0.25, -0.25, 0.5, 1.0,
                0.25, 0.25, 0.5, 1.0,),
                dtype='f4')

            glBufferData(GL_ARRAY_BUFFER, data, GL_STATIC_DRAW)
            glVertexAttribPointer(
                self.position_attrib_index,
                4,
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

        finally:
            glBindVertexArray(NULL_GL_OBJECT)

    @override(ISB6AppDelegate)
    def application_will_terminate(self, app):
        self._vao.invalidate()
        self._program.invalidate()
        self._vertices_buffer.invalidate()
        self._uniform_buffer.invalidate()

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

            self._uniform_block.offset = (
                math.sin(currentTime) * 0.5,
                math.cos(currentTime) * 0.6,
                0.0,
                0.0,
            )

            glBufferSubData(
                GL_UNIFORM_BUFFER,
                0,
                ctypes.sizeof(self._uniform_block),
                ctypes.byref(self._uniform_block))

            glDrawArrays(GL_TRIANGLES, 0, 3)

        finally:
            glBindVertexArray(NULL_GL_OBJECT)

    def run(self):
        self._app.run()


@click.command()
def main():
    app = MyApplication()
    app.run()

