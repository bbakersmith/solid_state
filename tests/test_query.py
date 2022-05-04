from solid_state.query import *


def test_parse():
    assert parse("foo") == Query([Path([Term(obj_name="foo")])])
    assert parse(".bar") == Query([Path([Term(state_name="bar")])])
    assert parse("foo.bar") == Query([Path([Term(obj_name="foo", state_name="bar")])])
    assert parse("foo bar") == Query(
        [Path([Term(obj_name="foo"), Term(obj_name="bar")])]
    )
    assert parse(".foo .bar") == Query(
        [Path([Term(state_name="foo"), Term(state_name="bar")])]
    )
    assert parse(".foo .bar zig.baz zag") == Query(
        [
            Path(
                [
                    Term(state_name="foo"),
                    Term(state_name="bar"),
                    Term(obj_name="zig", state_name="baz"),
                    Term(obj_name="zag"),
                ]
            )
        ]
    )
    assert parse("foo.bar, .baz zig") == Query(
        [
            Path([Term(obj_name="foo", state_name="bar")]),
            Path([Term(state_name="baz"), Term(obj_name="zig")]),
        ]
    )
