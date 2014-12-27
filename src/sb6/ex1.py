#!/usr/bin/env python
# encoding: utf-8
from .app import Application as SB6App, IApplicationDelegate as ISB6AppDelegate
from OpenGL.GL import *
import click
import math
import pkg_resources
from .util import override
from enum import Enum
import logging
import numpy as np
from lazy import lazy

NULL_GL_OBJECT = 0

logging.basicConfig()


class MyUniformBlock(ctypes.Structure):
    _fields_ = (
        ("offset", ctypes.c_float * 4),
    )


class MyApplication(ISB6AppDelegate):

    def __init__(self):
        self._app = SB6App(self)

        self._program = NULL_GL_OBJECT
        self._vao = NULL_GL_OBJECT
        self._vertices_buffer = NULL_GL_OBJECT
        self._uniform_buffer = NULL_GL_OBJECT

        self._uniform_block = MyUniformBlock()

    @property
    def position_attrib_index(self):
        return 0

    @property
    def uniform_bind_point(self):
        return 0

    @override(ISB6AppDelegate)
    def application_did_finish_launching(self, app):
        self._program = self.create_shader_program()

        self._vao = glGenVertexArrays(1)
        glBindVertexArray(self._vao)

        #######################################################################
        # Vertex array
        self._vertices_buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self._vertices_buffer)
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

        #######################################################################
        # Uniform block
        self._uniform_block_buffer = glGenBuffers(1)
        glBindBuffer(GL_UNIFORM_BUFFER, self._uniform_block_buffer)
        glBufferData(
            GL_UNIFORM_BUFFER,
            ctypes.sizeof(self._uniform_block),
            ctypes.byref(self._uniform_block),
            GL_STREAM_DRAW)

        glUniformBlockBinding(
            self._program,
            glGetUniformBlockIndex(self._program, "MyUniformBlock"),
            self.uniform_bind_point)
        glBindBufferBase(GL_UNIFORM_BUFFER, self.uniform_bind_point,
                         self._uniform_block_buffer)

        glEnableVertexAttribArray(self.position_attrib_index)
        glBindVertexArray(NULL_GL_OBJECT)

    @override(ISB6AppDelegate)
    def application_will_terminate(self, app):
        if self._vao:
            glDeleteVertexArrays(1, [self._vao])

        if self._program:
            glDeleteProgram(self._program)

        if self._uniform_block_buffer:
            glDeleteBuffers(1, [self._uniform_block_buffer])

        if self._vertices_buffer:
            glDeleteBuffers(1, [self._vertices_buffer])

    @classmethod
    def create_shader_program(cls):
        shader_descriptions = [
            (GL_VERTEX_SHADER, pkg_resources.resource_string(
                __name__, 'shaders/ex1.vert')),
            (GL_FRAGMENT_SHADER, pkg_resources.resource_string(
                __name__, 'shaders/ex1.frag')),
        ]

        program = glCreateProgram()
        try:
            for shader_type, shader_source in shader_descriptions:
                s = glCreateShader(shader_type)
                try:
                    glShaderSource(s, shader_source)
                    glCompileShader(s)
                    success = glGetShaderiv(s, GL_COMPILE_STATUS)
                    if not success:
                        raise RuntimeError(glGetShaderInfoLog(s))

                    glAttachShader(program, s)
                finally:
                    glDeleteShader(s)

            glLinkProgram(program)

            ret, program = program, NULL_GL_OBJECT
            return ret

        finally:
            if program:
                glDeleteProgram(program)

    @override(ISB6AppDelegate)
    def render(self, app, currentTime):
        glBindVertexArray(self._vao)
        glUseProgram(self._program)

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

        glBindVertexArray(NULL_GL_OBJECT)

    def run(self):
        self._app.run()


@click.command()
def main():
    app = MyApplication()
    app.run()

