import numpy as np
import json
from cat.mad_hatter.decorators import tool

@tool #(return_direct=True)
def zero_order_equation(tool_input, cat):
    """
    Provide only the structure of the tool_input as follow. No additional comments.

    Args:
        tool_input: A JSON string with the following structure:
            {
                "x": [x1, x2, x3, ...], 
                "a": <float>, 
                "b": <float>
            }
            where:
                - x: A list of float values representing the independent variable.
                - a: The slope of the linear equation (float).
                - b: The intercept of the linear equation (float).

    Returns:
        A JSON string containing the following keys:
            - x: List of float values for the independent variable.
            - slope: Value of the slope (float).
            - intercept: Value of the intercept (float).
            - y: List of float values for the dependent variable calculated using the zero-order kinetics equation (y = a*x + b).
    """

    data = json.loads(tool_input) 
    x = np.array(data["x"])
    a = data["a"]
    b = data["b"]

    # Zero order equation
    y = a * x + b

    # Prepare the output as JSON
    output = {
        "x": x.tolist(),
        "slope": a,
        "intercept": b,
        "y": y.tolist()
    }

    return str("Use the following JSON data in your response: " + json.dumps(output))
