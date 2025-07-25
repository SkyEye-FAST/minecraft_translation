"""Minecraft Translation Querier."""

from base import LANGUAGE_LIST as LANG_LIST
from init import language_data

# Map language codes to human-readable names.
LANGUAGE_NAMES: dict[str, str] = {
    "en_us": "源字符串，English (United States)",
    "zh_cn": "简体中文 (中国大陆)",
    "zh_hk": "繁體中文 (香港特別行政區)",
    "zh_tw": "繁體中文 (台灣)",
    "lzh": "文言 (華夏)",
    "ja_jp": "日本語 (日本)",
    "ko_kr": "한국어 (대한민국)",
    "vi_vn": "Tiếng Việt (Việt Nam)",
}


def print_translations(keys: list[str], languages: list[str]) -> None:
    """Print translations for a given list of keys across specified languages.

    Args:
        keys (list[str]): A list of localization keys.
        languages (list[str]): A list of language codes to display.

    """
    for key in keys:
        print(f"\nLocalization Key: {key}")
        for lang in languages:
            lang_name = LANGUAGE_NAMES.get(lang, lang)
            translation = language_data[lang].get(key, "N/A")
            print(f"{lang_name}: {translation}")
        print()


def get_user_choice(prompt: str, choices: list[int]) -> int:
    """Prompts the user for input and validates it against a list of choices.

    Args:
        prompt (str): The message to display to the user.
        choices (list[int]): A list of valid integer choices.

    Returns:
        int: The user's valid choice.

    """
    while True:
        try:
            choice = int(input(prompt))
            if choice in choices:
                return choice
        except ValueError:
            pass
        print("Invalid input. Please try again.")


def query_by_key() -> None:
    """Query translations by a specific localization key."""
    translation_key = input("\nEnter localization key: ")
    if translation_key in language_data.get("en_us", {}):
        print_translations([translation_key], LANG_LIST)
    else:
        print("Localization key not found. Please check your input.")


def query_by_source_string(exact_match: bool = True) -> None:
    """Query for keys by matching the source English string.

    Args:
        exact_match (bool): If True, performs an exact match.
                            If False, performs a case-insensitive substring match.

    """
    source_str = input("\nEnter source string (English): ")
    en_us_data = language_data.get("en_us", {})

    if exact_match:
        found_keys = [k for k, v in en_us_data.items() if v == source_str]
    else:
        found_keys = [k for k, v in en_us_data.items() if source_str.lower() in v.lower()]

    if found_keys:
        print_translations(found_keys, LANG_LIST)
    else:
        print("No matching source string found. Please check your input.")


def query_by_translation() -> None:
    """Query for keys by matching a substring in a translated string."""
    print("\nPlease select a language:")
    # Exclude en_us since we are searching by translation
    searchable_langs = [lang for lang in LANG_LIST if lang != "en_us"]
    for i, lang_code in enumerate(searchable_langs, 1):
        lang_name = LANGUAGE_NAMES.get(lang_code, lang_code)
        print(f"{i}. {lang_name}")

    choice_num = get_user_choice("Enter number: ", list(range(1, len(searchable_langs) + 1)))
    chosen_lang = searchable_langs[choice_num - 1]

    search_term = input(f"\nEnter part of the translated string in {LANGUAGE_NAMES[chosen_lang]}: ")
    lang_data = language_data.get(chosen_lang, {})
    found_keys = [k for k, v in lang_data.items() if search_term in v]

    if found_keys:
        print_translations(found_keys, LANG_LIST)
    else:
        print("No matching translation found. Please check your input.")


def main() -> None:
    """Drive the query interface."""
    print(
        "Select query method:\n"
        "1. By Localization Key\n"
        "2. By Source String (Exact Match)\n"
        "3. By Source String (Fuzzy Match)\n"
        "4. By Translated String (Fuzzy Match)"
    )
    method = get_user_choice("Enter number: ", [1, 2, 3, 4])

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
