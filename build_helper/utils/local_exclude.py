# SPDX-FileCopyrightText: Copyright (c) 2024-2025 沉默の金 <cmzj@cmzj.org>
# SPDX-License-Identifier: MIT
"""本地排除清单：在不修改上游配置文件的前提下，关闭指定的拓展包与 CONFIG 开关。

背景: 本仓库是上游的 fork。若直接删除上游的拓展包条目与配置开关,
每次合并上游都会在同一区域产生冲突。本模块把"要排除什么"收进一个
本地新增的清单文件(``config/<目标>/OpenWrt-K/local.config``),
由 prepare 阶段按清单过滤, 从而使上游文件保持原样。

容错: 清单文件缺失、键缺失或键留空, 都表示"不做任何排除",
此时行为与上游完全一致(本机制是纯增量的)。
"""

import fnmatch
import os
import re
from typing import Any

from .logger import logger

# 清单文件相对配置目录的位置(OpenWrt-K 子目录下的文件不参与顶层 *.config 拼接)
LOCAL_CONFIG_RELPATH = os.path.join("OpenWrt-K", "local.config")
# 清单支持的键名
KEY_EXTPACKAGES = "extpackages_exclude"
KEY_CONFIGS = "configs_exclude"


def load_local_exclude(config_dir: str) -> tuple[list[str], list[str]]:
    """读取本地排除清单, 返回 ``(要排除的拓展包名, 要排除的配置符号名)``。

    清单文件不存在时返回两个空列表; 无法识别的键会被忽略并给出告警。
    支持三种写法(可混用):

    - 单行多值: ``configs_exclude=A,B,C``
    - 同名键累加: 同名键出现多次时值依次累加, 便于"一行一项"并逐项写注释
    - 行尾注释: ``#`` 之前需有空白, 如 ``extpackages_exclude=tailscale  # 改用 EasyTier``
    """
    path = os.path.join(config_dir, LOCAL_CONFIG_RELPATH)
    if not os.path.isfile(path):
        return [], []
    excludes: dict[str, list[str]] = {}
    with open(path, encoding="utf-8") as f:
        for raw_line in f:
            # 先剔除行尾注释: 要求 # 之前有空白, 避免误伤取值中可能出现的 #
            line = re.split(r"\s+#", raw_line.strip(), maxsplit=1)[0].strip()
            # 跳过空行与整行注释
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            if key not in (KEY_EXTPACKAGES, KEY_CONFIGS):
                logger.warning("本地排除清单 %s 中存在未知配置项 %s, 已忽略", path, key)
                continue
            # 同名键多次出现时累加, 使清单可以一行一项
            excludes.setdefault(key, []).extend(item.strip() for item in value.split(",") if item.strip())
    return excludes.get(KEY_EXTPACKAGES, []), excludes.get(KEY_CONFIGS, [])


def filter_extpackages(extpackages: dict[str, dict[str, Any]], excludes: list[str]) -> dict[str, dict[str, Any]]:
    """按排除清单剔除拓展包(按 extpackages.config 中的 NAME 精确匹配)。"""
    if not excludes:
        return extpackages
    filtered: dict[str, dict[str, Any]] = {}
    for name, package in extpackages.items():
        if name in excludes:
            logger.info("本地排除清单: 跳过拓展包 %s", name)
            continue
        filtered[name] = package
    return filtered


def filter_config_text(config_text: str, excludes: list[str]) -> str:
    """按排除清单逐行剔除配置开关(支持 fnmatch 通配, 如 ``CONFIG_PACKAGE_luci-i18n-ddns-zh-*``)。"""
    if not excludes:
        return config_text
    kept: list[str] = []
    removed: list[str] = []
    for line in config_text.splitlines():
        symbol = extract_symbol(line)
        if symbol is not None and any(fnmatch.fnmatchcase(symbol, pattern) for pattern in excludes):
            removed.append(symbol)
            continue
        kept.append(line)
    if removed:
        preview = ", ".join(removed[:5]) + ("..." if len(removed) > 5 else "")
        logger.info("本地排除清单: 剔除 %d 行配置开关(%s)", len(removed), preview)
    return "\n".join(kept) + "\n" if kept else ""


def extract_symbol(line: str) -> str | None:
    """从一行 .config 文本中提取符号名, 不是配置行时返回 None。

    同时兼容 ``CONFIG_X=y`` 与 ``# CONFIG_X is not set`` 两种写法。
    """
    stripped = line.strip()
    if not stripped:
        return None
    if stripped.startswith("#"):
        parts = stripped.split()
        symbol = parts[1] if len(parts) >= 2 else ""
    else:
        symbol = stripped.split("=", 1)[0].strip()
    return symbol if symbol.startswith("CONFIG_") else None
