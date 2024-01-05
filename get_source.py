# -*- encoding: utf-8 -*-
"""Minecraft语言文件获取器"""

import hashlib
import sys
from zipfile import ZipFile
import requests as r
from base import config, V, version_manifest_json, LANG_DIR


def get_json(url: str):
    """获取JSON"""
    try:
        resp = r.get(url, timeout=60)
        resp.raise_for_status()
        return resp.json()
    except r.exceptions.RequestException as ex:
        print(f"请求发生错误: {ex}")
        sys.exit()


remove_client = config["remove_client"]
lang_list = config["language_list"]

# 存放版本语言文件的文件夹
LANG_DIR.mkdir(exist_ok=True)

# 获取client.json
client_manifest_url = next(
    (i["url"] for i in version_manifest_json["versions"] if i["id"] == V), None
)
if not client_manifest_url:
    print("无法在版本清单中找到此版本，请检查填写的版本号是否正确")
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
    en = next(
        (
            e
            for e in ["en_US.lang", "en_us.lang", "en_us.json"]
            if "assets/minecraft/lang/" + e in client.namelist()
        ),
        None,
    )
    if en:
        with client.open("assets/minecraft/lang/" + en) as content:
            with open(LANG_DIR / en, "wb") as f:
                print(f"正在从client.jar解压语言文件“{en}”……")
                f.write(content.read())
    else:
        print("无法找到English (US)的语言文件，跳过")

# 删除客户端JAR
if remove_client:
    print("正在删除client.jar……\n")
    client_path.unlink()

# 获取语言文件
for e in lang_list:
    if "minecraft/lang/" + e in asset_index:
        file_hash = asset_index["minecraft/lang/" + e]["hash"]
        print(f"正在下载语言文件“{e}”（{file_hash}）……")
        asset_url = (
            "https://resources.download.minecraft.net/"
            + file_hash[:2]
            + "/"
            + file_hash
        )
        lang_file_path = LANG_DIR / e
        try:
            response = r.get(asset_url, timeout=60)
            response.raise_for_status()
            with open(lang_file_path, "wb") as f:
                f.write(response.content)
            with open(lang_file_path, "rb") as f:
                if hashlib.file_digest(f, "sha1").hexdigest() == file_hash:
                    print("文件SHA1校验一致。\n")
        except r.exceptions.RequestException as e:
            print(f"请求发生错误: {e}")

print("\n已完成。")
