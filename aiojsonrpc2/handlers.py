import asyncio


def _get_callable(obj, iter_, prefix):
    for m in iter_:
        if m.startswith('_'):
            continue
        c = getattr(obj, m)
        if callable(c):
            yield "%s.%s" %(prefix, m), c


def handlers(*args, **kwargs):
    for arg in args:
        # FIXME use instanceof
        t = str(type(arg))
        if t == "<class 'function'>":
            kwargs[arg.__name__] = arg
        elif t == "<class 'module'>":
            if '__all__' not in dir(arg):
                continue
            kwargs.update(dict(_get_callable(arg, arg.__all__, arg.__name__)))
        else:
            kwargs.update(dict(_get_callable(arg, dir(arg),
                                             arg.__class__.__name__)))

    for method in kwargs.values():
        assert asyncio.iscoroutinefunction(method)
    return kwargs

