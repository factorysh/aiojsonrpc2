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
    """
    Build a dict of key/coroutine function from stuffs.

    args can be function, module or class.
    * function: function has a name.
    * module: all public functions (described in __all__ list), not starting with a _
    * class: all methods with name not starting with a _
    """
    for arg in args:
        if isinstance(arg, types.FunctionType): # It's a function
            kwargs[arg.__name__] = arg
        elif isinstance(arg, types.ModuleType): # It's a module
            if '__all__' not in dir(arg):
                continue
            kwargs.update(dict(_get_callable(arg, arg.__all__, arg.__name__)))
        else: # It's a class
            kwargs.update(dict(_get_callable(arg, dir(arg),
                                             arg.__class__.__name__)))

    for method in kwargs.values():
        assert asyncio.iscoroutinefunction(method)
    return kwargs

