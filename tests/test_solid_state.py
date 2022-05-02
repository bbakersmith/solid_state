import pytest
import solid

import solid_state.solid_state as solid_state


def test_pipe():
    result = solid_state.pipe(
        5,
        lambda x: x + 3,
        lambda y: y * 10,
        lambda z: z / 4,
    )

    assert result == 20


def test_pipe_solid():
    obj = solid_state.pipe(
        solid.cube(5),
        solid.rotate([15, 30, 45]),
        solid.translate([1, 2, 3]),
    )

    assert obj.name == "translate"

    assert len(obj.children) == 1
    assert obj.children[0].name == "rotate"

    assert len(obj.children[0].children) == 1
    assert obj.children[0].children[0].name == "cube"

    assert len(obj.children[0].children[0].children) == 0


def test_compose():
    composed = solid_state.compose(
        lambda x: x + 3,
        lambda y: y * 10,
        lambda z: z / 4,
    )

    assert composed(5) == 20
    assert composed(7) == 25


def test_compose_solid():
    composed = solid_state.compose(
        solid.rotate([15, 30, 45]),
        solid.translate([1, 2, 3]),
    )

    obj = composed(solid.cube(5))

    assert obj.name == "translate"

    assert len(obj.children) == 1
    assert obj.children[0].name == "rotate"

    assert len(obj.children[0].children) == 1
    assert obj.children[0].children[0].name == "cube"

    assert len(obj.children[0].children[0].children) == 0


def test_save_state():
    obj = solid.cube(5)
    result = solid_state.save_state("my-cube")(obj)

    state = result.get_trait("solid_state")
    assert state is not None
    assert state.get("name") == "my-cube"
    assert state.get("attributes") == {}


def test_state_decorator():
    @solid_state.state("my-cube")
    def create_my_cube():
        return solid.cube(5)

    result = create_my_cube()

    state = result.get_trait("solid_state")
    assert state is not None
    assert state.get("name") == "my-cube"
    assert state.get("attributes") == {}


def test_save_state_attributes():
    obj = solid.cube(5)
    result = solid_state.save_state("my-cube", dict(alpha=1, beta=2))(obj)

    state = result.get_trait("solid_state")
    assert state is not None
    assert state.get("name") == "my-cube"
    assert state.get("attributes") == dict(alpha=1, beta=2)


def test_state_decorator_attributes():
    @solid_state.state("my-cube", dict(alpha=1, beta=2))
    def create_my_cube():
        return solid.cube(5)

    result = create_my_cube()

    state = result.get_trait("solid_state")
    assert state is not None
    assert state.get("name") == "my-cube"
    assert state.get("attributes") == dict(alpha=1, beta=2)


def test_get_name():
    obj1 = solid_state.save_state("my-cube", dict(alpha=1, beta=2))(solid.cube(5))
    obj2 = solid_state.save_state("my-sphere", dict(alpha=7, beta=9))(solid.sphere(5))

    assert solid_state.get_name(obj1) == "my-cube"
    assert solid_state.get_name(obj2) == "my-sphere"


def test_get_objects():
    obj1 = solid_state.save_state("my-cube", dict(alpha=1, beta=2))(solid.cube(5))
    obj2 = solid_state.save_state("my-sphere", dict(alpha=3, beta=4))(solid.sphere(5))
    obj3 = solid_state.save_state("my-sphere", dict(alpha=7, beta=9))(solid.sphere(5))
    combined = obj1 + obj2 + obj3

    res1 = solid_state.get_objects(combined, "my-cube")
    res2 = solid_state.get_objects(combined, "my-sphere")

    assert len(res1) == 1
    assert len(res2) == 2
    assert solid_state.get_name(res1[0]) == "my-cube"
    assert solid_state.get_name(res2[0]) == "my-sphere"
    assert solid_state.get_name(res2[1]) == "my-sphere"


def test_get_objects_by_path():
    obj1a = solid_state.save_state("my-cube")(solid.cube(5))
    obj1b = solid_state.save_state("my-sphere")(solid.sphere(5))
    parent1 = solid_state.save_state("parent-1")(
        solid.translate([1, 2, 3])(obj1a + obj1b)
    )

    obj2a = solid_state.save_state("my-cube")(solid.cube(5))
    obj2b = solid_state.save_state("my-cube")(solid.cube(5))
    parent2 = solid_state.save_state("parent-2")(
        solid.translate([4, 5, 6])(obj2a + obj2b)
    )

    combined = parent1 + parent2

    res1 = solid_state.get_objects(combined, "parent-1.my-cube")
    res2 = solid_state.get_objects(combined, "parent-2.my-cube")

    assert len(res1) == 1
    assert len(res2) == 2
    assert solid_state.get_name(res1[0]) == "my-cube"
    assert solid_state.get_name(res2[0]) == "my-cube"
    assert solid_state.get_name(res2[1]) == "my-cube"


def test_get_object():
    obj1 = solid_state.save_state("my-cube", dict(alpha=1, beta=2))(solid.cube(5))
    obj2 = solid_state.save_state("my-sphere", dict(alpha=3, beta=4))(solid.sphere(5))
    obj3 = solid_state.save_state("my-sphere", dict(alpha=7, beta=9))(solid.sphere(5))
    combined = obj1 + obj2 + obj3

    res1 = solid_state.get_object(combined, "my-cube")

    with pytest.raises(Exception):
        solid_state.get_object(combined, "my-sphere")

    with pytest.raises(Exception):
        solid_state.get_object(combined, "my-other-thing")

    assert solid_state.get_name(res1) == "my-cube"


def test_get_attributes():
    obj1 = solid_state.save_state("my-cube", dict(alpha=1, beta=2))(solid.cube(5))
    obj2 = solid_state.save_state("my-sphere", dict(alpha=7, beta=9))(solid.sphere(5))
    combined = obj1 + obj2

    assert solid_state.get_attributes(combined, "my-cube").get("alpha") == 1
    assert solid_state.get_attributes(combined, "my-cube").get("beta") == 2
    assert solid_state.get_attributes(combined, "my-sphere").get("alpha") == 7
    assert solid_state.get_attributes(combined, "my-sphere").get("beta") == 9


def test_get_attributes_by_path():
    obj1 = solid_state.save_state("my-cube", dict(alpha=1, beta=2))(solid.cube(5))
    parent1 = solid_state.save_state("parent-1")(solid.translate([1, 2, 3])(obj1))

    obj2 = solid_state.save_state("my-cube", dict(alpha=7, beta=9))(solid.cube(5))
    parent2 = solid_state.save_state("parent-2")(solid.translate([4, 5, 6])(obj2))

    combined = parent1 + parent2

    assert solid_state.get_attributes(combined, "parent-1.my-cube").get("alpha") == 1
    assert solid_state.get_attributes(combined, "parent-1.my-cube").get("beta") == 2
    assert solid_state.get_attributes(combined, "parent-2.my-cube").get("alpha") == 7
    assert solid_state.get_attributes(combined, "parent-2.my-cube").get("beta") == 9


def test_get_transformations():
    obj = solid.cube(5)
    obj = solid.scale(5)(obj)
    obj = solid_state.save_state("my-cube")(obj)
    obj = solid.translate([1, 2, 3])(obj)
    obj = solid.rotate([45, 90, 180])(obj)
    obj = solid.color("red")(obj)

    obj2 = solid.sphere(5)
    obj2 = solid_state.save_state("my-sphere")(obj2)
    obj2 = solid.color("blue")(obj2)

    obj += obj2

    obj = solid_state.save_state("my-parent")(obj)
    obj = solid.mirror([1, 0, 0])(obj)
    obj = solid.rotate([90, 0, 0])(obj)

    for path in ["my-cube", "my-parent.my-cube"]:
        result = solid_state.get_transformations(obj, path)

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

    parent_result = solid_state.get_transformations(obj, "my-parent")

    assert len(parent_result) == 2

    assert parent_result[0].name == "mirror"
    assert parent_result[1].name == "rotate"

    assert parent_result[0].params["v"] == [1, 0, 0]
    assert parent_result[1].params["a"] == [90, 0, 0]

    sphere_result = solid_state.get_transformations(obj, "my-sphere")

    assert len(sphere_result) == 3

    assert sphere_result[0].name == "color"
    assert sphere_result[1].name == "mirror"
    assert sphere_result[2].name == "rotate"

    assert sphere_result[0].params["c"] == "blue"
    assert sphere_result[1].params["v"] == [1, 0, 0]
    assert sphere_result[2].params["a"] == [90, 0, 0]


# TODO test
# - transform_like
# - render_states
