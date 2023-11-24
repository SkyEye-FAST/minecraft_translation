# -*- encoding: utf-8 -*-
""" Minecraft翻译获取器 """

import json
import os
import sys
import tomllib as tl
import requests as r

# 当前绝对路径
P = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + os.path.sep + ".")

# 加载配置
config_path = os.path.join(P, "configuration.toml")
if not os.path.exists(config_path):
    print("\n无法找到配置文件，请将配置文件放置在与此脚本同级的目录下。")
    sys.exit()
with open(config_path, "rb") as f:
    config = tl.load(f)

VERSION_FOLDER = os.path.join(P, config["version_folder"])

# 获取的版本
V = config["version"]
# 获取最新版
if V == "latest":
    try:
        print("正在获取版本清单“version_manifest_v2.json”……\n")
        version_manifest = r.get(
            "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json",
            timeout=60,
        )
        with open(os.path.join(VERSION_FOLDER, "version_manifest_v2.json"), "wb") as f:
            f.write(version_manifest.content)
        V = version_manifest.json()["latest"]["snapshot"]
    except r.exceptions.RequestException:
        print("无法获取到版本清单，使用先前获取的版本清单。")
        with open(os.path.join(VERSION_FOLDER, "version_manifest_v2.json"), "rb") as f:
            version_manifest = json.load(f)
        V = version_manifest["latest"]["snapshot"]
print(f"选择的版本：{V}\n")

# 读取语言文件
language_dict = {
    "zh_cn": "简体中文（中国大陆）",
    "zh_hk": "繁體中文（香港特別行政區）",
    "zh_tw": "繁體中文（台灣）",
    "lzh": "文言（華夏）",
}
language_list = ["zh_cn", "zh_hk", "zh_tw", "lzh"]
language_files_list = [
    "en_us.json",
    "zh_cn.json",
    "zh_hk.json",
    "zh_tw.json",
    "lzh.json",
]
language_data = {}
for file in language_files_list:
    with open(os.path.join(P, config["version_folder"], V, file), "rb") as f:
        language_data[file.split(".", maxsplit=1)[0]] = json.load(f)

METHOD = 0
print("选择查询方式：\n1. 本地化键名\n2. 源字符串\n3. 源字符串（模糊匹配）\n4. 翻译后字符串（模糊匹配）")
while METHOD not in [1, 2, 3, 4]:
    METHOD = int(input("请输入编号："))

if METHOD == 1:
    translation_key = input("\n键名：")

    if translation_key in language_data["en_us"]:
        print(f"\n源字符串：{language_data['en_us'][translation_key]}")
        for lang in language_list:
            print(
                f"{language_dict[lang]}：{language_data[lang].get(translation_key, '不存在')}"
            )
        print()
    else:
        print("未找到对应的键名，请检查输入")
elif METHOD == 2:
    source_str = input("\n源字符串：")

    query_keys = [k for k, v in language_data["en_us"].items() if v == source_str]
    if query_keys:
        for key in query_keys:
            print(f"\n本地化键名：{key}")
            for lang in language_list:
                print(f"{language_dict[lang]}：{language_data[lang].get(key, '不存在')}")
            print()
    else:
        print("未找到对应的源字符串，请检查输入")
elif METHOD == 3:
    source_str = input("\n源字符串的一部分（不区分大小写）：")

    query_keys = [
        k for k, v in language_data["en_us"].items() if source_str.lower() in v.lower()
    ]
    if query_keys:
        for key in query_keys:
            print(f"\n本地化键名：{key}")
            print(f"源字符串：{language_data['en_us'][key]}")
            for lang in language_list:
                print(f"{language_dict[lang]}：{language_data[lang].get(key, '不存在')}")
            print()
    else:
        print("未找到对应的源字符串，请检查输入")
elif METHOD == 4:
    print("\n请选择语言：")
    for index, seq in enumerate(language_list):
        print(f"{index + 1}. {seq}：{language_dict[seq]}")
    LANGUAGE_NUM = 0
    while LANGUAGE_NUM not in [1, 2, 3, 4]:
        LANGUAGE_NUM = int(input("请输入编号："))
    chosen_language = language_list[LANGUAGE_NUM - 1]
    translation = input("\n翻译后字符串的一部分：")

    query_keys = [
        k for k, v in language_data[chosen_language].items() if translation in v
    ]
    if query_keys:
        for key in query_keys:
            print(f"\n本地化键名：{key}")
            print(f"源字符串：{language_data['en_us'][key]}")
            for lang in language_list:
                print(f"{language_dict[lang]}：{language_data[lang].get(key, '不存在')}")
            print()
    else:
        print("未找到对应的翻译后字符串，请检查输入")
