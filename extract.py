"""Minecraft Translation Extractor."""

import re

from base import LANGUAGE_LIST, OUTPUT_DIR
from init import language_data

# Prefixes for keys that should generally be included.
VALID_PREFIXES: tuple[str, ...] = (
    "block.",
    "item.minecraft.",
    "entity.minecraft.",
    "biome.",
    "effect.minecraft.",
    "enchantment.minecraft.",
    "trim_pattern.",
    "upgrade.",
    "filled_map",
)

# Matches keys that are intermediate categories and not actual names.
INVALID_HIERARCHICAL_KEY_PATTERN = re.compile(
    r"(block\.minecraft\.|item\.minecraft\.|entity\.minecraft\.)[^.]*\."
)
# Matches specific patterns for item effects that should be included.
ITEM_EFFECT_PATTERN = re.compile(r"item\.minecraft\.[^.]*\.effect\.[^.]*")
# Matches advancement titles, which are desired.
ADVANCEMENT_TITLE_PATTERN = re.compile(r"advancements\.(.*)\.title")

# A set of specific keys to be explicitly excluded from the output.
EXCLUDED_KEYS: set[str] = {
    "block.minecraft.set_spawn",
    "entity.minecraft.falling_block_type",
    "filled_map.id",
    "filled_map.level",
    "filled_map.locked",
    "filled_map.scale",
    "filled_map.unknown",
}


def is_valid_key(key: str) -> bool:
    """Determine if a localization key is valid for extraction based on a set of rules.

    Args:
        key (str): The localization key to validate.

    Returns:
        bool: True if the key is valid, False otherwise.

    """
    # Rule 1: Always include advancement titles.
    if ADVANCEMENT_TITLE_PATTERN.match(key):
        return True

    # Rule 2: Key must start with one of the valid prefixes.
    if not key.startswith(VALID_PREFIXES):
        return False

    # Rule 3: Exclude specific keys and pottery shard patterns.
    if key in EXCLUDED_KEYS or "pottery_shard" in key:
        return False

    # Rule 4: Always include item effect descriptions that match the pattern.
    if ITEM_EFFECT_PATTERN.match(key):
        return True

    # Rule 5: Exclude keys that are just containers for other keys (e.g., block.minecraft.banner.)
    if INVALID_HIERARCHICAL_KEY_PATTERN.match(key):
        return False

    return True


OUTPUT_DIR.mkdir(exist_ok=True)

# Filter translations based on valid keys.
output_translations: dict[str, list[str]] = {
    lang_code: [value for key, value in data.items() if is_valid_key(key)]
    for lang_code, data in language_data.items()
}

# Filter the keys themselves.
output_keys: list[str] = [key for key in language_data.get("en_us", {}).keys() if is_valid_key(key)]

# Write filtered translations to .txt files.
for lang_name in LANGUAGE_LIST:
    output_file = OUTPUT_DIR / f"{lang_name}.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(output_translations.get(lang_name, [])))
        f.write("\n")  # Add a final newline

# Write filtered keys to key.txt.
key_output_file = OUTPUT_DIR / "key.txt"
with open(key_output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(output_keys))
    f.write("\n")  # Add a final newline

print(f"Extraction complete. Files saved in '{OUTPUT_DIR.name}' directory.")
