import os
import re
import sys
from requests import get
from zipfile import ZipFile

# 获取的版本
V = "1.20.2"
print(f"选择的版本：{V}\n")

# 当前绝对路径
P = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + os.path.sep + ".")

# 版本文件夹
os.makedirs(VERSION_FOLDER := os.path.join(P, "versions", V), exist_ok=True)

# 定义获取JSON函数
get_json = lambda url: get(url).json()

# 获取version_manifest_v2.json
version_manifest_url = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
version_manifest = get_json(version_manifest_url)["versions"]
print("正在获取版本清单“version_manifest_v2.json”……")

# 获取client.json
client_manifest_url = next((i["url"] for i in version_manifest if i["id"] == V), None)
if client_manifest_url:
    print(f"正在获取客户端索引文件“{client_manifest_url.rsplit('/', 1)[-1]}”……")
    client_manifest = get_json(client_manifest_url)
else:
    print("无法在版本清单中找到此版本，请检查填写的版本号是否正确。")
    os.rmdir(VERSION_FOLDER)
    sys.exit()

# 获取资产索引文件
asset_index_url = client_manifest["assetIndex"]["url"]
print(f"正在获取资产索引文件“{asset_index_url.rsplit('/', 1)[-1]}”……\n")
asset_index = get_json(asset_index_url)["objects"]
# 获取客户端JAR
client_url = client_manifest["downloads"]["client"]["url"]
client_path = os.path.join(VERSION_FOLDER, "client.jar")
print("正在下载客户端Java归档（client.jar）……")
with open(client_path, "wb") as f:
    f.write(get(client_url).content)
# 解压English (US)语言文件
en_list = ["en_US.lang", "en_us.lang", "en_us.json"]
with ZipFile(client_path) as client:
    for e in en_list:
        if ("assets/minecraft/lang/" + e) in client.namelist():
            en = e
    with client.open("assets/minecraft/lang/" + en) as content:
        with open(os.path.join(VERSION_FOLDER, en), "wb") as f:
            print(f"正在从client.jar解压语言文件“{en}”……")
            f.write(content.read())
# 删除客户端JAR
print("正在删除client.jar……\n")
os.remove(client_path)

# 获取语言文件
lang_list = [
    "zh_CN.lang",
    "zh_TW.lang",
    "zh_cn.lang",
    "zh_tw.lang",
    "zh_cn.json",
    "zh_tw.json",
    "zh_hk.json",
    "lzh.json",
]
for e in lang_list:
    if ("minecraft/lang/" + e) in asset_index:
        hash = asset_index["minecraft/lang/" + e]["hash"]
        print(f"正在下载语言文件“{e}”（{hash}）……")
        asset_url = "https://resources.download.minecraft.net/" + hash[:2] + "/" + hash
        lang_file_path = os.path.join(VERSION_FOLDER, e)
        with open(lang_file_path, "wb") as f:
            f.write(get(asset_url).content)

print("\n已完成")
