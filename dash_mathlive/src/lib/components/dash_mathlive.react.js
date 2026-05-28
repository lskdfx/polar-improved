import 'mathlive'
import React, { useRef, useEffect } from 'react';
import PropTypes from 'prop-types';

/**
 * ExampleComponent is an example component.
 * It takes a property, `label`, and
 * displays it.
 * It renders an input with the property `value`
 * which is editable by the user.
 */
const dash_mathlive = (props) => {
    const {id, setProps, debounce, value} = props;

    const mathfieldRef = useRef(null);
    const timeoutRef = useRef(null);
    const debounceRef = useRef(debounce);
    debounceRef.current = debounce;

    useEffect(() => {
        const mf = mathfieldRef.current;
        if (value != null) {
            mf.value = value;
        }
        mf.addEventListener('input', () => {
            const d = debounceRef.current;
            if (timeoutRef.current) {
                clearTimeout(timeoutRef.current);
            }
            if (d && d > 0) {
                timeoutRef.current = setTimeout(() => {
                    setProps({ value: mf.value });
                }, d);
            } else {
                setProps({ value: mf.value });
            }
        });
    }, []);

    return (
        <div id={id}>
            <math-field ref={mathfieldRef} />
        </div>
    );
}

dash_mathlive.defaultProps = {
    debounce: 0,
};

dash_mathlive.propTypes = {
    /**
     * The ID used to identify this component in Dash callbacks.
     */
    id: PropTypes.string,

    /**
     * The value displayed in the input.
     */
    value: PropTypes.string,

    /**
     * Milliseconds to wait after the last keystroke before reporting the new
     * value to Dash. 0 (default) reports on every input event.
     */
    debounce: PropTypes.number,

    /**
     * Dash-assigned callback that should be called to report property changes
     * to Dash, to make them available for callbacks.
     */
    setProps: PropTypes.func
};

export default dash_mathlive;
