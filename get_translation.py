import json
import os

# 获取的版本
V = "1.20.2"

# 当前绝对路径
P = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + os.path.sep + ".")

# 存放语言文件的文件夹
VERSION_FOLDER = os.path.join(P, "versions")

# 读取语言文件
with open(os.path.join(VERSION_FOLDER, "zh_cn.json"), "rb") as f:
    zh_cn = json.load(f)
with open(os.path.join(VERSION_FOLDER, "zh_hk.json"), "rb") as f:
    zh_hk = json.load(f)
with open(os.path.join(VERSION_FOLDER, "zh_tw.json"), "rb") as f:
    zh_tw = json.load(f)
with open(os.path.join(VERSION_FOLDER, "lzh.json"), "rb") as f:
    lzh = json.load(f)
