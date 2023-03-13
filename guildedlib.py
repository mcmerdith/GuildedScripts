import getopt
import sys
import os
from typing import Any, Callable

import yaml


def process_arguments(script_name: str, help_msg: str) -> tuple[bool, bool, list[tuple, str], list[str]]:
    """Process argv with getopt.

    Parameters:
        script_name : The name of the script
        help_msg    : The message to be displayed when -h is passed

    Returns:
        force, novalidate, [opt, args from getopt]
        None if -h is passed"""

    opt, args = getopt.getopt(sys.argv[1:], "fvh", [
                              "force", "validate", "help"])

    force = False
    novalidate = False

    for o, _ in opt:
        if o == "-h" or o == "--help":
            print(f"""{script_name} [-h | --help] [-f | --force] [-v | --validate]

    {help_msg}
    Valid Options:
        -h | --help       : Show this help menu
        -f | --force      : Overwrite backups if they exist
        -v | --validate   : Validate item names""")
            exit()

        if o == "-f" or o == "--force":
            force = True
            continue

        if o == "-v" or o == "--validate":
            novalidate = True
            continue

    return (force, novalidate, opt, args)


def require_plugin(plugin: str, paths: list[str]):
    """Require a plugin and subdirectories to be present

    If any directory is not present, prints an error and exits

    Parameters:
        plugin : The name of the required plugin
        paths  : A list of relative paths that must be present in the plugin directory"""

    plugin_dir = f"plugins/{plugin}"

    if not os.path.exists(plugin_dir) or not os.path.isdir(plugin_dir):
        print(f"{plugin}: Plugin not present (make sure the script is run in the top level server directory)")
        exit()

    for path in paths:
        if not os.path.exists(f"{plugin_dir}/{path}"):
            print(
                f"{plugin}: Missing folder or file required for processing: {plugin_dir}/{path}"
            )
            exit()


def get_data_dir(plugin: str, path: str | None) -> str:
    return f"plugins/{plugin}{'' if path is None else ('/'+path)}"


def get_data_files(plugin: str, path: str | None, files: list[str]) -> list[str]:
    return [get_data_dir(plugin, path) + "/" + file for file in files]


def list_configurations(plugin: str, path: str | None) -> list[str]:
    """Require a plugin and subdirectories to be present.
    Prints errors if there were any

    Parameters:
        plugin : The name of the required plugin
        path   : The relative path to list in the plugin directory

    Returns:
        The list of files"""

    files = list(
        filter(lambda file: not file.endswith(
            ".backup"
        ), os.listdir(get_data_dir(plugin, path)))
    )

    for arg in files:
        print(f"Found {arg}")

    if not prompt_bool("OK?"):
        print(f"Provide desired file names as arguments to the script")
        exit()

    return [
        f"{get_data_dir(plugin, path)}/{file}" for file in files
    ]


def _file_ok(file: str, force: bool) -> bool:
    """Check if a file exists and is OK to process. Will prompt user
    to overwrite backups if they exist (unless force is set)

    Parameters:
        file  : The file to check
        force : Overwrite backups if they exist"""

    if not os.path.exists(file):
        print(f"Skipping {file}: no file")
        return False

    if os.path.exists(f"{file}.backup") \
            and not force \
            and not prompt_bool(f"{file}: backup already exists, overwrite?"):
        print(f"Skipping {file}: already processed")
        return False

    return True


def validate_files(files: list[str], force: bool) -> list[str]:
    """Validate that a list of files exist and are okay to process. Will prompt user
    to overwrite backups if they exist (unless force is set)

    Parameters:
        file  : The files to check
        force : Overwrite backups if they exist"""

    return [file for file in files if _file_ok(file, force)]


def prompt_bool(prompt: str) -> bool:
    """Prompt the user for y/N input

    Format: {prompt} [y/N]

    Parameters:
        prompt : The prompt to print

    Returns: The users input"""

    while True:
        result = input(
            f"{prompt} [y/N] "
        ).lower()
        if result == "y":
            return True
        elif result == "n" or result == "":
            return False


# Yaml configuration type definition
ConfigurationType = dict[str, "ConfigurationType"]
ItemType = dict[str,]
ConfigurationProcessor = Callable[[ConfigurationType], None]
"""Consume and modify a configuration"""
ItemProcessor = Callable[[ItemType], bool]
"""Consume and modify an item, returning if the item was modified"""


def open_and_backup_yaml_configuration(path: str) -> ConfigurationType | None:
    """Open a configuration file and backup its contents

    Parameters:
        path : The relative path to the configuration file"""

    with open(path, 'r', encoding='utf-8') as file:
        with open(path + '.backup', 'w', encoding='utf-8') as backup:
            backup.write(file.read())

        file.seek(0)

        print(f"Parsing {path}")

        return yaml.safe_load(file)


def save_yaml_configuration(path: str, configuration: ConfigurationType):
    """Save a configuration file

    Parameters:
        path          : The relative path to the configuration file
        configuration : The configuration to save"""

    with open(path, 'w', encoding='utf-8') as file:
        yaml.dump(configuration, file, allow_unicode=True)


def each_file(paths: list[str], processor: ConfigurationProcessor):
    """Execute the processor on all configuration files

    Parameters:
        paths     : A list of relative configuration file paths
        processor : Called on each configuration file"""
    for path in paths:
        configuration = open_and_backup_yaml_configuration(path)

        if configuration is None:
            print(f"Skipping: empty")
            continue

        processor(configuration)

        save_yaml_configuration(path, configuration)


def each_item(configuration: ConfigurationType, processor: ItemProcessor):
    """Execute the processor on all items in the configuration

    Parameters:
        configuration : An item configuration file
        processor     : Called on each item"""
    i = 0
    for item_name in configuration:
        if processor(configuration[item_name]["base"]):
            i += 1

    print(f"Updated {i} items")
