# -*- encoding: utf-8 -*-
"""初始化语言文件"""

import json
import sys
from pathlib import Path
from typing import Dict, List

from base import lang_list as base_lang_list, LANG_DIR


def check_missing_files(lang_list: List[str], lang_dir: Path) -> List[str]:
    """
    检查是否有语言文件缺失。

    Args:
        lang_list (List[str]): 语言代码列表。
        lang_dir (Path): 语言文件目录。

    Returns:
        List[str]: 缺失的语言文件列表。
    """
    missing_files = [
        f"{lang_code}.json"
        for lang_code in lang_list
        if not (lang_dir / f"{lang_code}.json").exists()
    ]
    return missing_files


def load_language_files(
    lang_list: List[str], lang_dir: Path
) -> Dict[str, Dict[str, str]]:
    """
    读取语言文件并返回语言数据。

    Args:
        lang_list (List[str]): 语言代码列表。
        lang_dir (Path): 语言文件目录。

    Returns:
        Dict[str, Dict[str, str]]: 语言数据字典。
    """
    lang_data = {}
    for lang_code in lang_list:
        lang_file = lang_dir / f"{lang_code}.json"
        try:
            with open(lang_file, "r", encoding="utf-8") as f:
                lang_data[lang_code] = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"错误: 无法读取语言文件 {lang_file} - {e}")
            sys.exit()
    return lang_data


def main(lang_list: List[str], lang_dir: Path) -> Dict[str, Dict[str, str]]:
    """
    主函数，执行语言文件检查和加载操作。

    Args:
        lang_list (List[str]): 语言代码列表。
        lang_dir (Path): 语言文件目录。

    Returns:
        Dict[str, Dict[str, str]]: 语言数据字典。
    """
    missing_files = check_missing_files(lang_list, lang_dir)
    if missing_files:
        print("以下语言文件不存在：")
        for file_name in missing_files:
            print(file_name)
        print("请补全语言文件或取消选择某些语言后重新尝试。")
        sys.exit()

    return load_language_files(lang_list, lang_dir)


language_data: Dict[str, Dict[str, str]] = main(base_lang_list, LANG_DIR)
