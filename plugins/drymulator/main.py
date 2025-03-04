"""
Author: Roberto Moscetti, Simone Massaro
Version: 0.0.3
Date: 2025/03/04

Interface with the drying simulator (drymulator)
"""

from cat.mad_hatter.decorators import tool, hook
from drymulator_client.api.default import current_state_state_current_get
from drymulator_client.client import Client


###########
## HOOKS ##
###########


# 1. Episodic Memory Hook
@hook(priority=1)
def before_cat_recalls_episodic_memories(episodic_recall_config, cat) -> dict:
    """Hook to manage the number of the episodic memories."""
    # Returns an maximum number of episodic memories
    episodic_recall_config["k"] = 3  # default
    return episodic_recall_config


# 2. Prompt Prefix Customization
@hook(priority=1)
def agent_prompt_prefix(prefix, cat) -> str:
    """Hook to change the prompt prefix of the LLM model to prioritize the usage of tools."""
    # Prioritize the usage of tools through the moficiation of the prompt prefix
    additional_string = (
        "\nIf available, the 'Context of executed system tools' is your priority."
    )
    prefix += additional_string
    return prefix


@tool()
def current_weight(tool_input, cat):
    """
    Query the drying system to get the current weight of the product.
    """
    settings = cat.mad_hatter.get_plugin().load_settings()
    with Client(settings["server_url"]) as client:
        state = current_state_state_current_get.sync(client)
        return state["weight"]
