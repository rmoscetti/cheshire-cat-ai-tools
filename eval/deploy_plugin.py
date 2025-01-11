# deploys the plugin into the cheshire cat container
from pyprojroot import here
from subprocess import run
import shutil
import sys

# def deploy_plugins():
#     # remove the old plugins
#     shutil.rmtree(here('docker-cat/plugins'), ignore_errors=True) # sometimes can't delete the folder because of permissions
#     # copy the new plugins
#     shutil.copytree(here('plugins'), here('docker-cat/plugins'), dirs_exist_ok=True)
    
#     compose = here('docker-cat/compose.yml')
#     out = run(f'docker compose -f {compose} up --build -d', shell=True, capture_output=True)
#     if out.returncode != 0:
#         print(out.stderr.decode())
#         sys.exit(1)



# if __name__ == '__main__':
#     deploy_plugins()

from dotenv import dotenv_values
from pathlib import Path
import cheshire_cat_api as ccat
config = ccat.Config()
cat_client = ccat.CatClient(config)
import time

env = dotenv_values('.env')
env = env | dotenv_values('.env.local')


def zip_plugin() -> bytes:
    """
    Zip the plugin directory.

    Returns:
        The zip file as bytes.
    """
    plugins_dir = here('plugins/cheshire-cat-ai-toolkit')
    zip_path = here('plugins/cheshire-cat-ai-toolkit.zip')
    # Remove the old zip file if it exists
    if zip_path.exists(): zip_path.unlink()

    # Create a zip file of the plugins directory
    shutil.make_archive(plugins_dir, 'zip', plugins_dir)

    # # Read the zip file into memory and return as byte array
    # with open(zip_path, 'rb') as f:
    #     zip_content = f.read()

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

    