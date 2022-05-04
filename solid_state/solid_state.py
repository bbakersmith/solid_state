from dataclasses import dataclass

from solid_state.lookup import get_name


def pipe(target, *fns):
    for fn in fns:
        target = fn(target)
    return target


def compose(*fns):
    def _compose(x):
        for fn in fns:
            x = fn(x)

        return x

    return _compose


def join(scad_obj):
    def _join(other_obj):
        return other_obj + scad_obj

    return _join


def save_state(name, attributes=None):
    """
    Add solid_state metadata to an object.
    """
    if attributes is None:
        attributes = {}

    def _save_state(scad_obj):
        scad_obj.add_trait("solid_state", dict(name=name, attributes=attributes))
        return scad_obj

    return _save_state


# TODO store wrapped function's arguments in attributes or another meta key?
def state(name, attributes=None):
    """
    Add solid_state metadata to an object returned from the decorated function.
    """

    def _state_decorator(func):
        def _state(*args, **kwargs):
            scad_obj = func(*args, **kwargs)
            return save_state(name, attributes)(scad_obj)

        return _state

    return _state_decorator
