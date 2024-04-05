# -*- encoding: utf-8 -*-
"""初始化语言文件"""

import json
import sys
from base import lang_list, LANG_DIR

# 检查是否有语言文件缺失
missing_files = []
for lang_code in lang_list:
    lang_file = LANG_DIR / f"{lang_code}.json"
    if not lang_file.exists():
        missing_files.append(f"{lang_code}.json")
if missing_files:
    print("以下语言文件不存在：")
    for file_name in missing_files:
        print(file_name)
    print("请补全语言文件或取消选择某些语言后重新尝试。")
    sys.exit()

# 读取语言文件
language_data = {}
for lang_name in lang_list:
    with open(LANG_DIR / f"{lang_name}.json", "r", encoding="utf-8") as f:
        language_data[lang_name] = json.load(f)
