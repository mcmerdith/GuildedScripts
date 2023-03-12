import getopt
import sys
import os


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


def list_configurations(plugin: str, path: str) -> list[str]:
    """Require a plugin and subdirectories to be present

    Prints errors if there were any

    Parameters:
        plugin : The name of the required plugin
        path   : The relative path to list in the plugin directory

    Returns:
        The list of files"""

    return list(
        filter(lambda file: not file.endswith(
            ".backup"
        ), os.listdir(f"plugins/{plugin}/{path}"))
    )


def _file_ok(file: str, force: bool):
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
    return [file for file in files if _file_ok(file, force)]


def prompt_bool(prompt: str) -> bool:
    while True:
        result = input(
            f"{prompt} [y/N] "
        ).lower()
        if result == "y":
            return True
        elif result == "n" or result == "":
            return False
