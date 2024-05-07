# -*- encoding: utf-8 -*-
"""Minecraft译名提取器"""

import re

from base import OUTPUT_DIR, lang_list
from init import language_data


def is_valid_key(translation_key: str):
    """判断是否为有效键名"""

    prefixes = (
        "block.",
        "item.minecraft.",
        "entity.minecraft.",
        "effect.minecraft.",
        "enchantment.minecraft.",
        "trim_pattern.",
        "upgrade.",
    )

    if (
        translation_key.startswith(prefixes)
        and not re.match(
            r"(block\.minecraft\.|item\.minecraft\.|entity\.minecraft\.)[^.]*\.",
            translation_key,
        )
        and translation_key
        not in ["block.minecraft.set_spawn", "entity.minecraft.falling_block_type"]
        and "pottery_shard" not in translation_key
    ):
        return True

    return False


# 输出文件夹
OUTPUT_DIR.mkdir(exist_ok=True)

output_data: dict[str, list[str]] = {
    name: [v for k, v in data.items() if is_valid_key(k)]
    for name, data in language_data.items()
}

output_key_data: list[str] = [
    k for k in language_data["en_us"].keys() if is_valid_key(k)
]

for lang_name in lang_list:
    with open(OUTPUT_DIR / f"{lang_name}.txt", "w", encoding="utf-8") as f:
        for line in output_data[lang_name]:
            f.writelines(line + "\n")

with open(OUTPUT_DIR / "key.txt", "w", encoding="utf-8") as f:
    for line in output_key_data:
        f.writelines(line + "\n")
