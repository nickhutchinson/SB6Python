cdef extern from "sb6-c.h":
    cdef struct __SB6Application:
        pass

    ctypedef __SB6Application * SB6ApplicationRef

    cdef struct SB6AppContext:
        void* self
        void (*render)(void* self, double currentTime)
        void (*startup)(void* self);
        void (*shutdown)(void* self);


    SB6ApplicationRef SB6ApplicationCreate(const SB6AppContext*)
    void SB6ApplicationRun(SB6ApplicationRef)
    void SB6ApplicationDispose(SB6ApplicationRef)


import abc, weakref

class IApplicationDelegate(object):
    __metaclass__ = abc.ABCMeta

    def render(self, application, currentTime):
        pass

    def application_did_finish_launching(self, application):
        pass

    def application_will_terminate(self, application):
        pass

cdef class Application:
    cdef readonly bint is_running
    cdef readonly object delegate
    cdef SB6ApplicationRef app

    def __cinit__(self):
        cdef SB6AppContext context
        context.self = <void*>self
        context.render = self._render
        context.startup = self._startup
        context.shutdown = self._shutdown

        self.is_running = False
        self.app = SB6ApplicationCreate(&context)

    def __init__(self, delegate):
        """
        Args:
            delegate: object implementing the IApplicationDelegate protocol.
        """
        self.delegate = weakref.proxy(delegate)

    def __dealloc__(self):
        SB6ApplicationDispose(self.app)

    def run(self):
        """Starts the main application loop."""
        assert(not self.is_running)
        self.is_running = True
        SB6ApplicationRun(self.app)

    @staticmethod
    cdef void _render(void* context_self, double currentTime):
        cdef Application self = <Application>context_self
        self.delegate.render(self, currentTime)

    @staticmethod
    cdef void _startup(void* context_self):
        cdef Application self = <Application>context_self
        self.delegate.application_did_finish_launching(self)

    @staticmethod
    cdef void _shutdown(void* context_self):
        cdef Application self = <Application>context_self
        self.delegate.application_will_terminate(self)
