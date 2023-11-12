# Minecraft翻译获取器

[![Pylint](https://github.com/SkyEye-FAST/minecraft_translation/actions/workflows/pylint.yml/badge.svg)](https://github.com/SkyEye-FAST/minecraft_translation/actions/workflows/pylint.yml)

此项目用于查询Java版Minecraft的翻译。

## 需求

由于使用了标准库`tomllib`，所以需要**Python >= 3.11**

需要库`requests`，请使用下面的命令安装：

``` shell
pip install requests
```

## 脚本使用

### 获取源文件

`get_source.py`用于从官方服务器获取Java版Minecraft的语言文件。

获取到的语言文件默认存储在与脚本同级的`versions`文件夹下的对应版本文件夹中。

### 查询翻译

`get_translation.py`用于从语言文件中查询翻译，有以下三种方式：

1. 本地化键名
2. 源字符串
3. 源字符串（模糊匹配）
4. 翻译后字符串（模糊匹配）

## 配置文件

配置文件名为`configuration.toml`，位置与脚本同级。

## 反馈

遇到的问题和功能建议等可以提出议题（Issue）。

欢迎创建拉取请求（Pull request）。
