# -*- encoding: utf-8 -*-
"""Minecraft语言文件获取器"""

import hashlib
import sys
from zipfile import ZipFile
import requests as r
from base import V, version_manifest_json, LANG_DIR, remove_client, lang_list


def get_json(url: str):
    """获取JSON"""
    try:
        resp = r.get(url, timeout=60)
        resp.raise_for_status()
        return resp.json()
    except r.exceptions.RequestException as ex:
        print(f"请求发生错误: {ex}")
        sys.exit()


# 存放版本语言文件的文件夹
LANG_DIR.mkdir(exist_ok=True)

# 获取client.json
client_manifest_url = next(
    (i["url"] for i in version_manifest_json["versions"] if i["id"] == V), None
)
if not client_manifest_url:
    print("无法在版本清单中找到此版本，请检查填写的版本号是否正确。")
    LANG_DIR.rmdir()
    sys.exit()

print(f"正在获取客户端索引文件“{client_manifest_url.rsplit('/', 1)[-1]}”……")
client_manifest = get_json(client_manifest_url)

# 获取资产索引文件
asset_index_url = client_manifest["assetIndex"]["url"]
print(f"正在获取资产索引文件“{asset_index_url.rsplit('/', 1)[-1]}”……\n")
asset_index = get_json(asset_index_url)["objects"]

# 获取客户端JAR
client_url = client_manifest["downloads"]["client"]["url"]
client_path = LANG_DIR / "client.jar"
print("正在下载客户端Java归档（client.jar）……")
try:
    response = r.get(client_url, timeout=120)
    response.raise_for_status()
    with open(client_path, "wb") as f:
        f.write(response.content)
except r.exceptions.RequestException as e:
    print(f"请求发生错误: {e}")
    client_path.unlink()
    sys.exit()

# 解压English (US)语言文件
with ZipFile(client_path) as client:
    with client.open("assets/minecraft/lang/en_us.json") as content:
        with open(LANG_DIR / "en_us.json", "wb") as f:
            print("正在从client.jar解压语言文件“en_us.json”……")
            f.write(content.read())

# 删除客户端JAR
if remove_client:
    print("正在删除client.jar……\n")
    client_path.unlink()

# 获取语言文件
MAX_RETRIES = 3  # 最大重试次数
lang_list.remove("en_us")
language_files_list = [f"{_}.json" for _ in lang_list]

for lang in language_files_list:
    lang_asset = asset_index.get(f"minecraft/lang/{lang}")
    if lang_asset:
        file_hash = lang_asset["hash"]
        print(f"正在下载语言文件“{lang}”（{file_hash}）……")
        asset_url = (
            f"https://resources.download.minecraft.net/{file_hash[:2]}/{file_hash}"
        )
        lang_file_path = LANG_DIR / lang

        for _ in range(MAX_RETRIES):
            try:
                response = r.get(asset_url, timeout=60)
                response.raise_for_status()
                with open(lang_file_path, "wb") as f:
                    f.write(response.content)
                with open(lang_file_path, "rb") as f:
                    if hashlib.file_digest(f, "sha1").hexdigest() == file_hash:
                        print("文件SHA1校验一致。\n")
                        break
                    print("文件SHA1校验不一致，重新尝试下载。\n")
            except r.exceptions.RequestException as e:
                print(f"请求发生错误: {e}")
        else:
            print(f"无法下载语言文件“{lang}”。\n")
    else:
        print(f"{lang}不存在。\n")

print("已完成。")
