import pytest
import solid

from solid_state.solid_state import (
    Path,
    Query,
    Term,
    compose,
    get_attributes,
    get_name,
    get_node_paths,
    get_object,
    get_objects,
    get_transformations,
    parse_path,
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


def test_get_name():
    obj1 = save_state("my-cube", dict(alpha=1, beta=2))(solid.cube(5))
    obj2 = save_state("my-sphere", dict(alpha=7, beta=9))(solid.sphere(5))

    assert get_name(obj1) == "my-cube"
    assert get_name(obj2) == "my-sphere"


def test_get_objects():
    obj1 = save_state("my-cube", dict(alpha=1, beta=2))(solid.cube(5))
    obj2 = save_state("my-sphere", dict(alpha=3, beta=4))(solid.sphere(5))
    obj3 = save_state("my-sphere", dict(alpha=7, beta=9))(solid.sphere(5))
    combined = obj1 + obj2 + obj3

    res1 = get_objects(combined, "my-cube")
    res2 = get_objects(combined, "my-sphere")

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

    res1 = get_objects(combined, "parent-1.my-cube")
    res2 = get_objects(combined, "parent-2.my-cube")

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

    res1 = get_object(combined, "my-cube")

    with pytest.raises(Exception):
        get_object(combined, "my-sphere")

    with pytest.raises(Exception):
        get_object(combined, "my-other-thing")

    assert get_name(res1) == "my-cube"


def test_get_attributes():
    obj1 = save_state("my-cube", dict(alpha=1, beta=2))(solid.cube(5))
    obj2 = save_state("my-sphere", dict(alpha=7, beta=9))(solid.sphere(5))
    combined = obj1 + obj2

    assert get_attributes(combined, "my-cube").get("alpha") == 1
    assert get_attributes(combined, "my-cube").get("beta") == 2
    assert get_attributes(combined, "my-sphere").get("alpha") == 7
    assert get_attributes(combined, "my-sphere").get("beta") == 9


def test_get_attributes_by_path():
    obj1 = save_state("my-cube", dict(alpha=1, beta=2))(solid.cube(5))
    parent1 = save_state("parent-1")(solid.translate([1, 2, 3])(obj1))

    obj2 = save_state("my-cube", dict(alpha=7, beta=9))(solid.cube(5))
    parent2 = save_state("parent-2")(solid.translate([4, 5, 6])(obj2))

    combined = parent1 + parent2

    assert get_attributes(combined, "parent-1.my-cube").get("alpha") == 1
    assert get_attributes(combined, "parent-1.my-cube").get("beta") == 2
    assert get_attributes(combined, "parent-2.my-cube").get("alpha") == 7
    assert get_attributes(combined, "parent-2.my-cube").get("beta") == 9


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

    for path in ["my-cube", "my-parent.my-cube"]:
        result = get_transformations(obj, path)

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

    parent_result = get_transformations(obj, "my-parent")

    assert len(parent_result) == 2

    assert parent_result[0].name == "mirror"
    assert parent_result[1].name == "rotate"

    assert parent_result[0].params["v"] == [1, 0, 0]
    assert parent_result[1].params["a"] == [90, 0, 0]

    sphere_result = get_transformations(obj, "my-sphere")

    assert len(sphere_result) == 3

    assert sphere_result[0].name == "color"
    assert sphere_result[1].name == "mirror"
    assert sphere_result[2].name == "rotate"

    assert sphere_result[0].params["c"] == "blue"
    assert sphere_result[1].params["v"] == [1, 0, 0]
    assert sphere_result[2].params["a"] == [90, 0, 0]


def test_parse_path():
    assert parse_path("foo") == Query([Path([Term(obj_name="foo")])])
    assert parse_path(".bar") == Query([Path([Term(state_name="bar")])])
    assert parse_path("foo.bar") == Query([
        Path([Term(obj_name="foo", state_name="bar")])
    ])
    assert parse_path("foo bar") == Query([
        Path([Term(obj_name="foo"), Term(obj_name="bar")])
    ])
    assert parse_path(".foo .bar") == Query([
        Path([Term(state_name="foo"), Term(state_name="bar")])
    ])
    assert parse_path(".foo .bar zig.baz zag") == Query([
        Path([
            Term(state_name="foo"),
            Term(state_name="bar"),
            Term(obj_name="zig", state_name="baz"),
            Term(obj_name="zag")
        ])
    ])
    assert parse_path("foo.bar, .baz zig") == Query([
        Path([Term(obj_name="foo", state_name="bar")]),
        Path([Term(state_name="baz"), Term(obj_name="zig")]),
    ])


# def test_get_node_paths():
#     class DummyNode:
#         def __init__(self, name, children):
#             self.name = name
#             self.children = children
#
#     tree = DummyNode("alpha", [
#         DummyNode("beta", [
#             DummyNode("delta", []),
#             DummyNode("epsilon", [
#                 DummyNode("fark", []),
#             ]),
#         ]),
#         DummyNode("charlie", []),
#     ])
#
#     assert get_node_paths(tree, "alpha") == [()]
#     assert get_node_paths(tree, "beta") == [(0,)]
#     assert get_node_paths(tree, "charlie") == [(1,)]
#     assert get_node_paths(tree, "delta") == [(0, 0)]
#     assert get_node_paths(tree, "epsilon") == [(0, 1)]
#     assert get_node_paths(tree, "fark") == [(0, 1, 0)]


def test_get_complex_node_paths():
    class DummyNode:
        def __init__(self, node_type="generic", children=None):
            if children is None:
                children = []

            self.name = node_type
            self.children = children
            self.traits = {}

        def get_trait(self, trait):
            return self.traits.get(trait)

    class DummyState(DummyNode):
        def __init__(self, name, children=None, node_type="generic"):
            super().__init__(node_type, children)
            self.traits["solid_state"] = dict(name=name, attributes={})

    tree = DummyState(
        "alpha",
        [
            DummyState(
                "beta",
                [
                    DummyState("other", [DummyState("thing", [])]),
                    DummyState("thing", [DummyState("other", [])]),
                ],
            ),
            DummyState(
                "charlie",
                [
                    DummyState("thing", [DummyState("other", [])]),
                    DummyState("other", [DummyState("thing", [])]),
                ],
            ),
        ],
    )

    assert get_node_paths(tree, "thing") == [
        (0, 0, 0),
        (0, 1),
        (1, 0),
        (1, 1, 0),
    ]
    assert get_node_paths(tree, "beta.other") == [(0, 0), (0, 1, 0)]
    assert get_node_paths(tree, "charlie.other") == [(1, 0, 0), (1, 1)]
    assert get_node_paths(tree, "charlie.thing.other") == [(1, 0, 0)]
    assert get_node_paths(tree, "charlie.other.thing") == [(1, 1, 0)]

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
