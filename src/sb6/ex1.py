#!/usr/bin/env python
# encoding: utf-8
from .app import Application as SB6App, IApplicationDelegate as ISB6AppDelegate
from OpenGL import GL
import click
import math
import pkg_resources


NULL_GL_OBJECT = 0


class MyApplication(ISB6AppDelegate):

    def __init__(self):
        self._app = SB6App(self)
        self._program = NULL_GL_OBJECT
        self._vao = NULL_GL_OBJECT

    def application_did_finish_launching(self, app):
        self._program = self.create_shader_program()
        self._vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self._vao)

    def application_will_terminate(self, app):
        if self._vao:
            GL.glDeleteVertexArrays(1, [self._vao])

        if self._program:
            GL.glDeleteProgram(self._program)

    @classmethod
    def create_shader_program(cls):
        shader_descriptions = [
            (GL.GL_VERTEX_SHADER, pkg_resources.resource_string(
                __name__, 'ex1.vert')),
            (GL.GL_FRAGMENT_SHADER, pkg_resources.resource_string(
                __name__, 'ex1.frag'))]

        program = GL.glCreateProgram()
        try:
            for shader_type, shader_source in shader_descriptions:
                s = GL.glCreateShader(shader_type)
                try:
                    GL.glShaderSource(s, shader_source)
                    GL.glCompileShader(s)
                    success = GL.glGetShaderiv(s, GL.GL_COMPILE_STATUS)
                    if not success:
                        raise RuntimeError(GL.glGetShaderInfoLog(s))

                    GL.glAttachShader(program, s)
                finally:
                    GL.glDeleteShader(s)

            GL.glLinkProgram(program)

            ret, program = program, NULL_GL_OBJECT
            return ret

        finally:
            if program:
                GL.glDeleteProgram(program)

    def render(self, app, currentTime):
        color = (
            math.sin(currentTime) * 0.5 + 0.5,
            math.cos(currentTime) * 0.5 + 0.5,
            0.0,
            1.0
        )
        GL.glClearBufferfv(GL.GL_COLOR, 0, color)

        GL.glUseProgram(self._program)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 3)

    def run(self):
        self._app.run()


@click.command()
def main():
    app = MyApplication()
    app.run()

