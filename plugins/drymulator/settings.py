from pydantic import BaseModel, AnyHttpUrl
from cat.mad_hatter.decorators import plugin


# settings
class DrymulatorSettings(BaseModel):
    server_url: AnyHttpUrl = (
        "http://localhost:7435"  # random unique port for the drymulator server
    )


# Give your settings model to the Cat.
@plugin
def settings_model():
    return DrymulatorSettings
