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
    const {id, setProps, value} = props;
    
    const mathfieldRef = useRef(null);  
    
    useEffect(() => {
      const mf = mathfieldRef.current;
      mf.addEventListener('input', () => {
        setProps({ value: mf.value });
      });
    }, []);

    return (
        <div id={id}>
            <math-field ref={mathfieldRef} />
        </div>
    );
}

dash_mathlive.defaultProps = {};

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
     * Dash-assigned callback that should be called to report property changes
     * to Dash, to make them available for callbacks.
     */
    setProps: PropTypes.func
};

export default dash_mathlive;
