import solid

from solid_state.lookup import get_name
from solid_state.solid_state import (
    compose,
    pipe,
    save_state,
    state,
)


def test_pipe():
    result = pipe(
        5,
        lambda x: x + 3,
        lambda y: y * 10,
        lambda z: z / 4,
    )

    assert result == 20


def test_pipe_solid():
    obj = pipe(
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
    composed = compose(
        lambda x: x + 3,
        lambda y: y * 10,
        lambda z: z / 4,
    )

    assert composed(5) == 20
    assert composed(7) == 25


def test_compose_solid():
    composed = compose(
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
    result = save_state("my-cube")(obj)

    meta = result.get_trait("solid_state")
    assert meta is not None
    assert meta.get("name") == "my-cube"
    assert meta.get("attributes") == {}


def test_state_decorator():
    @state("my-cube")
    def create_my_cube():
        return solid.cube(5)

    result = create_my_cube()

    meta = result.get_trait("solid_state")
    assert meta is not None
    assert meta.get("name") == "my-cube"
    assert meta.get("attributes") == {}


def test_save_state_attributes():
    obj = solid.cube(5)
    result = save_state("my-cube", dict(alpha=1, beta=2))(obj)

    meta = result.get_trait("solid_state")
    assert meta is not None
    assert meta.get("name") == "my-cube"
    assert meta.get("attributes") == dict(alpha=1, beta=2)


def test_state_decorator_attributes():
    @state("my-cube", dict(alpha=1, beta=2))
    def create_my_cube():
        return solid.cube(5)

    result = create_my_cube()

    meta = result.get_trait("solid_state")
    assert meta is not None
    assert meta.get("name") == "my-cube"
    assert meta.get("attributes") == dict(alpha=1, beta=2)


# TODO start building out more complete css syntax support...
# plan these features ahead, they don't need to be implemented all at once,
# but the list of reserved characters does.
#
# ".charlie .other .thing"
# "cube.thing, sphere.thing"


# TODO test
# - join
# - transform_like
# - render_states
# - a full on css style selector language?
#   ex. "#my_state#other_state.rotate.cube"
