"""
Author: Roberto Moscetti
Version: 0.0.1
Date: 2025/01/12

This plugin provides hooks and tools for managing interactions with an LLM model, focusing on episodic memory handling,
prompt customization, and the computations. 

Key Features:
1. Episodic Memory Hook:
   - Limits the number of episodic memories to enhance memory recall efficiency.
   - Configurable via the 'before_cat_recalls_episodic_memories' hook.

2. Prompt Prefix Customization:
   - Adjusts the LLM model's prompt to prioritize tool usage through the 'agent_prompt_prefix' hook.

3. Linear Equation Tool:
   - Implements a tool for solving linear equations of the form 'y = a*x + b'.
   - Accepts input as a JSON structure and returns output in a structured JSON format.
   - Designed to integrate seamlessly with the LLM's output system by adding necessary prefixes.
"""

import numpy as np
import json
from cat.mad_hatter.decorators import tool, hook

def output_prefix(text) -> str:
    """
    This function adds multiple prefixes to the tool output.
    It manipulates the behavior of the LLM model in managing the output.
    """
    prefixes = [
        "Do not perform your own computation. ",
        "Do not use mathematical formulas. "
    ]
    return ''.join(prefixes) + text

@hook(priority=1)
def before_cat_recalls_episodic_memories(episodic_recall_config, cat) -> dict:
    """Hook to manage the number of the episodic memories."""
    # Returns an maximum number of episodic memories
    episodic_recall_config["k"] = 3 # default
    return episodic_recall_config

@hook(priority=1)
def agent_prompt_prefix(prefix, cat) -> str:
    """Hook to change the prompt prefix of the LLM model to prioritize the usage of tools."""
    # Prioritize the usage of tools through the moficiation of the prompt prefix
    additional_string = "\nIf available, the 'Context of executed system tools' is your priority."
    prefix += additional_string
    return prefix

@tool (return_direct=False,
       examples=[
           "linear equation", 
           "linear function", 
           "y = a*x +b",
           "give me the results of a linear equation",
           "provide the solution to the linear equation",
           "compute a linear equation",
           "resolve a linear equation"
        ]
    )
def linear_equation(tool_input, cat):
    """
    Essential to compute the result (y) of a linear equation (y = a*x + b).
    Do not provide any partial results.

    Input is always a JSON string structures follows:
        {
            "x": [x1, x2, x3, ...], 
            "a": <float>, 
            "b": <float>
        }
        where:
            - "x": A list of float values representing the independent variable.
            - "a": The slope of the linear equation (float).
            - "b": The intercept of the linear equation (float).

    Returns:
        A JSON string containing the following keys:
            - x: List of float values for the independent variable.
            - slope (a): Value of the slope (float).
            - intercept (b): Value of the intercept (float).
            - y: List of float values for the dependent variable calculated using the linear equation
    """

    data = json.loads(tool_input) 
    x = np.array(data["x"])
    a = data["a"]
    b = data["b"]

    # Linear equation
    y = a * x + b

    # Output as JSON
    output = {
        "x": x.tolist(),
        "y": y.tolist()
    }

    result = output_prefix("Show the following equation: y = " + str(a) + "*x + " + str(b) + ", and organize the following raw data as a table: " + json.dumps(output))
    return result



