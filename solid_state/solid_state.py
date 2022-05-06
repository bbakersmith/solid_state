from dataclasses import dataclass
import inspect


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
def state(name):
    """
    Add solid_state metadata to an object returned from the decorated function.
    """

    def _state(func):
        def _wrapper(*args, **kwargs):
            scad_obj = func(*args, **kwargs)

            attributes = {}

            # TODO probably need to do more to support splat args

            sig = inspect.signature(func)

            for i, [k, param] in enumerate(sig.parameters.items()):
                if i < len(args):
                    attributes[k] = args[i]

                else:
                    attributes[k] = param.default

            attributes.update(kwargs)

            # argspec = inspect.getfullargspec(func)
            # import pdb;pdb.set_trace()
            #
            # for i, arg_name in enumerate(argspec.args):
            #     if i < len(args):
            #         attributes[arg_name] = args[i]
            #     else:
            #         attributes[arg_name] = argspec.defaults[i]
            #
            # attributes.update(kwargs)

            return save_state(name=name, attributes=attributes)(scad_obj)

        return _wrapper

    return _state
