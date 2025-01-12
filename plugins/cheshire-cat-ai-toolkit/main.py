"""
Author: Roberto Moscetti, Simone Massaro
Version: 0.0.3
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
   
4. Drying Time Prediction:
   - Provides a tool for estimating the remaining time until the drying process is complete.
   - Accepts an empty input and returns the remanining time.
"""

import numpy as np
import json
from cat.mad_hatter.decorators import tool, hook


###########
## HOOKS ##
###########

# 1. Episodic Memory Hook
@hook(priority=1)
def before_cat_recalls_episodic_memories(episodic_recall_config, cat) -> dict:
    """Hook to manage the number of the episodic memories."""
    # Returns an maximum number of episodic memories
    episodic_recall_config["k"] = 3 # default
    return episodic_recall_config

# 2. Prompt Prefix Customization
@hook(priority=1)
def agent_prompt_prefix(prefix, cat) -> str:
    """Hook to change the prompt prefix of the LLM model to prioritize the usage of tools."""
    # Prioritize the usage of tools through the moficiation of the prompt prefix
    additional_string = "\nIf available, the 'Context of executed system tools' is your priority."
    prefix += additional_string
    return prefix

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

###########
## TOOLS ##
###########

# 3. Linear Equation Tool (experimental tool - just for test)
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
            - y: List of float values for the dependent variable calculated using the linear equation.
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

# 4. Drying time prediction (experimental tool - just for test)
@tool
def time_to_finish(tool_input, cat) -> str:
    """
    Returns the time to the finish of the drying process.
    
    Provide an emtpy input
    The time left in minutes (integer).
    """

    # for testing all dryers will be done at midnight, so compute the minutes left until midnight
    import datetime

    now = datetime.datetime.now(datetime.timezone.utc)
    next_midnight = (now + datetime.timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    time_left = (next_midnight - now).total_seconds() // 60
    return str(time_left) # important must be a string other the cat crashes