import os
import re
import sys
from requests import get
from zipfile import ZipFile

# 获取的版本
V = "1.17"
print(f"选择的版本：{V}\n")

# 当前绝对路径
P = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + os.path.sep + ".")

# 版本文件夹
os.makedirs(VERSION_FOLDER := os.path.join(P, "versions", V), exist_ok=True)


# 分割快照版本号
def split_snapshot(snapshot: str):
    year = snapshot[:2]
    week = snapshot[2:4]
    identifier = snapshot[4:]
    return year, week, identifier


# 比较快照版本号，s1 >= s2则为True
def compare_snapshot(s1: str, s2: str):
    # 拆分快照版本号
    s1_parts = split_snapshot(s1)
    s2_parts = split_snapshot(s2)

    # 比较年份
    if int(s1_parts[0]) < int(s2_parts[0]):
        return False
    elif int(s1_parts[0]) > int(s2_parts[0]):
        return True
    # 比较周数
    if int(s1_parts[1]) < int(s2_parts[1]):
        return False
    elif int(s1_parts[1]) > int(s2_parts[1]):
        return True
    # 比较标识符
    if s1_parts[2] < s2_parts[2]:
        return False
    elif s1_parts[2] > s2_parts[2]:
        return True

    return True


# 比较正式版版本号，v1 >= v2则为True
def compare_release(v1: str, v2: str):
    # 拆分版本号
    v1_parts = v1.split(".")
    v2_parts = v2.split(".")
    # 补全缺失部分
    while len(v1_parts) < 3:
        v1_parts.append("0")
    while len(v2_parts) < 3:
        v2_parts.append("0")

    # 比较
    for i in range(len(v1_parts)):
        if int(v1_parts[i]) > int(v2_parts[i]):
            return True
        elif int(v1_parts[i]) < int(v2_parts[i]):
            return False

    return True


en = "en_us.json"
if re.match(r"^\d{2}w\d{2}[a-z]$", V.lower()):
    if compare_snapshot(V, "13w26a") and compare_snapshot("16w21b", V):
        en = "en_US.lang"
        lang_list = ["zh_CN.lang", "zh_TW.lang"]
    elif compare_snapshot(V, "16w32a") and compare_snapshot("18w01a", V):
        en = "en_us.lang"
        lang_list = ["zh_cn.lang", "zh_tw.lang"]
    elif compare_snapshot(V, "18w02a") and compare_snapshot("21w15a", V):
        lang_list = ["zh_cn.json", "zh_tw.json"]
    elif compare_snapshot(V, "21w16a") and compare_snapshot("21w20a", V):
        lang_list = ["zh_cn.json", "zh_tw.json", "zh_hk.json"]
    elif compare_snapshot(V, "21w37a"):
        lang_list = ["zh_cn.json", "zh_tw.json", "zh_hk.json", "lzh.json"]
elif re.match(r"^\d+(\.\d+)*$", V):
    if compare_release(V, "1.6.1") and compare_release("1.10.2", V):
        en = "en_US.lang"
        lang_list = ["zh_CN.lang", "zh_TW.lang"]
    elif compare_release(V, "1.11") and compare_release("1.12.2", V):
        en = "en_us.lang"
        lang_list = ["zh_cn.lang", "zh_tw.lang"]
    elif compare_release(V, "1.13") and compare_release("1.16.5", V):
        lang_list = ["zh_cn.json", "zh_tw.json"]
    elif V == "1.17" or V == "1.17.1":
        lang_list = ["zh_cn.json", "zh_tw.json", "zh_hk.json"]
    elif compare_release(V, "1.18"):
        lang_list = ["zh_cn.json", "zh_tw.json", "zh_hk.json", "lzh.json"]

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
print(f"正在从client.jar解压语言文件“{en}”……")
with ZipFile(client_path) as client:
    with client.open(r"assets/minecraft/lang/" + en) as content:
        with open(os.path.join(VERSION_FOLDER, en), "wb") as f:
            f.write(content.read())
# 删除客户端JAR
print("正在删除client.jar……\n")
os.remove(client_path)

# 获取语言文件
for e in lang_list:
    hash = asset_index["minecraft/lang/" + e]["hash"]
    print(f"正在下载语言文件“{e}”（{hash}）……")
    asset_url = "https://resources.download.minecraft.net/" + hash[:2] + "/" + hash
    lang_file_path = os.path.join(VERSION_FOLDER, e)
    with open(lang_file_path, "wb") as f:
        f.write(get(asset_url).content)

print("\n已完成")
