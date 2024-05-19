# -*- encoding: utf-8 -*-
"""Minecraft译名提取器"""

import re

from typing import Dict, List, Tuple, Set

from base import OUTPUT_DIR, lang_list
from init import language_data


# 定义常量
PREFIXES: Tuple[str, ...] = (
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

# 定义正则模式
INVALID_BLOCK_ITEM_ENTITY_PATTERN = re.compile(
    r"(block\.minecraft\.|item\.minecraft\.|entity\.minecraft\.)[^.]*\."
)
ITEM_EFFECT_PATTERN = re.compile(r"item\.minecraft\.[^.]*\.effect\.[^.]*")
ADVANCEMENTS_TITLE_PATTERN = re.compile(r"advancements\.(.*)\.title")

# 定义排除项
EXCLUSIONS: Set[str] = {
    "block.minecraft.set_spawn",
    "entity.minecraft.falling_block_type",
    "filled_map.id",
    "filled_map.level",
    "filled_map.locked",
    "filled_map.scale",
    "filled_map.unknown",
}


def is_valid_key(translation_key: str) -> bool:
    """
    判断是否为有效键名。

    Args:
        translation_key (str): 需要验证的键名。

    Returns:
        bool: 如果键名有效，返回 True；否则返回 False。
    """

    if ADVANCEMENTS_TITLE_PATTERN.match(translation_key):
        return True

    if not translation_key.startswith(PREFIXES):
        return False

    if translation_key in EXCLUSIONS or "pottery_shard" in translation_key:
        return False

    if ITEM_EFFECT_PATTERN.match(translation_key):
        return True

    if INVALID_BLOCK_ITEM_ENTITY_PATTERN.match(translation_key):
        return False

    return True


# 输出文件夹
OUTPUT_DIR.mkdir(exist_ok=True)

output_data: Dict[str, List[str]] = {
    name: [v for k, v in data.items() if is_valid_key(k)]
    for name, data in language_data.items()
}

output_key_data: List[str] = [
    k for k in language_data["en_us"].keys() if is_valid_key(k)
]

for lang_name in lang_list:
    with open(OUTPUT_DIR / f"{lang_name}.txt", "w", encoding="utf-8") as f:
        for line in output_data[lang_name]:
            f.writelines(line + "\n")

with open(OUTPUT_DIR / "key.txt", "w", encoding="utf-8") as f:
    for line in output_key_data:
        f.writelines(line + "\n")
