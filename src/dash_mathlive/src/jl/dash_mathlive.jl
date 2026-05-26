# AUTO GENERATED FILE - DO NOT EDIT

export dash_mathlive

"""
    dash_mathlive(;kwargs...)

A dash_mathlive component.
ExampleComponent is an example component.
It takes a property, `label`, and
displays it.
It renders an input with the property `value`
which is editable by the user.
Keyword arguments:
- `id` (String; optional): The ID used to identify this component in Dash callbacks.
- `value` (String; optional): The value displayed in the input.
"""
function dash_mathlive(; kwargs...)
        available_props = Symbol[:id, :value]
        wild_props = Symbol[]
        return Component("dash_mathlive", "dash_mathlive", "dash_mathlive", available_props, wild_props; kwargs...)
end

