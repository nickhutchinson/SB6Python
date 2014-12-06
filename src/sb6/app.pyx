cdef extern from "sb6-c.h":
    cdef struct __SB6Application:
        pass

    ctypedef __SB6Application * SB6ApplicationRef

    cdef struct SB6AppContext:
        void* self
        void (*render)(void* self, double currentTime)


    SB6ApplicationRef SB6ApplicationCreate(const SB6AppContext*)
    void SB6ApplicationRun(SB6ApplicationRef)
    void SB6ApplicationDispose(SB6ApplicationRef)


import abc, weakref

class IApplicationDelegate(object):
    __metaclass__ = abc.ABCMeta

    def render(self, application, currentTime):
        pass

cdef class Application:
    cdef bint running
    cdef SB6ApplicationRef app
    cdef object delegate

    def __cinit__(self):
        cdef SB6AppContext context
        context.self = <void*>self
        context.render = self._on_render

        self.running = False
        self.app = SB6ApplicationCreate(&context)

    def __init__(self, delegate):
        self.delegate = weakref.proxy(delegate)

    def __dealloc__(self):
        SB6ApplicationDispose(self.app)

    def run(self):
        assert(not self.running)
        self.running = True
        SB6ApplicationRun(self.app)

    @staticmethod
    cdef void _on_render(void* context_self, double currentTime):
        cdef Application self = <Application>context_self
        self.delegate.render(self, currentTime)
