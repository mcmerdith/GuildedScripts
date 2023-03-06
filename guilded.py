#!/usr/bin python3

current_size = 2354785
max_size = 2097152

difference = current_size - max_size


class Item:
    def __init__(self, lore_lines: int, add_lore_lines: int, add_lore_line_size: int, name: str):
        self.lore_lines = lore_lines
        self.add_lore_lines = add_lore_lines
        self.add_lore_line_size = add_lore_line_size
        self.name = name

    def binary_size(self) -> int:
        # 496 is an arbitrary offset for packet stuff
        return 496 + \
            (self.lore_lines * 20 + self.add_lore_lines * self.add_lore_line_size  + len(self.name)) * 8


class Recipe:
    def __init__(self, item: Item, per_recipe: int):
        self.item = item
        self.per_recipe = per_recipe

    def binary_size(self, count: int) -> int:
        return self.item.binary_size() * self.per_recipe * count

def analyze_item(item: Item):
    item_size = item.binary_size()
    print(f"Size of each item : {item_size} bits")
    print(f"Required to remove: {difference / item_size} items")
    pass

def analyze_recipe(recipe: Recipe):
    item_size = recipe.binary_size(1)
    print(f"Size of each recipe : {item_size} bits")
    print(f"Required to remove  : {difference / item_size} items")
    pass

if __name__ == "__main__":
    item = Item(5, 8, 10, "§EMask of the Night")
    optimistic_recipe = Recipe(item, 4)
    analyze_item(item)
    analyze_recipe(optimistic_recipe)