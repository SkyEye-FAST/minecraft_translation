# -*- encoding: utf-8 -*-
"""基础文件"""

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

# 获取的版本
V = config["version"]
VERSION_FOLDER = os.path.join(P, config["version_folder"])

# 获取version_manifest_v2.json
version_manifest_path = os.path.join(VERSION_FOLDER, "version_manifest_v2.json")
try:
    print("正在获取版本清单“version_manifest_v2.json”……\n")
    version_manifest = r.get(
        "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json",
        timeout=60,
    )
    version_manifest.raise_for_status()
    version_manifest_json = version_manifest.json()
    with open(version_manifest_path, "wb") as f:
        f.write(version_manifest.content)
except r.exceptions.RequestException as e:
    if os.path.exists(version_manifest_path):
        print("无法获取版本清单，使用先前获取的版本清单。\n")
        with open(version_manifest_path, "r", encoding="utf-8") as f:
            version_manifest_json = json.load(f)
    else:
        print("无法获取版本清单，并且不存在先前获取的版本清单。")
        print("请检查网络连接或手动提供有效的版本清单文件。")
        sys.exit()

# 获取的版本
V = config["version"]
VERSION_FOLDER = os.path.join(P, config["version_folder"])

# 获取最新版
if V == "latest":
    V = version_manifest_json["latest"]["snapshot"]
LANG_FOLDER = os.path.join(VERSION_FOLDER, V)
print(f"选择的版本：{V}\n")
