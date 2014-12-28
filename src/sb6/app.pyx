import os
import traceback

cdef extern from "sb6-c.h":
    cdef struct __SB6Application:
        pass

    ctypedef __SB6Application * SB6ApplicationRef

    cdef struct SB6AppContext:
        void* self
        void (*render)(void* self, double currentTime)
        void (*startup)(void* self);
        void (*shutdown)(void* self);
        void (*onResize)(void* self, int w, int h);


    SB6ApplicationRef SB6ApplicationCreate(const SB6AppContext*)
    void SB6ApplicationRun(SB6ApplicationRef)
    void SB6ApplicationDispose(SB6ApplicationRef)


cdef extern:
    void SB6TextureLoadFromFile(unsigned textureID, const char* path)


def texture_load_from_file(texture_id, path):
    SB6TextureLoadFromFile(texture_id, path)

import abc, weakref

class IApplicationDelegate(object):
    __metaclass__ = abc.ABCMeta

    def render(self, application, currentTime):
        pass

    def application_did_finish_launching(self, application):
        pass

    def application_will_terminate(self, application):
        pass

    def window_did_resize(self, application, width, height):
        pass

cdef class Application:
    cdef readonly object delegate
    cdef bint is_running
    cdef SB6ApplicationRef app

    def __cinit__(self):
        cdef SB6AppContext context
        context.self = <void*>self
        context.render = self._render
        context.startup = self._startup
        context.shutdown = self._shutdown
        context.onResize = self._resize

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
        try:
            self.delegate.render(self, currentTime)
        except:
            traceback.print_exc()
            os._exit(1)

    @staticmethod
    cdef void _startup(void* context_self):
        cdef Application self = <Application>context_self
        try:
            self.delegate.application_did_finish_launching(self)
        except:
            traceback.print_exc()
            os._exit(1)

    @staticmethod
    cdef void _shutdown(void* context_self):
        cdef Application self = <Application>context_self
        try:
            self.delegate.application_will_terminate(self)
        except:
            traceback.print_exc()
            os._exit(1)

    @staticmethod
    cdef void _resize(void* context_self, int w, int h):
        cdef Application self = <Application>context_self
        try:
            self.delegate.window_did_resize(self, w, h)
        except:
            traceback.print_exc()
            os._exit(1)
