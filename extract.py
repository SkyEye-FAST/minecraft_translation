# -*- encoding: utf-8 -*-
"""Minecraft译名提取器"""

import re
import json
from base import LANG_DIR, OUTPUT_DIR


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


# 读取语言文件
language_list = [
    "en_us",
    "zh_cn",
    "zh_hk",
    "zh_tw",
    "lzh",
]
language_data = {}
for lang_name in language_list:
    with open(LANG_DIR / f"{lang_name}.json", "r", encoding="utf-8") as f:
        language_data[lang_name] = json.load(f)

# 输出文件夹
OUTPUT_DIR.mkdir(exist_ok=True)

output_data = {
    name: [v for k, v in data.items() if is_valid_key(k)]
    for name, data in language_data.items()
}

output_key_data = [k for k in language_data["en_us"].keys() if is_valid_key(k)]

for lang_name in language_list:
    with open(OUTPUT_DIR / f"{lang_name}.txt", "w", encoding="utf-8") as f:
        for line in output_data[lang_name]:
            f.writelines(line + "\n")

with open(OUTPUT_DIR / "key.txt", "w", encoding="utf-8") as f:
    for line in output_key_data:
        f.writelines(line + "\n")
