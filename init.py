"""Initializes language files."""

import json
import sys
from pathlib import Path

from base import LANG_DIR, LANGUAGE_LIST


def check_missing_files(lang_list: list[str], lang_dir: Path) -> list[str]:
    """Check for missing language files in the specified directory.

    Args:
        lang_list (list[str]): A list of language codes to check.
        lang_dir (Path): The directory containing language files.

    Returns:
        list[str]: A list of missing language file names.

    """
    return [
        f"{lang_code}.json"
        for lang_code in lang_list
        if not (lang_dir / f"{lang_code}.json").exists()
    ]


def load_language_files(lang_list: list[str], lang_dir: Path) -> dict[str, dict[str, str]]:
    """Load language files from the specified directory.

    Args:
        lang_list (list[str]): A list of language codes to load.
        lang_dir (Path): The directory containing language files.

    Returns:
        dict[str, dict[str, str]]: A dictionary containing the loaded language data.

    """
    lang_data = {}
    for lang_code in lang_list:
        lang_file = lang_dir / f"{lang_code}.json"
        try:
            with open(lang_file, encoding="utf-8") as f:
                lang_data[lang_code] = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error: Could not read language file {lang_file} - {e}")
            sys.exit(1)
    return lang_data


def main(lang_list: list[str], lang_dir: Path) -> dict[str, dict[str, str]]:
    """Check for and load language files.

    Args:
        lang_list (list[str]): The list of language codes.
        lang_dir (Path): The directory of language files.

    Returns:
        dict[str, dict[str, str]]: The loaded language data.

    """
    missing_files = check_missing_files(lang_list, lang_dir)
    if missing_files:
        print("The following language files are missing:")
        for file_name in missing_files:
            print(f"- {file_name}")
        print("Please modify the language list in the configuration and try again.")
        sys.exit(1)

    return load_language_files(lang_list, lang_dir)


# Load language data upon module import.
language_data: dict[str, dict[str, str]] = main(LANGUAGE_LIST, LANG_DIR)
