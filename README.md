# Minecraft翻译获取器

此脚本用于从官方服务器获取Java版Minecraft的语言文件。

获取到的语言文件默认存储在与脚本同级的`versions`文件夹下的对应版本文件夹中。

## 需求

由于使用了标准库`tomllib`，所以需要**Python >= 3.11**

需要库`requests`，请使用下面的命令安装：

``` shell
pip install requests
```

## 配置文件

配置文件名为`configuration.toml`，位置与脚本同级。

## 反馈

遇到的问题和功能建议等可以提出议题（Issue）。

欢迎创建拉取请求（Pull request）。
