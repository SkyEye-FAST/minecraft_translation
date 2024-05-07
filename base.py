# -*- encoding: utf-8 -*-
"""基础文件"""

import json
import sys
import tomllib as tl
from datetime import datetime
from pathlib import Path
import requests as r

# 当前绝对路径
P = Path(__file__).resolve().parent

# 加载配置
CONFIG_DIR = P / "configuration.toml"
if not CONFIG_DIR.exists():
    print("\n无法找到配置文件，请将配置文件放置在与此脚本同级的目录下。")
    sys.exit()
with open(CONFIG_DIR, "rb") as f:
    config = tl.load(f)

# 读取配置
V = config["version"]
VERSION_DIR = P / config["version_folder"]
OUTPUT_DIR = P / config["output_folder"]
remove_client: bool = config["remove_client"]
lang_list: list[str] = config["language_list"]

# 版本文件夹
VERSION_DIR.mkdir(exist_ok=True)

# 获取version_manifest_v2.json
version_manifest_path = VERSION_DIR / "version_manifest_v2.json"
try:
    print("正在获取版本清单“version_manifest_v2.json”的内容……\n")
    version_manifest = r.get(
        "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json",
        timeout=60,
    )
    version_manifest.raise_for_status()
    version_manifest_json = version_manifest.json()
    with open(version_manifest_path, "wb") as f:
        f.write(version_manifest.content)
except r.exceptions.RequestException as e:
    if version_manifest_path.exists():
        print("无法获取版本清单，使用先前获取的版本清单。\n")
        with open(version_manifest_path, "r", encoding="utf-8") as f:
            version_manifest_json = json.load(f)
    else:
        print("无法获取版本清单，并且不存在先前获取的版本清单。")
        print("请检查网络连接或手动提供有效的版本清单文件。")
        sys.exit()

# 检查版本是否存在
if V == "latest":
    V = version_manifest_json["latest"]["snapshot"]
version_info: dict = next(
    (_ for _ in version_manifest_json["versions"] if _["id"] == V), {}
)
if not version_info:
    print("无法在版本清单中找到此版本，请检查填写的版本号是否正确。")
    sys.exit()
LANG_DIR = VERSION_DIR / V
print(f"选择的版本：{V}\n")

# 判断所选版本是否在18w02a及以后
time_18w02a = datetime.fromisoformat("2018-01-10T11:54:55+00:00")
time_chosen_ver = datetime.fromisoformat(version_info["releaseTime"])
if time_18w02a > time_chosen_ver:
    print("选择的版本使用.lang格式存储语言文件，请选择一个18w02a及以后的版本。")
    sys.exit()
