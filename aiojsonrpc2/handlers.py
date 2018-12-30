import types
import asyncio


def _get_callable(obj, iter_, prefix):
    for m in iter_:
        if m.startswith('_'):
            continue
        c = getattr(obj, m)
        #if callable(c):
        if asyncio.iscoroutinefunction(c):
            yield "%s.%s" %(prefix, m), c


def handlers(*args, **kwargs):
    for arg in args:
        if isinstance(arg, types.FunctionType): # It's a function
            kwargs[arg.__name__] = arg
        elif isinstance(arg, types.ModuleType):
            if '__all__' not in dir(arg): # It's a module
                continue
            kwargs.update(dict(_get_callable(arg, arg.__all__, arg.__name__)))
        else: # It's a class
            kwargs.update(dict(_get_callable(arg, dir(arg),
                                             arg.__class__.__name__)))

    for method in kwargs.values():
        assert asyncio.iscoroutinefunction(method)
    return kwargs

