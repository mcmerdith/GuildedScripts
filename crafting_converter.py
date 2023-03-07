#!/usr/bin python3

#   item_name:
#       base:
#           crafting:

import sys
import getopt
import oyaml as yaml
import os

def main():
    force = False
    novalidate = False

    opt, args = getopt.getopt(sys.argv[1:], "fnh", ["force", "novalidate", "help"])
    args = args[1:]

    for o, a in opt:
        if o == "-h" or o == "--help":
            print("""crafting_convert.py [-h | --help] [-f | --force] [-n | --novalidate]

    Convert MMOItems crafting recipes to crafting station recipes
    Valid Options:
        -h | --help       : Show this help menu
        -f | --force      : Overwrite backups if they exist
        -n | --novalidate : Don't validate item names
            """)
            return
        if o == "-f" or o == "--force":
            force = True
            continue

        if o == "-n" or o == "--novalidate":
            novalidate = True
            continue

    print(force, novalidate)
    return

    if args is None or len(args) == 0:
        arg: str = input("Enter a filename (or RETURN for all): ")
        
        if arg is None or len(arg) == 0:
            args = list(filter(lambda file: not file.endswith(".backup"), os.listdir(os.getcwd())))
        else:
            args = []
            while arg is not None and len(arg) != 0:
                args.append(arg)
                arg = input("Enter a filename (or RETURN to finish): ")
    
    for path in args:
        if not os.path.exists(path) or not os.path.isfile(path):
            print(f"Skipping {path}: no file")
        else:
            item_file: dict[str, dict]

            with open(path, 'r', encoding='utf-8') as file:
                if (os.path.exists(path + '.backup')):
                    result: str

                    while True:
                        result = input("backup already exists, overwrite? [y/N] ").lower()
                        if result == "y" or result == "n" or result == "":
                            break

                    if result != "y":
                        print(f"Skipping {path}: already exists")
                        continue

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
                    if "crafting" in item_file[item_name]["base"].keys():
                        item_file[item_name]["base"].pop("crafting")
                        i += 1
                
                print(f"Updated {path}: {i} items")

            with open(path, 'w', encoding='utf-8') as file:
                yaml.dump(item_file, file, allow_unicode=True)


if __name__ == "__main__":
    main()