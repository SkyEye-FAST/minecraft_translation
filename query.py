# -*- encoding: utf-8 -*-
"""Minecraft翻译查询器"""

from typing import List, Dict

from base import lang_list
from init import language_data

# 读取语言文件
language_names: Dict[str, str] = {
    "en_us": "源字符串，English (United States)",
    "zh_cn": "简体中文 (中国大陆)",
    "zh_hk": "繁體中文 (香港特別行政區)",
    "zh_tw": "繁體中文 (台灣)",
    "lzh": "文言 (華夏)",
    "ja_jp": "日本語 (日本)",
    "ko_kr": "한국어 (대한민국)",
    "vi_vn": "Tiếng Việt (Việt Nam)",
}


def print_translations(keys: List[str], languages: List[str]) -> None:
    """
    打印翻译结果。

    Args:
        keys (List[str]): 本地化键名列表。
        languages (List[str]): 语言列表。
    """
    for key in keys:
        print(f"\n本地化键名：{key}")
        for lang in languages:
            translation = language_data[lang].get(key, "不存在")
            print(f"{language_names[lang]}：{translation}")
        print()


def get_input_choice(prompt: str, choices: List[int]) -> int:
    """
    获取用户输入的有效选项。

    Args:
        prompt (str): 提示信息。
        choices (List[int]): 有效选项列表。

    返回:
        int: 用户选择的有效选项。
    """
    while True:
        try:
            choice = int(input(prompt))
            if choice in choices:
                return choice
        except ValueError:
            pass
        print("无效的输入，请重试。")


def query_by_key() -> None:
    """
    通过本地化键名查询翻译。
    """
    translation_key = input("\n键名：")
    if translation_key in language_data["en_us"]:
        print_translations([translation_key], lang_list)
    else:
        print("未找到对应的键名，请检查输入。")


def query_by_source_string(exact_match: bool = True) -> None:
    """
    通过源字符串查询翻译。

    Args:
        exact_match (bool): 是否进行精确匹配。默认值为 True。
    """
    source_str = input("\n源字符串，English (United States)：")
    if exact_match:
        query_keys = [k for k, v in language_data["en_us"].items() if v == source_str]
    else:
        query_keys = [
            k
            for k, v in language_data["en_us"].items()
            if source_str.lower() in v.lower()
        ]

    if query_keys:
        print_translations(query_keys, lang_list)
    else:
        print("未找到对应的源字符串，请检查输入。")


def query_by_translation() -> None:
    """
    通过翻译后字符串查询翻译。
    """
    print("\n请选择语言：")
    language_list = [lang for lang in lang_list if lang != "en_us"]
    for index, lang in enumerate(language_list):
        print(f"{index + 1}. {lang}：{language_names[lang]}")

    language_num = get_input_choice(
        "请输入编号：", list(range(1, len(language_list) + 1))
    )
    chosen_language = language_list[language_num - 1]

    translation = input("\n翻译后字符串的一部分：")
    query_keys = [
        k for k, v in language_data[chosen_language].items() if translation in v
    ]

    if query_keys:
        print_translations(query_keys, lang_list)
    else:
        print("未找到对应的翻译后字符串，请检查输入。")


def main() -> None:
    """
    主函数，提供查询选项并根据用户选择执行相应的查询操作。
    """
    print(
        "选择查询方式：\n1. 本地化键名\n2. 源字符串\n3. 源字符串（模糊匹配）\n4. 翻译后字符串（模糊匹配）"
    )
    method = get_input_choice("请输入编号：", [1, 2, 3, 4])

    if method == 1:
        query_by_key()
    elif method == 2:
        query_by_source_string(exact_match=True)
    elif method == 3:
        query_by_source_string(exact_match=False)
    elif method == 4:
        query_by_translation()


if __name__ == "__main__":
    main()
