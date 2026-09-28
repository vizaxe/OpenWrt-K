# AGENTS.md — OpenWrt-K 仓库工作指南

> 本文件面向在本仓库工作的 AI AGENT，也面向后来接手的人。
> 与上级 `~/.dsh/AGENTS.md` 冲突时以本文件为准（更近层级优先）。
>
> 本仓库是 [chenmozhijin/OpenWrt-K](https://github.com/chenmozhijin/OpenWrt-K) 的 fork，
> 已在插件集合上做过定制。本文件与 [UPSTREAM-CHANGES.md](UPSTREAM-CHANGES.md) 是**一对活文档**：
> 任何插件的增 / 改 / 删，以及任何会改变插件集合的脚本改动，都必须在同一批次内同步更新这两份文件（见第 8 节）。

---

## 0. 仓库定位

本仓库是 **OpenWrt 固件与软件包的自动云编译配置仓库**，**不存放插件源码**，只声明五件事：

1. 编译哪些第三方插件、从哪个仓库的哪个路径、哪个分支拉取；
2. 拉下来后怎么修补（修 Makefile 引用路径、补中文语言包、跳过 hash 校验）；
3. 哪些预置文件写进固件根文件系统；
4. 打哪些内核 / 软件包补丁、替换哪些上游包版本；
5. 最终启用哪些 `CONFIG_` 开关、编译哪些目标。

一句话：**改本仓库 = 改配方，不是改食材**。插件本身的 bug 要回到插件上游仓库去修。

本 fork 的定制遵循一条总原则：**能"新增"就不"修改"，能"开关"就不"删除"**——
目的只有一个：合并上游时冲突面尽可能小。落地手段见第 3.3 节的「本地排除清单」。

---

## 1. 目录职责

| 路径 | 职责 | 改动风险 |
| --- | --- | --- |
| `config/OpenWrt.config` | 声明启用哪些编译目标（`config=` 逗号分隔） | 高 |
| `config/default-extpackages.config` | 默认拓展包清单（模板 / 参考，不参与运行时解析） | 中 |
| `config/<目标>/` | 单个编译目标的完整配置目录 | 高 |
| `config/<目标>/*.config` | 顶层配置片段，会被拼接成 OpenWrt `.config` | 高 |
| `config/<目标>/OpenWrt-K/compile.config` | OpenWrt 版本、kmod 排除表、是否用缓存 | 高 |
| `config/<目标>/OpenWrt-K/extpackages.config` | **拓展插件清单**（仓库 + 路径 + 分支） | 高 |
| `config/<目标>/OpenWrt-K/local.config` | **本地排除清单**（本地新增；关闭上游条目而不改动上游文件） | 低 |
| `config/<目标>/OpenWrt-K/openwrtext.config` | 默认 IP、时区、golang 版本 | 中 |
| `build_helper/prepare.py` | 拉源码、替换上游同名包、修 Makefile、应用配置、打补丁 | 高 |
| `build_helper/utils/local_exclude.py` | 解析 `local.config`，在 prepare 阶段过滤拓展包与配置开关（本地新增） | 中 |
| `build_helper/build.py` | 四阶段构建流程（工具链 / 软件包 / ImageBuilder / 镜像） | 高 |
| `build_helper/utils/openwrt.py` | 封装 make / feeds / defconfig，以及 `fix_problems()` 修补 | 高 |
| `files/` | 原样覆盖进固件根文件系统（`/etc`、`/usr/share`、`/usr/bin` 等） | 中 |
| `patches/` | 补丁文件存放处；**必须被代码调用才生效** | 中 |
| `.github/workflows/build-openwrt.yml` | CI 流水线（prepare → base-builds → packages / IB → images） | 高 |
| `.github/action/{prepare,upload}/` | CI 复合动作（环境搭建、产物上传） | 中 |
| `config_build_tool.sh` | 本地交互式配置 / 构建工具 | 中 |
| `img/` | README 用图片 | 低 |

---

## 2. 配置是怎么被读取的

读取逻辑集中在 `build_helper/prepare.py::parse_configs()` 与 `build_helper/utils/paths.py`。

1. `config/OpenWrt.config` 的 `config=` 决定启用哪些目标（如 `config=x86_64`，多个用英文逗号分隔）。
2. 每个目标对应 `config/<目标>/`，该目录下**必须有** `OpenWrt-K/` 子目录，否则直接报错。
3. 目标**顶层**的所有 `*.config` 按 `os.listdir` 顺序拼接成 OpenWrt 的 `.config`；
   `OpenWrt-K/` 子目录下的文件**不参与**拼接，各自单独解析。
4. `OpenWrt-K/compile.config` 单独解析三个键：
   - `openwrt_tag/branch`：OpenWrt 源码的 tag 或分支（键名里带斜杠）
   - `kmod_compile_exclude_list`：不参与编译的 kmod，逗号分隔
   - `use_cache`：为真时追加 `CONFIG_DEVEL=y` 与 `CONFIG_CCACHE=y`
5. `OpenWrt-K/openwrtext.config` 单独解析四个键：`ipaddr`、`timezone`、`zonename`、`golang_version`。
6. `OpenWrt-K/extpackages.config` 单独解析 `EXT_PACKAGES_*` 四元组（见第 5 节）。
7. `OpenWrt-K/local.config`（可选，本地新增）最后被读取，用于剔除不需要的拓展包与配置开关（见第 3.3 节）。
8. 拼接结果经 `apply_config()` → `make defconfig` 归一化，再由 `get_diff_config()` 取回。

### 必须记住的三个坑

- **拼接顺序不确定**：`os.listdir` 顺序不保证稳定，**同一个 `CONFIG_` 开关只能在一个文件里定义一次**，严禁两个文件对同一开关给出不同值。
- **文件名即分组，但没有强制校验**：`luci.config`、`kmod.config`、`network.config`、`other.config`、`utilities.config`、`target.config`、`image.config` 只是人为分组，写错文件不会报错，但会让后人找不到。
- **新增目标需四件事齐备**：建 `config/<新目标>/`、建 `OpenWrt-K/` 三件套、准备若干 `*.config`、把目标名追加进 `config/OpenWrt.config` 的 `config=`。

---

## 3. 插件体系：四层结构

| 层次 | 载体 | 特点 |
| --- | --- | --- |
| ① 声明层 | `config/<目标>/OpenWrt-K/extpackages.config` | 描述式：仓库 + 路径 + 分支，复制到 `package/cmzj_packages/<NAME>` |
| ② 脚本层 | `build_helper/prepare.py`、`build_helper/utils/*.py` | 命令式：覆盖或删除上游 feed 同名包、注入内核补丁、替换上游库版本 |
| ③ 预置层 | `files/` | 整目录复制到 `openwrt/files`，随固件落地 |
| ④ 补丁层 | `patches/` | 补丁文件，需被代码真正调用才生效 |

### 3.1 声明层的自动修补（`prepare.py` 会做的事）

- 把 Makefile 里失效的相对引用改写为 `$(TOPDIR)` 绝对路径：
  `../../luci.mk` → `$(TOPDIR)/feeds/luci/luci.mk`，
  `../../lang/golang/golang-package.mk` → `$(TOPDIR)/feeds/packages/lang/golang/golang-package.mk`
  （后者是本地新增的改写，ddns-go 依赖它才能编译）；
- 尝试在插件的 `po/` 下建立 `zh-cn -> zh_Hans` 软链。注意**实际行为**：该符号链接只在 `zh_Hans` 不存在、或 `zh_Hans` 是个普通文件时才会创建；`zh_Hans` 已是目录时直接跳过。
  immortalwrt 系插件普遍自带 `po/zh_Hans`，所以这条修补多数情况下不会触发 —— 这**不影响** `luci-i18n-*-zh-cn` 的生成，因为 `openwrt/luci` 的 `luci.mk` 自带 `LUCI_LC_ALIAS.zh_Hans=zh-cn` 映射；
- 复制完成后删除包目录内的 `.git`；
- 若配置里的 `PATH` 在仓库中不存在，直接抛 `FileNotFoundError` **终止整个 prepare 阶段**。

### 3.2 脚本层的硬编码特殊处理

这些**不在** `extpackages.config` 里，改动它们必须同步文档：

| 对象 | 处理位置 | 处理方式 |
| --- | --- | --- |
| `netdata` | `prepare.py::prepare_cfg()` | 用 immortalwrt/packages 覆盖 feed 中的同名包 |
| `tailscale`、`luci-app-tailscale-community` | `prepare.py::prepare_cfg()` | 先删除 feed 中被固定的同名包，再由 extpackages 引入最新版。（本 fork 已把该组合列入排除清单，这段代码目前只空跑，保留是为了与上游一致） |
| `easytier`、`luci-app-easytier` | `prepare.py::prepare_cfg()` | **本地新增**：把仓库根的 `version.mk` 复制到 `package/cmzj_packages/`，供两个包的 `-include ../version.mk` 读取 |
| `golang` | `prepare.py::prepare_cfg()` | 整体替换为 sbwml/packages_lang_golang，分支取 `golang_version` |
| turboacc 相关 | `prepare.py::prepare_cfg()` | 注入内核补丁 952 / 953 / 613；替换 libnftnl、firewall4、nftables |
| `dnsmasq` → `dnsmasq-full` | `utils/openwrt.py::fix_problems()` | 改写 `include/target.mk` |
| `broadcom.mk` 路径 | `utils/openwrt.py::fix_problems()` | 修正 `b43-fwsquash.py` 路径 |
| rust 的 `llvm.download-ci-llvm` | `utils/openwrt.py::fix_problems()` | 由 `true` 改为 `false` |

> ⚠️ `patches/bcm27xx-gpu-fw.patch` 在上游 `fix_problems()` 中是**被注释掉的**，属留存文件、**并未生效**；
> 要用起来必须在代码里调用 `apply_patch`。

### 3.3 本地排除清单（`local.config`，本 fork 的核心机制）

> **目的**：把"本地不需要上游某个插件"表达成**新增文件里的开关**，而不是删改上游文件，
> 从而让上游合并几乎不产生冲突。

- **位置**：`config/<目标>/OpenWrt-K/local.config`。它位于 `OpenWrt-K/` 子目录，**不参与**顶层 `*.config` 拼接；
- **解析**：`build_helper/utils/local_exclude.py`，在 `parse_configs()` **出口处**应用，
  一次拦两层 —— 既决定"要不要拉源码"，也决定"要不要进 `.config`"；
- **两个键**：
  - `extpackages_exclude=`：按 `extpackages.config` 中的 `NAME` 精确匹配。命中者**不克隆、不复制**源码，自然也不进固件；
  - `configs_exclude=`：按配置符号名匹配，支持 fnmatch 通配（如 `CONFIG_PACKAGE_luci-i18n-ddns-zh-*`）。命中者从拼接后的配置文本中整行剔除，兼容 `CONFIG_X=y` 与 `# CONFIG_X is not set` 两种写法；
- **写法（三种可混用）**：
  - 单行多值：`configs_exclude=A,B,C`
  - 同名键累加：同名键可重复出现、值依次累加 —— **推荐一行一项**，便于逐项写注释
  - 行尾注释：`#` 之前留空白即可，如 `extpackages_exclude=tailscale  # 改用 EasyTier`
- **容错**：清单文件缺失、键缺失、键留空，都表示"不排除任何内容"，此时行为与上游**完全一致**；
- **边界**：本机制只做"剔除"，不会新增或改写任何开关。被排除的包若仍被其它选中包依赖，`defconfig` 会按依赖重新拉齐 —— 那时要把依赖项也写进清单。
- **当前内容**：见第 4.1 节中标记为 `✗` 的条目；清单文件里的每一项都带注释，写明它对应上游哪个编号、为什么排除。

### 3.4 本地 xray 透明代理（本 fork 的定制）

与上游最大的不同：**不再依赖 passwall / OpenClash 生成规则**，而是"官方 xray-core + 自写 nft 片段"。

| 环节 | 实现 | 落点 |
| --- | --- | --- |
| 内核能力 | `kmod-nft-tproxy`（`tproxy` 表达式）、`kmod-nft-socket`（`socket transparent`）；`kmod-nf-tproxy` / `kmod-nf-socket` / `kmod-nf-conntrack` 由依赖自动拉齐 | `config/<目标>/kmod.config` |
| 代理核心 | 官方 feed 的 `xray-core`（自带 `/etc/init.d/xray` 与 `/etc/config/xray`，版本与 passwall-packages 同为 26.9.9 一系） | `config/<目标>/network.config` |
| nft 规则 | `files/etc/nftables.d/xray.nft`，由 `firewall4` 自动 include 进 `table inet fw4`；`cn_ipv4` / `cn_ipv6` set 由同目录的 `.conf` 提供 | `files/` |
| 运行身份 | `xray` 用户/组 = uid 0、gid 966；由 `zzz-xray-user`（开机创建）与覆盖版 `init.d/xray`（`procd_set_param user/group`）共同保证 | `files/` |
| 启停 | `start-tproxy` / `stop-tproxy` 配置 `fwmark 0x11` 与本地路由表 100（v4）/106（v6） | `files/usr/bin/` |

**改动这块时必须同时想到的四件事**：

1. 规则里只要出现 `tproxy`，就必须有 `kmod-nft-tproxy`；出现 `socket transparent`，就必须有 `kmod-nft-socket`。**这两个不能跟随"代理清理"一起删掉**；
2. `meta skgid 966` 要生效，xray 必须以 gid 966 运行 —— 光建用户不够，还得让 init 用 `procd_set_param group` 切过去；
3. 启停脚本依赖 `ip-full`（BusyBox 的 `ip` 做不了带 table 的 rule/route）；
4. 这条链路**不需要 iptables**：`iptables-nft` 与 `iptables-mod-ipopt` 已在排除清单里，防火墙完全走 `firewall4` + nftables 原生语法。`kmod-nft-compat` 作为内核兼容层保留（体积小，且允许在 nft 规则里使用 xtables 风格匹配）。

---

## 4. 当前插件清单

> 本节是活文档。任何插件的增 / 改 / 删，都必须同步修改本节（见第 8 节）。
> 数据来源：`config/x86_64/OpenWrt-K/extpackages.config`（与 `config/rpi4b/`、`config/default-extpackages.config` 逐字节一致）。
> 启用状态依据各目标顶层 `*.config` 中**显式书写**的 `CONFIG_PACKAGE_*` 判定（`kmod-*`、`luci-app-*` 等同义名已折算）。
> ⚠️ 手写片段**不含** `make defconfig` 自动推导的依赖项，因此 `·` 只表示"未显式启用"，**不代表绝不会进固件**。
> 图例：`✔` 启用；`·` 未显式启用；`✗` 被 `local.config` 排除（不克隆、不复制、不进固件）。

### 4.1 拓展软件包（extpackages.config，37 项）

“路径”列的 `.` 表示**仓库根目录即包目录**；“分支”列的 `—` 表示使用仓库默认分支。

| # | 名称 | 来源仓库 | 路径 | 分支 | x86_64 | rpi4b |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | luci-app-usb-printer | coolsnowwolf/luci | applications/luci-app-usb-printer | — | ✔ | ✔ |
| 2 | luci-app-vlmcsd | immortalwrt/luci | applications/luci-app-vlmcsd | — | ✔ | · |
| 3 | luci-app-cifs-mount | coolsnowwolf/luci | applications/luci-app-cifs-mount | — | ✔ | ✔ |
| 4 | luci-app-netdata | coolsnowwolf/luci | applications/luci-app-netdata | — | ✔ | ✔ |
| 5 | vlmcsd | immortalwrt/packages | net/vlmcsd | — | ✔ | · |
| 6 | r8168 | coolsnowwolf/lede | package/kernel/r8168 | — | ✔ | ✔ |
| 7 | shortcut-fe | chenmozhijin/turboacc | shortcut-fe | package | · | · |
| 8 | luci-app-rclone | immortalwrt/luci | applications/luci-app-rclone | — | · | ✔ |
| 9 | tailscale | GuNanOvO/openwrt-tailscale | package/tailscale | — | ✗ | ✗ |
| 10 | luci-app-tailscale-community | Tokisaki-Galaxy/luci-app-tailscale-community | luci-app-tailscale-community | — | ✗ | ✗ |
| 11 | luci-app-fileassistant | kenzok8/openwrt-packages | luci-app-fileassistant | — | ✔ | ✔ |
| 12 | luci-app-passwall | Openwrt-Passwall/openwrt-passwall | luci-app-passwall | — | ✗ | ✗ |
| 13 | openwrt-passwall-packages | Openwrt-Passwall/openwrt-passwall-packages | . | — | ✗ | ✗ |
| 14 | passwall2 | Openwrt-Passwall/openwrt-passwall2 | luci-app-passwall2 | — | ✗ | ✗ |
| 15 | nft-fullcone | chenmozhijin/turboacc | nft-fullcone | package | ✔ | ✔ |
| 16 | luci-app-turboacc | chenmozhijin/turboacc | luci-app-turboacc | — | ✔ | ✔ |
| 17 | luci-app-adguardhome | chenmozhijin/luci-app-adguardhome | . | — | ✗ | ✗ |
| 18 | luci-app-argon-config | jerrykuku/luci-app-argon-config | . | — | ✔ | ✔ |
| 19 | luci-app-diskman | lisaac/luci-app-diskman | applications/luci-app-diskman | — | ✔ | ✔ |
| 20 | luci-app-netspeedtest | muink/luci-app-netspeedtest | . | — | ✔ | ✔ |
| 21 | luci-app-wechatpush | tty228/luci-app-wechatpush | . | — | ✔ | ✔ |
| 22 | luci-theme-argon | jerrykuku/luci-theme-argon | . | — | ✔ | ✔ |
| 23 | luci-app-socat | chenmozhijin/luci-app-socat | luci-app-socat | — | ✔ | ✔ |
| 24 | r8125 | sbwml/package_kernel_r8125 | . | — | ✔ | ✔ |
| 25 | luci-app-openclash | vernesong/OpenClash | luci-app-openclash | — | ✗ | ✗ |
| 26 | wrtbwmon | brvphoenix/wrtbwmon | wrtbwmon | — | · | · |
| 27 | ddns-scripts_aliyun | coolsnowwolf/lede | package/lean/ddns-scripts_aliyun | — | ✗ | ✗ |
| 28 | luci-app-qbittorrent | immortalwrt/luci | applications/luci-app-qbittorrent | openwrt-24.10 | ✗ | ✗ |
| 29 | qBittorrent-Enhanced-Edition | immortalwrt/packages | net/qBittorrent-Enhanced-Edition | — | ✗ | ✗ |
| 30 | qt6base | immortalwrt/packages | libs/qt6base | — | ✗ | ✗ |
| 31 | qt6tools | immortalwrt/packages | utils/qt6tools | — | ✗ | ✗ |
| 32 | libdouble-conversion | immortalwrt/packages | libs/libdouble-conversion | — | ✗ | ✗ |
| 33 | protobuf-compat | immortalwrt/packages | libs/protobuf/protobuf-compat | — | ✗ | ✗ |
| 34 | luci-app-ddns-go | immortalwrt/luci | applications/luci-app-ddns-go | — | · | ✔ |
| 35 | ddns-go | immortalwrt/packages | net/ddns-go | — | · | ✔ |
| 36 | easytier | EasyTier/luci-app-easytier | easytier | — | ✔ | ✔ |
| 37 | luci-app-easytier | EasyTier/luci-app-easytier | luci-app-easytier | — | ✔ | ✔ |

**已知情况说明**（不是错误，是有意为之，别"顺手修正"）：

- 编号 `1～33` 与上游 `extpackages.config` 一一对应，`34` 起为本地新增。**本地不删除上游条目**：需要关闭某项时写进 `local.config`，合并上游才省事。
- 第 7 项 `shortcut-fe`：其内核模块（`kmod-shortcut-fe`、`kmod-shortcut-fe-cm`、`kmod-fast-classifier`、`kmod-shortcut-fe-drv`）被 `compile.config` 的 `kmod_compile_exclude_list` **排除编译**，属"保留源码、当前不启用"。
- 第 9、10、27～33 项**被 `local.config` 排除**：tailscale 组合（9、10）、旧 DDNS 方案（27）、qBittorrent 及 Qt6 / libtorrent / boost 依赖链（28～33）。它们既不进固件，也不会被复制源码；上游声明保持原样，随时可以恢复。
- 第 12～14、25 项（passwall 家族与 OpenClash）**被 `local.config` 排除**：代理方案改为「官方 `xray-core` + 自写 nft 规则」，见第 3.4 节与 UC-0006 / UC-0007。第 13 项 `openwrt-passwall-packages` 是包合集，其中 `xray-core` 改从官方 feed 启用。
- 第 17 项 `luci-app-adguardhome` 已改用**官方实现**：扩展包条目保留、由 `local.config` 排除，改由官方 feed 的 `luci-app-adguardhome`（界面）与 `adguardhome`（守护进程包）接管，见 UC-0011。
- 第 26 项 `wrtbwmon`：两个目标都**未显式启用**，仅声明（保留源码）。
- 第 34、35 项（`luci-app-ddns-go`、`ddns-go`）取自 immortalwrt（OpenWrt 官方 `packages` / `luci` 均无这两个包）；`ddns-go` 的 `../../lang/golang/golang-package.mk` 需由 `prepare.py` 自动改写为 `$(TOPDIR)` 路径后才能编译。
- 第 36、37 项（`easytier`、`luci-app-easytier`）来自同一仓库，克隆只发生一次；**本体必须显式声明**，否则 LuCI 界面缺少 `/usr/bin/easytier` 而无法工作；两个包的版本号由仓库根的 `version.mk` 统一提供（`prepare.py` 会把它复制到 `package/cmzj_packages/`）。
- 第 28 项 `luci-app-qbittorrent` 的 `openwrt-24.10` 分支是上游的版本兼容妥协——虽然当前已被排除，但恢复时不要擅自改分支。

### 4.2 由 `files/` 预置的插件配置与工具

`files/` 会整目录覆盖复制进 OpenWrt 源码树（`openwrt/files`），改动或删除其中文件都会影响固件。

| 路径 | 内容 |
| --- | --- |
| `files/etc/nftables.d/xray.nft` | 本地透明代理 nft 片段：用 `tproxy` 把选中流量交给 xray，并用 `meta skgid 966` 放过 xray 自身的出站连接。`firewall4` 会自动 include `/etc/nftables.d/*.nft` |
| `files/etc/nftables.d/cn_ipv4.conf`、`cn_ipv6.conf` | 上面规则 `include` 的国内地址集（`cn_ipv4` / `cn_ipv6` 两个 set），直连判定用 |
| `files/usr/bin/start-tproxy`、`stop-tproxy` | 手动启停全局透明代理：配置 `fwmark 0x11` + `table 100/106` 的本地路由（依赖 `ip-full`） |
| `files/etc/init.d/xray` | **覆盖**官方 init：启动前兜底创建运行身份，并以 `xray` 用户/组（gid 966）运行 |
| `files/etc/uci-defaults/zzz-xray-user` | 首次开机创建 `xray` 用户/组（uid 0 / gid 966），与 nft 规则里的 `skgid 966` 对应 |
| `files/etc/config/xray` | 预置 xray 的 uci 配置：`enabled=1` + `confdir=/etc/xray`（配置文件需自备 `config.json`） |
| `files/etc/adguardhome/adguardhome.yaml` | AdGuardHome 主配置（官方方案的 `config_file`）。内容已按本地环境调整（见 UC-0010），包方案见 UC-0011 |
| `files/etc/adguardhome/data/filters/` | AdGuardHome 工作目录（官方 `work_dir`，本地设为 `/etc/adguardhome`）下的订阅缓存，编译期由 `prepare.py` 下载刷新；二进制由官方 `adguardhome` 包编译提供，装到 `/usr/bin/AdGuardHome` |
| `files/etc/AdGuardHome-dnslist(by cmzj).yaml` | 由 `prepare.py` **构建期下载生成**（不纳入版本控制）；当前主配置已清空 `upstream_dns_file`，该清单实际未被引用 |
| `files/etc/mosdns/config.yaml` | mosdns 主配置（使用者提供）：UDP/TCP 监听 `:5335`（AdGuardHome 的上游）、`http_server` 监听 `:8443`；含 hosts、缓存、双栈 ECS（`ecs_handler` × 2 由 `qtype` 分派）、域名分流（block / proxy / direct / easytier / dhcp）与 DoT 上游。**只使用官方 mosdns 插件**，不依赖任何自定义分支。构建期由 `files/` 覆盖包自带的默认配置 |
| `files/etc/mosdns/domain_set/` | 域名分流规则文本（`geosite_category-ads-all` / `geosite_gfw` / `geosite_github` / `geosite_google`，约 4 MB，随固件落地） |
| `files/etc/mosdns/ip_set/` | IP 集合规则（`geoip_private.txt`）；当前配置尚未引用，属预留 |
| `files/etc/uci-defaults/zzz-chenmozhijin` | 首次开机写入 LAN 地址、dnsmasq 缓存开关、aria2 配置、固件署名（AdGuardHome 相关已拆出，SmartDNS 相关随换用 mosdns 移除） |
| `files/etc/uci-defaults/zzz-adguardhome` | AdGuardHome 首次开机配置（官方方案的 uci 选项 + dnsmasq 上游指向）；从 `zzz-chenmozhijin` 拆出，自带 `has_package` 与等待逻辑，不再使用时直接删本文件即可 |
| `files/etc/uci-defaults/zzz-mosdns` | 启用并启动 mosdns（mosdns 包的 postinst 会 stop + disable，必须显式 enable）；配置缺失时不启动 |
| `files/usr/share/cmzj/openwrt-k_tool.sh` | 让固件支持 `openwrt-k` 命令升级非官方源软件包 |

### 4.3 补丁

| 文件 | 状态 |
| --- | --- |
| `patches/bcm27xx-gpu-fw.patch` | 仅影响 bcm27xx（树莓派）GPU 固件；**当前调用处被注释，未生效** |

---

## 5. 新增扩展插件指南

严格按顺序执行，任何一步跳过都可能让 CI 在 prepare 阶段直接失败。

### Step 0 · 先判断"真的需要拓展包吗"

优先用 OpenWrt 官方 feed 自带的包：

- 官方有 → **只改** `config/<目标>/*.config`，**不要**动 `extpackages.config`；
- 官方没有，或版本太旧 → 才走下面的拓展包流程。

判定方式：在 OpenWrt 源码树里 `./scripts/feeds search <关键词>`；本地没有源码树时，可到 <https://github.com/openwrt/packages>、<https://github.com/openwrt/luci> 查找。

### Step 1 · 确认三个坐标

| 坐标 | 要求 |
| --- | --- |
| 仓库 URL | 必须是能公开 clone 的仓库（克隆时用 `depth=1` 浅克隆） |
| 仓库内路径 | **必须亲自核对存在**；路径写错会让 prepare 阶段抛 `FileNotFoundError` 并整体失败 |
| 分支 | 不指定就用仓库默认分支（留空字符串）；指定就必须真实存在 |

### Step 2 · 在 `extpackages.config` 追加条目

格式是**严格正则匹配**的：`^EXT_PACKAGES_(NAME|PATH|REPOSITORIE|BRANCH)\[(\d+)\]="(.*)"$`

```ini
EXT_PACKAGES_NAME[38]="luci-app-example"
EXT_PACKAGES_PATH[38]="applications/luci-app-example"
EXT_PACKAGES_REPOSITORIE[38]="https://github.com/example/luci-app-example"
EXT_PACKAGES_BRANCH[38]=""
```

硬性约束：

- **四行齐全**，缺任何字段都会抛 `ConfigParseError`；没有分支就写空字符串 `""`；
- **行首不能有空格**，**行尾不能有注释或多余空格**，必须是 `...="值"` 直接收尾；
- `NAME` 在同一目标内**必须唯一**，重复会抛 `ConfigParseError`；
- 编号 `[n]` 只作分组键，**不要求连续**，推荐取当前最大编号 + 1；
- 字段名是 `REPOSITORIE`（上游历史拼写，**不要"改正"成 `REPOSITORY`**）；
- **三个文件别改漏**：`config/<目标>/OpenWrt-K/extpackages.config`、`config/default-extpackages.config`，以及其它目标的同名文件。

### Step 3 · 在目标配置里启用它

| 插件类型 | 加在哪 | 示例 |
| --- | --- | --- |
| LuCI 应用 | `config/<目标>/luci.config` | `CONFIG_PACKAGE_luci-app-example=y` |
| 语言包 | 同上，紧挨其后 | `CONFIG_PACKAGE_luci-i18n-example-zh-cn=y` |
| 子选项 | 同上 | `CONFIG_PACKAGE_luci-app-example_INCLUDE_xxx=y` |
| 内核模块 | `config/<目标>/kmod.config` | `CONFIG_PACKAGE_kmod-example=y` |
| 网络组件 | `config/<目标>/network.config` | — |
| 其它工具 | `config/<目标>/other.config`、`utilities.config` | — |

多个目标都要就逐个改。**声明了但不加开关，包不会进固件**。

### Step 4 · 若上游 feed 已有同名包

必须在 `prepare.py::prepare_cfg()` 中先删除 feed 里的同名目录，再让拓展包复制进来（可参照 `netdata`、`tailscale` 的写法）：

```python
shutil.rmtree(os.path.join(openwrt.path, "feeds", "packages", "net", "<包名>"), ignore_errors=True)
shutil.rmtree(os.path.join(openwrt.path, "feeds", "luci", "applications", "<包名>"), ignore_errors=True)
```

否则会出现同名包重复定义，在 `feeds install` 或 `defconfig` 阶段报错。

### Step 5 · 若插件需要预置配置

- 开机一次性写入 → `files/etc/uci-defaults/`（文件名以 `zzz-` 开头的最后执行）；
- 插件自带配置目录 → `files/etc/<插件目录>/`。

### Step 6 · 若插件需要编译期下载二进制

在 `prepare.py::prepare_cfg()` 中追加下载任务，参照 AdGuardHome 与 OpenClash 核心的写法：

- 下载目标写到 `files/<目标路径>`，并 `os.chmod(..., 0o755)`；
- 与架构相关的必须补全 `match arch` 映射分支；
- 下载路径要放在 `paths.get_tmpdir()` 之外，因为临时目录清理会带走文件。

### Step 7 · 若插件需要补丁或替换上游包版本

- 单纯补丁：可放 `patches/`，但**必须在代码里调用 `apply_patch`**，否则不会生效；
- 需要替换整个上游包（如 libnftnl / firewall4 / nftables）：参照 turboacc 段落，先探测版本再做目录替换，并在版本找不到时给出降级警告。

### Step 8 · 本地校验

见第 10 节。至少要确认：条目格式合法、`NAME` 不重复、四个字段齐全、目标配置里有对应开关。

### Step 9 · 同步文档（强制）

见第 8 节。**没有同步文档的插件改动，视为未完成。**

---

## 6. 更新插件指南

| 要改什么 | 怎么改 | 注意 |
| --- | --- | --- |
| 换仓库 | 改 `REPOSITORIE` | 必须重新核对 `PATH` 在新仓库里是否存在 |
| 换路径 | 改 `PATH` | 路径错 = prepare 直接失败 |
| 换分支 | 改 `BRANCH` | 注意被"钉版本"的条目（如 `luci-app-qbittorrent` 的 `openwrt-24.10`），别顺手升级 |
| 换显示名 / 包名 | 改 `NAME` | 等价于"删除旧条目 + 新增新条目"，`package/cmzj_packages/<NAME>` 目录名也会变 |
| 新增来源仓库 | 追加新编号条目 | 编号可以跳号，不必重排 |
| 改启用范围 | 改目标 `*.config` | 声明与启用是**两件事**，别只改一处 |

更新完成后：

1. 逐项核对 `PATH` 仍存在（能在 GitHub 上打开对应目录）；
2. 在 `UPSTREAM-CHANGES.md` 追加一条"更新插件"记录；
3. 同步 `AGENTS.md` 第 4.1 节表格中被改动的那一行。

---

## 7. 关闭或删除插件指南

> ⚠️ **优先用排除清单，而不是删除**。
> 若只是"本地不需要"，请写进 `config/<目标>/OpenWrt-K/local.config` 的 `extpackages_exclude`（连源码都不拉）
> 或 `configs_exclude`（只关开关），让上游文件保持原样。
> **只有确认要连上游声明一起移除时**，才走下面的删改流程。

删除必须**三处同清**，缺一处就留下"半死"状态：

1. `extpackages.config` 中的四行条目（三个目标的文件都要清）；
2. 各目标 `*.config` 中该插件的所有 `CONFIG_PACKAGE_*` 开关（含语言包 `luci-i18n-*` 与子选项 `_INCLUDE_*`）；
3. `files/` 中该插件专属的预置文件。

额外检查：

- 若该插件在 `prepare.py` 中被**特殊引用**（netdata / tailscale / golang / turboacc / EasyTier 的 `version.mk`），必须同步删除或改写对应代码块；
- 若该插件被其它包**依赖**（例如某个客户端会连带拉入一整套库包），必须一并评估是否连带删除，避免留下无人使用的构建链；
- 若该插件出现在 README 的"内置功能"列表中，一并更新；
- 在 `UPSTREAM-CHANGES.md` 登记一条记录（让后人知道"这是刻意删掉的，不是漏掉了"）。

---

## 8. 文档同步铁律 ⚠️

> **任何插件的"新增 / 更新 / 删除"，以及任何会改变插件集合的脚本改动，都必须在同一批次内同时更新：**
>
> 1. `AGENTS.md` —— 第 4 节"当前插件清单"
> 2. `UPSTREAM-CHANGES.md` —— 第五节差异索引表 + 第六节条目详情
>
> **未同步这两份文档的插件改动，视为未完成，不得提交。**

| 场景 | AGENTS.md | UPSTREAM-CHANGES.md | README.md |
| --- | --- | --- | --- |
| 新增拓展插件 | 必须（4.1 加行） | 必须（新增条目） | 建议（内置功能列表） |
| 更新插件（仓库 / 路径 / 分支） | 必须（改行） | 必须（新增条目） | 视情况 |
| 关闭或删除插件 | 必须（改行） | 必须（新增条目） | 建议 |
| 改 `prepare.py` 的特殊处理 | 必须（第 3 节 + 第 4 节） | 必须 | 视情况 |
| 改 `local.config` 的排除内容 | 必须（4.1 的状态列） | 必须 | 视情况 |
| 改 `files/` 预置 | 必须（4.2） | 必须 | 视情况 |
| 改补丁及其调用 | 必须（4.3） | 必须 | 否 |
| 仅改 `compile.config` 版本号 | 建议 | 必须 | 建议 |
| 仅改开关（不增删插件） | 建议（保持状态列准确） | 建议 | 否 |

> **CI 提醒**：CI 触发路径只有 `.github/**`、`files/**`、`build_helper/**`、`config/**`，
> `AGENTS.md`、`UPSTREAM-CHANGES.md`、`README.md` 的改动**不会**触发构建。
> 这是设计如此，也意味着文档一致性**没有任何自动校验托底**，只能靠自觉。

---

## 9. 相对上游的差异管理与合并

### 三方关系

| 角色 | 地址 | 用途 |
| --- | --- | --- |
| upstream（上游） | <https://github.com/chenmozhijin/OpenWrt-K> | 差异比较的基准 |
| origin（本仓库） | <https://github.com/vizaxe/OpenWrt-K> | 实际推送目标 |

### 差异登记簿

所有相对上游的本地改动都登记在 [UPSTREAM-CHANGES.md](UPSTREAM-CHANGES.md)：

- **第三节**记录当前的同步基准提交与日期；
- **第五节**是差异索引表（编号 / 类型 / 对象 / 文件 / 冲突风险 / 同步动作）；
- **第六节**是条目详情，说明"为什么这么改"，供冲突时判断意图。

### 合并上游的流程

> 涉及远程仓库与分支的操作（`remote add`、`fetch`、`merge`、`rebase`、`push`）
> **必须先向用户说明并取得明确同意**后才能执行。

1. **清点本地**：`git status` 确认没有未提交的临时改动；
2. **通读账簿**：打开 `UPSTREAM-CHANGES.md` 第五节，明确"哪些文件是我方改过的"；
3. **配置上游**：`git remote -v` 检查是否已有 upstream，没有则 `git remote add upstream https://github.com/chenmozhijin/OpenWrt-K.git`；
4. **拉取**：`git fetch upstream`；
5. **预览**：`git log --oneline HEAD..upstream/main`、`git diff HEAD upstream/main --stat`；
6. **合并**：`git merge upstream/main`（用 merge 还是 rebase 由用户决定）；
7. **处理冲突**：凡在差异索引表里登记过的文件，冲突时**默认保留本地意图**，再逐条评估上游改动是否值得吸收；
8. **合并后复核**：重点检查 `extpackages.config`、各目标 `*.config`、`prepare.py` 是否被上游整段覆盖；
9. **刷新账簿**：更新第三节的基准提交与日期，并在第五节标注各条差异的同步结果；
10. **触发验证**：推送后由 CI 全流程验证；纯文档改动不会触发构建，需要时用 `workflow_dispatch` 手动跑。

### 冲突风险分级（登记时使用）

| 级别 | 含义 | 典型场景 |
| --- | --- | --- |
| 低 | 纯追加，上游不会碰到同一区域 | 在 `extpackages.config` 末尾加条目、新增独立文件（如 `local.config`） |
| 中 | 修改上游已有行 | 改 `compile.config` 版本号、改 `luci.config` 已有开关、改 `prepare.py` |
| 高 | 重写 / 删除上游内容，或与上游改动区域重叠 | 删除 feed 同名包、替换整个上游包目录、大段重写 `prepare_cfg()` |

---

## 10. 验证清单

| 改动类型 | 验证动作 |
| --- | --- |
| `extpackages.config` | 跑下面的格式校验脚本；人工核对 `PATH` 真实存在 |
| `local.config` | 跑下面的清单校验脚本；确认被排除项确实不再出现 |
| 目标 `*.config` | 确认同一开关只在一处定义；确认插件开关与 extpackages 声明对应 |
| `compile.config` | 确认 `openwrt_tag/branch` 是真实存在的 tag（如 `v25.12.5`） |
| `prepare.py` / `build.py` / `utils/*.py` | `cd build_helper && ruff check .`（line-length 159，`select = ["ALL"]`） |
| `files/etc/uci-defaults/*` | `sh -n files/etc/uci-defaults/<文件>` 语法检查 |
| `files/etc/**/*.yaml` | `python3 -c "import yaml;yaml.safe_load(open('files/etc/adguardhome/adguardhome.yaml'))"` |
| `patches/*.patch` | 在 OpenWrt 源码树中 `git apply --check <补丁>` |
| 全量 | 推送触发 CI，或在 GitHub 上手动 `workflow_dispatch` |

### extpackages 格式校验片段

```bash
python3 - <<'PY'
import re

path = "config/x86_64/OpenWrt-K/extpackages.config"
pat = re.compile(r'^EXT_PACKAGES_(NAME|PATH|REPOSITORIE|BRANCH)\[(\d+)\]="(.*)"$')
groups, names, bad = {}, {}, []

for no, line in enumerate(open(path, encoding="utf-8"), 1):
    s = line.strip()
    if not s or not s.startswith("EXT_PACKAGES_"):
        continue
    m = pat.match(s)
    if not m:
        bad.append((no, s))
        continue
    key, idx, val = m.group(1), m.group(2), m.group(3)
    groups.setdefault(idx, {})[key] = val
    if key == "NAME":
        names.setdefault(val, []).append(no)

for no, s in bad:
    print(f"[格式错误] 第 {no} 行: {s}")
for idx, kv in sorted(groups.items(), key=lambda x: int(x[0])):
    miss = {"NAME", "PATH", "REPOSITORIE", "BRANCH"} - kv.keys()
    if miss:
        print(f"[字段缺失] 编号 {idx}: 缺 {sorted(miss)}")
for name, lines in names.items():
    if len(lines) > 1:
        print(f"[名称重复] {name}: 出现在第 {lines} 行")

print(f"检查完成：共 {len(groups)} 组条目，格式错误 {len(bad)} 处")
PY
```

### local.config 校验片段

```bash
python3 - <<'PY'
# 校验本地排除清单：键名合法、同名键累加正确、被排除的包名确实存在于 extpackages
import os, re

for target in ("x86_64", "rpi4b"):
    base = os.path.join("config", target, "OpenWrt-K")
    cfg = os.path.join(base, "local.config")
    if not os.path.isfile(cfg):
        print(f"{target}: 无 local.config（合法）")
        continue
    keys, values = {"extpackages_exclude", "configs_exclude"}, {}
    for line in open(cfg, encoding="utf-8"):
        line = re.split(r"\s+#", line.strip(), maxsplit=1)[0].strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        k = k.strip()
        if k not in keys:
            print(f"[未知键] {target}: {k}")
            continue
        values.setdefault(k, []).extend(i.strip() for i in v.split(",") if i.strip())
    names = set(re.findall(r'^EXT_PACKAGES_NAME\[\d+\]="(.*?)"$',
                           open(os.path.join(base, "extpackages.config"), encoding="utf-8").read(), re.M))
    ghost = set(values.get("extpackages_exclude", [])) - names
    print(f"{target}: 排除拓展包 {len(values.get('extpackages_exclude', []))} 个、"
          f"排除开关 {len(values.get('configs_exclude', []))} 个"
          + (f"；[不存在于 extpackages] {sorted(ghost)}" if ghost else "；包名全部有效"))
PY
```

---

## 11. 环境约束与风险边界

### 执行环境

- 文件沙箱为 `workspace-write`：只能改动本仓库目录内的文件；
- **`/tmp` 在每条命令结束后会被清空**（沙箱每次调用都是全新的 tmpfs），跨命令传递的中间产物必须写在**工作目录内**；
- 网络可访问 GitHub。

### 必须先取得用户确认的操作

- 删除核心文件（`config/`、`build_helper/`、`files/`、`patches/` 下的关键文件）；
- 任何远程 Git 操作：`fetch`、`merge`、`rebase`、`push`、`reset`、`force` 系列；
- 引入新依赖（改 `build_helper/requirements.txt`、`pyproject.toml`）；
- 显著改变编译产物范围的动作（增删编译目标、改镜像格式矩阵）；
- 涉及真实发布、外部服务或付费资源的操作。

### 编码规范

- 本仓库只有 **Python** 与 **Shell**，不涉及 Go / Java / Nix，因此无需加载对应语言的编码规范 Skill；
- Python 遵循 `build_helper/pyproject.toml` 的 ruff 配置：`target-version = "py312"`、`line-length = 159`、`select = ["ALL"]`；
- 所有文件默认 UTF-8（无 BOM），面向用户的输出使用中文。

### 与上级规则的关系

上级 `~/.dsh/AGENTS.md` 的通用要求（思考与输出使用中文、进度面板、需求澄清门、交付摘要、高风险操作需确认等）在本仓库**继续有效**。
本文件是它在**项目层面**的补充与细化；两者冲突时以本文件为准。
