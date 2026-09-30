# SPDX-FileCopyrightText: Copyright (c) 2024-2025 沉默の金 <cmzj@cmzj.org>
# SPDX-License-Identifier: MIT
"""AdGuardHome 配置读取: 由 adguardhome.yaml 推出构建期需要预置的文件。

背景(过滤器缓存): prepare 阶段原先硬编码了一份第三方订阅清单(17 个黑名单 + 5 个白名单),
与固件实际使用的 ``files/etc/adguardhome/adguardhome.yaml`` 长期脱节 —— AdGuardHome 是按
filter 的 id 去寻找 ``data/filters/<id>.txt`` 的缓存, 而那份清单用的文件名是订阅时间戳,
于是下载下来的文件一个也不会被引用, 白占体积。现改为以配置为唯一真源, 只收集 enabled
为真的条目并按下发的 id 命名。

背景(上游DNS分流清单): 该清单原先无条件下载到写死的 ``/etc/`` 路径, 但主配置的
``upstream_dns_file`` 为空, AdGuardHome 根本不会读它。现改为只在配置确实引用时才下载,
且落点直接取自配置里的路径, 使"下载什么、放在哪里"始终与配置一致。

容错: 配置文件缺失、YAML 解析失败、缺少 filters 列表, 都只告警并返回空结果, 调用方据此
跳过下载; 单条过滤器缺少 url / 数字 id 时只跳过该条; ``upstream_dns_file`` 不是绝对路径或
含 ``..`` 时同样跳过, 避免配置里的异常路径把文件写到 files/ 之外。
"""

import os
import sys
from typing import Any

import yaml

from .logger import logger

# 上游 DNS 分流清单的取用地址(取自 chenmozhijin/AdGuardHome-Rules 项目)
UPSTREAM_DNS_LIST_URL = "https://raw.githubusercontent.com/chenmozhijin/AdGuardHome-Rules/main/AdGuardHome-dnslist(by%20cmzj).yaml"


def _load_yaml(yaml_path: str) -> dict[str, Any] | None:
    """读取并解析 AdGuardHome 主配置, 失败时只告警并返回 None。"""
    if not os.path.isfile(yaml_path):
        logger.warning("AdGuardHome 配置不存在, 跳过相关下载: %s", yaml_path)
        return None
    try:
        with open(yaml_path, encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except (OSError, yaml.YAMLError) as e:
        logger.warning("解析 AdGuardHome 配置失败(%s), 跳过相关下载: %s", e.__class__.__name__, yaml_path)
        return None
    if not isinstance(config, dict):
        logger.warning("AdGuardHome 配置的内容不是映射表, 跳过相关下载: %s", yaml_path)
        return None
    return config


def _is_enabled(entry: dict[str, Any]) -> bool:
    """判断一条过滤器是否启用(兼容 bool 与字符串两种写法)。"""
    enabled = entry.get("enabled")
    if isinstance(enabled, bool):
        return enabled
    return isinstance(enabled, str) and enabled.strip().lower() == "true"


def _cache_name(entry: dict[str, Any]) -> str | None:
    """由条目得到缓存文件名 ``<id>.txt``; id 缺失或不是纯数字时返回 None。

    AdGuardHome 的缓存文件名就是 filter 的 id, 名称对不上等于没预置; 这里强制
    纯数字, 既与它的约定一致, 也避免 id 里混入路径分隔符之类的意外字符。
    """
    raw = entry.get("id")
    if raw is None:
        return None
    text = str(raw).strip()
    return f"{text}.txt" if text.isdigit() else None


def load_filter_downloads(yaml_path: str) -> dict[str, str]:
    """读取 AdGuardHome 主配置, 返回 {缓存文件名: 下载地址}。

    只收集 filters 中启用、且 url 与 id 齐备的条目; 同一个 id 重复出现时以先出现者为准。
    文件缺失、解析失败或没有可用条目时返回空字典, 调用方据此跳过预置。
    """
    config = _load_yaml(yaml_path)
    if config is None:
        return {}

    entries = config.get("filters")
    if not isinstance(entries, list):
        logger.warning("AdGuardHome 配置里没有可用的 filters 列表: %s", yaml_path)
        return {}

    downloads: dict[str, str] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        name = entry.get("name") or "未命名"
        if not _is_enabled(entry):
            logger.debug("过滤器未启用, 跳过: %s", name)
            continue
        url = entry.get("url")
        if not isinstance(url, str) or not url.startswith(("http://", "https://")):
            logger.warning("过滤器缺少可用的 url, 跳过: %s", name)
            continue
        cache_name = _cache_name(entry)
        if cache_name is None:
            logger.warning("过滤器缺少数字 id(无法确定缓存文件名), 跳过: %s", name)
            continue
        if cache_name in downloads:
            logger.warning("过滤器 id 重复, 只保留先出现的条目: %s", name)
            continue
        downloads[cache_name] = url
    logger.info("从 AdGuardHome 配置读到 %d 个启用的过滤器", len(downloads))
    return downloads


def _asset_rel_path(raw: str) -> str | None:
    """把配置里的设备内绝对路径转成 files/ 之下的相对路径; 不合法时返回 None。

    只接受以 ``/`` 开头的绝对路径, 并拒绝含 ``..`` 的写法 —— 该值会参与拼装落盘位置,
    必须挡住"配置写什么就能落到哪里"的意外。
    """
    path = raw.strip()
    if not path.startswith("/") or ".." in path.split("/"):
        return None
    rel = os.path.normpath(path).lstrip("/")
    return rel or None


def load_upstream_dns_file(yaml_path: str) -> str | None:
    """读取配置里的 upstream_dns_file, 返回可落地的相对路径; 未配置或非法时返回 None。

    返回值是相对 files/ 根的路径(如 ``etc/AdGuardHome-dnslist(by cmzj).yaml``), 调用方
    拼上 global_files_path 即可, 从而保证"配置里写哪个路径, 固件里就落哪个路径"。
    该键的位置随 AdGuardHome 版本变化(新版在 ``dns`` 段下, 旧版在顶层), 两处都会查。
    """
    config = _load_yaml(yaml_path)
    if config is None:
        return None

    raw = config.get("upstream_dns_file")
    if not isinstance(raw, str) or not raw.strip():
        dns_section = config.get("dns")
        raw = dns_section.get("upstream_dns_file") if isinstance(dns_section, dict) else None
    if not isinstance(raw, str) or not raw.strip():
        logger.info("AdGuardHome 配置未引用上游DNS分流清单(upstream_dns_file 为空), 跳过下载")
        return None
    rel = _asset_rel_path(raw)
    if rel is None:
        logger.warning("upstream_dns_file 不是可用的绝对路径(%s), 跳过下载", raw)
        return None
    logger.info("AdGuardHome 配置引用了上游DNS分流清单, 将下载到: /%s", rel)
    return rel


def main(argv: list[str] | None = None) -> int:
    """命令行入口: 打印某份 adguardhome.yaml 将要预置的过滤器与上游DNS清单。"""
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        sys.stderr.write("用法: python3 build_helper/utils/adguardhome.py <adguardhome.yaml>\n")
        return 1
    downloads = load_filter_downloads(args[0])
    for cache_name, url in sorted(downloads.items()):
        sys.stdout.write(f"{cache_name}\t{url}\n")
    sys.stdout.write(f"共 {len(downloads)} 个启用的过滤器\n")
    dns_file = load_upstream_dns_file(args[0])
    sys.stdout.write(f"上游DNS分流清单: {dns_file or '未被配置引用, 不会下载'}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
