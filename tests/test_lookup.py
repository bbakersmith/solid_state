import pytest
import solid

from solid_state.solid_state import save_state
from solid_state.lookup import (
    _get_paths_for_query,
    get_attributes,
    get_name,
    get_object,
    get_objects,
    get_transformations,
)


def test_get_name():
    obj1 = save_state("my-cube", dict(alpha=1, beta=2))(solid.cube(5))
    obj2 = save_state("my-sphere", dict(alpha=7, beta=9))(solid.sphere(5))

    assert get_name(obj1) == "my-cube"
    assert get_name(obj2) == "my-sphere"


def test_get_paths_for_query():
    scad_obj = solid.mirror([1, 0, 0])(
        solid.union()(
            solid.translate([10, 20, 30])(
                solid.cube(5),
                solid.rotate([20, 40, 60])(
                    solid.union()(
                        solid.cylinder(h=10, d=5),
                        solid.sphere(6),
                    ),
                ),
            ),
            solid.sphere(3),
        )
    )

    assert _get_paths_for_query(scad_obj, "mirror") == [()]
    assert _get_paths_for_query(scad_obj, "translate") == [
        (
            0,
            0,
        )
    ]
    assert _get_paths_for_query(scad_obj, "sphere") == [
        (
            0,
            0,
            1,
            0,
            1,
        ),
        (
            0,
            1,
        ),
    ]
    assert _get_paths_for_query(scad_obj, "cube") == [
        (
            0,
            0,
            0,
        )
    ]
    assert _get_paths_for_query(scad_obj, "rotate") == [
        (
            0,
            0,
            1,
        )
    ]
    assert _get_paths_for_query(scad_obj, "cylinder") == [
        (
            0,
            0,
            1,
            0,
            0,
        )
    ]
    assert _get_paths_for_query(scad_obj, "rotate sphere") == [
        (
            0,
            0,
            1,
            0,
            1,
        )
    ]
    assert _get_paths_for_query(scad_obj, "cube, cylinder") == [
        (
            0,
            0,
            0,
        ),
        (
            0,
            0,
            1,
            0,
            0,
        ),
    ]

    # TODO more paths


def test_get_objects():
    obj1 = save_state("my-cube", dict(alpha=1, beta=2))(solid.cube(5))
    obj2 = save_state("my-sphere", dict(alpha=3, beta=4))(solid.sphere(5))
    obj3 = save_state("my-sphere", dict(alpha=7, beta=9))(solid.sphere(5))
    combined = obj1 + obj2 + obj3

    res1 = get_objects(combined, ".my-cube")
    res2 = get_objects(combined, ".my-sphere")

    assert len(res1) == 1
    assert len(res2) == 2
    assert get_name(res1[0]) == "my-cube"
    assert get_name(res2[0]) == "my-sphere"
    assert get_name(res2[1]) == "my-sphere"


def test_get_objects_by_path():
    obj1a = save_state("my-cube")(solid.cube(5))
    obj1b = save_state("my-sphere")(solid.sphere(5))
    parent1 = save_state("parent-1")(solid.translate([1, 2, 3])(obj1a + obj1b))

    obj2a = save_state("my-cube")(solid.cube(5))
    obj2b = save_state("my-cube")(solid.cube(5))
    parent2 = save_state("parent-2")(solid.translate([4, 5, 6])(obj2a + obj2b))

    combined = parent1 + parent2

    res1 = get_objects(combined, ".parent-1 .my-cube")
    res2 = get_objects(combined, ".parent-2 .my-cube")

    assert len(res1) == 1
    assert len(res2) == 2
    assert get_name(res1[0]) == "my-cube"
    assert get_name(res2[0]) == "my-cube"
    assert get_name(res2[1]) == "my-cube"


def test_get_object():
    obj1 = save_state("my-cube", dict(alpha=1, beta=2))(solid.cube(5))
    obj2 = save_state("my-sphere", dict(alpha=3, beta=4))(solid.sphere(5))
    obj3 = save_state("my-sphere", dict(alpha=7, beta=9))(solid.sphere(5))
    combined = obj1 + obj2 + obj3

    res1 = get_object(combined, ".my-cube")

    with pytest.raises(Exception):
        get_object(combined, ".my-sphere")

    with pytest.raises(Exception):
        get_object(combined, ".my-other-thing")

    assert get_name(res1) == "my-cube"


def test_get_attributes():
    obj1 = save_state("my-cube", dict(alpha=1, beta=2))(solid.cube(5))
    obj2 = save_state("my-sphere", dict(alpha=7, beta=9))(solid.sphere(5))
    combined = obj1 + obj2

    assert get_attributes(combined, ".my-cube").get("alpha") == 1
    assert get_attributes(combined, ".my-cube").get("beta") == 2
    assert get_attributes(combined, ".my-sphere").get("alpha") == 7
    assert get_attributes(combined, ".my-sphere").get("beta") == 9


def test_get_attributes_by_path():
    obj1 = save_state("my-cube", dict(alpha=1, beta=2))(solid.cube(5))
    parent1 = save_state("parent-1")(solid.translate([1, 2, 3])(obj1))

    obj2 = save_state("my-cube", dict(alpha=7, beta=9))(solid.cube(5))
    parent2 = save_state("parent-2")(solid.translate([4, 5, 6])(obj2))

    combined = parent1 + parent2

    assert get_attributes(combined, ".parent-1 .my-cube").get("alpha") == 1
    assert get_attributes(combined, ".parent-1 .my-cube").get("beta") == 2
    assert get_attributes(combined, ".parent-2 .my-cube").get("alpha") == 7
    assert get_attributes(combined, ".parent-2 .my-cube").get("beta") == 9


def test_get_transformations():
    obj = solid.cube(5)
    obj = solid.scale(5)(obj)
    obj = save_state("my-cube")(obj)
    obj = solid.translate([1, 2, 3])(obj)
    obj = solid.rotate([45, 90, 180])(obj)
    obj = solid.color("red")(obj)

    obj2 = solid.sphere(5)
    obj2 = save_state("my-sphere")(obj2)
    obj2 = solid.color("blue")(obj2)

    obj += obj2

    obj = save_state("my-parent")(obj)
    obj = solid.mirror([1, 0, 0])(obj)
    obj = solid.rotate([90, 0, 0])(obj)

    for path in [".my-cube", ".my-parent .my-cube"]:
        result = get_transformations(obj, path)[0] # TODO FIXME

        assert len(result) == 5

        assert result[0].name == "translate"
        assert result[1].name == "rotate"
        assert result[2].name == "color"
        assert result[3].name == "mirror"
        assert result[4].name == "rotate"

        assert result[0].params["v"] == [1, 2, 3]
        assert result[1].params["a"] == [45, 90, 180]
        assert result[2].params["c"] == "red"
        assert result[3].params["v"] == [1, 0, 0]
        assert result[4].params["a"] == [90, 0, 0]

    parent_result = get_transformations(obj, ".my-parent")[0] # TODO FIXME

    assert len(parent_result) == 2

    assert parent_result[0].name == "mirror"
    assert parent_result[1].name == "rotate"

    assert parent_result[0].params["v"] == [1, 0, 0]
    assert parent_result[1].params["a"] == [90, 0, 0]

    sphere_result = get_transformations(obj, ".my-sphere")[0] # TODO FIXME

    assert len(sphere_result) == 3

    assert sphere_result[0].name == "color"
    assert sphere_result[1].name == "mirror"
    assert sphere_result[2].name == "rotate"

    assert sphere_result[0].params["c"] == "blue"
    assert sphere_result[1].params["v"] == [1, 0, 0]
    assert sphere_result[2].params["a"] == [90, 0, 0]
