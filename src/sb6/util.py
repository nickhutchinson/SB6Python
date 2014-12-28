from OpenGL import GL
from .app import texture_load_from_file

NULL_GL_OBJECT = 0

class GLObject(object):

    def __init__(self, ident=NULL_GL_OBJECT):
        self._identifier = ident

    def __del__(self):
        self.invalidate()

    @property
    def identifier(self):
        return self._identifier

    def invalidate(self):
        if self.identifier != NULL_GL_OBJECT:
            self._delete(self.identifier)
            self._identifier = NULL_GL_OBJECT

    @classmethod
    def _delete(cls, identifier):
        raise NotImplementedError


class BufferObject(GLObject):

    @classmethod
    def _delete(cls, identifier):
        GL.glDeleteBuffers(1, [identifier])


class VertexArrayObject(GLObject):

    @classmethod
    def _delete(cls, identifier):
        GL.glDeleteVertexArrays(1, [identifier])


class ProgramObject(GLObject):

    @classmethod
    def _delete(cls, identifier):
        GL.glDeleteProgram(identifier)

class TextureObject(GLObject):

    @classmethod
    def create(cls):
        return cls(GL.glGenTextures(1))

    def _delete(cls, identifier):
        # Passing an explict length seems to error, unlke other glDeleteXXX
        # calls.
        GL.glDeleteTextures([identifier])



def override(klass):
    def f(meth):
        name = meth.__name__
        if not getattr(klass, name):
            raise TypeError(
                'Method {!r} must be overridden from class {!r}'.format(
                    name,
                    klass.__name__))
        return meth

    return f

