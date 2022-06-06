#!/usr/bin/env python3
import importlib
import sys
import types

import click
import solid
import solid_state


@click.command()
# TODO use package.module:function syntax instead
@click.argument("target") # TODO better name for target, and make it an option again
@click.option("--module", "-m")
@click.option("--output", "-o")
@click.option("--selector", "-s", default=None)
@click.option("--colorize/--no-colorize", default=True)
@click.option("--color-scheme", "-c", default="solid_state.colors:default")
@click.option("--transform/--no-transform", default=True)
@click.option("--arg", "-a", multiple=True, default=[])
def main(target, module, output, selector, colorize, color_scheme, transform, arg):
    try:
        target_package, target_name = target.split(":")
    except ValueError:
        print(
            (
                "ERROR: Target must be specified in following form:"
                " package.module:var, where var is an OpenSCADObject or a"
                " function which returns an OpenSCADObject, got {target}"
            )
        )
        sys.exit(1)

    target_module = importlib.import_module(target_package)
    target_var = getattr(target_module, target_name)

    if isinstance(target_var, solid.OpenSCADObject):
        target_object = target_var

    elif isinstance(target_var, types.FunctionType):
        args = {}
        for a in arg:
            k, v = a.split("=")
            args[k] = v

        target_object = target_var(**args)

        if not isinstance(target_object, solid.OpenSCADObject):
            raise ValueError(
                (
                    "ERROR: Target function must return an OpenSCADObject"
                    f", got {type(target_object)}"
                )
            )

    else:
        raise ValueError(
            (
                "ERROR: Target must be OpenSCADObject or a function which"
                f" returns an OpenSCADObject, got {type(target_var)}"
            )
        )

    solid_state.render_scad(
        scad_obj=target_object,
        file_path=output,
        selector=selector,
        transform=transform,
        colorize=colorize,
        color_scheme=color_scheme,
    )


if __name__ == "__main__":
    main()
