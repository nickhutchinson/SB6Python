
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

