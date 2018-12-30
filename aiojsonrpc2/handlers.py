import asyncio


def handlers(*args, **kwargs):
    for arg in args:
        # FIXME use instanceof
        t = str(type(arg))
        if t == "<class 'function'>":
            kwargs[arg.__name__] = arg
        elif t == "<class 'module'>":
            if '__all__' not in dir(arg):
                continue
            for m in arg.__all__:
                if m.startswith('_'):
                    continue
                c = getattr(arg, m)
                if callable(c):
                    kwargs["%s.%s" %(arg.__name__, m)] = c
    for method in kwargs.values():
        assert asyncio.iscoroutinefunction(method)
    return kwargs

