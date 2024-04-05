# -*- encoding: utf-8 -*-
"""Minecraft语言文件获取器"""

import hashlib
import sys
from zipfile import ZipFile
import requests as r
from base import LANG_DIR, remove_client, lang_list, version_info


def get_response(url: str):
    """获取响应"""
    try:
        resp = r.get(url, timeout=60)
        resp.raise_for_status()
        return resp
    except r.exceptions.RequestException as ex:
        print(f"请求发生错误: {ex}")
        sys.exit()


def get_file(url: str, file_name: str, file_path: str, sha1: str):
    """下载文件"""
    for _ in range(3):
        with open(file_path, "wb") as f:
            f.write(get_response(url).content)
        size_in_bytes = file_path.stat().st_size
        if size_in_bytes > 1048576:
            size = f"{round(size_in_bytes / 1048576, 2)} MB"
        else:
            size = f"{round(size_in_bytes / 1024, 2)} KB"
        with open(file_path, "rb") as f:
            if hashlib.file_digest(f, "sha1").hexdigest() == sha1:
                print(f"文件SHA1校验一致。文件大小：{size_in_bytes} B（{size}）\n")
                break
            print("文件SHA1校验不一致，重新尝试下载。\n")
    else:
        print(f"无法下载文件“{file_name}”。\n")


# 存放版本语言文件的文件夹
LANG_DIR.mkdir(exist_ok=True)

# 获取client.json
client_manifest_url = version_info["url"]
print(f"正在获取客户端索引文件“{client_manifest_url.rsplit('/', 1)[-1]}”的内容……")
client_manifest = get_response(client_manifest_url).json()

# 获取资产索引文件
asset_index_url = client_manifest["assetIndex"]["url"]
print(f"正在获取资产索引文件“{asset_index_url.rsplit('/', 1)[-1]}”的内容……\n")
asset_index = get_response(asset_index_url).json()["objects"]

# 获取客户端JAR
client_url = client_manifest["downloads"]["client"]["url"]
client_sha1 = client_manifest["downloads"]["client"]["sha1"]
client_path = LANG_DIR / "client.jar"
print(f"正在下载客户端Java归档“client.jar”（{client_sha1}）……")
get_file(client_url, "client.jar", client_path, client_sha1)

# 解压English (United States)语言文件
with ZipFile(client_path) as client:
    with client.open("assets/minecraft/lang/en_us.json") as content:
        with open(LANG_DIR / "en_us.json", "wb") as en:
            print("正在从client.jar解压语言文件“en_us.json”……")
            en.write(content.read())

# 删除客户端JAR
if remove_client:
    print("正在删除client.jar……\n")
    client_path.unlink()

# 获取语言文件
lang_list.remove("en_us")
language_files_list = [f"{_}.json" for _ in lang_list]

for lang in language_files_list:
    lang_asset = asset_index.get(f"minecraft/lang/{lang}")
    if lang_asset:
        file_hash = lang_asset["hash"]
        print(f"正在下载语言文件“{lang}”（{file_hash}）……")
        get_file(
            f"https://resources.download.minecraft.net/{file_hash[:2]}/{file_hash}",
            lang,
            LANG_DIR / lang,
            file_hash,
        )
    else:
        print(f"{lang}不存在。\n")

print("已完成。")
