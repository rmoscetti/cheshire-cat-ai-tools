"""
Deploys the plugin into the Cheshire Cat Container using the rest API
Compresses the plugin directory into a zip, uploads it and then if then enables the plugin if necessary 
"""

from pyprojroot import here
import shutil
import time
from dotenv import dotenv_values
import cheshire_cat_api as ccat

config = ccat.Config()
cat_client = ccat.CatClient(config)

env = dotenv_values('.env')
env = env | dotenv_values('.env.local')


def zip_plugin() -> str:
    """
    Zip the plugin directory.

    Returns:
        The zip file path
    """
    plugins_dir = here('plugins/cheshire-cat-ai-toolkit')
    zip_path = here('plugins/cheshire-cat-ai-toolkit.zip')
    # Remove the old zip file if it exists
    if zip_path.exists(): zip_path.unlink()

    # Create a zip file of the plugins directory
    shutil.make_archive(plugins_dir, 'zip', plugins_dir)

    return str(zip_path)

def is_plugin_installed():
    plugins = cat_client.plugins.get_available_plugins(query="cheshire_cat_ai_toolkit")['installed']
    return len(plugins) == 1 and plugins[0]['id'] == 'cheshire_cat_ai_toolkit'
    
def wait_for_plugin(timeout=60):
    while not is_plugin_installed():
        timeout -= 1
        if timeout == 0:
            raise TimeoutError("Timeout waiting for plugin to be installed")
        time.sleep(1)
        
def is_plugin_enabled():
    plugins = cat_client.plugins.get_available_plugins(query="cheshire_cat_ai_toolkit")['installed']
    return len(plugins) == 1 and plugins[0]['active']

def deploy_plugins():
    plugin_zip = zip_plugin()
    if is_plugin_installed():
        cat_client.plugins.delete_plugin('cheshire_cat_ai_toolkit')
    cat_client.plugins.install_plugin(plugin_zip)
    wait_for_plugin()
    if not is_plugin_enabled():
        cat_client.plugins.toggle_plugin('cheshire_cat_ai_toolkit')
    print("Plugin deployed successfully")

if __name__ == '__main__':
    deploy_plugins()

    