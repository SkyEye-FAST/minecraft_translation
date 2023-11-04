import os
import sys
import tomllib
from requests import get
from zipfile import ZipFile

# 当前绝对路径
P = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + os.path.sep + ".")

# 加载配置
with open(os.path.join(P, "configuration.toml"), "rb") as f:
    config = tomllib.load(f)

remove_client = config["remove_client"]
lang_list = config["language_list"]

# 获取的版本
V = config["version"]

# 定义获取JSON函数
get_json = lambda url: get(url).json()

# 获取version_manifest_v2.json
version_manifest = get_json(
    "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
)
print("正在获取版本清单“version_manifest_v2.json”……\n")
# 获取最新版
if V == "latest":
    V = version_manifest["latest"]["snapshot"]
    # 版本文件夹
    os.makedirs(
        VERSION_FOLDER := os.path.join(P, config["version_folder"], V), exist_ok=True
    )
    print(f"选择的版本：{V}\n")

# 获取client.json
if client_manifest_url := next(
    (i["url"] for i in version_manifest["versions"] if i["id"] == V), None
):
    print(f"正在获取客户端索引文件“{client_manifest_url.rsplit('/', 1)[-1]}”……")
    client_manifest = get_json(client_manifest_url)
else:
    print("无法在版本清单中找到此版本，请检查填写的版本号是否正确")
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
with ZipFile(client_path) as client:
    if en := next(
        (
            e
            for e in ["en_US.lang", "en_us.lang", "en_us.json"]
            if ("assets/minecraft/lang/" + e) in client.namelist()
        ),
        None,
    ):
        with client.open("assets/minecraft/lang/" + en) as content:
            with open(os.path.join(VERSION_FOLDER, en), "wb") as f:
                print(f"正在从client.jar解压语言文件“{en}”……")
                f.write(content.read())
    else:
        print("无法找到English (US)的语言文件，跳过")

# 删除客户端JAR
if remove_client:
    print("正在删除client.jar……\n")
    os.remove(client_path)

# 获取语言文件
for e in lang_list:
    if ("minecraft/lang/" + e) in asset_index:
        hash = asset_index["minecraft/lang/" + e]["hash"]
        print(f"正在下载语言文件“{e}”（{hash}）……")
        asset_url = "https://resources.download.minecraft.net/" + hash[:2] + "/" + hash
        lang_file_path = os.path.join(VERSION_FOLDER, e)
        with open(lang_file_path, "wb") as f:
            f.write(get(asset_url).content)

print("\n已完成")
