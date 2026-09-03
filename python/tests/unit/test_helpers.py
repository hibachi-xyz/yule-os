from dataclasses import dataclass

import pytest

from hibachi_xyz.helpers import create_list_with, create_with


@dataclass
class Widget:
    id: int
    label: str | None


def test_create_with_filters_unknown_fields():
    widget = create_with(Widget, {"id": 1, "label": "a", "extra_field": "ignored"})

    assert widget == Widget(id=1, label="a")


def test_create_with_raises_on_missing_required_field():
    with pytest.raises(TypeError):
        create_with(Widget, {"label": "a"})


def test_create_with_implicit_null_fills_missing_nullable_field():
    widget = create_with(Widget, {"id": 1}, implicit_null=True)

    assert widget == Widget(id=1, label=None)


def test_create_with_implicit_null_does_not_override_present_value():
    widget = create_with(Widget, {"id": 1, "label": "present"}, implicit_null=True)

    assert widget.label == "present"


def test_create_list_with_builds_one_instance_per_item():
    widgets = create_list_with(
        Widget, [{"id": 1, "label": "a"}, {"id": 2, "label": "b"}]
    )

    assert widgets == [Widget(id=1, label="a"), Widget(id=2, label="b")]


def test_create_list_with_empty_list_returns_empty_list():
    assert create_list_with(Widget, []) == []


def test_create_list_with_forwards_implicit_null_to_each_item():
    widgets = create_list_with(Widget, [{"id": 1}, {"id": 2}], implicit_null=True)

    assert widgets == [Widget(id=1, label=None), Widget(id=2, label=None)]
