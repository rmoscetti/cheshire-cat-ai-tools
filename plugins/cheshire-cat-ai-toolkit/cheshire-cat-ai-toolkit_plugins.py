import numpy as np
import json
from cat.mad_hatter.decorators import tool

@tool (return_direct=False, examples=["linear equation", "give me the results of a linear equation", "provide the solution to the linear equation", "compute a linear equation"])
def linear_equation(tool_input, cat):
    """
    Essential to compute the result (y) of a linear equation (y = a*x + b).

    Input is always a JSON string structures follows:
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
            - y: List of float values for the dependent variable calculated using the linear equation
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

    return str(json.dumps(output))
