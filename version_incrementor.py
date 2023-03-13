#!/usr/bin python3

#   item_name:
#       base:
#           crafting:

import guildedlib
import oyaml as yaml
import os


def processor(item: guildedlib.ItemType) -> bool:
    if "revision-id" in item.keys():
        item["revision-id"] += 1
        return True

    return False


def main():
    force, _, _, filenames = guildedlib.process_arguments(
        "version_incrementor.py", "Increment all item version ids by 1"
    )

    guildedlib.require_plugin("MMOItems", ["item"])

    if filenames is None or len(filenames) == 0:
        filenames = guildedlib.list_configurations("MMOItems", "item")
    else:
        filenames = guildedlib.get_data_files("MMOItems", "item", filenames)

    filenames = guildedlib.validate_files(filenames, force)

    guildedlib.each_file(
        filenames,
        lambda item_file: guildedlib.each_item(item_file, processor)
    )


if __name__ == "__main__":
    main()
