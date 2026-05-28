# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal # noqa: F401
from dash.development.base_component import Component, _explicitize_args

ComponentSingleType = typing.Union[str, int, float, Component, None]
ComponentType = typing.Union[
    ComponentSingleType,
    typing.Sequence[ComponentSingleType],
]

NumberType = typing.Union[
    typing.SupportsFloat, typing.SupportsInt, typing.SupportsComplex
]


class dash_mathlive(Component):
    """A dash_mathlive component.
ExampleComponent is an example component.
It takes a property, `label`, and
displays it.
It renders an input with the property `value`
which is editable by the user.

Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- value (string; optional):
    The value displayed in the input.

- debounce (number; default 0):
    Milliseconds to wait after the last keystroke before reporting the new
    value to Dash. 0 (default) reports on every input event."""
    _children_props: typing.List[str] = []
    _base_nodes = ['children']
    _namespace = 'dash_mathlive'
    _type = 'dash_mathlive'


    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        value: typing.Optional[str] = None,
        debounce: typing.Optional[NumberType] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'value', 'debounce']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'value', 'debounce']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(dash_mathlive, self).__init__(**args)

setattr(dash_mathlive, "__init__", _explicitize_args(dash_mathlive.__init__))
