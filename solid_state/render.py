import importlib

import solid

import solid_state.colors as colors
import solid_state.lookup as lookup
import solid_state.solid_state as solid_state


def render_scad(scad_obj, file_path, selector=None, transform=True, colorize=True, color_scheme="solid_state.colors:default"):
    """
    Render all objects with matching solid_state names to file.
    """
    color_scheme_package, color_scheme_name = color_scheme.split(":")
    color_scheme_module = importlib.import_module(color_scheme_package)
    color_scheme = getattr(color_scheme_module, color_scheme_name)

    if selector is None:
        combined = scad_obj
        if colorize is True:
            combined = solid.color(color_scheme[0])(combined)

    else:
        groups = map(lambda x: x.strip(), selector.split(","))

        # TODO support color schemes, also cycle to not overflow

        combined = solid.cube([0, 0, 0])
        for i, selector in enumerate(groups):
            objects = lookup.get_objects(scad_obj, selector)
            if transform is True:
                # TODO should get_transformations just return composed already?
                # will i ever want to do anything but apply them as a whole?
                transformations = map(
                    lambda t: solid_state.compose(*t),
                    lookup.get_transformations(scad_obj, selector)
                )

                objects = [
                    func(obj) for func, obj in zip(transformations, objects)
                ]

            if colorize is True:
                objects = map(solid.color(color_scheme[i]), objects)

            for obj in objects:
                combined += obj

    solid.scad_render_to_file(combined, file_path)
