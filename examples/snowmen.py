#!/usr/bin/env python3
from solid import *

import solid_state


@solid_state.state("snowman")
def create_snowman(height):
    bottom = height / 9 * 4
    middle = height / 9 * 3
    top = height / 9 * 2

    return solid_state.pipe(
        sphere(d=top),
        translate([0, 0, (top / 2) + (middle / 2)]),
        solid_state.join(sphere(d=middle)),
        translate([0, 0, (middle / 2) + (bottom / 2)]),
        solid_state.join(sphere(d=bottom)),
        translate([0, 0, bottom / 2]),
    )


@solid_state.state("spiral_snowmen")
def create_spiral_snowmen():
    snowman_1 = create_snowman(10)
    snowman_2 = create_snowman(15)
    snowman_3 = create_snowman(20)
    snowman_4 = create_snowman(25)
    snowman_5 = create_snowman(30)

    return solid_state.pipe(
        snowman_1,
        translate([5, 5, 0]),
        rotate([0, 0, 45]),
        solid_state.join(snowman_2),
        translate([10, 10, 0]),
        rotate([0, 0, 45]),
        solid_state.join(snowman_3),
        translate([15, 15, 0]),
        rotate([0, 0, 45]),
        solid_state.join(snowman_4),
        translate([20, 20, 0]),
        rotate([0, 0, 45]),
        solid_state.join(snowman_5),
        translate([25, 25, 0]),
        rotate([0, 0, 45]),
    )


# def create_top_hat(snowman):
#     # TODO
#     # - allow for get_attributes without a path to indicate current object
#     snowman_height = solid_state.get_attributes(snowman).get("height")
#     brim_diameter = snowman_height / 9 * 3
#     brim_height = snowman_height / 18
#     diameter = snowman_height / 9 * 2
#     height = diameter * 2
#
#     return solid_state.pipe(
#         cylinder(h=height, d=diameter) + cylinder(h=brim_height, d=brim_diameter),
#         solid_state.save_state("top_hat", dict(height=height)),
#         translate([0, 0, snowman_height]),
#         translate_like(snowman),
#     )


# TODO
# - create different styles of hat for each group
# - or randomly create hats for all snowmen


# scene = create_snowman(height=20)


scene = create_spiral_snowmen()


# for snowman in get_objects(scene, "spiral_snowmen.snowman"):
#     scene += create_top_hat(snowman)


# scad_render_to_file(scene, "snowmen.scad")
