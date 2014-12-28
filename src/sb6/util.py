from OpenGL import GL

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

