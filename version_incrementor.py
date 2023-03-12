#!/usr/bin python3

#   item_name:
#       base:
#           crafting:

import guildedlib
import oyaml as yaml
import os


def main():
    force, _, opt, filenames = guildedlib.process_arguments(
        "version_incrementor.py", "Increment all item version ids by 1"
    )

    guildedlib.require_plugin("MMOItems", ["item"])

    if filenames is None or len(filenames) == 0:
        filenames = guildedlib.list_configurations("MMOItems", "item")

        for arg in filenames:
            print(f"Found {arg.split('/')[-1]}")

        if not guildedlib.prompt_bool("OK?"):
            print(f"Exit: provide desired file names as arguments to the script")
            exit()

    filenames = guildedlib.validate_files([
        f"plugins/MMOItems/item/{filename}" for filename in filenames
    ], force)

    for path in filenames:
        item_file: dict[str, dict]

        with open(path, 'r', encoding='utf-8') as file:
            with open(path + '.backup', 'w', encoding='utf-8') as backup:
                backup.write(file.read())

            file.seek(0)

            item_file = yaml.safe_load(file)

            if (item_file is None):
                print(f"Skipping {path}: empty")
                continue

            print(f"Parsing {path}")

            i = 0
            for item_name in item_file:
                if "revision-id" in item_file[item_name]["base"].keys():
                    item_file[item_name]["base"]["revision-id"] += 1
                    i += 1

            print(f"Updated {i} items")

        with open(path, 'w', encoding='utf-8') as file:
            yaml.dump(item_file, file, allow_unicode=True)


if __name__ == "__main__":
    main()
