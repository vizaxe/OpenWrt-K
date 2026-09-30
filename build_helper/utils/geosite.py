# SPDX-FileCopyrightText: Copyright (c) 2024-2025 沉默の金 <cmzj@cmzj.org>
# SPDX-License-Identifier: MIT
"""GeoSite(geosite.dat) 解析与 mosdns 域名集生成。

背景: 固件里 xray 的分流数据(``/usr/share/xray/geosite.dat``)与 mosdns 的域名集
(``/etc/mosdns/domain_set/*.txt``)本是同一份内容, 若各自离线维护就会逐渐漂移。
本模块用纯标准库解析 protobuf(不依赖任何第三方库, 可直接单独运行), 在 prepare
阶段把 geosite.dat 解成 mosdns 可读的文本, 使二者永远同源。

匹配方式由 protobuf 的 type 字段决定, 映射到 mosdns 的文本前缀:
  Domain(2) -> 裸域名(后缀匹配) / Full(3) -> ``full:``(精确匹配)
  Regex(1) -> ``regexp:`` / Plain(0) -> ``keyword:``(子串匹配)
输出保持数据源顺序并按行去重, 同一份 geosite.dat 必得同一份文本, 便于比对差异。

容错: 清单文件缺失、键留空都表示"不生成任何文件", 此时不触碰既有域名集;
某个 tag 在数据里不存在时只告警并跳过该文件, 保留原快照。
"""

import argparse
import logging
import os
import re
import sys
from collections.abc import Iterator

logger = logging.getLogger("build_helper.geosite")

# 上游 geosite 数据源(与 prepare 阶段给 xray 下载的那份完全一致)
GEOSITE_URL = "https://github.com/Loyalsoldier/v2ray-rules-dat/releases/latest/download/geosite.dat"

# protobuf Domain.Type -> mosdns 文本前缀; 未列出的类型按 Plain(子串匹配)处理
_DOMAIN_PREFIXES = {0: "keyword:", 1: "regexp:", 2: "", 3: "full:"}

# 数据源若已自带前缀, 则不再重复添加
_KNOWN_PREFIXES = ("full:", "domain:", "regexp:", "keyword:")


def _varint(data: bytes, pos: int) -> tuple[int, int]:
    """读取一个 protobuf varint, 返回 (值, 新下标)。"""
    result = 0
    shift = 0
    while True:
        if pos >= len(data):
            msg = "varint 越界, 数据可能已损坏"
            raise ValueError(msg)
        byte = data[pos]
        pos += 1
        result |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return result, pos
        shift += 7


def _fields(data: bytes) -> Iterator[tuple[int, int | bytes]]:
    """遍历 protobuf 字段, 产出 (字段号, 值): varint 给 int, length-delimited 给 bytes。"""
    pos = 0
    end = len(data)
    while pos < end:
        key, pos = _varint(data, pos)
        field_no = key >> 3
        wire_type = key & 0x7
        if wire_type == 0:
            value, pos = _varint(data, pos)
            yield field_no, value
        elif wire_type == 2:
            size, pos = _varint(data, pos)
            yield field_no, data[pos:pos + size]
            pos += size
        elif wire_type == 5:
            pos += 4
        elif wire_type == 1:
            pos += 8
        else:
            msg = f"不支持的 protobuf wire type: {wire_type}"
            raise ValueError(msg)


def _parse_domain(raw: bytes) -> str:
    """解析单条 Domain 子消息, 返回 mosdns 文本形式的匹配串(无有效值时返回空串)。"""
    domain_type = 0
    value = ""
    for field_no, field in _fields(raw):
        if field_no == 1 and isinstance(field, int):
            domain_type = field
        elif field_no == 2 and isinstance(field, bytes):
            value = field.decode("utf-8", "replace")
    if not value:
        return ""
    if value.startswith(_KNOWN_PREFIXES):
        return value
    return f"{_DOMAIN_PREFIXES.get(domain_type, _DOMAIN_PREFIXES[0])}{value}"


def parse_geosite(data: bytes) -> dict[str, list[str]]:
    """解析 geosite.dat, 返回 {tag: [带前缀的匹配串, ...]}(保持原顺序并去重)。

    数据结构: GeoSiteList{entry=1: GeoSite{country_code=1, domain=2: Domain{type=1,value=2}}}
    """
    sources: dict[str, list[str]] = {}
    for field_no, entry in _fields(data):
        if field_no != 1 or not isinstance(entry, bytes):
            continue
        tag = ""
        domains: list[str] = []
        for sub_no, sub in _fields(entry):
            if sub_no == 1 and isinstance(sub, bytes):
                tag = sub.decode("utf-8", "replace")
            elif sub_no == 2 and isinstance(sub, bytes):
                pattern = _parse_domain(sub)
                if pattern:
                    domains.append(pattern)
        if tag:
            sources[tag] = list(dict.fromkeys(domains))
    return sources


def load_domainset_config(path: str) -> dict[str, str]:
    """读取域名集清单, 返回 {输出文件名: geosite tag}。

    格式: 一行一项 ``文件名=tag``; 空行与 ``#`` 起始的注释忽略, 行尾 `` #`` 注释同样忽略。
    文件缺失或没有任何有效项时返回空字典(调用方据此跳过生成)。
    """
    mapping: dict[str, str] = {}
    if not os.path.isfile(path):
        logger.warning("域名集清单不存在, 跳过生成: %s", path)
        return mapping
    with open(path, encoding="utf-8") as f:
        for raw_line in f:
            line = re.split(r"\s+#", raw_line.strip(), maxsplit=1)[0].strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, _, tag = line.partition("=")
            if name.strip() and tag.strip():
                mapping[name.strip()] = tag.strip()
    return mapping


def write_domainset(source: str | bytes, mapping: dict[str, str], out_dir: str) -> dict[str, int]:
    """按清单把 geosite 数据写成域名集文本, 返回 {文件名: 条数}。

    ``source`` 既可以是已读入的 bytes, 也可以是本地路径或 http(s) 地址(交给
    ``_load_source``) —— prepare 阶段直接传 ``geosite.dat`` 的路径即可, 库与 CLI
    两种用法由此统一。⚠️ 这里原先只接受 bytes, 而调用方传的是路径, 结果构建期
    在 `_varint` 里对字符串做位运算而崩溃(见 UC-0024)。

    tag 名称大小写不敏感。某个 tag 在数据里不存在(例如上游改了分类名)时只告警并
    跳过该文件, 不删除既有快照, 避免"生成失败反而把可用数据清空"。
    """
    if not isinstance(source, (str, bytes)):
        msg = f"source 类型不支持, 需要 str 路径/URL 或 bytes 数据: {type(source).__name__}"
        raise TypeError(msg)
    data = _load_source(source) if isinstance(source, str) else source
    sources = {name.upper(): items for name, items in parse_geosite(data).items()}
    stats: dict[str, int] = {}
    os.makedirs(out_dir, exist_ok=True)
    for filename, tag in mapping.items():
        items = sources.get(tag.upper())
        if items is None:
            logger.warning("geosite.dat 中不存在 tag %s, 跳过生成 %s", tag, filename)
            continue
        with open(os.path.join(out_dir, filename), "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(items))
            f.write("\n")
        stats[filename] = len(items)
    return stats


def _load_source(source: str) -> bytes:
    """读取 geosite.dat: 以 http(s):// 开头视为 URL, 否则视为本地文件路径。

    urllib 只在需要联网时才导入 —— 固件里的精简 Python 环境可能没有这个模块,
    而设备端更新域名集走的是本地文件模式, 不该因为缺一个网络模块就跑不起来。
    """
    if source.startswith(("http://", "https://")):
        import urllib.request  # noqa: PLC0415

        request = urllib.request.Request(source, headers={"User-Agent": "OpenWrt-K build_helper"})  # noqa: S310
        with urllib.request.urlopen(request, timeout=120) as resp:  # noqa: S310
            return resp.read()
    with open(source, "rb") as f:
        return f.read()


def _list_tags(data: bytes) -> None:
    """按条数降序把全部 tag 打印到标准输出。"""
    sources = parse_geosite(data)
    ranked = sorted(sources.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    for name, items in ranked:
        sys.stdout.write(f"{len(items):>8}  {name}\n")
    sys.stdout.write(f"共 {len(sources)} 个 tag, {sum(len(v) for v in sources.values())} 条匹配串\n")


def _print_tag(data: bytes, tags: list[str], limit: int) -> None:
    """把指定 tag 的匹配串打印到标准输出, limit 大于 0 时截断。"""
    sources = {name.upper(): items for name, items in parse_geosite(data).items()}
    for tag in tags:
        items = sources.get(tag.upper())
        if items is None:
            sys.stderr.write(f"不存在 tag: {tag}\n")
            continue
        shown = items[:limit] if limit > 0 else items
        sys.stdout.write(f"# {tag} ({len(items)} 条)\n")
        sys.stdout.write("\n".join(shown))
        sys.stdout.write("\n")


def _write_by_mapping(data: bytes, mapping: dict[str, str], out_dir: str) -> dict[str, int]:
    """写出清单中的域名集并把结果打印到标准输出。"""
    stats = write_domainset(data, mapping, out_dir)
    for name, count in stats.items():
        sys.stdout.write(f"{name}: {count} 条\n")
    return stats


def main(argv: list[str] | None = None) -> int:
    """命令行入口: 列 tag、导出 tag, 或按清单批量生成域名集。"""
    parser = argparse.ArgumentParser(description="解析 geosite.dat 并生成 mosdns 域名集")
    parser.add_argument("-s", "--source", default=GEOSITE_URL, help="geosite.dat 的本地路径或 URL")
    parser.add_argument("-l", "--list", action="store_true", help="列出全部 tag 与条数")
    parser.add_argument("-t", "--tag", action="append", default=[], help="导出指定 tag, 可重复")
    parser.add_argument("-n", "--limit", type=int, default=0, help="配合 --tag 时限制输出条数")
    parser.add_argument("-a", "--all", action="store_true", help="导出全部 tag(需配合 --out)")
    parser.add_argument("-c", "--config", help="域名集清单(文件名=tag), 配合 --out 批量生成")
    parser.add_argument("-o", "--out", help="输出目录")
    args = parser.parse_args(argv)

    if not (args.list or args.tag or args.all or args.config):
        parser.print_help()
        return 1

    data = _load_source(args.source)
    if args.list:
        _list_tags(data)
    if args.config:
        if not args.out:
            sys.stderr.write("--config 需要配合 --out\n")
            return 2
        _write_by_mapping(data, load_domainset_config(args.config), args.out)
    elif args.all:
        if not args.out:
            sys.stderr.write("--all 需要配合 --out\n")
            return 2
        mapping = {name.lower() + ".txt": name for name in parse_geosite(data)}
        _write_by_mapping(data, mapping, args.out)
    elif args.tag:
        if args.out:
            _write_by_mapping(data, {tag.lower() + ".txt": tag for tag in args.tag}, args.out)
        else:
            _print_tag(data, args.tag, args.limit)
    return 0


if __name__ == "__main__":
    sys.exit(main())
